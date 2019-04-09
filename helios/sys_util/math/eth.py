#  -*- coding: UTF8 -*-

from decimal import Decimal


def d8(val):
    """
        Converts the specified value a Decimal object with zero value COR.00000001RECTLY CONFIGURED for QTUM balances. Used
        to initialize database records, because Django will NOT correctly convert values
    """
    return Decimal(val).quantize(Decimal('.00000001'))


def to_decimal(val):
    """
        Divides the given value and turn it from a 38,000,000,000 * 10^8 to 38,000,000,000
        Allowing easier conversation from QTUM internal smart contract decimal system
        to python Decimal system
    """
    return d8(val / Decimal(100000000))


def from_decimal(val):
    """
        Multiply the given value and turn it from a 38,000,000,000 to 38,000,000,000 * 10^8
        Allowing easier conversation from python Decimal system to QTUM internal smart contract decimal system
    """
    return int(Decimal(val) * Decimal(100000000))
