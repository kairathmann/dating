#!/usr/bin/env bash

cd /srv/luna/helios
python luna.py stop

cd ..
rm -r static/dist
git reset --hard HEAD
git checkout develop
git pull
npm install --silent --prefix static/src # Install deps for frontend
npm run build:staging --prefix static/src # Create new build
echo "Frontend succeeded"

cd helios
python manage.py migrate
python luna.py restart
