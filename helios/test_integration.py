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

from plant_hermes.test_hermes_integration import HermesIntegrationTest

HermesIntegrationTest().main()

# Uncomment the following to perform Hermes stress test
# from plant_hermes.test_hermes_stress import HermesStressTest
# HermesStressTest().main()

# from util_test.user import test_user
# from util_test.platform import flush_database
#
# flush_database()
# test_user()
