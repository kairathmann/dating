#  -*- coding: UTF8 -*-

import random
import string


class AssetEngine(object):
    TYPE_IMAGE_CROP = 'TYPE_IMAGE_CROP'

    STATE_NONE = 'NONE'
    STATE_WAITING = 'WAITING'
    STATE_STARTED = 'STARTED'
    STATE_DONE = 'DONE'
    STATE_FAILED = 'FAILED'

    VALID_STATES = (

        (STATE_NONE, "STATE_NONE"),
        (STATE_WAITING, "STATE_WAITING"),
        (STATE_STARTED, "STATE_STARTED"),
        (STATE_DONE, "STATE_DONE"),
        (STATE_FAILED, "STATE_FAILED")
    )

    @classmethod
    def generate_stash_guid(cls):
        """
            Generates random alphanumeric stash GUID's
            :return: 16-character string containing GUID.
        """

        # 62^16 = 47672401706823533450263330816 possibilities. Collision checking is pointless.
        return ''.join([random.choice(string.ascii_letters + string.digits) for x in range(16)])
