# -*- coding: utf-8 -*-

from __future__ import division

# 1) This script *must* be located in the application root because Django is based on relative
#    filepaths and can't handle things being called from other folders
#
# 2) We load-up django and run our scripts ourselves because the django-extensions "Run script
#    in Django context" feature is *horribly* designed. It eats exceptions, even when set to
#    verbose mode, tries to send emails when things fail, and all sorts of other ridiculous things.


# Load our 3rd-party modules folder
# =====================================================


import os, sys, settings

# Import and load-up Django
# =====================================================

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

django.setup()

import json, requests, time
from datetime import datetime, timedelta

from util_test.base import get_url, create_test_user, login_test_user

from plant_hermes.hsm.adapter import HSMadapter

from silo_user.user.db import User

# result = create_test_user()

s, viewer_hid = login_test_user()

result = json.loads(s.post(

    url=get_url('ApiHelios.Geo.LocateByIP'),

    data={

        'target_hid': viewer_hid
    }

).text)

print result
