# -*- coding: utf-8 -*-

from __future__ import division

import json, requests, sys, time, timeit
import newrelic.agent

from datetime import datetime

from django.conf import settings
from django.db import transaction

from plant_eos.handlers.routing import render_notice
from plant_eos.queues.db import Notice
from plant_eos.journal.db import SentNotice

from silo_user.email.db import EmailAddress
from sys_base.exceptions import HeliosException


def worker(worker_id, arm_worker):
    if settings.USE_NEWRELIC_ON_EOS:
        newrelic.agent.initialize(settings.NEWRELIC_INI_FILE)

    while True:

        start = timeit.default_timer()

        if settings.USE_NEWRELIC_ON_EOS:

            total = monitor_reap_queue(worker_id, arm_worker)

        else:
            total = reap_queue(worker_id, arm_worker)

        stop = timeit.default_timer()

        sys.stdout.write("\nNOTICES | {} in {} seconds | RATE: {} / hour".format(

            str(total), stop - start,
            str((total / (stop - start)) * 3600))
        )

        sys.stdout.flush()

        # Placing the sleep call here causes the worker to run at maximum throughput until it
        # runs out of tasks, then go to sleep to avoid excessive database calls.

        time.sleep(10)


@newrelic.agent.background_task(name='eos_notice', group='Eos')
def monitor_reap_queue(worker_id, arm_worker):
    return reap_queue(worker_id, arm_worker)


def reap_queue(worker_id, arm_worker):
    """
        Processes transactional notifications
    """

    total = 0

    while True:

        if total > 1000:
            return total

        raise_exception = False
        exception_text = None

        with transaction.atomic():

            if worker_id == '*':

                # Allow a single worker to process records for all workers by passing '*' instead of an
                # integer worker_id. Note that you have to put quotes around the * character at the command
                # prompt. This is used when monitoring the rendering queue during testing.

                notice = Notice.objects.select_for_update().all().order_by('queued').first()

            else:

                notice = Notice.objects.select_for_update().filter(worker_id=worker_id).order_by('queued').first()

            # CASE 1: If we've run out of items, quit
            # ---------------------------------------------------------------------------------------------

            if not notice:

                return total

            # CASE 2: This is not a whitelisted email address, and the worker isn't armed
            # ---------------------------------------------------------------------------------------------

            elif (notice.email not in settings.EMAIL_WHITELIST) and (arm_worker is not True):

                discard_test_notice(notice)

            # CASE 3: The recipient's email address is disabled
            # ---------------------------------------------------------------------------------------------

            elif EmailAddress.objects.filter(user=notice.user, primary=True, disabled=True).exists():

                discard_drop_notice(notice)

            # CASE 4: Otherwise, try to send the message using the Email API Provider's endpoint
            # ---------------------------------------------------------------------------------------------

            else:

                raise_exception, exception_text = send_notice(notice)

            # Finally, delete the Notice
            # --------------------------------------

            notice.delete()
            total += 1

        # Raise exception so NewRelic logs the event. This has to be done outside the transaction block
        # so it doesn't get rolled-back. Supervisord will automatically restart the worker after the
        # exception causes it to exit
        # ====================================================================================================

        if raise_exception:
            newrelic.agent.add_custom_parameter('guid', notice.guid)
            newrelic.agent.add_custom_parameter('user', notice.user)
            newrelic.agent.add_custom_parameter('email', notice.email)
            newrelic.agent.add_custom_parameter('worker_id', notice.worker_id)
            newrelic.agent.add_custom_parameter('type', notice.type)

            raise HeliosException(desc=exception_text, code='rendering_error')


def discard_test_notice(notice):
    """

        :param notice:
        :return:
    """

    SentNotice.objects.create(

        user=notice.user,
        email=notice.email,
        notice_type=notice.type,
        queued=notice.queued,
        processed=datetime.now(),
        data=notice.data,
        api_response=None,
        status=SentNotice.STATUS_EOS_TEST,
        guid=notice.guid
    )


def discard_drop_notice(notice):
    """

        :param notice:
        :return:
    """

    SentNotice.objects.create(

        user=notice.user,
        email=notice.email,
        notice_type=notice.type,
        queued=notice.queued,
        processed=datetime.now(),
        data=notice.data,
        api_response=None,
        status=SentNotice.STATUS_EOS_DROP,
        guid=notice.guid
    )


def send_notice(notice):
    """

        :param notice:
        :return:
    """

    status = SentNotice.STATUS_EOS_SENT
    raise_exception = False
    exception_text = None

    try:
        email_data = render_notice(notice)

    except Exception as e:

        status = SentNotice.STATUS_EOS_FAIL

        exception_text = str(e)
        raise_exception = True

    if status != SentNotice.STATUS_EOS_FAIL:

        data = {

            'personalizations': [

                {
                    'to': [
                        {
                            'email': email_data['to_email'],
                            'name': email_data['to_name']
                        }
                    ],
                    'subject': email_data['subject']
                }
            ],

            'from': {

                'email': email_data['from_email'],
                'name': email_data['from_name']
            },

            'content': [

                {'type': 'text/plain', 'value': email_data['rendered_text']},
                {'type': 'text/html', 'value': email_data['rendered_html']}
            ],

            'custom_args': {

                'origin': 'plant_eos',
                'guid': str(notice.guid)
            }
        }

        # SendGrid's API returns beautiful JSON-encoded error messages
        # ========================================================================================
        # {
        #   'field': 'custom_args',
        #   'message': 'Invalid type. Expected: object, given: array.',
        #   'help': 'http://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/errors.html#message.custom_args'
        # }

        try:

            response = requests.post(

                url='https://api.sendgrid.com/v3/mail/send',
                headers={
                    'Content-type': 'application/json',
                    'Authorization': 'Bearer {}'.format(settings.SENDGRID_API_SEND_KEY)
                },
                data=json.dumps(data),

                # Requests MUST be time-limited to prevent the process from infinitely blocking if
                # the remote server never responds

                timeout=10
            )

        except Exception as e:

            status = SentNotice.STATUS_EOS_FAIL
            exception_text = str(e)
            raise_exception = True

        if response.status_code not in [200, 202]:
            print response.status_code
            print response.content
            status = SentNotice.STATUS_API_ERROR
            exception_text = json.loads(response.content)
            raise_exception = True

    SentNotice.objects.create(

        user=notice.user,
        email=notice.email,
        notice_type=notice.type,
        queued=notice.queued,
        processed=datetime.now(),
        data=notice.data,
        api_response=exception_text,
        status=status,
        guid=notice.guid
    )

    return raise_exception, exception_text
