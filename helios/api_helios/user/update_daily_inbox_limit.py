#  -*- coding: UTF8 -*-

import newrelic.agent

from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint

from plant_eos.handlers.auction.losing import dispatch_notice_auction_losing

from silo_message.conversation import Conversation
from silo_user.user.db import User


class UserUpdateDailyInboxLimit(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Updates a User's max daily messages

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
                    "max_intros": 8             // (int) 1-9 | max number of new conversations to start daily
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
        max_intros = request.POST.get('max_intros')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Sanitize
        # =========================================================================

        try:
            max_intros = int(max_intros)

        except:
            return self.render_error(request, code='max_intros_not_int', status=400)

        if not (0 < max_intros < 10):  # Between 1 and 9
            return self.render_error(request, code='max_intros_invalid', status=400)

        with transaction.atomic():

            # Reselect target_user with an UPDATE LOCK
            user = User.objects.select_for_update().get(id=upstream['target_user'].id)

            # Disable bidding as long as we do not support Know Your Customer (KYC)
            # rescan_bids = True if max_intros < user.inbox_settings.get().max_daily_intros else False
            rescan_bids = False

            introSettings = user.inbox_settings.get()
            introSettings.max_daily_intros = max_intros
            introSettings.save()

            # If target_user is DECREASING the number of intros they receive per day, and they have one or more
            # bids that exceed that threshold, set the lowest-priced conversations that exceed the new threshold
            # to status BID_LOSING

            if rescan_bids:

                filters = {

                    'recipient': user,
                    'bid_status': Conversation.BID_WINNING
                }

                # Order conversations from highest to lowest bid price, then oldest to newest (to handle the
                # case where two or more Conversations have the same bid price)

                ordr = ('-bid_price', 'created')

                conversations = list(Conversation.objects.filter(**filters).select_for_update().order_by(*ordr))

                if len(conversations) > max_intros:

                    for conversation in conversations[max_intros:]:
                        conversation.bid_status = Conversation.BID_LOSING
                        conversation.save()

                        # TODO: notifying users of being outbid is not in the MVP

                        # dispatch_notice_auction_losing(
                        #
                        #     sender = sender,
                        #     recipient = recipient,
                        #     conversation = conversation,
                        #     message = message,
                        #     min_bid = recipient.inbox_settings.min_bid
                        # )

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
