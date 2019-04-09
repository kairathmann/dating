FROM python:2

ENV LUNA_SECRET_KEY 0#05001e@o@@fczx13qhd_%aj5v@-w3r@^dmu8mgzzfo&f5s22

RUN apt-get update -qq
RUN apt-get upgrade -y -qq
RUN apt-get install -y -qq gdal-bin python-gdal

COPY ./helios/requirements.txt /srv/luna/helios/
RUN bash -c 'cd /srv/luna/helios; export PATH=/usr/local/bin:$PATH; export PYTHONHONE=/usr/local; pip install -r requirements.txt'

COPY ./modules /srv/luna/modules/
COPY ./helios /srv/luna/helios/
COPY ./run_python_docker.sh /srv/luna/
COPY ./config/newrelic_luna.ini /srv/luna/config/

ENTRYPOINT /srv/luna/run_python_docker.sh

EXPOSE 8001
