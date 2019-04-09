# -*- coding: utf-8 -*-

from __future__ import division

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import get_template

from plant_eos.queues.db import Notice


def dispatch_notice_join_platform(profile_owner, token):
    """
        Dispatches the Notice

        :param profile_owner: The user creating the profile
        :param token: Confirmation token
    """

    base_url = settings.SITE_PROTOCOL + settings.SITE_DOMAIN

    Notice.objects.create(

        type=Notice.TYPE_HELIOS_SIGNUP,

        user_id=profile_owner.id,
        email=profile_owner.email,
        worker_id=Notice.calculate_worker_id(profile_owner.id),

        data={

            'recipient': {

                'first_name': profile_owner.first_name
            },

            # New user signups are sent to the same URL as standard email confirmations. Building
            # a separate endpoint just to confirm new signups is a waste of time.

            'confirm_url': base_url + reverse('AppHelios.Auth.ConfirmEmail', kwargs={'token': token})
        },

        queued=datetime.now()
    )


def render(notice):
    """
        Renders the Notice

        :param notice: Notice objec
    """

    fields = {

        'RECIPIENT_FIRST_NAME': notice.data['recipient']['first_name'],
        'RECIPIENT_EMAIL': notice.email,
        'CONFIRM_URL': notice.data['confirm_url'],

        'LUNA_URL': settings.SITE_PROTOCOL + settings.SITE_DOMAIN
    }

    html_context = {'event_card': 'helios/new_user.html'}
    txt_context = {'event_card': 'helios/new_user.txt'}

    html_context.update(fields)
    txt_context.update(fields)

    return {

        'to_name': notice.data['recipient']['first_name'],
        'to_email': notice.email,

        'subject': 'Just one more step to get started on Luna',
        'from_name': settings.EMAIL_NAME,
        'from_email': settings.EMAIL_NO_REPLY,

        'rendered_html': get_template('event.html').render(html_context),
        'rendered_text': get_template('event.txt').render(txt_context)
    }
