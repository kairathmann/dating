#  -*- coding: UTF8 -*-

import random
import string

from django.contrib.gis.db import models
from datetime import datetime


class ForgotPassword(models.Model):
    """
        Stores forgot password email requests for User records
    """

    # Email address confirmation request was sent to
    user = models.ForeignKey('silo_user.User', related_name='forgot_password_requests')

    # When the request was created
    created = models.DateTimeField(default=datetime.now)

    # Randomly generated key
    key = models.CharField(max_length=32, unique=True)

    @classmethod
    def generate_key(cls):
        """
            Generates random alphanumeric password reset tokens. We use 32 characters to make it look 'secure' to
            the user, even though its massive overkill, and we use a cryptographic RNG instead of Python's
            Mersenne-Twister PRNG "just to be sure".

            :return: 32-character string containing GUID
        """

        # Create a cryptographically secure rng instance
        # See: http://stackoverflow.com/questions/18047338/creating-a-uncrackable-random-number-with-python

        secure_rng = random.SystemRandom()

        # 62^32 = 47672401706823533450263330816 * 47672401706823533450263330816 possibilities

        return ''.join([secure_rng.choice(string.ascii_letters + string.digits) for x in range(32)])
