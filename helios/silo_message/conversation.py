#  -*- coding: UTF8 -*-

from datetime import datetime

from django.db import models

from sys_base.hsm.model import SecureModel

from sys_base.fields.field_fulltext import VectorField

from sys_util.math.eth import d8

from .message import MessageType


class Conversation(SecureModel, models.Model):
    """
        Stores a Conversation between two People
    """

    class Meta:
        # There can only ever be ONE conversation between a pair of People. The 'unique_together' constraint
        # will allow a pair of records where [sender=A, recipient=B] and [sender=B, recipient=A]. While its
        # possible to create record structures that enforce one conversation per pair of users at the database level
        # using triggers or duplicate columns, it creates a big efficiency hit. So we just query the table for both
        # combinations before doing the insert.
        #
        # See: https://stackoverflow.com/questions/1450883/how-to-implement-a-bidirectional-unique-index-across-multiple-columns

        unique_together = ('sender', 'recipient')
        index_together = ('sender', 'recipient')

    # NOTE: The values of fields prefixed with [HSM] are used by the HSM to calculate the signature for
    # this record. Whenever one of these fields is updated, the record has to be re-signed by the HSM

    # ==== BEGIN SECURE BLOCK =====================================================================================

    # [HSM] The id of this record. An implicit field in Django, but explicitly called-out here because
    # its under HSM control to prevent an attacker from swapping record ids

    id = models.AutoField(primary_key=True)

    # [HSM] When this record was created.
    created = models.DateTimeField(default=datetime.now, db_index=True)

    # [HSM] The amount of tokens the sender paid to start the Conversation
    bid_price = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] User that created this Conversation
    sender = models.ForeignKey('silo_user.User', related_name='sent_conversations', db_index=True,
                               on_delete=models.PROTECT)

    # [HSM] User that this Conversation was sent to
    recipient = models.ForeignKey('silo_user.User', related_name='received_conversations', db_index=True,
                                  on_delete=models.PROTECT)

    # [HSM] The HSM signature for this record. Used to detect if the record has been tampered with.
    hsm_sig = models.BinaryField(null=True)

    # ==== END SECURE BLOCK =======================================================================================

    # When a message was last added to the Conversation
    last_update = models.DateTimeField(db_index=True)

    # The last User who sent a message in this Conversation
    last_message_sender = models.ForeignKey('silo_user.User', db_index=True, null=True, on_delete=models.PROTECT)

    BID_WINNING = 1
    BID_LOSING = 2
    BID_WON = 3
    BID_LOST = 4
    BID_ACCEPTED = 5
    BID_TIMEOUT = 6

    BID_STATUSES = (

        (BID_WINNING, "BID_WINNING"),  # This Conversation is one of the winning bids
        (BID_LOSING, "BID_LOSING"),  # This Conversation is one of the losing bids
        (BID_WON, "BID_WON"),  # This Conversation is a winner, and has not been read by the recipient
        (BID_LOST, "BID_LOST"),  # This Conversation is a loser, and was not shown to the recipient
        (BID_ACCEPTED, "BID_ACCEPTED"),  # This Conversation is a winner, and has been read by the recipient
        (BID_TIMEOUT, "BID_TIMEOUT")  # This Conversation is a winner, and was not read within the time limit
    )

    bid_status = models.SmallIntegerField(db_index=True, choices=BID_STATUSES)

    # Conversation Statuses
    # ============================================================================
    # These flags are used to show the correct read/unread state for conversations in a User's
    # inbox without having to do an expensive subquery on the Messages inside the Conversation

    STATUS_PENDING = 1
    STATUS_CURRENT = 2

    SENDER_STATUSES = (

        (STATUS_PENDING, "STATUS_PENDING"),  # There are one or more unread replies from the Recipient
        (STATUS_CURRENT, "STATUS_CURRENT")  # There are no unread replies from the Recipient
    )

    sender_status = models.SmallIntegerField(db_index=True, choices=SENDER_STATUSES)

    RECIPIENT_STATUSES = (

        (STATUS_PENDING, "STATUS_PENDING"),  # There are one or more unread replies from the Sender
        (STATUS_CURRENT, "STATUS_CURRENT")  # There are no unread replies from the Sender
    )

    recipient_status = models.SmallIntegerField(db_index=True, choices=RECIPIENT_STATUSES)

    # Subject of the Conversation. This is copied from the latest message in the Conversation. We intentionally
    # duplicate the value here to avoid an expensive subquery against the Conversation's Messages

    subject = models.CharField(max_length=255)
    subject_type = models.CharField(max_length=8, default=MessageType.STANDARD)

    # Postgres GIN fulltext search field. We need to set this field as indexed so Django's ORM handles
    # it properly, but we change the index type in the importer. Both the "subject" and "body" columns
    # are indexed in "fulltext" as it greatly improves search speed.

    fulltext = VectorField(null=True, db_index=True)

    def generate_hsm_hash(self):
        """
            Concatenates all HSM controlled columns in a record into a string, for processing by the HSM
        """

        return ''.join([

            str(self.id),
            str(self.created),
            str(d8(self.bid_price)),
            str(self.sender_id),
            str(self.recipient_id)
        ])
