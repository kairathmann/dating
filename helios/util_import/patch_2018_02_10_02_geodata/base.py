#  -*- coding: UTF8 -*-

import sys, timeit, datetime

from multiprocessing.pool import Pool

from django.db import connection


def create_fulltext_search(concurrency):
    # INDEX, VACUUM, AND CLUSTER THE BASE TABLES WE'VE BUILT SO FAR
    # ==================================================================================

    start = timeit.default_timer()

    sys.stdout.write('\nGEODATA: Build Vector Indexes')
    sys.stdout.flush()

    # Before we put any data into the fulltext columns, we need to remove the BTREE indexes that
    # Django has automatically created on them. If we fail to do this, and the contents of the fulltext
    # column exceeds ~1024 characters, Postgress will throw an error.

    # TO DISPLAY INDEXES:
    # --------------------------------------------------
    # su postgres
    # psql
    # \connect platform3
    # \d [TABLE NAME]
    # then, \q to get out of the table display

    jobs = [

        """DROP INDEX silo_geodata_admin1_fulltext_ed8f1b62;""",
        """DROP INDEX silo_geodata_admin2_fulltext_4867f8a5;""",
        """DROP INDEX silo_geodata_admin3_fulltext_ddf7d5c4;""",
        """DROP INDEX silo_geodata_admin4_fulltext_c1dfe36b;""",
        """DROP INDEX silo_geodata_place_fulltext_fba6c07a;""",
        """DROP INDEX silo_geodata_place_fulltext_chain_9f6b7a17;""",
        """DROP INDEX silo_geodata_altname_fulltext_3603b373;""",
        """DROP INDEX silo_geodata_postalcode_fulltext_b61c29c1;"""
    ]

    connection.close()

    pool = Pool(concurrency)
    pool.map(query_worker, jobs)
    pool.close()

    jobs = [

        # Add GIN indexes to the vector columns. Its faster to add the index AFTER loading the fulltext column. If
        # the index is added first, Postgres will first index the empty column, then rebuild the index on each update.

        """CREATE INDEX silo_geodata_place_fulltext_fba6c07a ON silo_geodata_place USING GIN(fulltext);""",
        """CREATE INDEX silo_geodata_place_fulltext_chain_9f6b7a17 ON silo_geodata_place USING GIN(fulltext_chain);""",
        """CREATE INDEX silo_geodata_altname_fulltext_3603b373 ON silo_geodata_altname USING GIN(fulltext);""",
        """CREATE INDEX silo_geodata_postalcode_fulltext_b61c29c1 ON silo_geodata_postalcode USING GIN(fulltext);""",
        """CREATE INDEX silo_geodata_admin1_fulltext_ed8f1b62 ON silo_geodata_admin1 USING GIN(fulltext);""",
        """CREATE INDEX silo_geodata_admin2_fulltext_4867f8a5 ON silo_geodata_admin2 USING GIN(fulltext);""",
        """CREATE INDEX silo_geodata_admin3_fulltext_ddf7d5c4 ON silo_geodata_admin3 USING GIN(fulltext);""",
        """CREATE INDEX silo_geodata_admin4_fulltext_c1dfe36b ON silo_geodata_admin4 USING GIN(fulltext);""",

        # As part of the same task group to take advantage of multiple cores, build the clustering indexes.
        # See: https://stackoverflow.com/questions/22658515/multicolumn-index-on-3-fields-with-heterogenous-data-types

        """CREATE INDEX silo_geodata_place_cluster ON silo_geodata_place (country_id, admin1_id) WITH (FILLFACTOR=100);""",
        """CREATE INDEX silo_geodata_altname_cluster ON silo_geodata_altname (country_id, admin1_id) WITH (FILLFACTOR=100);""",
        """CREATE INDEX silo_geodata_postalcode_cluster ON silo_geodata_postalcode (country_id, admin1_id) WITH (FILLFACTOR=100);""",
        """CREATE INDEX silo_geodata_admin1_cluster ON silo_geodata_admin1 (country_id, id) WITH (FILLFACTOR=100);""",
        """CREATE INDEX silo_geodata_admin2_cluster ON silo_geodata_admin2 (country_id, admin1_id) WITH (FILLFACTOR=100);""",
        """CREATE INDEX silo_geodata_admin3_cluster ON silo_geodata_admin3 (country_id, admin1_id) WITH (FILLFACTOR=100);""",
        """CREATE INDEX silo_geodata_admin4_cluster ON silo_geodata_admin4 (country_id, admin1_id) WITH (FILLFACTOR=100);""",
    ]

    connection.close()

    pool = Pool(concurrency)
    pool.map(query_worker, jobs)
    pool.close()

    stop = timeit.default_timer()
    sys.stdout.write("\nGEODATA: Build Vector Indexes | Time: {} seconds".format(stop - start))
    sys.stdout.flush()


def optimize_base_tables():
    start = timeit.default_timer()

    sys.stdout.write('\nGEODATA: Optimize Base Tables')
    sys.stdout.flush()

    # language=SQL --INTELLIJ
    jobs = [

        """VACUUM silo_geodata_place;""",
        """VACUUM silo_geodata_altname;""",
        """VACUUM silo_geodata_postalcode;""",
        """VACUUM silo_geodata_admin1;""",
        """VACUUM silo_geodata_admin2;""",
        """VACUUM silo_geodata_admin3;""",
        """VACUUM silo_geodata_admin4;"""
    ]

    connection.close()

    pool = Pool(8)
    pool.map(query_worker, jobs)
    pool.close()

    # language=SQL --INTELLIJ
    jobs = [

        """CLUSTER silo_geodata_place USING silo_geodata_place_cluster;""",
        """CLUSTER silo_geodata_altname USING silo_geodata_altname_cluster;""",
        """CLUSTER silo_geodata_postalcode USING silo_geodata_postalcode_cluster;""",
        """CLUSTER silo_geodata_admin1 USING silo_geodata_admin1_cluster;""",
        """CLUSTER silo_geodata_admin2 USING silo_geodata_admin2_cluster;""",
        """CLUSTER silo_geodata_admin3 USING silo_geodata_admin3_cluster;""",
        """CLUSTER silo_geodata_admin4 USING silo_geodata_admin4_cluster;""",
    ]

    connection.close()

    pool = Pool(8)
    pool.map(query_worker, jobs)
    pool.close()

    # language=SQL --INTELLIJ
    jobs = [

        """VACUUM ANALYZE silo_geodata_place;""",
        """VACUUM ANALYZE silo_geodata_altname;""",
        """VACUUM ANALYZE silo_geodata_postalcode;""",
        """VACUUM ANALYZE silo_geodata_admin1;""",
        """VACUUM ANALYZE silo_geodata_admin2;""",
        """VACUUM ANALYZE silo_geodata_admin3;""",
        """VACUUM ANALYZE silo_geodata_admin4;""",
        """VACUUM ANALYZE silo_geodata_ipcache;"""
    ]

    connection.close()

    pool = Pool(8)
    pool.map(query_worker, jobs)
    pool.close()

    stop = timeit.default_timer()
    sys.stdout.write("\nGEODATA: Optimize Base Tables | Time: {} seconds".format(stop - start))
    sys.stdout.flush()


def migrate():
    concurrency = 8

    geo_start = datetime.datetime.now()

    create_fulltext_search(concurrency)
    optimize_base_tables()

    geo_end = datetime.datetime.now()

    elapsed_time = geo_end - geo_start

    sys.stdout.write("\nGEODATA: Total Time: {} seconds".format(str(divmod(elapsed_time.total_seconds(), 60))))

    # https://stackoverflow.com/questions/2513501/postgresql-full-text-search-how-to-search-partial-words


def query_worker(job):
    cursor = connection.cursor()
    result = cursor.execute(job)

    return result
