"""
    WSGI config for helios

    It exposes the WSGI callable as a module-level variable named 'application'.

    For more information on this file, see
    https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

# Add our modules folder to the python modules search path
import os, sys, settings
import newrelic.agent
from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helios.settings")

if settings.USE_NEWRELIC_ON_HELIOS:
    newrelic.agent.initialize(settings.NEWRELIC_INI_FILE)

application = get_wsgi_application()
