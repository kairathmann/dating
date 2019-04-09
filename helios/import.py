#  -*- coding: UTF8 -*-

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

import util_import.patch_2018_02_15_01_reset_sequences.base as reset_sequences


# Run database import scripts
# =====================================================

def migrate():
    reset_sequences.migrate()

    pass


migrate()
print "\n"
