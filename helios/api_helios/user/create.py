#  -*- coding: UTF8 -*-

import sys
import newrelic.agent

from datetime import datetime

from django.contrib.auth.hashers import make_password

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.db import transaction
from plant_hermes.account.db import TokenAccount
from silo_message.intro_settings import IntroSettings
from silo_user.email.db import EmailConfirmation

from plant_eos.handlers.helios.new_user import dispatch_notice_join_platform

from silo_user.email.db import EmailAddress
from silo_user.user.db import User

from api_helios.base import AbstractHeliosEndpoint

from sys_base.exceptions import HeliosException

from .login import Login


class UserCreate(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Creates a User profile on the platform

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "email": "test@example.com",   // (ASCII), automatically converted to lowercase before storage
                    "password": "testpassword", // (unicode) 8-255 characters
                    "first_name": "Test"        // (unicode) 3-40 characters
                    "year": "1987"              // (unicode) 4 characters
                    "month": "02"               // (unicode) 2 characters
                    "date": "12"                // (unicode) 2 characters
                    "gid_is": "1"               // 1=Male,2=Female,3=Both
                    "gid_seeking": "1"          // 1=Male,2=Female,3=Both
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5"
                    },
                    "success": true
                }

        """

        email = request.POST.get('email')
        password = request.POST.get('password', '')[:255]

        try:

            # IMPORTANT: we convert all email addresses to lowercase using .lower(), because the database *is*
            # case sensitive, but the email protocol *is not*. If we failed to do this, attackers could
            # hijack profiles by using email addresses with mixed capitalization.

            clean_email = str(email).lower()

        except:
            return self.render_error(request, code='malformed_email', status=400)

        try:
            validate_email(clean_email)

        except ValidationError:
            return self.render_error(request, code='invalid_email', status=400)

        try:
            password = str(password)[:255]

        except:
            return self.render_error(request, code='malformed_password', status=400)

        if len(password) < 8:
            return self.render_error(request, code='invalid_password', status=400)

        # Create records
        # =======================================================

        try:

            with transaction.atomic():

                # Email Address
                # -----------------------------------

                # We have to test against EmailAddress (instead of User) to account for a user that's in the process
                # of changing from one email address to another

                if EmailAddress.objects.filter(email=clean_email).exists():
                    raise HeliosException(desc='Specified email is already in use', code='email_in_use')

                # Create User
                # -----------------------------------

                now = datetime.now()

                token_account = TokenAccount.objects.create(updated=now)
                token_account.hsm_sig = token_account.calculate_hsm_sig()

                token_account.save()

                user = User.objects.create(

                    token_account=token_account,
                    avatar_prefix=None,
                    avatar_set=False,
                    hid=User.generate_hid(),
                    email=clean_email,
                    first_name=None,
                    last_name=None,
                    dob=None,
                    gid_is=None,
                    gid_seeking=None,
                    is_staff=False,
                    created=now,
                    updated=now,
                    last_login=now,

                    # Burn 500ms of CPU time creating the password hash
                    password=make_password(password),

                    tagline=None,
                    bio=None,
                    roles=list(set([0]))  # 'ROLE_EVERYONE'
                )

                primary_email = EmailAddress.objects.create(

                    email=clean_email,
                    verified=False,
                    primary=True,
                    user=user
                )

                token = EmailConfirmation.generate_key()

                EmailConfirmation.objects.create(

                    user=user,
                    email=primary_email,
                    created=now,
                    key=token
                )

                intro_settings = IntroSettings.objects.create(

                    user=user
                )

                intro_settings.jitter_next_check()
                intro_settings.save()

                dispatch_notice_join_platform(

                    profile_owner=user,
                    token=token
                )


        except HeliosException as e:

            if e.code in ['email_in_use']:
                return self.render_error(request, code=e.code, status=400)
            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        ## Login with created cradentials
        return Login().post(request)
