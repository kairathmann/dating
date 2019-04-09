#  -*- coding: UTF8 -*-

from datetime import datetime, timedelta
from random import randint

from django.db import models

from sys_util.math.eth import d8


class IntroSettings(models.Model):
    """
        Stores the rules that each user sets for their inbox
    """

    # User these settings are for
    user = models.ForeignKey('silo_user.User', related_name='inbox_settings')

    # When this record was last updated
    updated = models.DateTimeField(default=datetime.now)

    # The minimum amount of tokens a bidder has to pay to start a conversation with this user
    min_bid = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # The maximum number of new conversations to send a User each day for free
    max_daily_intros = models.PositiveSmallIntegerField(default=4, db_index=True)

    # The next time we'll process this User's auction. This value is jittered by +/-3 hours to prevent
    # bid sniping. See plant_eos queues for more info.

    next_check = models.DateTimeField(db_index=True, default=datetime.now)

    def jitter_next_check(self):
        """
            Jitter next_check. Randomize by +/- 3 hours to prevent sniping and keep things interesting
        """
        now = datetime.now()
        hours_in_day = 86400
        noise = randint(-10800, 10800)
        offset = timedelta(seconds=(hours_in_day + noise))
        self.next_check = now + offset
