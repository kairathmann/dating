#  -*- coding: UTF8 -*-

import sys

from api_helios.base import AbstractHeliosEndpoint


class SetAsRoot(AbstractHeliosEndpoint):

    def post(self, request, **kwargs):
        """
            Sets the Viewer's context to be helios_root

            :param request: The current request
            :return:  JSON empty object on success
        """

        target_hid = request.POST.get('target_hid')

        # Enforce policy
        # =========================================================================

        try:
            upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        except Exception as e:

            exc_info = sys.exc_info()
            raise exc_info[0], exc_info[1], exc_info[2]

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        if not request.user.is_staff:
            return self.render_error(request, code='no_access', status=403)

        # Update session
        # =========================================================================

        # Clear 'speaking_as' if Viewer currently has it set

        if 'speaking_as' in request.session:
            del request.session['speaking_as']

        request.session['root_active'] = True
        request.session.modified = True

        return self.render_response(

            request=request,

            data={

                'viewer_hid': upstream['viewer'].hid
            }
        )
