#  -*- coding: UTF8 -*-

import random
from datetime import datetime
from api_helios.base import AbstractHeliosEndpoint
from django.db.models import Q
from sys_util.text.date import add_years
from silo_user.user.db import User
from silo_user.user.gender_id import GenderId


class UserRetrieve(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Retrieves the "recommend" view for multiple User profile. The recommend view is used when a User
            Request a recommendations for profiles to match with.

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5"
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": [{
                        "target_hid": "b3665ea5",

                        "min_bid": "2.75024",

                        "age": "28",
                        "first_name": "Test",
                        "tagline": "Tagline Text",
                        "bio": "Bio Text",
                        "avatar_url": "https://example.com/test.jpg"
                    },
                    {
                        "target_hid": "a1975dc2",

                        "min_bid": "0",

                        "age": "29",
                        "first_name": "Rumi",
                        "tagline": "Love will find its way through all languages on its own",
                        "bio": "Bio Text",
                        "avatar_url": "https://example.com/test.jpg"
                    }],
                    "success": true
                }
        """

        target_hid = request.POST.get('target_hid')
        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        target_user = upstream['target_user']

        people = self.people(target_user, 15)

        return self.render_response(

            request=request,

            data={
                'target_hid': target_user.hid,

                'people': [{

                    'hid': user.hid,
                    'min_bid': user.inbox_settings.get().min_bid,
                    'age': user.age,
                    'gid_is': user.gid_is,
                    'first_name': user.first_name,
                    'tagline': user.tagline,
                    'bio': user.bio,

                    'avatar_url': user.get_avatar_url(

                        req_x=512,
                        req_y=512
                    )

                } for user in people]
            }
        )

    def recommended(self, target_user, max_results):
        """
        Returns recommended users for a given user.
        :param target_user: The user for whom recommended users should be returned.
        :param max_results: The maximum number of recommended users to return.
        :return: A list of between 0 and max_results recommended users.
        :raise ValueError: If max_results < 0.
        """

        if max_results < 0:
            return ValueError('max_results must not be negative.')

        if max_results == 0:
            return []

        # Exclude current user, Exclude past reactions (Matches, Un-matches for the current user)
        excl = (
            Q(hid=target_user.hid) |
            Q(sender_reaction__recipient=target_user.id) |
            Q(recipient_reaction__sender=target_user.id)
        )

        now = datetime.now()
        incl = {
            # Filter by state
            'state': User.ACTIVE,

            # Filter by wanted age
            'dob__gte': add_years(now, -target_user.seeking_age_to),
            'dob__lte': add_years(now, -target_user.seeking_age_from),

            # Filter by result user wanted age
            'seeking_age_from__lte': target_user.age,
            'seeking_age_to__gte': target_user.age,

            # Filter by sexuality and gender
            'gid_seeking__in': [target_user.gid_is, GenderId.ID_BOTH],
        }
        if target_user.gid_seeking != GenderId.ID_BOTH:
            incl['gid_is'] = target_user.gid_seeking

        # Limit results to prevent scaling issues.
        return list(User.objects.filter(**incl).exclude(excl)[:max_results])


class UserRetrieveForRecommend(UserRetrieve):
    def people(self, target_user, max_results):
        return self.recommended(target_user, max_results)


class UserRetrieveForSkipped(UserRetrieve):

    def people(self, target_user, max_results):
        result = self.recommended(target_user, max_results)
        result.extend(self.skipped(target_user, max_results - len(result)))
        return result

    def skipped(self, target_user, max_results):
        """
        Returns skipped users for a given user that still match the search criteria of both sides. If there exist
        non-skipped users, those are returned first.
        :param target_user: The user for whom skipped users should be returned.
        :param max_results: The maximum number of skipped users to return.
        :return: A list of between 0 and max_results skipped users.
        :raise ValueError: If max_results < 0.
        """

        if max_results < 0:
            return ValueError('max_results must not be negative.')

        if max_results == 0:
            return []

        # Exclude current user
        excl = (
            Q(hid=target_user.hid)
        )

        now = datetime.now()
        incl = {
            # Filter by existing negative reaction
            'recipient_reaction__sender': target_user.id,
            'recipient_reaction__is_match': False,

            # Filter by state
            'state': User.ACTIVE,

            # Filter by wanted age
            'dob__gte': add_years(now, -target_user.seeking_age_to),
            'dob__lte': add_years(now, -target_user.seeking_age_from),

            # Filter by result user wanted age
            'seeking_age_from__lte': target_user.age,
            'seeking_age_to__gte': target_user.age,

            # Filter by sexuality and gender
            'gid_seeking__in': [target_user.gid_is, GenderId.ID_BOTH],
        }
        if target_user.gid_seeking != GenderId.ID_BOTH:
            incl['gid_is'] = target_user.gid_seeking

        # Limit results to prevent scaling issues.
        return list(User.objects.filter(**incl).exclude(excl).order_by('recipient_reaction__last_update')[:max_results])
