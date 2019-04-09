#  -*- coding: UTF8 -*-

from __future__ import division

import sys

from django.conf import settings

from api_helios.base import AbstractHeliosEndpoint

from silo_user.user.db import User
from silo_user.asset.manage.stash import stash_user_avatar
from sys_base.exceptions import HeliosException


class UserAvatarStash(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Stashes an image for use on a User profile

            :param request: HTTP request containing

            1)  A key called 'image' in the FILES object, which contains an image file

            2)  .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",

                    // These set the maximum size of the returned image, which is used as a template for
                    // cropping the image in the browser

                    "resize_width": 600,
                    "resize_height": 400
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

        # Enforce policy
        # =========================================================================

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        # Process the request
        # =========================================================================
        # See: https://docs.djangoproject.com/en/1.8/ref/files/uploads/#django.core.files.uploadedfile

        if 'image' not in request.FILES:
            return self.render_error(request, code='image_key_not_in_files', status=400)

        elif not request.FILES['image']:
            return self.render_error(request, code='invalid_file_handle', status=400)

        try:

            crop_params = stash_user_avatar(

                user=upstream['target_user'],

                # See: https://docs.djangoproject.com/en/1.8/ref/files/uploads/#django.core.files.uploadedfile
                filehandle=request.FILES['image'],

                resize_width=request.POST['resize_width'],
                resize_height=request.POST['resize_height']
            )

        except HeliosException as e:

            if e.code in ['resize_width_not_int', 'invalid_resize_width', 'resize_height_not_int',
                          'invalid_resize_height',
                          'invalid_filehandle', 'invalid_file_format', 'below_min_dimensions']:

                return self.render_error(request, code=e.code)

            else:
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]

        # Render
        # =========================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid,
                'x': crop_params['x'],
                'y': crop_params['y'],
                'min_crop_x': (User.AVATAR_MIN_SIZE['x'] / crop_params['original_image_x']) * 1.02,
                'min_crop_y': (User.AVATAR_MIN_SIZE['y'] / crop_params['original_image_y']) * 1.02,
                'guid': crop_params['guid'],
                'image': settings.H1_STASH_URL + crop_params['file']
            }
        )
