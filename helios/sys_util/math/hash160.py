#  -*- coding: UTF8 -*-

# Based on https://bitcoin.stackexchange.com/questions/59777/how-to-produce-a-hash160-bitcoin-address/59787
def hash160(string):
    hash160 = string.encode('hex')
    # First byte is version byte. Last 4 bytes are checksum
    return hash160[2:-8]
