# -*- coding: utf-8 -*-

from __future__ import division

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import get_template

from plant_eos.queues.db import Notice


def dispatch_notice_change_email(user, proposed_email, token):
    """
        Dispatches the Notice

        :param user: The user changing their email
        :param proposed_email: The email address the User wants to change to
        :param token: Confirmation token
    """

    base_url = settings.SITE_PROTOCOL + settings.SITE_DOMAIN

    Notice.objects.create(

        type=Notice.TYPE_HELIOS_CHANGE_EMAIL,

        user_id=user.id,
        email=proposed_email,
        worker_id=Notice.calculate_worker_id(user.id),

        data={

            'recipient': {

                'first_name': user.first_name,
                'email': user.email
            },

            'confirm_url': base_url + reverse('AppHelios.Auth.ConfirmEmail', kwargs={'token': token})
        },

        queued=datetime.now()
    )


def render(notice):
    """
        Renders the Notice

        :param notice: Notice object
    """

    fields = {

        'RECIPIENT_FIRST_NAME': notice.data['recipient']['first_name'],
        'RECIPIENT_EMAIL': notice.data['recipient']['email'],
        'PROPOSED_EMAIL': notice.email,
        'CONFIRM_URL': notice.data['confirm_url'],
        'LUNA_URL': settings.SITE_PROTOCOL + settings.SITE_DOMAIN
    }

    html_context = {'event_card': 'helios/change_email.html'}
    txt_context = {'event_card': 'helios/change_email.txt'}

    html_context.update(fields)
    txt_context.update(fields)

    return {

        'to_name': notice.data['recipient']['first_name'],

        # Remember, we're sending this message to their *proposed email* ...so we can verify they own it
        'to_email': notice.email,

        'subject': 'Email confirmation required for Luna',
        'from_name': settings.EMAIL_NAME,
        'from_email': settings.EMAIL_NO_REPLY,

        'rendered_html': get_template('event.html').render(html_context),
        'rendered_text': get_template('event.txt').render(txt_context)
    }
