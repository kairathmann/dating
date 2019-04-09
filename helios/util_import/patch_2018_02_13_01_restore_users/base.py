#  -*- coding: UTF8 -*-

import sys, timeit, datetime

from datetime import datetime

from django.db import connection, transaction

from plant_hermes.account.db import TokenAccount
from silo_message.intro_settings import IntroSettings

from silo_user.email.db import EmailAddress
from silo_user.user.db import User


def load_csv():
    DATA_PATH = '/srv/luna'

    start = timeit.default_timer()

    sys.stdout.write('\nUSERS: Load User Profiles')
    sys.stdout.flush()

    cursor = connection.cursor()

    # language=SQL --INTELLIJ
    cursor.execute("""
        COPY silo_user_user (
            id,
            password,
            last_login,
            email,
            created,
            updated,
            hid,
            avatar_prefix,
            avatar_size,
            avatar_set,
            is_staff,
            roles,
            dob,
            gid_is,
            gid_seeking,
            seeking_age_from,
            seeking_age_to,
            first_name,
            last_name,
            tagline,
            bio,
            name_tsv,
            email_tsv,
            tagline_tsv,
            bio_tsv,
            text_tsv,
            hsm_sig,
            token_account
        )
        FROM '{}/people.csv' WITH (FORMAT csv);

        """.format(DATA_PATH))

    stop = timeit.default_timer()

    sys.stdout.write("\nUSERS: Load User Profiles | Time: {} seconds".format(stop - start))
    sys.stdout.flush()


def relink_tables():
    start = timeit.default_timer()

    sys.stdout.write('\nUSERS: Re-link Tables')
    sys.stdout.flush()

    with transaction.atomic():
        for user in User.objects.select_for_update().all():
            now = datetime.now()

            token_account = TokenAccount.objects.create(updated=now)
            token_account.hsm_sig = token_account.calculate_hsm_sig()

            token_account.save()

            user.token_account = token_account
            user.save()

            EmailAddress.objects.create(

                email=user.email,
                verified=False,
                primary=True,
                user=user
            )

            intro_settings = IntroSettings.objects.create(

                user=user
            )

            intro_settings.jitter_next_check()
            intro_settings.save()

    stop = timeit.default_timer()

    sys.stdout.write("\nUSERS: Re-link Tables | Time: {} seconds".format(stop - start))
    sys.stdout.flush()


def migrate():
    # load_csv()
    relink_tables()
