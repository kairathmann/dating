#  -*- coding: UTF8 -*-

import sys
import newrelic.agent

from datetime import datetime, timedelta

from django.contrib.auth import login
from django.db import transaction
from silo_user.email.db import EmailConfirmation, EmailAddress
from silo_user.user.db import User

from api_helios.base import AbstractHeliosEndpoint

from sys_base.exceptions import HeliosException


class EmailProcessConfirmation(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Processes an email confirmation request

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "token": "9Q9rGfymnFUjXmzkaAJw2u4js4eGKo3l",     // Email confirmation token
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

        token = request.POST.get('token', '')[:32]

        if not token or (len(token) != 32):
            return self.render_error(request, code='invalid_token')

        try:

            with transaction.atomic():

                # Fetched using select_for_update() to block other threads from claiming this item, as
                # could potentially happen with two page refreshes in rapid succession

                confirmation = EmailConfirmation.objects.select_for_update().filter(key=token).first()

                if not confirmation:
                    raise HeliosException(desc='Nonexistent token', code='nonexistent_token')

                user = User.objects.select_for_update().get(id=confirmation.user_id)

                email = EmailAddress.objects.select_for_update().filter(id=confirmation.email_id).first()

                # Already confirmed
                # -------------------------------------

                if email and email.verified:
                    raise HeliosException(desc='Already confirmed', code='already_confirmed')

                # Voided or expired
                # -------------------------------------

                voided = confirmation.status in [EmailConfirmation.STATUS_USED, EmailConfirmation.STATUS_VOID]
                expired = confirmation.created < (datetime.now() - timedelta(3))

                if voided or expired:
                    raise HeliosException(desc='Confirmation expired', code='expired')

                # Bounced or disabled
                # -------------------------------------

                # CASE #1: The user reports the confirmation message as spam through their email provider, then decides
                # to open it up later and click on the confirmation link
                #
                # CASE #2: A customer is using a poorly designed anti-spam system that reports messages as bounced,
                # but then eventually delivers them to the user "because we can totally fool spammers that way!"
                #
                # In both of these cases, we can't let a user use the email address, because SendGrid will block
                # all further sends to it until we manually reset it.

                if email.disabled:
                    raise HeliosException(desc='Bounced or Invalid email', code='bounced_or_invalid')

                # Delete all email addresses that belong to the User, except the one we just confirmed
                EmailAddress.objects.filter(user=email.user).exclude(id=email.id).delete()

                # The confirmed email address becomes the User's new primary address
                email.primary = True

                email.verified = True
                email.verified_timestamp = datetime.now()

                email.save()

                # We also have to update the email address in the User record

                user.email = email.email
                user.save()

                # Mark this confirmation as used so that the user receives the correct error message when
                # they click on a stale confirmation link

                confirmation.status = EmailConfirmation.STATUS_USED
                confirmation.save()

                # Void all existing confirmations so that the user receives the correct error message when
                # they click on a stale confirmation link

                filters = {

                    'user': email.user,
                    'status': EmailConfirmation.STATUS_READY
                }

                for record in EmailConfirmation.objects.filter(**filters):
                    record.status = EmailConfirmation.STATUS_VOID
                    record.save()

                # Login the user

                modified_user = email.user
                modified_user.backend = "silo_user.user.auth_handlers.auth_backends.AuthenticationBackend"

                login(request, modified_user)


        except HeliosException as e:

            if e.code in ['invalid_token', 'nonexistent_token', 'already_confirmed',
                          'expired', 'bounced_or_invalid']:

                return self.render_error(request, code=e.code)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        return self.render_response(request=request, data={})
