#  -*- coding: UTF8 -*-

import bleach
import warnings
from bs4 import BeautifulSoup
from sys_base.exceptions import HeliosException


def sanitize_title(text):
    """
        Strips every possible HTML tag from the input string

        :param text: raw text
        :return: sanitized text
    """

    # First run through BS to fix unbalanced tags and remove entities, because Bleach will
    # pass them through. Then run through bleach to strip low-level tags like <font> because
    # the BS "text" method will pass them through.

    try:

        # BeautifulSoup is written by idiots, and raises all sorts of warnings to give various "tips" to
        # the user. This is a huge misuse of warnings, and it causes NewRelic to re-raise the warnings
        # as exceptions, causing execution to halt. Setting warnings.filterwarnings to 'ignore' disables
        # warnings so BeautifulSoup can run reliably.

        prev_warnings_setting = warnings.filterwarnings
        warnings.filterwarnings('ignore')

        raw = BeautifulSoup(text, 'lxml').get_text()

        # Restore previous system warnings setting
        warnings.filterwarnings = prev_warnings_setting

        result = bleach.clean(raw, tags=[], strip=True)

        # Bleach is also written by idiots. It replaces all instances if '&' with the '&amp;' HTML entity
        # code but lets everything else through (users can paste Ñ, Œ, £ and any other HTML entity and it
        # passes through as unicode). So we have to swap this one code back.
        #
        # See: http://www.ascii.cl/htmlcodes.htm

        result = result.replace('&amp;', '&')

    except:
        raise HeliosException(desc='parse failure', code='parse_failure')

    return result


def sanitize_textfield(text):
    """
        Strips everything except newlines from a block of raw input text

        :param text: raw text
        :return: sanitized text
    """

    # First run through BS to fix unbalanced tags and remove entities, because Bleach will
    # pass them through. Then run through bleach to strip low-level tags like <font> because
    # the BS "text" method will pass them through.

    try:

        # BeautifulSoup is written by idiots, and raises all sorts of warnings to give various "tips" to
        # the user. This is a huge misuse of warnings, and it causes NewRelic to re-raise the warnings
        # as exceptions, causing execution to halt. Setting warnings.filterwarnings to 'ignore' disables
        # warnings so BeautifulSoup can run reliably.

        prev_warnings_setting = warnings.filterwarnings
        warnings.filterwarnings('ignore')

        raw = BeautifulSoup(text, 'lxml').get_text()

        # Restore previous system warnings setting
        warnings.filterwarnings = prev_warnings_setting

        content_rules = {'tags': ['br'], 'attributes': {}, 'styles': [], 'strip': True}
        result = bleach.clean(raw, content_rules, strip=True)

        # Bleach is also written by idiots. It replaces all instances if '&' with the '&amp;' HTML entity
        # code but lets everything else through (users can paste Ñ, Œ, £ and any other HTML entity and it
        # passes through as unicode). So we have to swap this one code back.
        #
        # See: http://www.ascii.cl/htmlcodes.htm

        result = result.replace('&amp;', '&')

    except:
        raise HeliosException(desc='parse failure', code='parse_failure')

    return result


def sanitize_qtum_addr(text):
    """
        A placeholder method until we actually have time to implement this properly

        :param text: raw text string believed to be an ethereum address
    """

    valid_chars = {str(key): None for key in '01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'}

    for char in text:

        if str(char) not in valid_chars:
            raise HeliosException(desc='Wallet address - Invalid character', code='qtum_address_invalid_char')

    if text[0] not in ['Q', 'q']:
        raise HeliosException(desc='Wallet address - Malformed address', code='qtum_address_malformed_address')

    if not len(text) == 34:
        raise HeliosException(desc='Wallet address - Wrong length. Needs to be 34 characters',
                              code='qtum_address_wrong_length')

    return text
