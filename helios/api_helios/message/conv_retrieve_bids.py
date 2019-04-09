#  -*- coding: UTF8 -*-

import newrelic.agent

from api_helios.base import AbstractHeliosEndpoint

from silo_message.conversation import Conversation


class ConversationRetrieveBids(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Retrieves all bids created by target_hid

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
                                "bid_status": 2     // See silo_message.conversation.BID_STATUSES
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

        filters = {

            'sender': target_user,

            'bid_status__in': [

                Conversation.BID_WINNING,
                Conversation.BID_WON,
                Conversation.BID_LOSING,
                Conversation.BID_LOST,
                Conversation.BID_TIMEOUT
            ]
        }

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                'conversations': [{

                    'id': conversation.id,
                    'last_update': conversation.last_update,
                    'partner_avatar': conversation.recipient.get_avatar_url(req_x=255, req_y=255),
                    'partner_name': conversation.recipient.name_first,
                    'partner_hid': conversation.recipient.hid,
                    'subject': conversation.subject,
                    'bid_status': conversation.bid_status

                } for conversation in Conversation.objects.filter(**filters).order_by('-last_update')]
            }
        )
