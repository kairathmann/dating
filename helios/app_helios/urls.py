# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from .auth import AuthConfirmEmail, AuthForgotPass, AuthLogin
from .user import UserLanding

urlpatterns = [

    url(r'^user/(?P<hid>[a-f0-9]+)/', include([

        url(r'^landing/$', UserLanding.as_view(), name='AppHelios.User.Home')

    ])),

    url(r'^auth/', include([

        url(r'^confirm-email/(?P<token>[a-zA-Z0-9]+)/$', AuthConfirmEmail.as_view(),
            name='AppHelios.Auth.ConfirmEmail'),
        url(r'^forgot-pass/(?P<token>[a-zA-Z0-9]+)/$', AuthForgotPass.as_view(), name='AppHelios.Auth.ForgotPass'),
        url(r'^login/$', AuthLogin.as_view(), name='AppHelios.Auth.Login')
    ]))
]
