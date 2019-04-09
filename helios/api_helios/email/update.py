#  -*- coding: UTF8 -*-

import sys

import newrelic.agent

from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint

from plant_eos.handlers.helios.change_email import dispatch_notice_change_email

from silo_user.email.db import EmailConfirmation, EmailAddress

from sys_base.exceptions import HeliosException


class EmailUpdate(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Starts the process of updating a User's email address. Sends an email update confirmation email
            to the specified address. If the user clicks on the unique URL in the email, their email address
            will be updated. This endpoint is rate-limited.

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "proposed_email": "test02@example.com",    // New email address
                    "password": "12345678",                 // User's current password
                    "target_hid": "b3665ea5"                // hid of User to modify
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

        proposed_email = request.POST.get('proposed_email')
        password = request.POST.get('password', '')[:255]
        target_hid = request.POST.get('target_hid')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        if not upstream['root_active']:

            if not upstream['target_is_viewer']:
                return self.render_error(request, code='access_denied', status=403)

            elif not password:
                return self.render_error(request, code='password_empty', status=400)

            elif not upstream['viewer'].check_password(password):
                return self.render_error(request, code='password_invalid', status=400)

        # Sanitize inputs
        # =======================================================================

        if not proposed_email:
            return self.render_error(request, code='email_empty', status=400)

        try:
            validate_email(proposed_email)

        except ValidationError:
            return self.render_error(request, code='email_invalid', status=400)

        if len(proposed_email) > 254:
            return self.render_error(request, code='email_exceeds_max_length', status=400)

        # IMPORTANT: we convert all email addresses to lowercase using .lower(), because the database *is*
        # case sensitive, but the email protocol *is not*. If we failed to do this, attackers could
        # hijack profiles by using email addresses with mixed capitalization.

        clean_email = proposed_email.lower()
        user = upstream['target_user']

        if user.email == clean_email:
            return self.render_error(request, code='already_current_email', status=400)

        if EmailAddress.objects.filter(email=clean_email).exclude(user=user).exists():
            # This traps trying to use an email that another user is currently confirming
            return self.render_error(request, code='email_already_exists', status=400)

        # Rate-limit requests
        # =======================================================================

        filters = {

            'email__user': user,
            'created__gte': datetime.now() - timedelta(minutes=EmailConfirmation.THROTTLE_WINDOW)
        }

        if bool(EmailConfirmation.objects.filter(**filters).count() > EmailConfirmation.THROTTLE_LIMIT):
            return self.render_error(request, code='request_throttled', status=400)

        # Create db records and send confirmation email
        # =======================================================================

        try:

            with transaction.atomic():

                # If the user doesn't already have an EmailAddress record set for the proposed email address
                # they want to update their primary email address to, create one
                # ----------------------------------------------------------------------------------------------

                email_address = EmailAddress.objects.select_for_update().filter(user=user, primary=False).first()

                if not email_address:

                    email_address = EmailAddress.objects.create(

                        user=user,
                        email=clean_email,
                        verified=False,
                        primary=False
                    )

                # If the user has an existing confirmation underway using a different email address, clear
                # the records for the old address and create a new one
                # ----------------------------------------------------------------------------------------------

                elif email_address.email != clean_email:

                    # Void all existing confirmations so that the user receives the correct error message when
                    # they click on a stale confirmation link

                    filters = {

                        'user': user,
                        'status': EmailConfirmation.STATUS_READY
                    }

                    for confirmation in EmailConfirmation.objects.filter(**filters):
                        confirmation.status = EmailConfirmation.STATUS_VOID
                        confirmation.save()

                    # SECURITY: delete the current EmailAddress record and create a new one for the new address to
                    # stop the user confirming an email address they don't control by recycling a stale confirmation

                    email_address.delete()

                    email_address = EmailAddress.objects.create(

                        user=user,
                        email=clean_email,
                        verified=False,
                        primary=False
                    )


                # If the user is trying to send a second, third, etc confirmation email to an address that we've
                # already disabled due to it being invalid or having multiple bounces, reject the request
                # ----------------------------------------------------------------------------------------------

                elif (email_address.email == clean_email) and email_address.disabled:
                    raise HeliosException(desc='Bounced or Invalid email', code='bounced_or_invalid')

                # Generate a confirmation record and send the email

                token = EmailConfirmation.generate_key()

                EmailConfirmation.objects.create(

                    user=user,
                    email=email_address,
                    created=datetime.now(),
                    key=token
                )

                dispatch_notice_change_email(

                    user=user,
                    proposed_email=proposed_email,
                    token=token
                )


        # Trap errors
        # =======================================================================

        except HeliosException as e:

            if e.code in ['bounced_or_invalid']:
                return self.render_error(request, code=e.code)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
