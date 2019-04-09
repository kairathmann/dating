# -*- coding: utf-8 -*-

from django.conf.urls import url, include

urlpatterns = [

    url(r'^admin/', include('api_helios.admin.urls')),
    url(r'^auth/', include('api_helios.auth.urls')),
    url(r'^email/', include('api_helios.email.urls')),
    url(r'^geo/', include('api_helios.geo.urls')),
    url(r'^message/', include('api_helios.message.urls')),
    url(r'^user/', include('api_helios.user.urls')),
    url(r'^token/', include('api_helios.token.urls'))
]
