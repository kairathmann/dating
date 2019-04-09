# -*- coding: utf-8 -*-

from django.conf.urls import url

from .set_as_root import SetAsRoot
from .set_as_self import SetAsSelf

urlpatterns = [

    url(r'^set_as_root/$', SetAsRoot.as_view(), name='ApiHelios.Admin.SetAsRoot'),
    url(r'^set_as_self/$', SetAsSelf.as_view(), name='ApiHelios.Admin.SetAsSelf')
]
