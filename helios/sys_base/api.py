#  -*- coding: UTF8 -*-

import unicodedata

from sys_base.exceptions import HeliosException


def get_client_ip(request):
    """
        Tries to determine the user's IP address. Relatively easy for evil users to spoof, but as we handle nothing
        of value, there's currently zero incentive for people to try and trick the site. There are a variety of
        ways to deter IP spoofing, but they'd add a great deal of complexity to the platform.

        :param request: The current request.
        :return: IP address
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:

        ip = x_forwarded_for.split(',')[0]

    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def remap_utf8_to_ascii(input_string):
    """
        Makes a best-effort attempt to translate a UTF-8 bytecode string (16K possible characters) to an ASCII
        string (128 possible characters). This is an unsolved problem in web design. See the function body
        for details.

        http://en.wikipedia.org/wiki/Internationalized_resource_identifier
        http://en.wikipedia.org/wiki/IDN_homograph_attack

        :param input_string: Input string in UTF-8 format.
        :return: Best possible equivalent of input string in ASCII.
    """

    return unicodedata.normalize('NFKD', input_string).encode('ascii', 'ignore')


def strip_punctuation(input_string):
    """
        Strips all punctuation from a string. ASCII strings are automatically converted to UTF8.

        :param input_string:  String to process.
        :return: Processed string.
    """

    # Automatically convert the inbound string to UTF-8, if necessary, to avoid common errors
    if isinstance(input_string, str):
        input_string = unicode(input_string, "utf-8")

    # This removes punctuation characters.
    return ''.join(x for x in input_string if unicodedata.category(x) != 'Po')


def parse_search_string(search_str):
    """
        Converts wildly varying strings into unicode, strips out punctuation, and then splits the string
        into tokens using whitespace characters as the delimeter

        :param search_str: (almost) any possible string
        :return: list of UTF-8 unicode tokens
    """

    try:

        # Automatically convert the inbound string to UTF-8, if necessary, to avoid common errors
        if isinstance(search_str, str):
            search_str = unicode(search_str, "utf-8")

        # This removes punctuation characters.
        punctuation_removed = ''.join(x for x in search_str if unicodedata.category(x) != 'Po')

        # Python split() without an argument splits on whitespace. There are some reasonable compromises made
        # with this, because with 64K characters in UTF-8, there are some disputes over precisely WHAT constitutes
        # whitespace. See: http://stackoverflow.com/questions/8928557/python-splitting-string-by-all-space-characters

        return punctuation_removed.split()

    except:
        raise HeliosException(desc='Malformed search_str string', code='malformed_search_str')


def honeybadger_replace(template, tokens):
    """
        Replaces all instances in 'template' with the marker:value pairs in 'tokens'. This method
        is absolutely bullet-proof compared to alternatives like python templates, named parameters, etc.

        :param template: A string, typically HTML, containing markers to replace
        :param tokens: A dict of the form {'marker':'value'}
        :return: A string with the markers replaced, if they exist in the string.
    """

    return reduce(lambda a, kv: a.replace(*kv), tokens.iteritems(), template)
