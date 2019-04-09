#  -*- coding: UTF8 -*-

import sys
import newrelic.agent

from datetime import datetime

from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint

from plant_hermes.account.db import TokenAccount
from plant_hermes.hsm.adapter import HSMadapter
from plant_hermes.journal.outbound import JournalOut

from silo_user.user.db import User

from sys_base.exceptions import HeliosException

from sys_util.math.eth import d8
from sys_util.text.number import hid_is_valid, parse_str_to_eth
from sys_util.text.sanitize import sanitize_qtum_addr


class QtumSendTransOut(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Transfers tokens OUT of a user's account to the specified QTUM address

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
                    "destination_address": "qHt1QU7TM3SbdmP2QqRNPJkiYMx6ur9rsA",
                    "amount": "0.00963289000"
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",
                        "txid": "483f9afbdc0b983a1fd809ed47a97e3b757ee0bd261b19a020af7231996543d3",
                        "txid_url": "https://explorer.qtum.org/tx/483f9afbdc0b983a1fd809ed47a97e3b757ee0bd261b19a020af7231996543d3",
                        "amount": "0.00963289000"
                    },
                    "success": true
                }
        """

        target_hid = request.POST.get('target_hid')
        destination_address = request.POST.get('destination_address')
        amount = request.POST.get('amount')

        if not request.user.is_anonymous:
            target_hid = target_hid or request.user.hid

        if not hid_is_valid(target_hid):
            return self.render_error(request, code='invalid_target_hid', status=400)

        if not destination_address:
            return self.render_error(request, code='missing_destination_address',
                                     data='Please enter destination address', status=400)

        if not amount:
            return self.render_error(request, code='missing_amount', status=400)

        if d8(amount) <= 0.0:
            return self.render_error(request, code='amount_must_be_bigger_then_zero',
                                     data='Amount must be bigger then zero', status=400)

        upstream = self.get_upstream_for_platform(request)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        # Verify that either the sender is the viewer, or the viewer has helios_root set

        elif not (upstream['root_active'] or (upstream['viewer'].hid == target_hid)):
            return self.render_error(request, code='cannot_become_other_user', status=403)

        # dest_addr
        # ----------------------------------------------------------------------

        try:
            clean_destination_addr = sanitize_qtum_addr(destination_address)
            print(clean_destination_addr)

        except HeliosException as e:

            if e.code in ['qtum_address_invalid_char', 'qtum_address_malformed_address', 'qtum_address_wrong_length']:
                return self.render_error(request, data=e.desc, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        # amount
        # ----------------------------------------------------------------------

        try:
            clean_amount = parse_str_to_eth(amount)

        except HeliosException as e:

            if e.code in ['invalid_char_in_string', 'invalid_decimal_point', 'invalid_leading_digits',
                          'invalid_trailing_digits']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        if clean_amount < d8(0.0):
            return self.render_error(request, code='negative_amount', status=400)

        # Run db operations
        # =======================================================================

        target = User.objects.filter(hid=target_hid).first()

        if not target:
            return self.render_error(request, code='nonexistent_target', status=400)

        try:

            # HSM connection opened here to reduce blocking inside the transaction block
            hsm = HSMadapter()

            with transaction.atomic():

                account = TokenAccount.objects.filter(id=target.token_account_id).select_for_update().first()

                if account.confirmed_balance < clean_amount:
                    raise HeliosException(desc='Insufficient balance', code='insufficient_balance')

                elif not account.sig_is_valid():  # This is a serious exception, so we don't trap it
                    raise HeliosException(desc='Invalid HSM sig', code='invalid_hsm_sig')

                # TODO: we don't know enough about this RPC endpoint to know if it can get stuck in an
                # TODO: indeterminate state, return an error but still do the transfer, etc. It may be
                # TODO: necessary to READ BACK from the blockchain to guarantee correct operation

                txid, new_policy_data = hsm.transfer_to_sovereign_address(

                    data_iv=account.data_iv,
                    policy_data=account.policy_data,
                    dest_addr=clean_destination_addr,
                    amount=clean_amount
                )

                account.add_confirmed_balance(-clean_amount)
                account.policy_data = new_policy_data
                account.updated = datetime.now()
                account.revision += 1

                account.hsm_sig = account.calculate_hsm_sig()
                account.save()

                luna_fee = d8(clean_amount * d8(0.25))

                entry = JournalOut.objects.create(

                    user=target,
                    amount=clean_amount,
                    luna_fee=luna_fee,
                    total=d8(amount) - d8(luna_fee),
                    dest_address=clean_destination_addr,
                    txid=txid,
                    send_gas=d8(0.0)
                )

                entry.hsm_sig = entry.calculate_hsm_sig()
                entry.save()


        # Trap exceptions during transaction
        # =======================================================================

        except HeliosException as e:

            if e.code in ['insufficient_balance']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,
                'txid': txid,
                'txid_url': 'https://explorer.qtum.org/tx/{}'.format(txid),
                'amount': clean_amount
            }
        )
