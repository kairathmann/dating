# -*- coding: utf-8 -*-

from __future__ import division

import os, sys, settings

import django
from django.conf import settings

from setproctitle import setproctitle

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

worker_id = sys.argv[1]

# If the worker is running on a devbox
if settings.RUNNING_ON_PROD:

    arm_worker = True
    setproctitle("LUNA > EOS Notice {} [ARMED]".format(str(worker_id)))

else:
    arm_worker = False
    setproctitle("LUNA > EOS Notice {} [SAFE]".format(str(worker_id)))

django.setup()

from plant_eos.queues.notice import worker

worker(worker_id, arm_worker)
