#  -*- coding: UTF8 -*-


from api_helios.base import AbstractHeliosEndpoint


class UserRetrieveForSingle(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Retrieves the "single" view for a User profile. The single view is used when a User
            views another User's profile.

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

                        "min_bid": "2.75024",
                        "gid_is": 2, // Gender
                        "age": "28",
                        "first_name": "Test",
                        "tagline": "Tagline Text",
                        "bio": "Bio Text",
                        "avatar_url": "https://example.com/test.jpg"
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

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                # Used to send messages to this User
                'target_hid': upstream['target_user'].hid,
                'birthdate': upstream['target_user'].dob,
                'min_bid': upstream['target_user'].inbox_settings.get().min_bid,
                'gid_is': upstream['target_user'].gid_is,
                'age': upstream['target_user'].age,
                'first_name': upstream['target_user'].first_name,
                'tagline': upstream['target_user'].tagline,
                'bio': upstream['target_user'].bio,

                'avatar_url': upstream['target_user'].get_avatar_url(

                    req_x=512,
                    req_y=512
                )
            }
        )
