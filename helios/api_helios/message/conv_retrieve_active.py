#  -*- coding: UTF8 -*-

import newrelic.agent
from conv_util import ConversationUtil
from django.db.models import Q
from api_helios.base import AbstractHeliosEndpoint

from silo_message.conversation import Conversation
from silo_message.message import MessageType


class ConversationRetrieveActive(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Retrieves all active conversations for target_hid

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

                        "conversations": [

                            {
                                "id": 82583950,
                                "last_update": "",
                                "partner_avatar": "https://example.com/test.jpg",
                                "partner_name": "Test",
                                "partner_hid": "2c968e7f",
                                "subject": "Test Message",
                                "pending": true
                            },

                            // ...
                        ]
                    },
                    "success": true
                }
        """

        target_hid = request.POST.get('target_hid')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Fetch conversations
        # ----------------------------------------------------------------------

        target_user = upstream['target_user']

        incl = (

            # Ensure that the target_user is a participant in the Conversation
            Q(sender=target_user) | Q(recipient=target_user)
        )

        excl = {

            # Since we can't mix column filters with Q objects in the filter construct, we have to
            # add an "exclude" block that removes all records except those with bid_status in
            # [Conversation.BID_WON, Conversation.BID_ACCEPTED]

            'bid_status__in': [

                Conversation.BID_WINNING,
                Conversation.BID_LOSING,
                Conversation.BID_LOST,
                Conversation.BID_TIMEOUT
            ]
        }

        conversations = list(Conversation.objects.filter(incl).exclude(**excl).order_by('-last_update'))
        result_conversations = []
        for conversation in conversations:
            partner = ConversationUtil.calc_partner(conversation, target_user)
            result_conversations.append({
                'id': conversation.id,
                'last_update': conversation.last_update,
                'last_message_sender_hid': self.calc_last_message_sender(conversation),
                'partner_avatar_small': ConversationUtil.avatar(partner, 64, 64),
                'partner_avatar_medium': ConversationUtil.avatar(partner, 256, 256),
                'partner_name': ConversationUtil.first_name(partner),
                'partner_hid': partner.hid,
                'partner_gender': ConversationUtil.gender(partner),
                'subject': 'Bubble Message' if conversation.subject_type == MessageType.BUBBLE else conversation.subject,
                'subject_type': conversation.subject_type,
                'pending': self.calc_pending(conversation, target_user)
            })

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                'conversations': result_conversations
            }
        )

    def calc_last_message_sender(self, conversation):
        if (conversation.last_message_sender):
            return conversation.last_message_sender.hid
        else:
            return None

    def calc_pending(self, conversation, target_user):
        """
            Calculates the "pending" status of a Conversation

            :param conversation:
            :param target_user:
            :return: True if there's a message in the Conversation that target_user hasn't read yet, otherwise False
        """

        if conversation.sender == target_user:

            return True if (conversation.sender_status == Conversation.STATUS_PENDING) else False

        else:
            return True if (conversation.recipient_status == Conversation.STATUS_PENDING) else False
