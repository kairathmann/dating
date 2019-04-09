#  -*- coding: UTF8 -*-

from __future__ import division

import requests
import shutil
from django.conf import settings
from requests.exceptions import Timeout
from sys_base.exceptions import HeliosException


def download_file_to_stash(url, prefix, accepted_types=None, max_wait_time=30, max_retries=0):
    """
        Downloads the file at 'url' to the stash

        :param url: URL to download.
        :param prefix: String to prepend to file. Path and extension are automatically set.
        :param accepted_types: List of accepted file extensions. Example: ['doc', 'pdf']
        :param max_wait_time: Max seconds to wait for a response before aborting.
        :param max_retries: Max number of times to retry the download.

        :return: Filename, with path.
    """

    # Try to fetch the file using requests
    # =====================================================================

    total_retries = 0

    while True:

        try:

            response = requests.get(

                url=url,

                # Stream must be True to prevent broken downloads of large files
                stream=True,

                # Requests MUST be time-limited. If the remote server never responds due to packets
                # being dropped, the timeout stops the process from infinitely blocking.

                timeout=min(30, max_wait_time)
            )

            break

        except Timeout:

            if total_retries >= max_retries:
                raise HeliosException(desc='Connection timeout', code='connection_timeout')

            total_retries += 1

        except:
            raise HeliosException(desc='URL was invalid', code='invalid_url')

    if response.status_code != 200:
        raise HeliosException(desc='Remote server rejected request', code='request_rejected')

    # Save the downloaded file to the stash folder
    # ===============================================================================

    if not accepted_types:

        # In "don't care" mode, we set the extension of all downloaded files to '.raw' and the filetype
        # to 'RAW' to indicate the file is a raw bitstream.
        #
        # Never use this mode for downloading files that could span processor types, for example the file could
        # be "an image" OR "a document". If this was the case, we would have to attempt to process the file as
        # an image, then as a document, see which processor (if any) worked and also deal with false positives, for
        # example a corrupt JPG failing the image processor but successfully processing as a TXT file through Box.

        extension = 'RAW'

    else:

        # Input 'fail.linkedin.com/attachments/bc764e0539ca.JPG?version=1.5'
        # Output: 'jpg'

        # Truncate everything past a '?' character if it exists
        params_removed = url if (url.rfind("?") == -1) else url[:url.rfind("?")]

        extension = params_removed[params_removed.rfind(".") + 1:].upper()

        if not extension:
            raise HeliosException(desc='could not determine file extension', code='bad_file_extension')

        if extension not in accepted_types:
            raise HeliosException(desc='unsupported file extension', code='unsupported_file_extension')

    filename = settings.H1_STASH_ROOT + prefix + '.' + extension.lower()

    try:

        with open(filename, 'wb') as out_file:

            # This handles that *one* time someone randomly decides to enable gzip compression on images
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)

    except:
        raise HeliosException(desc='Error saving file to disk', code='error_saving_file')

    return filename, extension
