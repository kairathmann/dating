# -*- coding: utf-8 -*-

from django.conf.urls import url

from .forgot_pass_reset import ForgotPassReset
from .forgot_pass_email import ForgotPassSendEmail

urlpatterns = [

    url(r'^forgot-pass-email/$', ForgotPassSendEmail.as_view(), name='ApiHelios.Auth.ForgotPassSendEmail'),
    url(r'^forgot-pass-reset/$', ForgotPassReset.as_view(), name='ApiHelios.Auth.ForgotPassReset')
]
