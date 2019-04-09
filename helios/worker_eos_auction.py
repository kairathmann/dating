# -*- coding: utf-8 -*-

from __future__ import division

import os, sys, settings

import django
from setproctitle import setproctitle

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

setproctitle("LUNA > EOS Auction")

django.setup()

from plant_eos.queues.auction import worker

worker()
