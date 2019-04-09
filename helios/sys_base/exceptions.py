#  -*- coding: UTF8 -*-


class AuthException(Exception):
    """
        An exception that was raised at any scope which requires an auth redirect sequence
    """

    def __init__(self, auth_url, target_url, desc, code):
        self.auth_url = auth_url
        self.target_url = target_url
        self.desc = desc
        self.code = code

    def __str__(self):
        return repr(self.desc)


class HeliosException(Exception):
    """
        An exception that was raised at the Helios scope
    """

    def __init__(self, desc, code):
        self.desc = desc
        self.code = code

    def __str__(self):
        return repr(self.desc)


class JSONRequestException(Exception):

    def __init__(self, desc, code):
        self.desc = desc
        self.code = code

    def __str__(self):
        return repr(self.desc)


class POSTRequestException(Exception):

    def __init__(self, desc, code):
        self.desc = desc
        self.code = code

    def __str__(self):
        return repr(self.desc)


class GETRequestException(Exception):

    def __init__(self, desc, code):
        self.desc = desc
        self.code = code

    def __str__(self):
        return repr(self.desc)
