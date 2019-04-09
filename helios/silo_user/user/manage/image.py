# -*- coding: utf-8 -*-

from silo_user.user.db import User
from sys_base.exceptions import HeliosException


def get_user_image_url(user, mode):
    """
        Returns the profile's avatar URL. This API method is *only* intended to be used for fetching an
        image on a User profile's 'manage' page.

        :param user: a User object representing the user to fetch an avatar for
        :param mode: One of ['avatar']

        :return: URL to the User's current avatar image.
    """

    if mode not in ['avatar', ]:
        raise HeliosException(desc='Invalid mode parameter', code='invalid_mode')

    modes = {

        'avatar': lambda: user.get_avatar_url(User.AVATAR_MIN_SIZE['x'], User.AVATAR_MIN_SIZE['y'])
    }

    return modes[mode]()
