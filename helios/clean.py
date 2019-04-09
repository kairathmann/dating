#  -*- coding: UTF8 -*-

import os

# Migrations
for d in [d for d in os.listdir('/srv/luna/helios') if os.path.isdir('/srv/luna/helios/' + d)]:

    try:

        folder_path = '/srv/luna/helios/' + d + '/migrations'

        for f in [f for f in os.listdir(folder_path) if os.path.isfile(folder_path + '/' + f)]:

            if (f != '__init__.py') and (f != '__init__.pyc'):
                item_path = '/srv/luna/helios/' + d + '/migrations/' + f

                os.remove(item_path)

    except:
        pass
