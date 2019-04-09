#  -*- coding: UTF8 -*-

import sys, timeit

from django.db import connection, transaction

from silo_user.user.db import User


def reset_sequences():
    start = timeit.default_timer()

    sys.stdout.write('\nUSERS: Reset Postgres ID Sequence')
    sys.stdout.flush()

    cursor = connection.cursor()

    with transaction.atomic():
        latest_record = User.objects.latest('id')
        cursor.execute("ALTER SEQUENCE silo_user_user_id_seq RESTART WITH %s", [latest_record.id + 1])

    stop = timeit.default_timer()

    sys.stdout.write("\nUSERS: Reset Postgres ID Sequence | Time: {} seconds".format(stop - start))
    sys.stdout.flush()


def migrate():
    reset_sequences()
