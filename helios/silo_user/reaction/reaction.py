#  -*- coding: UTF8 -*-

from datetime import datetime

from django.db import models
from sys_base.exceptions import HeliosException


class Reaction(models.Model):
    """
        Stores a user reaction - which can be a matched or unmatched.
        When a user send a user a message he create a match reaction,
        Whenever a user set a user as unmatch he creates an unmatch reaction
        We use reaction as a way to store and exclude existing matches when recommending people
    """

    # User that initiated the reaction.
    sender = models.ForeignKey('silo_user.User', db_index=True, related_name='sender_reaction')

    # User that was affected by this reaction. The target user.
    recipient = models.ForeignKey('silo_user.User', db_index=True, related_name='recipient_reaction')

    # True if match was made. False otherwise.
    is_match = models.BooleanField(default=False, db_index=True)

    # When the Conversation was created. A Conversation isn't created until the first message inside it is SENT.
    created = models.DateTimeField(db_index=True)

    # When a reactions was last updated. As a user may set a match to unmatch
    last_update = models.DateTimeField(db_index=True)


class ReactionUtil(object):
    """
    Utility class for reactions.
    """

    @staticmethod
    def create_or_update_reaction(sender, recipient, is_match):
        """
        Creates a new reaction. Updates an existing negative reaction with the same sender and recipient.
        :param sender: The user that reacted.
        :param recipient: The user that was reacted to.
        :param is_match: Whether the reaction was positive.
        :return: Nothing.
        :raise HeliosException:
            If an inverse reaction (sender and recipient switched) or a positive reaction already exists.
        """

        filters = {
            'sender__in': [sender, recipient],
            'recipient__in': [sender, recipient]
        }
        now = datetime.now()
        for reaction in Reaction.objects.filter(**filters).select_for_update():
            if reaction.sender == recipient and reaction.recipient == sender:
                raise HeliosException(desc='Inverse reaction already exists', code='existing_inverse_reaction')
            elif reaction.is_match:
                raise HeliosException(desc='Positive reaction already exists', code='existing_positive_reaction')
            else:
                reaction.is_match = is_match
                reaction.last_update = now
                reaction.save()
                break
        else:
            # Create a new reaction
            Reaction.objects.create(
                is_match=is_match,
                created=now,
                last_update=now,
                sender=sender,
                recipient=recipient
            )
