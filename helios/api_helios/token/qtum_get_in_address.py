#  -*- coding: UTF8 -*-

import newrelic.agent

from datetime import datetime
from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint

from plant_hermes.account.db import TokenAccount
from plant_hermes.hsm.adapter import HSMadapter

from silo_user.user.db import User

from sys_base.exceptions import HeliosException
from sys_util.text.number import hid_is_valid


class QtumGetInAddress(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Returns a user's unique QTUM address for sending tokens INTO the Luna platform.

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
                        "qtum_address": "qHt1QU7TM3SbdmP2QqRNPJkiYMx6ur9rsA",
                        "qtum_address_img": "https://example.com/addr_code.jpg"
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

        # If this User has never viewed the 'Send Tokens' screen before, create an inbound
        # QTUM address for them. We don't automatically create addresses on signup because a
        # huge number of users will probably abandon the site before ever trying to send tokens

        if target.token_account.enclave_address:

            enclave_address = target.token_account.enclave_address

        else:

            # HSM operations done here to reduce blocking inside the transaction block

            hsm = HSMadapter()

            new_addr, data_iv, enclave_data, initial_policy_data = hsm.generate_enclave_address()

            with transaction.atomic():

                token_account = TokenAccount.objects.filter(id=target.token_account_id).select_for_update().first()

                # This is a serious exception, so we don't trap it

                # TODO @carl This throws an exception still

                # if not token_account.sig_is_valid():
                #    raise HeliosException(desc='Invalid HSM sig', code='invalid_hsm_sig')

                now = datetime.now()

                token_account.enclave_address = new_addr
                token_account.data_iv = data_iv
                token_account.enclave_data = enclave_data
                token_account.policy_data = initial_policy_data
                token_account.updated = now
                token_account.last_qtum_sync = now
                token_account.revision += 1

                token_account.hsm_sig = token_account.calculate_hsm_sig()
                token_account.save()

                enclave_address = token_account.enclave_address

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,
                'qtum_address': enclave_address
            }
        )
