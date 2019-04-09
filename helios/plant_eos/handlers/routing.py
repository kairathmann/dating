# -*- coding: utf-8 -*-

from plant_eos.handlers.auction import accept, expired, losing, lost, won
from plant_eos.handlers.helios import change_email, forgot_pass, new_user
from plant_eos.handlers.message import message_new

from plant_eos.queues.db import Notice


def render_notice(notice):
    """
        Returns a rendered email dict suitable for sending with SendGrid

        :param notice: Notice object
        :return: email data dict
    """

    return {

        Notice.TYPE_AUCTION_ACCEPT: lambda n: accept.render(n),
        Notice.TYPE_AUCTION_EXPIRED: lambda n: expired.render(n),
        Notice.TYPE_AUCTION_LOSING: lambda n: losing.render(n),
        Notice.TYPE_AUCTION_LOST: lambda n: lost.render(n),
        Notice.TYPE_AUCTION_WON: lambda n: won.render(n),

        Notice.TYPE_HELIOS_SIGNUP: lambda n: new_user.render(n),
        Notice.TYPE_HELIOS_CHANGE_EMAIL: lambda n: change_email.render(n),
        Notice.TYPE_HELIOS_FORGOT_PASS: lambda n: forgot_pass.render(n),

        Notice.TYPE_MESSAGE_NEW: lambda n: message_new.render(n)

    }[notice.type](notice)
