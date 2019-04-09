# -*- coding: utf-8 -*-


def get_viewer_credentials(request):
    """
        Returns the current viewer's credentials

        WARNING: the 'speaking_as' object represents a cached set of info about an Org that the viewer
        wants to speak as; it does not mean the viewer *can* speak as the Org.

        :param request: The current request
        :return: Tuple (<User>, roles, root_active) on success. Exception on failure.
    """

    # Ensure that 'viewer' and 'root_active' are set in a failsafe way
    # =========================================================================

    viewer = None
    speaking_as = None
    root_active = False

    if request.user.is_authenticated():

        viewer = request.user

        if 'root_active' in request.session:

            if viewer.is_staff and request.session['root_active']:

                root_active = True

            else:

                # Flush incorrectly set 'root_active' keys. These should never be set to an incorrect state in
                # the first place, but ensuring they're clear helps eliminate a lot of WTF's during testing.

                del request.session['root_active']
                request.session.modified = True

        if 'speaking_as' in request.session:

            if isinstance(request.session['speaking_as'], dict):

                speaking_as = request.session['speaking_as']

            else:

                # Flush incorrectly set 'speaking_as' records. These should never be set to an incorrect state in
                # the first place, but ensuring they're clear helps eliminate a lot of WTF's during testing.

                del request.session['speaking_as']
                request.session.modified = True

    roles = [0] + viewer.roles if viewer else [0]

    return viewer, roles, speaking_as, root_active
