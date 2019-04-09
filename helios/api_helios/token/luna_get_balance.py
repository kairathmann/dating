#  -*- coding: UTF8 -*-

import newrelic.agent

from api_helios.base import AbstractHeliosEndpoint
from silo_user.user.db import User
from sys_util.text.number import hid_is_valid


class LunaGetBalance(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Returns the user's current available and pending balances

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5"
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",
                        "confirmed": "13.37153846742200084",
                        "unconfirmed": "0.00000000312480023"
                    },
                    "success": true
                }
        """

        target_hid = request.POST.get('target_hid')

        if not request.user.is_anonymous:
            target_hid = target_hid or request.user.hid

        if not hid_is_valid(target_hid):
            return self.render_error(request, code='invalid_target_hid', status=400)

        upstream = self.get_upstream_for_platform(request)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        # Verify that either the sender is the viewer, or the viewer has helios_root set

        elif not (upstream['root_active'] or (upstream['viewer'].hid == target_hid)):
            return self.render_error(request, code='cannot_become_other_user', status=403)

        # Run db operations
        # =======================================================================

        target = User.objects.filter(hid=target_hid).prefetch_related('token_account').first()

        if not target:
            return self.render_error(request, code='nonexistent_target', status=400)

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                'confirmed': str(target.token_account.confirmed_balance),
                'unconfirmed': str(target.token_account.unconfirmed_balance)
            }
        )
