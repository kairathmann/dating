# -*- coding: utf-8 -*-

from __future__ import division

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import get_template

from plant_eos.queues.db import Notice


def dispatch_notice_forgot_pass(profile_owner, token):
    """
        Dispatches the Notice

        :param profile_owner: The user creating the profile
        :param token: Confirmation token
    """

    base_url = settings.SITE_PROTOCOL + settings.SITE_DOMAIN

    Notice.objects.create(

        type=Notice.TYPE_HELIOS_FORGOT_PASS,

        user_id=profile_owner.id,
        email=profile_owner.email,
        worker_id=Notice.calculate_worker_id(profile_owner.id),

        data={

            'recipient': {

                'first_name': profile_owner.first_name
            },

            'confirm_url': base_url + reverse('AppHelios.Auth.ForgotPass', kwargs={'token': token})
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

    html_context = {'event_card': 'helios/forgot_pass.html'}
    txt_context = {'event_card': 'helios/forgot_pass.txt'}

    html_context.update(fields)
    txt_context.update(fields)

    return {

        'to_name': notice.data['recipient']['first_name'],

        # Remember, we're sending this message to their proposed email so we can verify they own it
        'to_email': notice.email,

        'subject': 'Password reset on Luna',
        'from_name': settings.EMAIL_NAME,
        'from_email': settings.EMAIL_NO_REPLY,

        'rendered_html': get_template('event.html').render(html_context),
        'rendered_text': get_template('event.txt').render(txt_context)
    }
