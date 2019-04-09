#  -*- coding: UTF8 -*-

import sys
import newrelic.agent

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.db import transaction

from silo_user.forgot_pass.db import ForgotPassword
from sys_base.exceptions import HeliosException

from api_helios.base import AbstractHeliosEndpoint


class ForgotPassReset(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Resets a User's password

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "token": "9Q9rGfymnFUjXmzkaAJw2u4js4eGKo3l",     // Password reset token
                    "password": "12345678"                           // New password to use
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

        # Truncate token to 32 characters to prevent attackers triggering a database error by
        # posting a 2,000 character long key and overflowing the Btree index

        token = request.POST.get('token', '')[:32]

        password = request.POST.get('password', '')[:255]

        # Sanitize inputs
        # =======================================================================

        if not token:
            return self.render_error(request, code='token_empty', status=400)

        if not password:
            return self.render_error(request, code='new_pass_empty', status=400)

        if len(password) < 8:
            return self.render_error(request, code='new_pass_too_short', status=400)

        # Reset password
        # =======================================================================

        try:

            with transaction.atomic():

                # Lock record to block other threads.

                record = ForgotPassword.objects.select_for_update().filter(key=token).first()

                if not record:
                    raise HeliosException(desc='This password reset token has expired', code='token_expired')

                user = record.user
                user.password = make_password(password)
                user.save()

                record.delete()

                # Clear all other reset tokens for the user
                ForgotPassword.objects.filter(user=user).delete()

            user = authenticate(email=user.email, password=password)

            if not user.is_authenticated():
                raise HeliosException(desc='User cannot be authenticated', code='auth_failure')

            login(request, user)


        # Trap errors
        # =======================================================================

        except HeliosException as e:

            if e.code in ['token_expired', 'auth_failure']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': user.hid
            }
        )
