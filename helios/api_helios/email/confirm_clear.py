#  -*- coding: UTF8 -*-

from datetime import datetime, timedelta

import newrelic.agent

from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint
from silo_user.email.db import EmailAddress, EmailConfirmation


class EmailClearConfirmations(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Clears all email address confirmations the User has in progress. This endpoint is rate-limited.

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5"
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "code": null,
                    "data": {

                        "viewer_hid": "b3665ea5"
                    },
                    "success": true
                }
        """

        target_hid = request.POST.get('target_hid')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Rate-limit requests
        # =======================================================================

        user = upstream['target_user']

        filters = {

            'email__user': user,
            'created__gte': datetime.now() - timedelta(minutes=EmailConfirmation.THROTTLE_WINDOW)
        }

        if bool(EmailConfirmation.objects.filter(**filters).count() > EmailConfirmation.THROTTLE_LIMIT):
            return self.render_error(request, code='request_throttled')

        filters = {

            'user': user,
            'status': EmailConfirmation.STATUS_READY
        }

        if EmailConfirmation.objects.filter(**filters).exists():

            with transaction.atomic():

                # Void all existing confirmations so that the user receives the correct error message when
                # they click on a stale confirmation link

                filters = {

                    'user': user,
                    'status': EmailConfirmation.STATUS_READY
                }

                for confirmation in EmailConfirmation.objects.filter(**filters):
                    confirmation.status = EmailConfirmation.STATUS_VOID
                    confirmation.save()

                # Delete all email address records that belong to the user EXCEPT the one that corresponds to
                # the user's current email address as set in their User record

                EmailAddress.objects.filter(user=user).exclude(email=user.email).delete()

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
