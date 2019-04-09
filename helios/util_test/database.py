import os, shutil, subprocess

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from django.conf import settings
from django.core.management import execute_from_command_line


def flush_database():
    print "\n\nFLUSHING DATABASE\n======================================================"

    # Kill any orphan importer threads
    # subprocess.call(["pkill", "-f", "import.py"])

    # Restart postgres to break any active DB connections that would block modifying the database
    subprocess.call(["service", "postgresql", "restart"])

    con = connect(

        dbname='postgres',
        user=settings.DB_USER,
        host=settings.DB_HOST,
        password=settings.DB_PASS
    )

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    cur.execute("""DROP DATABASE IF EXISTS """ + settings.DB_PROD + """;""")
    cur.execute("""CREATE DATABASE """ + settings.DB_PROD + """ WITH OWNER=""" + settings.DB_USER + """;""")

    cur.close()
    con.close()

    con = connect(

        dbname=settings.DB_PROD,
        user=settings.DB_USER,
        host=settings.DB_HOST,
        password=settings.DB_PASS
    )

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    cur.execute("""CREATE EXTENSION postgis;""")
    cur.execute("""CREATE EXTENSION postgis_topology;""")
    cur.execute("""CREATE EXTENSION fuzzystrmatch;""")
    cur.execute("""CREATE EXTENSION postgis_tiger_geocoder;""")
    cur.execute("""CREATE EXTENSION btree_gin;""")
    cur.execute("""CREATE EXTENSION btree_gist;""")

    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])

    print "\n======================================================\n"
