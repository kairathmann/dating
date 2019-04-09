# -*- coding: utf-8 -*-

import sys, timeit

from django.db import connection


def update_tables():
    sys.stdout.write('\nUser modify tables...')
    sys.stdout.flush()

    start = timeit.default_timer()

    cursor = connection.cursor()

    # language=SQL --INTELLIJ
    cursor.execute(
        """
            --- Arrays

            DROP INDEX silo_user_user_4295e806;
            CREATE INDEX silo_user_user_4295e806 ON silo_user_user USING GIN(roles gin__int_ops);

            --- Combined index

            DROP INDEX silo_user_user_dfc95e71;
            CREATE INDEX silo_user_user_dfc95e71 ON silo_user_user USING GIN(text_tsv);

            DROP TRIGGER IF EXISTS silo_user_user_tsvectorupdate ON silo_user_user;

            CREATE TRIGGER silo_user_user_tsvectorupdate BEFORE INSERT OR UPDATE
            OF tagline, bio, first_name ON silo_user_user FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger("text_tsv", 'pg_catalog.english', tagline, bio, first_name);

            --- Email

            DROP INDEX silo_user_user_1fa0eb1e;
            CREATE INDEX silo_user_user_1fa0eb1e ON silo_user_user USING GIN(email_tsv);

            DROP TRIGGER IF EXISTS silo_user_user_email_tsvectorupdate ON silo_user_user;

            CREATE TRIGGER silo_user_user_email_tsvectorupdate BEFORE INSERT OR UPDATE
            OF email ON silo_user_user FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger("email_tsv", 'pg_catalog.english', email);

            --- Name

            DROP INDEX silo_user_user_5b94aaa2;
            CREATE INDEX silo_user_user_5b94aaa2 ON silo_user_user USING GIN(name_tsv);

            DROP TRIGGER IF EXISTS silo_user_user_name_tsvectorupdate ON silo_user_user;

            CREATE TRIGGER silo_user_user_name_tsvectorupdate BEFORE INSERT OR UPDATE
            OF first_name ON silo_user_user FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger("name_tsv", 'pg_catalog.english', first_name);

            --- Tagline

            DROP INDEX silo_user_user_7bd7ac9f;
            CREATE INDEX silo_user_user_7bd7ac9f ON silo_user_user USING GIN(tagline_tsv);

            DROP TRIGGER IF EXISTS silo_user_user_tagline_tsvectorupdate ON silo_user_user;

            CREATE TRIGGER silo_user_user_tagline_tsvectorupdate BEFORE INSERT OR UPDATE
            OF tagline ON silo_user_user FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger("tagline_tsv", 'pg_catalog.english', tagline);

            --- Bio

            DROP INDEX silo_user_user_a3a351d6;
            CREATE INDEX silo_user_user_a3a351d6 ON silo_user_user USING GIN(bio_tsv);

            DROP TRIGGER IF EXISTS silo_user_user_bio_tsvectorupdate ON silo_user_user;

            CREATE TRIGGER silo_user_user_bio_tsvectorupdate BEFORE INSERT OR UPDATE
            OF bio ON silo_user_user FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger("bio_tsv", 'pg_catalog.english', bio);
        """
    )

    stop = timeit.default_timer()
    sys.stdout.write(" | Time: {} seconds".format(stop - start))
    sys.stdout.flush()


def migrate():
    update_tables()
