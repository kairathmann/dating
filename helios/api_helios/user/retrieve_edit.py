#  -*- coding: UTF8 -*-

from api_helios.base import AbstractHeliosEndpoint


class UserRetrieveForEdit(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Retrieves the "edit" view for a User profile. The edit view is used when a User
            edits their own profile.

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
                        "target_hid": "b3665ea5",   // Used when an admin is editing this User
                        "age": "28",
                        "first_name": "Test",
                        "tagline": "Tagline Text",
                        "bio": "Bio Text",
                        "email": "test@example.com",
                        "avatar_url": "https://example.com/test.jpg"
                        "seeking_age_from": "25",
                        "seeking_age_to": "42",
                        "max_intros": "5"
                    },
                    "success": true
                }
        """

        target_hid = request.POST.get('target_hid')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                # Used when an admin is editing this User
                'target_hid': upstream['target_user'].hid,
                'birthday': upstream['target_user'].dob,
                'age': upstream['target_user'].age,
                'first_name': upstream['target_user'].first_name,
                'tagline': upstream['target_user'].tagline,
                'bio': upstream['target_user'].bio,
                'email': upstream['target_user'].email,

                'avatar_url': upstream['target_user'].get_avatar_url(

                    req_x=255,
                    req_y=255
                ),
                'seeking_age_from': upstream['target_user'].seeking_age_from,
                'seeking_age_to': upstream['target_user'].seeking_age_to,
                'gid_is': upstream['target_user'].gid_is,
                'gid_seeking': upstream['target_user'].gid_seeking,
                # Disable bidding as long as we do not support Know Your Customer (KYC)
                # 'max_intros': upstream['target_user'].inbox_settings.get().max_daily_intros,
            }
        )
