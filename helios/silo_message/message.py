#  -*- coding: UTF8 -*-
from django.db import models
from sys_base.fields.field_fulltext import VectorField

class MessageType:

    def __init__(self):
        pass

    @staticmethod
    def supports(type):
        return type == MessageType.BUBBLE or type == MessageType.STANDARD

    BUBBLE = 'BUBBLE'
    STANDARD = 'STANDARD'

class Message(models.Model):
    """
        Stores messages within a conversation
    """

    # When this message was sent. While Conversations are ordered using a combination of Gravity and
    # DateTime, Messages within a Conversation are ALWAYS ordered by DateTime. We don't have 'draft'
    # functionality because it would take too much time to build.

    sent_time = models.DateTimeField(null=True, db_index=True)

    # Conversation that this Message is part of
    conversation = models.ForeignKey('silo_message.Conversation', related_name='messages', db_index=True)

    # User that created THIS message. Not necessarily the sender of the Conversation.
    sender = models.ForeignKey('silo_user.User', related_name='sent_messages', db_index=True)

    # User that received THIS message. Not necessarily the receiver of the Conversation.
    recipient = models.ForeignKey('silo_user.User', related_name='received_messages', db_index=True)

    # Body of this message
    body = models.TextField(db_index=False)

    # Postgres GIN fulltext search field. We need to set this field as indexed so Django's ORM handles
    # it properly, but we change the index type in the importer. Both the "subject" and "body" columns
    # are indexed in "fulltext" as it greatly improves search speed.

    fulltext = VectorField(null=True, db_index=True)

    type = models.CharField(max_length=8, default=MessageType.STANDARD)
