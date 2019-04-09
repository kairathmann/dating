#  -*- coding: UTF8 -*-

# Add our modules folder to the python modules search path

import os, sys, settings

# from plant_hermes.hsm.keyring import HSMkeyring

# Add Django's settings to the OS environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# setproctitle("LUNA > Helios")

# TODO: Implement credentials encryption

# sys.stdout.write("LAUNCH KEY: ")
#
# choice = raw_input()
#
# keyring = HSMkeyring(master_key=choice)
#
# settings.keyring = keyring
# settings.DATABASES = keyring.get_key('DATABASES')

# Import Gunicorn and have it autoload the WSGI file
from gunicorn.app.wsgiapp import run

run()
