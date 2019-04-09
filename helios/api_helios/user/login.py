#  -*- coding: UTF8 -*-

import newrelic.agent

from datetime import datetime
from django.contrib.auth import authenticate, login
from django.db import transaction

from silo_user.user.db import User
from user_util import UserUtil
from api_helios.base import AbstractHeliosEndpoint
from plant_hermes.account.db import TokenAccount


class Login(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Logs-in a User on the platform

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "email": "test@example.com",   // email address used when User was created
                    "password": "testpassword"  // password used when User was created
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

        email = request.POST.get('email', '')
        password = request.POST.get('password', '')[:255]

        clean_email = email.lower()  # Email addresses MUST be lowercase

        # IMPORTANT: authenticate() returns a User object with extra attributes.
        # See: https://docs.djangoproject.com/en/1.8/topics/auth/default/#how-to-log-a-user-in

        modified_user = authenticate(email=clean_email, password=password)

        if modified_user:
            if not modified_user.token_account:
                with transaction.atomic():
                    now = datetime.now()
                    token_account = TokenAccount.objects.create(updated=now)
                    token_account.hsm_sig = token_account.calculate_hsm_sig()
                    token_account.save()
                    thisuser = User.objects.filter(hid=modified_user.hid).select_for_update().first()
                    thisuser.token_account = token_account
                    thisuser.save()

            if modified_user.state == User.DELETED:
                return self.render_error(request, code='deleted_user', status=400)

            # If the User has a status that can log in, log them in. This sets their session cookie
            # and CSRF token

            login(request, modified_user)

            # Prevent 'speaking_as' spanning sessions by clearing it from the session on login

            if 'speaking_as' in request.session:
                del request.session['speaking_as']
                request.session.modified = True

            # If the user has helios_root access, set their root_active flag so they
            # can enter any Org

            if modified_user.is_staff:
                request.session['root_active'] = True
                request.session.modified = True

            reactivated = modified_user.state == User.DISABLED
            if reactivated:
                with transaction.atomic():
                    user = User.objects.select_for_update().get(id=modified_user.id)
                    user.state = (
                        User.ACTIVE
                        if UserUtil.is_complete(modified_user)
                        else User.INCOMPLETE
                    )
                    user.save()

        else:

            # If the User's credentials don't authenticate, find out why. Returning an error along the lines
            # of "you either have the wrong password OR this user doesn't exist" makes users sad and does NOT
            # improve security: an attacker can discover if a User exists by trying to sign-up as that email
            # address.

            if User.objects.filter(email=clean_email).exists():

                return self.render_error(request, code='wrong_password', status=400)

            else:
                return self.render_error(request, code='nonexistent_user', status=400)

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={
                'viewer_hid': modified_user.hid,
                'reactivated': reactivated
            }
        )
