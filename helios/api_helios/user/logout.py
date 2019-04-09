#  -*- coding: UTF8 -*-

import newrelic.agent

from django.contrib.auth import authenticate, logout

from silo_user.user.db import User

from api_helios.base import AbstractHeliosEndpoint


class Logout(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Logs-out a User on the platform

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5"
                    },
                    "success": true
                }
        """

        logout(request)

        return self.render_response(
            request=request,
            data={
            }
        )
