#  -*- coding: UTF8 -*-

import sys
import newrelic.agent

from datetime import timedelta, datetime

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from plant_eos.handlers.helios.forgot_pass import dispatch_notice_forgot_pass
from silo_user.forgot_pass.db import ForgotPassword
from silo_user.user.db import User
from sys_base.exceptions import HeliosException

from api_helios.base import AbstractHeliosEndpoint


class ForgotPassSendEmail(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Sends a password reset email to the specified email, if it exists on the platform

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "email": "test@example.com"      // Email address to send reset email to
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": None
                    },
                    "success": true
                }
        """

        email = request.POST.get('email')

        # Sanitize inputs
        # =======================================================================

        if not email:
            return self.render_error(request, code='email_empty', status=400)

        try:
            validate_email(email)

        except ValidationError:
            return self.render_error(request, code='email_invalid')

        clean_email = email.lower()

        # Generate db records and send email
        # =======================================================================

        try:

            with transaction.atomic():

                user = User.objects.filter(email=clean_email).first()

                if not user:
                    raise HeliosException(desc='Email cannot be found', code='email_not_found')

                # Rate-limit requests to maximum of 3 requests per minute

                filters = {

                    'user': user,
                    'created__gte': datetime.now() - timedelta(minutes=1)
                }

                if ForgotPassword.objects.filter(**filters).count() > 2:
                    raise HeliosException(desc='Too many requests', code='too_many_requests')

                # Generate token and create event

                token = ForgotPassword.generate_key()

                ForgotPassword.objects.create(

                    user=user,
                    created=datetime.now(),
                    key=token
                )

                dispatch_notice_forgot_pass(

                    profile_owner=user,
                    token=token
                )


        # Trap errors
        # =======================================================================

        except HeliosException as e:

            if e.code in ['email_not_found', 'too_many_requests']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': None
            }
        )
