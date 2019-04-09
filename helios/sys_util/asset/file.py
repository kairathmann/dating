# -*- coding: utf-8 -*-

import settings

from django.template.library import Library

from sys_base.exceptions import HeliosException

register = Library()


@register.filter(is_safe=True)
def asset_img(path):
    """
        Returns the URL to a given image
    """

    offset = path.find('/')

    root = path[0:offset]
    asset = path[offset + 1:]

    if root == 'lib':
        return settings.H1_IMG_LIB_URL + asset

    elif root == 'src':
        return settings.H1_IMG_SRC_URL + asset

    else:
        raise HeliosException(desc='Invalid img asset root', code='invalid_asset_root')
