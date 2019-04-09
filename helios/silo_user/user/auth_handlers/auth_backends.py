#  -*- coding: UTF8 -*-

from django.contrib.auth.backends import ModelBackend
from silo_user.user.db import User


class AuthenticationBackend(ModelBackend):
    """
        This custom authentication backend replaces the standard Django auth backend, letting us
        authenticate users using passwords *and* other authentication methods
    """

    def authenticate(self, **credentials):

        # Support for django admin auth
        username = credentials.get('username')
        if username:
            user = User.objects.filter(email=username).first()
            if user and user.check_password(credentials["password"]) and user.is_superuser:
                return user

        email = credentials.get('email')

        if email:

            # All emails are stored as lower-case
            email = email.lower()

            user = User.objects.filter(email=email).first()

            if user and user.check_password(credentials["password"]):
                return user

        return None
