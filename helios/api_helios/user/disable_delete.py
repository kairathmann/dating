#  -*- coding: UTF8 -*-

from api_helios.base import AbstractHeliosEndpoint
from django.contrib.auth import authenticate, logout
from django.db import transaction
from silo_user.exit_survey.exit_survey import ExitSurvey
from silo_user.user.db import User


class UserDisableDelete(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Disables or deletes a user.

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5"
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",
                    },
                    "success": true
                }
        """

        password = request.POST.get('password', '')[:255]
        target_hid = request.POST.get('target_hid')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        target_user = upstream['target_user']

        if not authenticate(email=target_user.email, password=password):
            return self.render_error(request, code='wrong_password', status=400)

        if target_user.state != User.INCOMPLETE and target_user.state != User.ACTIVE:
            return self.render_error(request, code='illegal_state', status=400)

        reasons = request.POST.get('reasons')
        reasons_list = reasons.split(';')
        comment = request.POST.get('comment')

        if comment:
            clean_comment = comment[:ExitSurvey.COMMENT_MAX_LENGTH]
        else:
            clean_comment = None

        state = self.state()

        with transaction.atomic():
            exit_survey = ExitSurvey.objects.create(
                user=target_user,
                state=state,
                reason1='1' in reasons_list,
                reason2='2' in reasons_list,
                reason3='3' in reasons_list,
                reason4='4' in reasons_list,
                reason5='5' in reasons_list,
                comment=clean_comment,
            )
            exit_survey.save()

            user = User.objects.select_for_update().get(id=target_user.id)
            user.state = state
            self.adjust_user(user)
            user.save()

        logout(request)

        return self.render_response(
            request=request,
            data={'viewer_hid': upstream['viewer'].hid}
        )


class UserDisable(UserDisableDelete):

    def state(self):
        return User.DISABLED

    def adjust_user(self, user):
        pass


class UserDelete(UserDisableDelete):

    def state(self):
        return User.DELETED

    def adjust_user(self, user):
        # TODO set various fields to None
        pass
