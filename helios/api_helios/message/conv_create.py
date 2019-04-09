#  -*- coding: UTF8 -*-

import sys
import newrelic.agent

from datetime import datetime, timedelta
from decimal import Decimal

from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint
from django.db.models import Q

from plant_eos.handlers.auction.losing import dispatch_notice_auction_losing
from plant_eos.handlers.message.message_new import dispatch_notice_message_new

from plant_hermes.account.db import TokenAccount

from silo_message.conversation import Conversation
from silo_message.message import Message, MessageType
from silo_user.user.db import User
from silo_user.reaction.reaction import Reaction, ReactionUtil

from sys_base.exceptions import HeliosException
from sys_util.math.eth import d8
from sys_util.text.number import hid_is_valid, parse_str_to_eth
from sys_util.text.sanitize import sanitize_title, sanitize_textfield


class ConversationCreate(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Creates a new Conversation

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "sender_hid": "b3665ea5",
                    "recipient_hid": "2c968e7f",
                    "body": "Body Text"             // (unicode) 0-16K characters
                    "bid_price": "1337.33"          // (float) 0.0 to Inf
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",
                        "conversation_id": 82583950
                    },
                    "success": true
                }
        """

        sender_hid = request.POST.get('sender_hid')

        if not request.user.is_anonymous:
            sender_hid = sender_hid or request.user.hid

        recipient_hid = request.POST.get('recipient_hid')
        body = request.POST.get('body')
        type = request.POST.get('type')
        bid_price = request.POST.get('bid_price')

        # sender_hid / recipient_hid
        # ----------------------------------------------------------------------

        if not hid_is_valid(sender_hid):
            return self.render_error(request, code='invalid_sender_hid', status=400)

        if not hid_is_valid(recipient_hid):
            return self.render_error(request, code='invalid_recipient_hid', status=400)

        if sender_hid == recipient_hid:
            return self.render_error(request, code='cannot_send_to_self', status=400)

        # viewer / sender
        # ----------------------------------------------------------------------

        upstream = self.get_upstream_for_platform(request)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        # Verify that either the sender is the viewer, or the viewer has helios_root set

        elif not (upstream['root_active'] or (upstream['viewer'].hid == sender_hid)):
            return self.render_error(request, code='cannot_become_other_user', status=403)

        # body
        # ----------------------------------------------------------------------

        try:
            clean_body = sanitize_textfield(body).strip()[:2048]

        except HeliosException as e:

            if e.code == 'parse_failure':
                return self.render_error(request, code='body_not_string', status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        if len(clean_body) == 0:
            return self.render_error(request, code='body_empty', status=400)

        # subject
        # ----------------------------------------------------------------------
        # We use the first 120 characters of the body as the subject

        try:
            clean_subject = sanitize_title(body).strip()[:120]

        except HeliosException as e:

            if e.code == 'parse_failure':
                return self.render_error(request, code='subject_not_string', status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        if len(clean_subject) == 0:
            return self.render_error(request, code='subject_empty', status=400)

        # bid_price
        # ----------------------------------------------------------------------

        try:
            clean_bid_price = parse_str_to_eth(bid_price)

        except HeliosException as e:

            if e.code in ['invalid_char_in_string', 'invalid_decimal_point', 'invalid_leading_digits',
                          'invalid_trailing_digits']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        if clean_bid_price < Decimal('0'):
            return self.render_error(request, code='negative_bid_price', status=400)

        # Run db operations
        # =======================================================================

        try:

            with transaction.atomic():

                # We have to select the recipient again with a WRITE LOCK because we might have to update
                # their min_bid value

                recipient = User.objects.filter(hid=recipient_hid).select_for_update().first()

                if not recipient:
                    raise HeliosException(desc='Nonexistent recipient', code='nonexistent_recipient')

                # We have to select the sender again with a WRITE LOCK to prevent double spends
                sender = User.objects.filter(hid=sender_hid).select_for_update().first()

                # Check for invalid API request (already an existing conversation)
                # =======================================================================

                filters = {

                    'sender__in': [sender, recipient],
                    'recipient__in': [sender, recipient]
                }

                if Conversation.objects.filter(**filters).select_for_update().exists():
                    raise HeliosException(desc='Conversation already exists', code='existing_conversation')

                # Update sender balance
                # =======================================================================

                token_account = TokenAccount.objects.filter(id=sender.token_account_id).select_for_update().first()

                if token_account.confirmed_balance < clean_bid_price:
                    raise HeliosException(desc='Insufficient balance', code='insufficient_balance')

                # elif clean_bid_price < recipient.inbox_settings.get().min_bid:
                #     raise HeliosException(desc='Bid too low', code='bid_too_low')

                # TODO: this is where we dispatch an event to Hermes to move the tokens from the sender's
                # TODO: wallet into escrow
                # TODO: Make sure that we do it after the atomic transaction success or have some promise with confirmation

                token_account.add_confirmed_balance(-clean_bid_price)
                token_account.revision += 1
                token_account.calculate_hsm_sig()
                token_account.save()

                # Update recipient min_bid and conversations for this auction
                # We are updating the min_bid in the case we have active bids
                # OR we have free bids (Bids who won with price of 0 in the last 24 hours)

                filters = (

                    Q(recipient=recipient) &

                    (Q(bid_status=Conversation.BID_WINNING) |

                     (Q(bid_status=Conversation.BID_WON) &
                      Q(bid_price=0) &
                      Q(created__gte=datetime.now() - timedelta(days=1))
                      )
                     )
                )

                # Order conversations from highest to lowest bid price, then oldest to newest (to handle the
                # case where two or more Conversations have the same bid price)
                # Get BID_WINNING Which are active conversations and BID_WON which are conversation
                # That were passed freely in the last 24 hours

                ordr = ('-bid_price', 'created')

                conversations = list(Conversation.objects.filter(filters).select_for_update().order_by(*ordr))

                recipient_intro_settings = recipient.inbox_settings.get()
                # Disable bidding as long as we do not support Know Your Customer (KYC)
                # if (len(conversations) + 1) > recipient_intro_settings.max_daily_intros:
                if False:

                    bid_starting_status = Conversation.BID_WINNING

                    # Increase the recipient's min_bid

                    recipient_intro_settings.min_bid = clean_bid_price + d8(1.0)
                    recipient_intro_settings.save()

                    # Set the losing conversation (or conversations, if there was an anomoly) to status BID_LOSING

                    start = recipient.inbox_settings.get().max_daily_intros - 1

                    for conversation in conversations[start:]:
                        conversation.bid_status = Conversation.BID_LOSING
                        conversation.save()

                        # TODO: notifying users of being outbid is not in the MVP

                        # dispatch_notice_auction_losing(
                        #
                        #     sender = sender,
                        #     recipient = recipient,
                        #     conversation = conversation,
                        #     message = message,
                        #     min_bid = recipient.inbox_settings.get().min_bid
                        # )


                # If the user didn't reached his daily max_intros then immidiatly pass the messages through
                # and set the bid status to WON
                else:
                    bid_starting_status = Conversation.BID_WON

                # Create Conversation and first Message
                # =======================================================================

                now = datetime.now()

                conversation = Conversation.objects.create(

                    created=now,
                    last_update=now,
                    last_message_sender=sender,
                    bid_price=clean_bid_price,
                    bid_status=bid_starting_status,
                    sender=sender,
                    recipient=recipient,
                    sender_status=Conversation.STATUS_CURRENT,
                    recipient_status=Conversation.STATUS_PENDING,
                    subject=clean_subject
                )

                # First message
                message = Message.objects.create(

                    sent_time=now,
                    conversation=conversation,
                    sender=sender,
                    recipient=recipient,
                    body=body,
                    type=type if type else MessageType.STANDARD
                )

                # Notify user of message
                dispatch_notice_message_new(

                    sender=sender,
                    recipient=recipient,
                    conversation=conversation,
                    message=message
                )

                # Update reaction - set to match
                # =======================================================================

                ReactionUtil.create_or_update_reaction(sender, recipient, True)

        # Trap exceptions during transaction
        # =======================================================================

        except HeliosException as e:

            if e.code in [
                'nonexistent_recipient',
                'existing_conversation',
                'insufficient_balance',
                'bid_too_low',
                'existing_inverse_reaction',
                'existing_positive_reaction',
            ]:
                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,
                'conversation_id': conversation.id
            }
        )
