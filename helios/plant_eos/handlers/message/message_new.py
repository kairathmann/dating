# -*- coding: utf-8 -*-

from __future__ import division

import requests
import os

from api_helios.message.conv_util import ConversationUtil


def dispatch_notice_message_new(sender, recipient, conversation, message):
    """
    Calls OneSignal API to send push notification to recipient
    :param sender: User object
    :param recipient: User object
    :param conversation: Conversation object
    :param message: Message object
    :return:
    """

    message_data = {
        "app_id": os.environ['ONESIGNAL_APPID'],
        "headings": {
            "en": sender.first_name,
        },
        "include_external_user_ids": [recipient.hid],
        "contents": {
            "en": message.body,
        },
        "isEmail": False,
        "data": {
            "type": "new_message",
            "target_hid": recipient.hid,
            "conversation": {
                "id": conversation.id,
                "last_message_sender_hid": conversation.last_message_sender.hid,
                "last_update": conversation.last_update.isoformat(),
                "partner_avatar_medium": ConversationUtil.avatar(recipient, 256, 256),
                "partner_avatar_small": ConversationUtil.avatar(recipient, 64, 64),
                "partner_gender": recipient.gid_is,
                "partner_hid": recipient.hid,
                "partner_name": recipient.first_name,
                "pending": True,
                "subject": conversation.subject,
                "bid_status": conversation.bid_status,
            },
            "message": {
                "body": message.body,
                "id": message.id,
                "is_recipient": True,
                "recipient_hid": recipient.hid,
                "sender_avatar": ConversationUtil.avatar(sender, 256, 256),
                "sender_gender": sender.gid_is,
                "sender_hid": sender.hid,
                "sender_name": sender.first_name,
                "sent_time": message.sent_time.isoformat(),
            },
        }
    }

    requests.post(
        os.environ['ONESIGNAL_API_ENDPOINT'],
        headers={"Authorization": os.environ['ONESIGNAL_AUTHORIZATION_HEADER']},
        json=message_data,
        verify=os.environ['CACERT_PATH'],
    )


def process(event):
    pass


def render(guid, data):
    pass
