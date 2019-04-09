# -*- coding: utf-8 -*-

import sys

from . import platform
from . import user


def migrate():
    sys.stdout.write('\n\nPATCH 2018-02-10.01')
    sys.stdout.write('\n===================================================================')
    sys.stdout.flush()

    platform.migrate()
    # user.migrate()
