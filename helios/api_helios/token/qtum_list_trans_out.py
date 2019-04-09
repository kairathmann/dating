#  -*- coding: UTF8 -*-

import newrelic.agent

from api_helios.base import AbstractHeliosEndpoint

from plant_hermes.journal.outbound import JournalOut

from silo_user.user.db import User

from sys_util.text.number import hid_is_valid


class QtumListTransfersOut(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Returns a list of all outbound transfers from a user's account to the QTUM network. This is
            intended to be shown on the same screen as where they transfer tokens out of the platform. It's
            implemented as a separate endpoint because eventually we're going to have to paginate this data.

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

                        "items": [

                            {
                                "created": "2018-04-21 09:05:21",
                                "amount": "-5.0000741",             // Amount is always NEGATIVE
                                "luna_fee": "1.250018525",          // Fee is always POSITIVE
                                "total": "-3.750055575",
                                "dest_address": "qJ2wFcprHW2xdqEhvrioNnWzuRx1qiWXjM",
                                "send_gas": "0.000000623856134"
                            }
                        ]
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

        target = User.objects.filter(hid=target_hid).first()

        if not target:
            return self.render_error(request, code='nonexistent_target', status=400)

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                'items': [{

                    'created': item.created,
                    'amount': '-' + str(item.amount),
                    'luna_fee': str(item.luna_fee),
                    'total': '-' + str(item.total),
                    'dest_address': item.dest_address,
                    'send_gas': str(item.send_gas)

                } for item in JournalOut.objects.filter(user=target).order_by('-created')]
            }
        )
