#  -*- coding: UTF8 -*-

from django.http import JsonResponse
from django.views.generic import View


class AbstractJSONEndpoint(View):
    RATE_LIMIT = {

        'max_1s': 1,
        'max_10s': 3,
        'max_100s': 20,
        'max_1000s': 100
    }

    def viewer_logged_in(self, upstream):
        """
            Evaluates the current request against policy 'logged_in'

            :param upstream:
            :return: True if the current request should be permitted, otherwise False
        """

        return upstream['request'].user.is_authenticated()

    def render_error(self, request, code, data='', status=200):
        """
            Renders an error
        """

        return JsonResponse({'data': data, 'code': code, 'success': False}, status=status)

    def render_response(self, request, data, status=200):
        """
            Renders a response
        """

        return JsonResponse({'data': data, 'code': None, 'success': True}, status=status)
