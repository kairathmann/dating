#  -*- coding: UTF8 -*-


from api_helios.base import AbstractHeliosEndpoint
from silo_user.user.db import User


class UserRetrieveForSelf(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Retrieves the "self" view for a User profile. The self view is used when a User
            views his profile. It is similar to the single view but also contains the user token balance

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

                        "state": "2",
                        "age": "28",
                        "first_name": "Test",
                        "tagline": "Tagline Text",
                        "bio": "Bio Text",
                        "avatar_url": "https://example.com/test.jpg",
                        "balance": {
                            "confirmed": "13.37153846742200084",
                            "unconfirmed": "0.00000000312480023"
                        }
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

        token_account = upstream['target_user'].token_account

        if not token_account:
            return self.render_error(request, code='nonexistent_target', status=400)

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,

                # Used to send messages to this User
                'target_hid': upstream['target_user'].hid,

                'min_bid': upstream['target_user'].inbox_settings.get().min_bid,

                'state': upstream['target_user'].state,
                'age': upstream['target_user'].age,
                'first_name': upstream['target_user'].first_name,
                'tagline': upstream['target_user'].tagline,
                'bio': upstream['target_user'].bio,
                'gid_is': upstream['target_user'].gid_is,
                'gid_seeking': upstream['target_user'].gid_seeking,
                'seeking_age_from': upstream['target_user'].seeking_age_from,
                'seeking_age_to': upstream['target_user'].seeking_age_to,
                'birthday': upstream['target_user'].dob,
                'avatar_url': upstream['target_user'].get_avatar_url(

                    req_x=512,
                    req_y=512
                ),

                'balance': {
                    'confirmed': str(token_account.confirmed_balance),
                    'unconfirmed': str(token_account.unconfirmed_balance)
                }
            }
        )
