#  -*- coding: UTF8 -*-

import newrelic.agent

from django.db import transaction

from datetime import datetime, timedelta

from api_helios.base import AbstractHeliosEndpoint

from plant_hermes.account.db import TokenAccount
from plant_hermes.hsm.adapter import HSMadapter
from plant_hermes.journal.inbound import JournalIn

from sys_util.math.eth import d8
from sys_util.text.number import hid_is_valid


class QtumNetworkSync(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Synchronizes our cached copy of the user's unique QTUM address balance with the value reported by
            the QTUM blockchain. If a non-zero balance is present, we sweep the inbound wallet's balance to our
            cold wallet, then update the user's available account balance.

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
                        "confirmed": "12.85206753084677741",
                        "unconfirmed": "0.000000127481200012"
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

        target = upstream['viewer']

        if not target:
            return self.render_error(request, code='nonexistent_target', status=400)

        # Run db operations
        # =======================================================================

        hsm = HSMadapter()

        with transaction.atomic():

            account = TokenAccount.objects.filter(id=target.token_account_id).select_for_update().first()

            # DO NOT DECREASE request_interval below 360 seconds. QTUM has a 2 minute block time, and until we rewrite
            # their API so we can actually read transactions out of it, all we can do is "guess" based on time elapsed.
            # In a "normal" data transmission scenario, doing this at the Nyquist rate of 2f would be sufficient, but
            # in the case of QTUM, blocks can be mined faster or slower than 120 seconds, introducing jitter. As a
            # result, we need MINIMUM TWO BLOCKS to pass + margin. This assumes our transactions always have enough
            # gas to run!

            request_interval = 360

            if (account.last_qtum_sync + timedelta(seconds=request_interval)) > datetime.now():
                return self.render_error(request, code='too_many_requests', status=420)

            else:

                enclave_confirmed_bal, enclave_unconfirmed_bal, txid = hsm.sweep_enclave_address(

                    data_iv=account.data_iv,
                    enclave_data=account.enclave_data
                )

                if not txid:

                    # If no tokens could be transferred from the enclave address, just update the last_qtum_sync value

                    account.last_qtum_sync = datetime.now()
                    account.save()

                else:

                    account.add_confirmed_balance(enclave_confirmed_bal)
                    account.unconfirmed_balance = enclave_unconfirmed_bal
                    account.updated = datetime.now()
                    account.last_qtum_sync = datetime.now()
                    account.revision += 1

                    account.hsm_sig = account.calculate_hsm_sig()
                    account.save()

                    # We currently charge 0% on INBOUND transfers, but that could change in the future
                    luna_fee = d8(enclave_confirmed_bal * d8(0.0))

                    entry = JournalIn.objects.create(

                        user=target,
                        amount=enclave_confirmed_bal,
                        luna_fee=luna_fee,
                        total=d8(enclave_confirmed_bal - luna_fee),
                        txid=txid,
                        send_gas=d8(0.0)
                    )

                    entry.hsm_sig = entry.calculate_hsm_sig()
                    entry.save()

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                'confirmed': str(account.confirmed_balance),
                'unconfirmed': str(account.unconfirmed_balance)
            }
        )
