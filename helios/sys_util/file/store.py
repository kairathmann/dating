#  -*- coding: UTF8 -*-

from __future__ import division

import shutil

from django.conf import settings
from sys_base.exceptions import HeliosException


def store_fileobject_to_stash(handle, prefix, accepted_types=None):
    """
        Stores a fileobject to the stash, then closes its handle. If the fileobject was a temporary file
        created by Django, this will cause the fileobject to be deleted.

        :param handle: The fileobject to store.
        :param prefix: String to prepend to file. Path and extension are automatically set.
        :param accepted_types: List of accepted file extensions. Example: ['doc', 'pdf']

        :return: Filename, with path.
    """

    if not handle:
        raise HeliosException(desc='Invalid file handle', code='invalid_file_handle')

    extension = handle.name[handle.name.rfind(".") + 1:].upper()

    if not extension:
        handle.close()
        raise HeliosException(desc='could not determine file extension', code='bad_file_extension')

    if accepted_types and (extension not in accepted_types):
        handle.close()
        raise HeliosException(desc='unsupported file extension', code='unsupported_file_extension')

    filename = settings.H1_STASH_ROOT + prefix + '.' + extension.lower()

    try:
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(handle, out_file)

    except:
        raise HeliosException(desc='Error saving file to disk', code='error_saving_file')

    finally:
        handle.close()

    return filename, extension
