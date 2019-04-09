#  -*- coding: UTF8 -*-

from silo_asset.engine.image_crop.stash import ImageCroppable
from silo_user.user.db import User


def stash_user_avatar(user, filehandle, resize_width, resize_height):
    """
        Stashes an image for use on a User profile.

        :param user: a User object
        :param filehandle: A file handle to the uploaded image
        :param resize_width: The x-pixels dimension of the cropping canvas in the user's browser
        :param resize_height: The y-pixels dimension of the cropping canvas in the user's browser

        :return: dict

        .. code-block:: python
            {
                'x': 320,                                # x-value of in-browser cropping image
                'y': 240,                                # y-value of in-browser cropping image
                'guid': 'MDzd6Yyow5HVqUyv',              # 16-character alphanumeric GUID for stashed image
                'file': 'MDzd6Yyow5HVqUyv_BROWSER.jpg',  # Image filename

                # Full path to file
                'file': '/mnt/cdn3/stash/pzaQj1meYI2NKUgi_BROWSER.jpg'
            }
    """

    return ImageCroppable.stash_item(

        guid=ImageCroppable.generate_stash_guid(),
        requester=user,
        filehandle=filehandle,
        formats=ImageCroppable.IMAGE_FORMATS,
        resize_width=resize_width,
        resize_height=resize_height,
        min_x=User.AVATAR_MIN_SIZE['x'],
        min_y=User.AVATAR_MIN_SIZE['y']
    )


def set_user_avatar_from_stash(user, stash_guid, x1, y1, x2, y2):
    """
        Replaces a User profile image with the stash image represented by 'guid', generating all necessary
        child sizes. See plant_media.engines.profile.core.crop_stashed_profile_image() for detailed usage examples.

        :param user: a User object
        :param stash_guid: Stash guid representing an image.
        :param x1: x-value of the upper-left coordinate to crop from
        :param y1: y-value of the upper-left coordinate to crop from
        :param x2: x-value of the lower-right coordinate to crop to
        :param y2: y-value of the lower-right coordinate to crop to

        :return: New maximum image size id.
    """

    return User.set_avatar_from_stash(

        profile_id=user.id,
        guid=stash_guid,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2
    )
