# -*- coding: utf-8 -*-

import sys, timeit

from django.db import connection


def migrate():
    sys.stdout.write('\nConfigure Postgres...')

    start = timeit.default_timer()

    cursor = connection.cursor()

    cursor.execute(
        """
            CREATE AGGREGATE array_agg_mult (anyarray)  (
                SFUNC     = array_cat
               ,STYPE     = anyarray
               ,INITCOND  = '{}'
            );
        """
    )

    cursor.execute("""SET client_encoding = 'UTF8';""")

    cursor.execute("""CREATE EXTENSION IF NOT EXISTS hstore;""")
    cursor.execute("""CREATE EXTENSION IF NOT EXISTS postgis;""")
    cursor.execute("""CREATE EXTENSION IF NOT EXISTS postgis_topology;""")
    cursor.execute("""CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;""")
    cursor.execute("""CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;""")
    cursor.execute("""CREATE EXTENSION IF NOT EXISTS btree_gin;""")
    cursor.execute("""CREATE EXTENSION IF NOT EXISTS btree_gist;""")
    cursor.execute("""CREATE EXTENSION IF NOT EXISTS intarray;""")

    stop = timeit.default_timer()
    sys.stdout.write(" | Time: {} seconds".format(stop - start))
    sys.stdout.flush()
