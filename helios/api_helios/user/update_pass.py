#  -*- coding: UTF8 -*-

import newrelic.agent

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint

from silo_user.user.db import User


class UserUpdatePass(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Updates a User's password. Implemented as a separate endpoint because updating a password
            requires a CPU-intensive hashing step.

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
                    "old_password": "12345678",  // (unicode) 8-255 characters
                    "new_password": "87654321"   // (unicode) 8-255 characters
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

        target_hid = request.POST.get('target_hid')
        old_password = request.POST.get('old_password')[:255]
        new_password = request.POST.get('new_password')[:255]

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        user = upstream['target_user']

        # If the viewer doesn't have helios_root active, check old_password
        # --------------------------------------------------------------------------

        if not upstream['root_active']:

            if not old_password:
                return self.render_error(request, code='old_password_empty', status=400)

            # Handle someone trying to overflow the old_password parameter

            if not user.check_password(old_password):
                return self.render_error(request, code='old_password_invalid', status=400)

        if not new_password or len(new_password) < 8:
            return self.render_error(request, code='password_too_short', status=400)

        with transaction.atomic():

            # Reselect target_user with an UPDATE LOCK
            user = User.objects.select_for_update().get(id=user.id)

            user.password = make_password(new_password)
            user.save()

        # If the viewer doesn't have helios_root active, log them in with the new password
        # --------------------------------------------------------------------------

        if not upstream['root_active']:

            user = authenticate(email=user.email, password=new_password)

            if not user.is_authenticated():
                return self.render_error(request, code='authentication_failed', status=401)

            login(request, user)

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
