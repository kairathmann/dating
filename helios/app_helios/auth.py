#  -*- coding: UTF8 -*-

import newrelic.agent

from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.generic import View


class AuthConfirmEmail(View):

    @newrelic.agent.function_trace()
    @cache_control(no_cache=True)
    def get(self, request, **kwargs):
        return render(request, 'root.html', {})


class AuthForgotPass(View):

    @newrelic.agent.function_trace()
    @cache_control(no_cache=True)
    def get(self, request, **kwargs):
        return render(request, 'root.html', {})


class AuthLogin(View):

    @newrelic.agent.function_trace()
    @cache_control(no_cache=True)
    def get(self, request, **kwargs):
        return render(request, 'root.html', {})
