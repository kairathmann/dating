#  -*- coding: UTF8 -*-

# These imports make Django think all of our models are in the same file, even though putting
# all of them in one file would be ridiculous
# =============================================================================================

from silo_geodata.cache.db import IpCache
from silo_geodata.geography.db import Country, TimeZone, Admin1, Admin2, Admin3, Admin4, Place, AltName, PostalCode
