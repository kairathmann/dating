# -*- coding: utf-8 -*-

import uuid

from django.db import models

from sys_base.fields.field_json import JSONField


class Notice(models.Model):
    """
        Every time something happens on the site that a User should be notified about, the system generates
        a Notice. Although there are hundreds of possible events we could notify people about, we limit them to
        the bare minimum to avoid excessive system complexity (and annoying people).
    """

    # User that this notice will be sent to
    user = models.ForeignKey('silo_user.User', related_name='eos_queued')

    # Email address to send Notice to
    email = models.EmailField(blank=False, db_index=True)

    # Used to split notices across multiple workers
    worker_id = models.SmallIntegerField(db_index=True)

    # When this notice was added to the queue
    queued = models.DateTimeField(auto_now_add=True, db_index=True)

    # Notice type
    # ================================================================================================

    TYPE_AUCTION_ACCEPT = 1
    TYPE_AUCTION_EXPIRED = 2
    TYPE_AUCTION_LOSING = 3
    TYPE_AUCTION_LOST = 4
    TYPE_AUCTION_WON = 5

    TYPE_HELIOS_SIGNUP = 10
    TYPE_HELIOS_CHANGE_EMAIL = 11
    TYPE_HELIOS_FORGOT_PASS = 12

    TYPE_MESSAGE_NEW = 20

    VALID_TYPES = (

        (TYPE_AUCTION_ACCEPT, "TYPE_AUCTION_ACCEPT"),
        (TYPE_AUCTION_EXPIRED, "TYPE_AUCTION_EXPIRED"),
        (TYPE_AUCTION_LOSING, "TYPE_AUCTION_LOSING"),
        (TYPE_AUCTION_LOST, "TYPE_AUCTION_LOST"),
        (TYPE_AUCTION_WON, "TYPE_AUCTION_WON"),

        (TYPE_HELIOS_SIGNUP, "TYPE_HELIOS_SIGNUP"),
        (TYPE_HELIOS_CHANGE_EMAIL, "TYPE_HELIOS_CHANGE_EMAIL"),
        (TYPE_HELIOS_FORGOT_PASS, "TYPE_HELIOS_FORGOT_PASS"),

        (TYPE_MESSAGE_NEW, "TYPE_MESSAGE_NEW")
    )

    type = models.SmallIntegerField(choices=VALID_TYPES, db_index=True)

    # ================================================================================================

    # Event-specific data
    data = JSONField()

    # Unique id for this notice. We use GUID's because we need a unique, non-sequential identifier. We
    # do NOT use the guid as the model's primary key, because doing so would cause table fragmentation. The
    # time penalty for indexing the guid column isn't important, because insertion into the table is done by
    # a backend worker process.

    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)

    @classmethod
    def calculate_worker_id(cls, user_id):
        """
            Splits a task across the worker pool based on the recipient's id

            :param user_id: id of user to send notice to
            :return: id of worker to use. Zero-based.
        """

        return user_id % 4
