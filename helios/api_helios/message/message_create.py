#  -*- coding: UTF8 -*-

import requests
import sys
import newrelic.agent
import traceback
from conv_util import ConversationUtil
from datetime import datetime

from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint

from plant_eos.handlers.message.message_new import dispatch_notice_message_new

from silo_message.conversation import Conversation
from silo_message.message import Message, MessageType
from silo_user.user.db import User
from django.conf import settings

from sys_base.exceptions import HeliosException
from sys_util.text.number import hid_is_valid
from sys_util.text.sanitize import sanitize_title, sanitize_textfield

import boto3


class MessageCreate(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Creates a new Message
        """

        sender_hid = request.POST.get('sender_hid')
        if not request.user.is_anonymous:
            sender_hid = sender_hid or request.user.hid

        recipient_hid = request.POST.get('recipient_hid')
        body = request.POST.get('body')
        type = request.POST.get('type')

        if not type:
            type = MessageType.STANDARD

        # sender_hid / recipient_hid / recipient state
        # ----------------------------------------------------------------------

        if not hid_is_valid(sender_hid):
            return self.render_error(request, code='invalid_sender_hid', status=400)

        if not hid_is_valid(recipient_hid):
            return self.render_error(request, code='invalid_recipient_hid', status=400)

        if sender_hid == recipient_hid:
            return self.render_error(request, code='cannot_send_to_self', status=400)

        try:
            recipient = User.objects.get(hid=recipient_hid)
            if recipient.is_deleted:
                return self.render_error(request, code='deleted_recipient', status=400)
        except User.DoesNotExist:
            return self.render_error(request, code='nonexistent_recipient', status=400)

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

        # viewer / sender
        # ----------------------------------------------------------------------

        # Get the User record for the viewer making the request
        upstream = self.get_upstream_for_platform(request)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        # Verify that either the sender is the viewer, or the viewer has helios_root set

        elif not (upstream['root_active'] or (upstream['viewer'].hid == sender_hid)):
            return self.render_error(request, code='cannot_become_other_user', status=403)

        if not MessageType.supports(type):
            return self.render_error(request, code='not_supported_message_type', status=400)

        if type == MessageType.BUBBLE:
            s3 = boto3.resource('s3')
            try:
                s3.Object(settings.BUCKET_NAME, body).load()
            except:
                traceback.print_exc()
                return self.render_error(request, code='file_not_found', status=400)

        try:

            with transaction.atomic():

                message_recipient = User.objects.filter(hid=recipient_hid).first()

                if not message_recipient:
                    raise HeliosException(desc='Nonexistent recipient', code='nonexistent_recipient')

                # We HAVE to select the sender again with a WRITE LOCK to prevent double spends
                message_sender = User.objects.filter(hid=sender_hid).select_for_update().first()

                # Check for invalid API request (already an existing conversation)
                # ----------------------------------------------------------------------

                filters = {

                    'sender__in': [message_sender, message_recipient],
                    'recipient__in': [message_sender, message_recipient]
                }

                conversation = Conversation.objects.filter(**filters).select_for_update().first()

                if not conversation:
                    raise HeliosException(desc='No conversation exists', code='no_existing_conversation')

                if conversation.bid_status != Conversation.BID_ACCEPTED:
                    raise HeliosException(desc='Wrong bid_status', code='wrong_bid_status')

                # Create Message / update Conversation
                # ----------------------------------------------------------------------

                now = datetime.now()

                message = Message.objects.create(

                    sent_time=now,
                    conversation=conversation,
                    sender=message_sender,
                    recipient=message_recipient,
                    body=body,
                    type=type if type else MessageType.STANDARD
                )

                if message_recipient == conversation.recipient:
                    conversation.recipient_status = Conversation.STATUS_PENDING

                elif message_recipient == conversation.sender:
                    conversation.sender_status = Conversation.STATUS_PENDING

                conversation.subject = clean_subject
                conversation.subject_type = type
                conversation.last_update = now
                conversation.last_message_sender = message_sender
                conversation.save()

                # notify user of new message

                dispatch_notice_message_new(

                    sender=message_sender,
                    recipient=message_recipient,
                    conversation=conversation,
                    message=message
                )

        # Trap exceptions during transaction
        # =======================================================================

        except HeliosException as e:

            if e.code in ['nonexistent_recipient', 'blocked_by_both', 'blocked_by_sender', 'blocked_by_recipient',
                          'no_existing_conversation', 'wrong_bid_status']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,
                'conversation_id': conversation.id,
                'message_id': message.id
            }
        )
