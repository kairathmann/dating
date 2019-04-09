#  -*- coding: UTF8 -*-

import random, string

from datetime import datetime

from django.db import models


class EmailAddress(models.Model):
    """
        Stores email addresses associated with a User. We need to be able to handle multiple email addresses
        per User because people sometimes use different email addresses for each of their social website
        accounts. Multiple email addresses are also necessary for people to be able to change their primary
        email account
    """

    # User instance that owns this email address
    user = models.ForeignKey('silo_user.User', related_name='email_addresses')

    # Email address for this record. Its EXTREMELY IMPORTANT that this column has a unique flag.
    email = models.EmailField(unique=True)

    # True if primary email address. False if not. A user can only have ONE primary email address.
    primary = models.BooleanField(default=False)

    # True if verified. False if not. (Needs to be here until importer is run)
    verified = models.BooleanField(default=False, db_index=True)

    # When this email address was verified
    verified_timestamp = models.DateTimeField(null=True, db_index=True)

    # Whether or not this email address can be sent to. If an email address is reported as invalid by
    # SendGrid, or has multiple failures, it will be disabled

    disabled = models.BooleanField(default=False, db_index=True)


class EmailConfirmation(models.Model):
    """
        Stores active email address confirmations to prevent hackers using our site as a DoS tool by
        rapidly requesting millions of confirmations for the same email address. This data structure
        also lets us send "reasonable" length confirmation links, because we don't have to encrypt a
        bunch of data and encode it in the confirmation link.
    """

    # If the user has sent THROTTLE_LIMIT emails in the last THROTTLE_WINDOW minutes, block
    # them from sending any further confirmation emails until they fall back below the limit
    # ==================================================================================================

    THROTTLE_WINDOW = 1
    THROTTLE_LIMIT = 3

    # User instance that owns this confirmation
    user = models.ForeignKey('silo_user.User', related_name='email_confirmations')

    # Email address confirmation request was sent to. We keep this record even if they delete the email address
    # record so we can throttle confirmation requests

    email = models.ForeignKey('silo_user.EmailAddress', related_name='email_confirmations', null=True,
                              on_delete=models.SET_NULL)

    # When the request was created
    created = models.DateTimeField(default=datetime.now)

    # Randomly generated key. This field MUST be a charfield so that searches are case sensitive.
    key = models.CharField(max_length=32, unique=True)

    # Status
    # ======================================================================================================

    STATUS_READY = 1  # This confirmation has not been used
    STATUS_USED = 2  # This confirmation has been used
    STATUS_VOID = 3  # This confirmation has been voided because the user cancelled the confirmation
    # request, or confirmed the email address using a different confirmation key

    VALID_STATUSES = (

        (STATUS_READY, "STATUS_READY"),
        (STATUS_USED, "STATUS_USED"),
        (STATUS_VOID, "STATUS_VOID")
    )

    status = models.SmallIntegerField(db_index=True, choices=VALID_STATUSES, default=STATUS_READY)

    @classmethod
    def generate_key(cls):
        """
            Generates random alphanumeric stash GUID's. We use 32 characters to make it look 'secure'
            to the user, even though its massive overkill.

            :return: 32-character string containing GUID
        """

        # 62^32 = 47672401706823533450263330816 * 47672401706823533450263330816 possibilities. Collision
        # checking is pointless.

        return ''.join([random.choice(string.ascii_letters + string.digits) for x in range(32)])
