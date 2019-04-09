#!/usr/bin/env bash

set -x

export PYTHONPATH=/srv/luna/helios:/srv/luna/modules
export PYTHONHOME=/usr/local

cd /srv/luna/helios/

echo ===== RUN DATABASE MIGRATION =====
python manage.py migrate auth
python manage.py migrate sites
python manage.py migrate

echo ===== RUN PYTHON SERVER =====
python -u manage.py runserver 0.0.0.0:8001
