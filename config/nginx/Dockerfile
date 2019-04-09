FROM nginx

COPY ./config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./config/nginx/helios/dev_server /srv/luna/config/nginx/helios/dev_server
COPY ./config/nginx/ssl/dev_server /srv/luna/config/nginx/ssl/dev_server
COPY ./static/dist /srv/luna/static/dist/

EXPOSE 443
