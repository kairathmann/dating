#  -*- coding: UTF8 -*-

from datetime import datetime, timedelta

import newrelic.agent

from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint

from plant_eos.handlers.helios.change_email import dispatch_notice_change_email

from silo_user.email.db import EmailConfirmation


class EmailResendConfirmation(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Resends a confirmation email for the user, if they have an email confirmation in progress. This
            endpoint is rate-limited.

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

        elif not (upstream['root_active'] or upstream['target_is_viewer']):
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

        # NOTE: we don't void the existing confirmations for this address because its possible that the previously
        # sent confirmations were delayed, not lost, and they might arrive before the new confirmation message we're
        # generating arrives. We generate a new confirmation record for each request to make it easier to track how
        # many failures users are experiencing

        with transaction.atomic():

            latest_confirmation = EmailConfirmation.objects.filter(user=user).order_by('-id').first()

            if not latest_confirmation:
                return

            token = EmailConfirmation.generate_key()

            EmailConfirmation.objects.create(

                user=user,
                email=latest_confirmation.email,
                created=datetime.now(),
                key=token
            )

            dispatch_notice_change_email(

                user=user,
                proposed_email=latest_confirmation.email.email,
                token=token
            )

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
