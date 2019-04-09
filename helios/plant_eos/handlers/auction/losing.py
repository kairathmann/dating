# -*- coding: utf-8 -*-

from __future__ import division

import time

from django.conf import settings
from django.db import connection
from django.template.loader import get_template
from silo_user.user.db import User

from plant_eos.queues.db import Notice


def dispatch_notice_auction_losing(sender, recipient, conversation):
    pass


def process(event):
    pass


def render(guid, data):
    pass
