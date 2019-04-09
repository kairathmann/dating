# -*- coding: utf-8 -*-

from __future__ import division

import newrelic.agent

import sys, time, timeit

from datetime import datetime, timedelta
from random import randint

from django.conf import settings
from django.db import transaction

from plant_eos.handlers.auction.expired import dispatch_notice_auction_expired
from plant_eos.handlers.auction.lost import dispatch_notice_auction_lost
from plant_eos.handlers.auction.won import dispatch_notice_auction_won
from plant_hermes.account.db import TokenAccount
from plant_hermes.journal.user import JournalUser

from silo_message.conversation import Conversation
from silo_message.intro_settings import IntroSettings
from silo_user.user.db import User

from sys_util.math.eth import d8


def worker():
    if settings.USE_NEWRELIC_ON_EOS:
        newrelic.agent.initialize(settings.NEWRELIC_INI_FILE)

    while True:

        start = timeit.default_timer()

        # If we're running on production, wrap the worker with the NewRelic agent
        # ========================================================================

        if settings.USE_NEWRELIC_ON_EOS:

            total = monitor_reap_queue()

        else:
            total = reap_queue()

        stop = timeit.default_timer()
        sys.stdout.write("\nAUCTIONS | {} in {} seconds | RATE: {} / hour".format(str(total), stop - start,
                                                                                  str((total / (stop - start)) * 3600)))
        sys.stdout.flush()

        # Placing the sleep call here causes the worker to run at maximum throughput until it
        # runs out of tasks, then go to sleep to avoid excessive database calls.

        time.sleep(10)


@newrelic.agent.background_task(name='eos_backlog', group='Eos')
def monitor_reap_queue():
    return reap_queue()


def reap_queue():
    """
        STAGE 3 OF 4 IN THE TRANSACTIONAL MESSAGE PIPELINE

        1) Continuously queries silo_user.user.db.User for People who's auctions have between
           now and the previous run

        2) Processes the auctions for each of these People
    """

    total = 0

    while True:

        if total > 1000:
            return total

        with transaction.atomic():

            # All operations must be done with reference to a single timestamp (as opposed to repeatedly calling
            # datetime.now() to avoid failures where the timestamp rolls forward to the next day between calls

            now = datetime.now()

            filters = {

                'next_check__lte': now
            }

            recipient = User.objects.select_for_update().order_by('last_checked').filter(**filters).first()

            # If there are no matching items left, quit
            if not recipient:
                return total

            total += 1

            # Expire unread conversations from their previous auction
            # ===================================================================================================

            filters = {

                'recipient': recipient,
                'bid_status': Conversation.BID_WON
            }

            for record in Conversation.objects.filter(**filters).select_for_update():
                record.bid_status = Conversation.BID_TIMEOUT
                record.last_update = now
                record.save()

                # Return tokens to the message sender

                # Updating of balance and creating a JournalUser records
                amount = record.bid_price
                # Luna fee is 25%
                # TODO need to check what happens on refund regarding fee
                luna_fee = d8(amount * d8(0.0))

                account = TokenAccount.objects.filter(id=record.sender.token_account_id).select_for_update().first()
                account.add_confirmed_balance(d8(amount - luna_fee))
                account.updated = datetime.now()
                account.last_qtum_sync = datetime.now()
                account.revision += 1

                account.hsm_sig = account.calculate_hsm_sig()
                account.save()

                # TODO: What Journal Entry should be updated in that case?
                # TODO Do We want to track those? like refund

                # TODO: notifying users of a conversation expiring is not in the MVP

                # dispatch_notice_auction_expired(
                #
                #     sender = sender,
                #     recipient = recipient,
                #     conversation = conversation,
                #     message = message
                # )

            # Process losing bids from their current auction
            # ===================================================================================================

            filters = {

                'recipient': recipient,
                'bid_status': Conversation.BID_LOSING
            }

            for record in Conversation.objects.filter(**filters).select_for_update():
                record.bid_status = Conversation.BID_LOST
                record.last_update = now
                record.save()

                # Return tokens to the message sender

                # Updating of balance and creating a JournalUser records
                amount = record.bid_price
                # Luna fee is 25%
                # TODO need to check what happens on refund regarding fee
                luna_fee = d8(amount * d8(0.0))

                account = TokenAccount.objects.filter(id=record.sender.token_account_id).select_for_update().first()
                account.add_confirmed_balance(d8(amount - luna_fee))
                account.updated = datetime.now()
                account.last_qtum_sync = datetime.now()
                account.revision += 1

                account.hsm_sig = account.calculate_hsm_sig()
                account.save()

                # TODO: What Journal Entry should be updated in that case?
                # TODO - Add to JournalUser reason? like refund
                # TODO Otherwise it might look like the sender
                # bid on the recipient and that the recipient has
                # bid the sender

                # TODO: notifying users of their bid losing is not in the MVP

                # dispatch_notice_auction_lost(
                #
                #     sender = sender,
                #     recipient = recipient,
                #     conversation = conversation,
                #     message = message
                # )

            # Process winning bids from their current auction
            # ===================================================================================================

            filters = {

                'recipient': recipient,
                'bid_status': Conversation.BID_WINNING
            }

            for record in Conversation.objects.filter(**filters).select_for_update():
                record.bid_status = Conversation.BID_WON
                record.last_update = now
                record.save()

                # TODO: notifying users of their bid winning is not in the MVP

                # dispatch_notice_auction_won(
                #
                #     sender = sender,
                #     recipient = recipient,
                #     conversation = conversation,
                #     message = message
                # )

            # Reset next_check timestamp. Randomize by +/- 3 hours to prevent sniping and keep things interesting
            # ===================================================================================================
            recipient_intro_settings = recipient.inbox_settings.get()
            recipient_intro_settings.next_check = recipient_intro_settings.jitter_time()
            recipient_intro_settings.min_bid = d8(0.0)
            recipient_intro_settings.save()
