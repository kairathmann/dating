#  -*- coding: UTF8 -*-

import sys
import newrelic.agent
from conv_util import ConversationUtil
from datetime import datetime
from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint
from django.conf import settings
from plant_eos.handlers.auction.accept import dispatch_notice_auction_accept

from plant_hermes.account.db import TokenAccount
from plant_hermes.journal.user import JournalUser

from silo_message.conversation import Conversation
from silo_message.message import Message, MessageType
from silo_user.user.db import User

from sys_base.exceptions import HeliosException
from sys_util.math.eth import d8


class ConversationRetrieveSingle(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Retrieves the Conversation corresponding to conversation_id

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
                    "conversation_id": 82583950
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",

                        "conversation": {

                            "id": 82583950,
                            "last_update": "",
                            "bid_status": 2     // See silo_message.conversation.BID_STATUSES
                        },

                        'messages': [

                            {
                                "id": 179042570,
                                "sent_time": "",
                                "body": "Test Message A",
                                'sender_hid': "b3665ea5",
                                'sender_avatar': "https://example.com/test01.jpg",
                                'sender_name': "Test01",
                                'recipient_hid': "2c968e7f",
                                'is_recipient': false
                            },
                            {
                                "id": 179042571,
                                "sent_time": "",
                                "body": "Test Message B",
                                'sender_hid': "2c968e7f",
                                'sender_avatar': "https://example.com/test02.jpg",
                                'sender_name': "Test02",
                                'recipient_hid': "b3665ea5",
                                'is_recipient': true
                            },

                            // ...
                        ]
                    },
                    "success": true
                }

        """

        target_hid = request.POST.get('target_hid')
        conversation_id = request.POST.get('conversation_id')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Fetch conversation
        # ----------------------------------------------------------------------

        target_user = upstream['target_user']

        awsUrl = 'https://s3.' + settings.REGION_NAME + '.amazonaws.com/' + settings.BUCKET_NAME + '/'

        try:

            with transaction.atomic():

                conversation = Conversation.objects.filter(id=conversation_id).select_for_update().first()

                if not conversation:
                    raise HeliosException(desc='Nonexistent conversation', code='nonexistent_conversation')

                # Verify target_user is a participant in the Conversation

                if not ((conversation.sender == target_user) or (conversation.recipient == target_user)):
                    raise HeliosException(desc='Access denied', code='access_denied')

                # CASE 1: Sender is viewing the Conversation
                # =============================================================================================

                if conversation.sender == target_user:

                    conversation.sender_status = Conversation.STATUS_CURRENT
                    conversation.save()

                elif conversation.recipient == target_user:

                    # CASE 2: Recipient is viewing the Conversation and has previously viewed it
                    # =============================================================================================

                    if conversation.bid_status == Conversation.BID_ACCEPTED:

                        conversation.recipient_status = Conversation.STATUS_CURRENT
                        conversation.save()


                    # CASE 3: Recipient is viewing the Conversation for the first time
                    # =============================================================================================
                    # We currently treat the recipient viewing the conversation for the first time as them accepting
                    # the sender's bid. As such, if bid_status is BID_WINNING or BID_WON we know the recipient has
                    # never viewed the conversation, so we set it to BID_ACCEPTED, transfer the Conversation's
                    # bid_price to the recipient's balance, and update the recipient_status flag.

                    elif conversation.bid_status in [Conversation.BID_WINNING, Conversation.BID_WON]:

                        recipient = User.objects.filter(id=conversation.recipient.id).first()

                        if not recipient:
                            raise HeliosException(desc='Invalid recipient record', code='invalid_recipient')

                        conversation.bid_status = Conversation.BID_ACCEPTED
                        conversation.last_update = datetime.now()
                        conversation.recipient_status = Conversation.STATUS_CURRENT
                        conversation.save()

                        # Updating of balance and creating a JournalUser records
                        amount = conversation.bid_price

                        # Luna fee is 25%
                        luna_fee = d8(amount * d8(0.25))

                        account = TokenAccount.objects.filter(id=recipient.token_account_id).select_for_update().first()
                        account.add_confirmed_balance(d8(amount - luna_fee))
                        account.updated = datetime.now()
                        account.last_qtum_sync = datetime.now()
                        account.revision += 1

                        account.hsm_sig = account.calculate_hsm_sig()
                        account.save()

                        entry = JournalUser.objects.create(

                            source=conversation.sender,
                            target=conversation.recipient,
                            amount=amount,
                            luna_fee=luna_fee,
                            total=d8(amount - luna_fee),
                        )

                        entry.hsm_sig = entry.calculate_hsm_sig()
                        entry.save()

                        # TODO: notifying users of conversations being accepted is not in the MVP

                        # dispatch_notice_auction_accept(
                        #
                        #     sender = message_sender,
                        #     recipient = message_recipient,
                        #     conversation = conversation
                        # )


                    # CASE 4: Conversation has expired
                    # =============================================================================================
                    # Expired Conversations are normally automatically removed from the Recipient's inbox. This
                    # handles the edge case where a User leaves their inbox open in a browser for several hours
                    # and one or more conversations expire before they refresh the page.

                    elif conversation.bid_status == Conversation.BID_TIMEOUT:

                        raise HeliosException(desc='Conversation has expired', code='conversation_expired')

                else:

                    # This exception should not be trapped
                    raise HeliosException(desc='Invalid conversation state', code='invalid_state')


        except HeliosException as e:

            if e.code in ['nonexistent_conversation', 'access_denied', 'invalid_recipient', 'conversation_expired']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        filters = {'conversation': conversation}
        pre = ['sender', 'recipient']
        partner = ConversationUtil.calc_partner(conversation, target_user)

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                'conversation': {

                    'id': conversation.id,
                    'created': conversation.created,
                    'last_update': conversation.last_update,
                    'bid_status': conversation.bid_status,
                    'partner_name': ConversationUtil.first_name(partner),
                    'partner_id': partner.hid,
                    'partner_avatar_small': ConversationUtil.avatar(partner, 64, 64),
                    'partner_avatar_medium': ConversationUtil.avatar(partner, 256, 256),
                    'partner_gender': ConversationUtil.gender(partner),
                    'partner_state': partner.state
                },

                'messages': [{

                    'id': message.id,
                    'sent_time': message.sent_time,
                    'body': message.body if message.type == MessageType.STANDARD else awsUrl + message.body,
                    'sender_hid': message.sender.hid,
                    'sender_avatar': ConversationUtil.avatar(message.sender, 64, 64),
                    'sender_name': ConversationUtil.first_name(message.sender),
                    'sender_gender': ConversationUtil.gender(message.sender),
                    'recipient_hid': message.recipient.hid,
                    'state': message.sender.state,
                    'is_recipient': (target_user == message.recipient),
                    'type': message.type if message.type else MessageType.STANDARD

                    # It's possible to prefetch the Messages in the Conversation query, but ordering the messages
                    # would require doing a subquery. So in the interest of simplicity, we just do a second query.

                } for message in list(Message.objects.filter(**filters).select_related(*pre).order_by('sent_time'))]
            }
        )
