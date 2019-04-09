#  -*- coding: UTF8 -*-

from django.conf import settings

from api_helios.base import AbstractHeliosEndpoint

from silo_user.user.db import User
from silo_user.asset.manage.upload import upload_user_avatar
from silo_user.user.imgix_service import ImgixService
from sys_base.exceptions import HeliosException


class UserAvatarUpload(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Stashes an image for use on a User profile

            :param request: HTTP request containing

            1)  A key called 'image' in the FILES object, which contains an image file

            2)  .. code-block:: javascript
                {
                    "target_hid": "b3665ea5",
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
            upload_user_avatar(request.FILES['image'], upstream['target_user'].hid)

        except HeliosException as e:
            exc_info = sys.exc_info()
            raise exc_info[0], exc_info[1], exc_info[2]

        # Render
        # =========================================================================
        return self.render_response(

            request=request,

            data={
                'viewer_hid': upstream['viewer'].hid,
                'avatar_url': ImgixService().build_avatar_url(upstream['target_user'], 1000, 1000)
            }
        )
