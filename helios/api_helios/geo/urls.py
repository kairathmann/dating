# -*- coding: utf-8 -*-

from django.conf.urls import url

from .by_ip import GeolocateByIP
from .by_name import GeolocateByName
from .by_point import GeolocateByPoint

urlpatterns = [

    url(r'^by-ip/$', GeolocateByIP.as_view(), name='ApiHelios.Geo.LocateByIP'),
    url(r'^by-name/$', GeolocateByName.as_view(), name='ApiHelios.Geo.LocateByName'),
    url(r'^by-point/$', GeolocateByPoint.as_view(), name='ApiHelios.Geo.LocateByPoint')
]
