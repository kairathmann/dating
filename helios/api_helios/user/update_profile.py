#  -*- coding: UTF8 -*-

import sys
import newrelic.agent

from datetime import datetime

from django.db import transaction

from silo_user.user.db import User

from sys_util.text.sanitize import sanitize_title, sanitize_textfield
from user_util import UserUtil
from api_helios.base import AbstractHeliosEndpoint

from sys_base.exceptions import HeliosException


class UserUpdateProfile(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Updates a User profile on the platform. Updating a User's password is done using a separate function,
            since it requires ~500ms of CPU time to calculate the hash

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
                    "first_name": "Test",       // (unicode) 3-40 characters
                    "tagline": "Tagline Text",  // (unicode) 0-255 characters
                    "bio": "Bio Text",           // (unicode) 0-16K characters
                    "seeking_age_from": "28",
                    "seeking_age_to": "42",
                    "gid_is": 1,
                    "gid_seeking": 2
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

        birth_date = request.POST.get('birth_date')
        target_hid = request.POST.get('target_hid')
        first_name = request.POST.get('first_name')
        tagline = request.POST.get('tagline')
        bio = request.POST.get('bio')
        seeking_age_from = request.POST.get('seeking_age_from')
        seeking_age_to = request.POST.get('seeking_age_to')
        gid_is = request.POST.get('gid_is')
        gid_seeking = request.POST.get('gid_seeking')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Sanitize
        # =========================================================================

        # birth_date
        # ----------------------

        if birth_date:
            try:
                year = int(birth_date[:4])
                month = int(birth_date[5:7])
                day = int(birth_date[8:10])
                dob = datetime(year, month, day)

                # Prevent age below 18 years
                now = datetime.now()
                if now.year - year < 18 or now.year - year == 18 and (
                    now.month < month or now.month == month and now.day < day
                ):
                    return self.render_error(request, code='error', status=400)

            except:
                return self.render_error(request, code='invalid_dob', status=400)

        else:
            dob = None

        # first_name
        # ----------------------

        if first_name is not None:
            try:
                clean_first_name = sanitize_title(first_name).strip()[:40]

            except HeliosException as e:

                if e.code == 'parse_failure':
                    return self.render_error(request, code='first_name_not_string', status=400)

                else:
                    exc_info = sys.exc_info()
                    raise exc_info[0], exc_info[1], exc_info[2]

            if len(clean_first_name) == 0:
                return self.render_error(request, code='first_name_empty', status=400)

        else:
            clean_first_name = None

        # tagline
        # ----------------------

        if tagline is not None:
            try:
                clean_tagline = sanitize_textfield(tagline).strip()[:120]

            except HeliosException as e:

                if e.code == 'parse_failure':
                    return self.render_error(request, code='tagline_not_string', status=400)

                else:
                    exc_info = sys.exc_info()
                    raise exc_info[0], exc_info[1], exc_info[2]

        else:
            clean_tagline = None

        # bio
        # ----------------------

        if bio is not None:
            try:
                clean_bio = sanitize_textfield(bio).strip()[:2048]

            except HeliosException as e:

                if e.code == 'parse_failure':
                    return self.render_error(request, code='bio_not_string', status=400)

                else:
                    exc_info = sys.exc_info()
                    raise exc_info[0], exc_info[1], exc_info[2]

        else:
            clean_bio = None

        # seeking age
        # ----------------------

        if seeking_age_from and seeking_age_to:
            try:
                clean_seeking_age_from = int(seeking_age_from)
                clean_seeking_age_to = int(seeking_age_to)

            except:
                return self.render_error(request, code='seeking_age_not_int', status=400)

            if not (18 <= clean_seeking_age_from < 120):  # Between 18 and 120
                return self.render_error(request, code='seeking_age_from_invalid', status=400)

            if not (18 <= clean_seeking_age_to < 120):  # Between 18 and 120
                return self.render_error(request, code='seeking_age_to_invalid', status=400)

            if clean_seeking_age_from > clean_seeking_age_to:
                return self.render_error(request, code='seeking_age_from_bigger_then_to', status=400)

        else:
            clean_seeking_age_from = None
            clean_seeking_age_to = None

        # gid_is
        # =======================================================

        if gid_is:
            try:
                clean_gid_is = int(gid_is)
            except:
                return self.render_error(request, code='invalid_gid_is', status=400)

            if clean_gid_is not in User.VALID_GID_IS:
                return self.render_error(request, code='invalid_gid_is', status=400)
        else:
            clean_gid_is = None

        # gid_seeking
        # =======================================================

        if gid_seeking:
            try:
                clean_gid_seeking = int(gid_seeking)
            except:
                return self.render_error(request, code='invalid_gid_seeking', status=400)

            if clean_gid_seeking not in User.VALID_GID_SEEKING:
                return self.render_error(request, code='invalid_gid_seeking', status=400)
        else:
            clean_gid_seeking = None

        # Update DB
        # =========================================================================

        with transaction.atomic():

            # Reselect target_user with an UPDATE LOCK
            user = User.objects.select_for_update().get(id=upstream['target_user'].id)

            if dob:
                user.dob = dob
            if clean_first_name is not None:
                user.first_name = clean_first_name
            if clean_tagline is not None:
                user.tagline = clean_tagline
            if clean_bio is not None:
                user.bio = clean_bio
            if clean_seeking_age_from:
                user.seeking_age_from = clean_seeking_age_from
            if clean_seeking_age_to:
                user.seeking_age_to = clean_seeking_age_to
            if clean_gid_seeking:
                user.gid_seeking = clean_gid_seeking
            if clean_gid_is:
                user.gid_is = clean_gid_is

            # Update state
            if user.state == User.INCOMPLETE and UserUtil.is_complete(user):
                user.state = User.ACTIVE

            user.updated = datetime.now()

            user.save()

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
