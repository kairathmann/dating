#  -*- coding: UTF8 -*-

from django.contrib.gis.db import models

from django.contrib.postgres.fields import JSONField


class IpCache(models.Model):
    """
        Caches geolocation info for a given IP address so we don't have to repeatedly query it from MaxMind
    """

    TYPE_BUSINESS = 1
    TYPE_CAFE = 2
    TYPE_CELLULAR = 3
    TYPE_COLLEGE = 4
    TYPE_CDN = 5
    TYPE_DIALUP = 6
    TYPE_GOVERNMENT = 7
    TYPE_HOSTING = 8
    TYPE_LIBRARY = 9
    TYPE_MILITARY = 10
    TYPE_RESIDENTIAL = 11
    TYPE_ROUTER = 12
    TYPE_SCHOOL = 13
    TYPE_SPIDER = 14
    TYPE_TRAVELER = 15

    VALID_TYPES = (

        (TYPE_BUSINESS, "TYPE_BUSINESS"),
        (TYPE_CAFE, "TYPE_CAFE"),
        (TYPE_CELLULAR, "TYPE_CELLULAR"),
        (TYPE_COLLEGE, "TYPE_COLLEGE"),
        (TYPE_CDN, "TYPE_CDN"),
        (TYPE_DIALUP, "TYPE_DIALUP"),
        (TYPE_GOVERNMENT, "TYPE_GOVERNMENT"),
        (TYPE_HOSTING, "TYPE_HOSTING"),
        (TYPE_LIBRARY, "TYPE_LIBRARY"),
        (TYPE_MILITARY, "TYPE_MILITARY"),
        (TYPE_RESIDENTIAL, "TYPE_RESIDENTIAL"),
        (TYPE_ROUTER, "TYPE_ROUTER"),
        (TYPE_SCHOOL, "TYPE_SCHOOL"),
        (TYPE_SPIDER, "TYPE_SPIDER"),
        (TYPE_TRAVELER, "TYPE_TRAVELER")
    )

    # GUID for this row
    id = models.AutoField(primary_key=True)

    # True if MaxMind returned valid data, False if not
    valid = models.BooleanField()

    # IP address
    ip = models.GenericIPAddressField(unique=True, db_index=True)

    # The user type for this IP address
    user_type = models.PositiveSmallIntegerField(null=True, db_index=True, choices=VALID_TYPES)

    # Country this Location marker is part of
    country = models.ForeignKey('silo_geodata.Country', null=True, db_index=True, related_name='country_ips')

    # Admin1 area this Location marker is part of, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True, related_name='admin1_ips')

    # Admin2 area this Location marker is part of, if relationship exists
    admin2 = models.ForeignKey('silo_geodata.Admin2', null=True, db_index=True, related_name='admin2_ips')

    # Admin3 area this Location marker is part of, if relationship exists
    admin3 = models.ForeignKey('silo_geodata.Admin3', null=True, db_index=True, related_name='admin3_ips')

    # Admin4 area this Location marker is part of, if relationship exists
    admin4 = models.ForeignKey('silo_geodata.Admin4', null=True, db_index=True, related_name='admin4_ips')

    # Place this Location marker is part of, if relationship exists
    place = models.ForeignKey('silo_geodata.Place', null=True, db_index=True, related_name='place_ips')

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(null=True, max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(null=True, max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(null=True, geography=False, spatial_index=True)

    # Accuracy radius in km around point
    loc_accuracy = models.PositiveSmallIntegerField(null=True)

    # When the record was created
    created = models.DateTimeField(null=True)

    # Last time this record was accessed
    last_hit = models.DateTimeField(null=True)

    # Number of times this record has been accessed
    hits = models.PositiveIntegerField(null=True)

    # Raw JSON response from API
    raw_result = JSONField(null=True)

    # ISO code for this Admin3 area
    code = models.CharField(max_length=20, null=True, db_index=True)

    objects = models.GeoManager()
