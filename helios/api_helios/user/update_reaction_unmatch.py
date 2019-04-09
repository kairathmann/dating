#  -*- coding: UTF8 -*-

from datetime import datetime

import sys
import newrelic.agent

from django.db import transaction

from api_helios.base import AbstractHeliosEndpoint
from silo_user.reaction.reaction import Reaction, ReactionUtil
from sys_base.exceptions import HeliosException

from sys_util.text.number import hid_is_valid
from silo_user.user.db import User


class UserUpdateReactionUnmatch(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Set a user reaction on another user to un-match.
            We are separating match to un-match because match is triggered
            internally by "Bidding" on a user and should not be called from the external user

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
                    "recipient_hid": "2c968e7f"
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5"
                    },
                    "success": true
                }

        """

        target_hid = request.POST.get('target_hid')
        recipient_hid = request.POST.get('recipient_hid')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # sender_hid / recipient_hid
        # ----------------------------------------------------------------------
        sender = upstream['target_user']

        if not hid_is_valid(recipient_hid):
            return self.render_error(request, code='invalid_recipient_hid', status=400)

        if target_hid == recipient_hid:
            return self.render_error(request, code='cannot_react_to_self', status=400)

        # Run db operations
        # =======================================================================

        try:

            with transaction.atomic():

                recipient = User.objects.filter(hid=recipient_hid).first()

                if not recipient:
                    raise HeliosException(desc='Nonexistent recipient', code='nonexistent_recipient')

                # Check for invalid API request (already an existing reaction)
                # =======================================================================

                ReactionUtil.create_or_update_reaction(sender, recipient, False)

            # Trap exceptions during transaction
            # =======================================================================

        except HeliosException as e:

            if e.code in [
                'nonexistent_recipient',
                'existing_inverse_reaction',
                'existing_positive_reaction',
            ]:
                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
