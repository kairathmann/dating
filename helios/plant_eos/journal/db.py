#  -*- coding: UTF8 -*-

from django.db import models

from plant_eos.queues.db import Notice

from sys_base.fields.field_json import JSONField


class SentNotice(models.Model):
    """
        Stores sent email notices
    """

    # User that this notice was sent to
    user = models.ForeignKey('silo_user.User', related_name='eos_sent')

    # Email address to send Notice to
    email = models.EmailField(blank=False, db_index=True)

    # The event type that generated the notice. This column has to be indexed so that we can generate
    # metrology for messages that were sent but not opened or clicked on.

    notice_type = models.SmallIntegerField(db_index=True, choices=Notice.VALID_TYPES)

    # When this notice was added to the queue
    queued = models.DateTimeField(db_index=True)

    # When this notice was sent to the email provider's API
    processed = models.DateTimeField(db_index=True)

    # Event-specific data
    data = JSONField()

    # Response returned by the mail API provider (used in the case of an API error)
    api_response = JSONField(null=True)

    # Status
    # =============================================================================

    STATUS_EOS_SENT = 1  # Message was successfully posted to the Email API provider's endpoint

    STATUS_EOS_TEST = 2  # Message was discarded as a test message by EOS before being sent to the Email
    # API provider's endoint

    STATUS_EOS_DROP = 3  # Message was discarded by EOS before being sent to the Email API provider's
    # endpoint because the destination email address exceeded its send fail limit

    STATUS_API_ERROR = 4  # Email provider's API returned an error when EOS posted the message. It is
    # unknown whether or not the message was actually sent

    STATUS_EOS_FAIL = 5  # Message was discarded by EOS before being sent due to the message triggering
    # an exception during rendering

    VALID_STATUSES = (

        (STATUS_EOS_SENT, "STATUS_EOS_SENT"),
        (STATUS_EOS_TEST, "STATUS_EOS_TEST"),
        (STATUS_EOS_DROP, "STATUS_EOS_DROP"),
        (STATUS_API_ERROR, "STATUS_API_ERROR"),
        (STATUS_EOS_FAIL, "STATUS_EOS_FAIL")
    )

    status = models.SmallIntegerField(db_index=True, choices=VALID_STATUSES)

    # Unique id for this notice. We use GUID's because we need a unique, non-sequential identifier. We
    # do NOT use the guid as the model's primary key, because doing so would cause table fragmentation. The
    # time penalty for indexing the guid column isn't important, because insertion into the table is done by
    # a backend worker process.

    guid = models.UUIDField(db_index=True)
