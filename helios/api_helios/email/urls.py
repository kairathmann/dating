# -*- coding: utf-8 -*-

from django.conf.urls import url

from .confirm_clear import EmailClearConfirmations
from .confirm_process import EmailProcessConfirmation
from .confirm_resend import EmailResendConfirmation
from .update import EmailUpdate

urlpatterns = [

    url(r'^clear/$', EmailClearConfirmations.as_view(), name='ApiHelios.Email.ClearConfirmations'),
    url(r'^process/$', EmailProcessConfirmation.as_view(), name='ApiHelios.Email.ProcessConfirmation'),
    url(r'^resend/$', EmailResendConfirmation.as_view(), name='ApiHelios.Email.ResendConfirmation'),
    url(r'^update/$', EmailUpdate.as_view(), name='ApiHelios.Email.Update')
]
