#  -*- coding: UTF8 -*-

from django.conf.urls import url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = [

    url(r'^api-helios/', include('api_helios.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('app_helios.urls'))
]
