#!/usr/bin/env bash

service nginx start
cd /srv/luna/helios
python manage.py runserver 0.0.0.0:8001
