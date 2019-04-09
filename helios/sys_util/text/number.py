#  -*- coding: UTF8 -*-

from sys_base.exceptions import HeliosException
from sys_util.math.eth import d8


def hid_is_valid(text):
    """
        Validates a HeliosId

        :param text: raw text string
    """

    if len(text) != 8:
        return False

    # Create a hash table then look-up each char against it. There are faster, more exotic ways
    # to do this, but ~16 character strings this is strategy is probably the most efficient.

    valid_chars = {str(key): None for key in '01234567890abcdef'}

    for char in text:

        if str(char) not in valid_chars:
            return False

    return True


def parse_str_to_eth(text):
    """
        Converts a string to a Decimal object configured for Ethereum's number system. This
        method BLOCKS NEGATIVE VALUES because ethereum wallets can't have negative values.

        :param text: raw text string
    """

    # IMPORTANT: the documentation for the python Decimal module is absolutely HORRIBLE, especially regarding
    # what happens when its fed invalid inputs. For that, the Python docs reference a specification on another
    # website that then references six other specifications, each over 100 pages long. So short of doing a full
    # audit of the module's C source code, we CANNOT feed it random text strings from the internet and expect
    # it to raise exceptions if the string is invalid. As such, we validate the input string using our own code
    # and then pass it to the Decimal module. See: https://docs.python.org/2/library/decimal.html#module-decimal
    #
    # In addition to this, Ethereum has to be treated as a Decimal datatype with precise, specific
    # limitations which must be followed EXACTLY to prevent miscalculations, rounding errors, and error
    # amplification. In the interest of database efficiency, we allow a maximum of 6 leading digits, but
    # Ethereum REQUIRES precisely 18 trailing digits for transactions to be valid.
    # See: http://ethdocs.org/en/latest/ether.html

    # Anly allow valid characters, and also block the negative sign '-'

    valid_chars = {str(key): None for key in '01234567890.'}

    for char in text:

        if str(char) not in valid_chars:
            raise HeliosException(desc='Invalid character in string', code='invalid_char_in_string')

    blocks = text.split('.')

    # Require that the value have ONE and ONLY one decimal point

    if len(blocks) != 2:
        raise HeliosException(desc='Invalid number of decimal points', code='invalid_decimal_point')

    leading = blocks[0]
    trailing = blocks[1]

    # Prevent an overflow attack against our 6-leading-digit database configuration
    if (len(leading) > 6) or (len(leading) < 1):
        raise HeliosException(desc='Invalid number of leading digits', code='invalid_leading_digits')

    # Prevent an overflow attack against ethereum's numeric system
    if (len(trailing) > 18) or (len(trailing) < 1):
        raise HeliosException(desc='Invalid number of trailing digits', code='invalid_trailing_digits')

    clean_str = str(leading) + '.' + str(trailing)

    # Quantize to 18 trailing digits
    return d8(clean_str)
