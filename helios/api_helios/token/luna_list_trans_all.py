#  -*- coding: UTF8 -*-

import newrelic.agent

from operator import itemgetter

from api_helios.base import AbstractHeliosEndpoint

from plant_hermes.journal.inbound import JournalIn
from plant_hermes.journal.outbound import JournalOut
from plant_hermes.journal.user import JournalUser

from silo_user.user.db import User

from sys_util.text.number import hid_is_valid


class LunaListTransfersAll(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Returns a list of ALL transfers IN and OUT of a User's account

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
                                "type": "0",                        // USER > OWNER transfers are TYPE 0

                                "created": "2018-01-03 11:02:17",
                                "amount": "0.1231928",              // Payment is always POSITIVE
                                "luna_fee": "-0.0307982",           // Fee is always NEGATIVE
                                "total": "0.0923946",

                                "name": "Sarah Stevens",            // The user this transfer was RECEIVED FROM
                                "hid": "e7165eb2",
                                "avatar_url": "https://example.com/test.jpg"
                            },
                            {
                                "type": "1",                        // OWNER > USER transfers are TYPE 1

                                "created": "2018-01-01 13:44:25",
                                "amount": "-0.8241927",             // Payment is always NEGATIVE
                                "luna_fee": "0.0",                  // We only charge fees on INBOUND transfers
                                "total": "-0.8241927",

                                "name": "Jason Brown",              // The user this transfer was SENT TO
                                "hid": "9c62ac41",
                                "avatar_url": "https://example.com/test.jpg"
                            },
                            {
                                "type": "2",                        // QTUM > OWNER transfers are TYPE 2

                                "created": "2018-02-01 22:15:02",
                                "amount": "5.0000741",              // Payment is always POSITIVE
                                "luna_fee": "0.0",                  // We only charge fees on OUTBOUND QTUM transfers
                                "total": "5.0000741"
                            },
                            {
                                "type": "3",                        // OWNER > QTUM transfers are TYPE 3

                                "created": "2018-04-21 09:05:21",
                                "amount": "-5.0000741",             // Payment is always NEGATIVE
                                "luna_fee": "1.250018525",          // Fee is always POSITIVE
                                "total": "-3.750055575"
                            }

                            // NOTE: Detailed info for QTUM transactions is available via the "qtum_list_trans_in"
                            // and "qtum_list_trans_out" endpoints
                            // ======================================================================================
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

        # Although it's technically possible to do ALL four queries and all of the data composition in a single
        # postgres query, very few team members would understand how it worked and be able to maintain it, and
        # the performance gains would be so small we wouldn't be able to measure them for typical results sets.
        # ======================================================================================================

        local_in = [{

            'type': 0,

            'created': item.created,
            'amount': str(item.amount),
            'luna_fee': '-' + str(item.luna_fee),
            'total': str(item.total),

            'name': item.source.get_full_name,
            'hid': item.source.hid,
            'avatar_url': item.source.get_avatar_url(64, 64),

        } for item in JournalUser.objects.filter(dest=target).select_related('source')]

        local_out = [{

            'type': 1,

            'created': item.created,
            'amount': str(item.amount),
            'luna_fee': '-' + str(item.luna_fee),
            'total': str(item.total),

            'name': item.dest.get_full_name,
            'hid': item.dest.hid,
            'avatar_url': item.dest.get_avatar_url(64, 64),

        } for item in JournalUser.objects.filter(source=target).select_related('dest')]

        qtum_in = [{

            'type': 2,
            'created': item.created,
            'amount': str(item.amount),
            'luna_fee': str(item.luna_fee),
            'total': str(item.total)

        } for item in JournalIn.objects.filter(user=target)]

        qtum_out = [{

            'type': 3,
            'created': item.created,
            'amount': '-' + str(item.amount),
            'luna_fee': str(item.luna_fee),
            'total': '-' + str(item.total)

        } for item in JournalOut.objects.filter(user=target)]

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,
                'items': sorted(local_in + local_out + qtum_in + qtum_out, key=itemgetter('created'), reverse=True)
            }
        )
