# -*- coding: utf-8 -*-

import newrelic.agent

from silo_user.user.api import get_viewer_credentials
from silo_user.user.db import User

from sys_base.endpoint.base import AbstractJSONEndpoint
from sys_base.exceptions import HeliosException


class AbstractHeliosEndpoint(AbstractJSONEndpoint):
    """
        Provides base methods for Helios AJAX endpoints
    """

    TOKENS = []

    KEYS = {}

    def viewer_has_role(self, upstream, caps):
        """
            Evaluates the current request against this endpoint's policy

            :param upstream:
            :param caps:

            :return: True if the current request should be permitted, otherwise False
        """

        if not caps:
            raise HeliosException(desc='Endpoint ALLOW_CAPS array is empty', code='config_error')

        # Viewer owns profile. The 'owns_profile' role check is necessary so that we can create endpoints
        # on a User profile which can only be accessed by viewers with helios_root access
        # ===================================================================================================

        if ('owns_profile' in self.ALLOW_ROLE) and (upstream['viewed_user'].id == upstream['viewer'].id):

            return True

        # Endpoint allows 'helios_root' role and viewer has helios_root set active
        # ===================================================================================================

        elif ('helios_root' in self.ALLOW_ROLE) and upstream['root_active']:

            return True

        else:
            return False

    @newrelic.agent.function_trace()
    def get_upstream_for_user(self, request, target_hid):
        """
            Returns a dict containing the upstream objects for an API call at the User scope

            :param request: the current request
            :param target_hid: HeliosID of target User. If not target_hid is supplied then the logged in user id is used

            :return: dict containing base objects
        """
        if not request.user.is_anonymous:
            target_hid = target_hid or request.user.hid

        viewer, viewer_roles, speaking_as, root_active = get_viewer_credentials(request)

        host_domain = request.get_host()

        if not host_domain:
            raise HeliosException(desc='Cannot determine current domain', code='no_domain')

        # We fetch the entire User record because trying to optimize by only requesting the needed columns in
        # any given situation introduces so much complexity its just not worth it.

        target_user = User.objects.filter(hid=target_hid).first()

        return {

            'request': request,
            'target_user': target_user,
            'viewer': viewer,
            'target_is_viewer': viewer and target_user and (viewer.id == target_user.id),
            'viewer_roles': viewer_roles,
            'speaking_as': speaking_as,
            'root_active': root_active
        }

    @newrelic.agent.function_trace()
    def get_upstream_for_platform(self, request):
        """
            Returns a dict containing the upstream objects for an API call that operates at the Platform scope

            :param request: the current request
            :param kwargs: kwargs

            :return: dict containing base objects
        """

        viewer, viewer_roles, speaking_as, root_active = get_viewer_credentials(request)

        host_domain = request.get_host()

        if not host_domain:
            raise HeliosException(desc='Cannot determine current domain', code='no_domain')

        return {

            'request': request,
            'viewer': viewer,
            'viewer_roles': viewer_roles,
            'speaking_as': speaking_as,
            'root_active': root_active
        }
