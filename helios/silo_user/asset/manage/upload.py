#  -*- coding: UTF8 -*-

import boto3

from django.db import transaction

from silo_user.user.db import User
import settings


def upload_user_avatar(filehandle, target_user_hid):
    """
        Upload an image for use on a User profile.

        :param user: a User object
        :param filehandle: A file handle to the uploaded image

        :return: dict

        .. code-block:: python
            {
                'guid': 'MDzd6Yyow5HVqUyv',              # 16-character alphanumeric GUID for stashed image
                'file': 'MDzd6Yyow5HVqUyv_BROWSER.jpg',  # Image filename

                # Full URL to file
                'file': 'https://...'
            }
    """

    s3 = boto3.client('s3')
    s3.upload_fileobj(filehandle, settings.BUCKET_NAME, 'avatar/%s.jpg'%target_user_hid)

    with transaction.atomic():
        User.objects.filter(hid=target_user_hid).update(avatar_set = True)

