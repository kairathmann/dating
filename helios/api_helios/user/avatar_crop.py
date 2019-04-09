#  -*- coding: UTF8 -*-

import sys

from api_helios.base import AbstractHeliosEndpoint
from silo_user.asset.manage.stash import set_user_avatar_from_stash
from sys_base.exceptions import HeliosException


class UserAvatarCrop(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Crops a stashed avatar image and sets it as the User's avatar

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
                    "stash_guid": "c38b59a0",   // GUID of stashed item
                    "x1": 20,                   // (int) Upper-left crop coordinate X (pixels)
                    "y1": 20,                   // (int) Upper-left crop coordinate Y (pixels)
                    "x2": 300,                  // (int) Lower-right crop coordinate X (pixels)
                    "y2": 300                   // (int) Lower-right crop coordinate Y (pixels)
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",
                        "avatar_url": "https://example.com/test.jpg"
                    },
                    "success": true
                }
        """

        target_hid = request.POST.get('target_hid')
        stash_guid = request.POST.get('stash_guid')
        x1 = request.POST.get('x1')
        y1 = request.POST.get('y1')
        x2 = request.POST.get('x2')
        y2 = request.POST.get('y2')

        # Enforce policy
        # =========================================================================

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        try:

            avatar_url = set_user_avatar_from_stash(

                user=upstream['target_user'],
                stash_guid=stash_guid,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2
            )

        except HeliosException as e:

            if e.code in ['invalid_guid', 'guid_not_string', 'crop_coords_not_int', 'invalid_crop_coords',
                          'invalid_aspect_ratio', 'nonexistent_guid', 'below_min_dimensions']:

                return self.render_error(request, code=e.code, status=400)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        # Render
        # =========================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,
                'avatar_url': avatar_url
            }
        )
