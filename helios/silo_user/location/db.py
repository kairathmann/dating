#  -*- coding: UTF8 -*-

from django.contrib.gis.db import models


class Location(models.Model):
    """
        A location marker that represents a place the User is associated with
    """

    # Location context
    # ======================================================================================

    CONTEXT_NORMAL = 1
    CONTEXT_GEOLOCATED = 2
    CONTEXT_RANDOM = 3  # Randomly assigned by P2->P3 importer

    VALID_CONTEXTS = (

        (CONTEXT_NORMAL, "CONTEXT_NORMAL"),
        (CONTEXT_GEOLOCATED, "CONTEXT_GEOLOCATED"),
        (CONTEXT_RANDOM, "CONTEXT_RANDOM")
    )

    context = models.SmallIntegerField(choices=VALID_CONTEXTS, db_index=True)

    # Country this Location marker is part of
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Admin1 area this Location marker is part of, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True)

    # Admin2 area this Location marker is part of, if relationship exists
    admin2 = models.ForeignKey('silo_geodata.Admin2', null=True, db_index=True)

    # Admin3 area this Location marker is part of, if relationship exists
    admin3 = models.ForeignKey('silo_geodata.Admin3', null=True, db_index=True)

    # Admin4 area this Location marker is part of, if relationship exists
    admin4 = models.ForeignKey('silo_geodata.Admin4', null=True, db_index=True)

    # Postal Code area this Location marker is part of, if relationship exists
    postalcode = models.ForeignKey('silo_geodata.PostalCode', null=True, db_index=True)

    # Place this Location marker is part of, if relationship exists
    place = models.ForeignKey('silo_geodata.Place', null=True, db_index=True)

    # We store the User's latitude, longitude, and GIS point to make it possible to search for people by
    # geographic location when a user hasn't set their location with PRECISION_POINT precision.

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # When the record was created
    created = models.DateTimeField()

    # When the record was last updated
    updated = models.DateTimeField()

    # Precision
    # ======================================================================================

    PRECISION_POINT = 1
    PRECISION_PLACE = 2
    PRECISION_ADMIN4 = 3
    PRECISION_ADMIN3 = 4
    PRECISION_ADMIN2 = 5
    PRECISION_ADMIN1 = 6
    PRECISION_COUNTRY = 7

    VALID_PRECISIONS = (

        (PRECISION_POINT, "PRECISION_POINT"),
        (PRECISION_PLACE, "PRECISION_PLACE"),
        (PRECISION_ADMIN4, "PRECISION_ADMIN4"),
        (PRECISION_ADMIN3, "PRECISION_ADMIN3"),
        (PRECISION_ADMIN2, "PRECISION_ADMIN2"),
        (PRECISION_ADMIN1, "PRECISION_ADMIN1"),
        (PRECISION_COUNTRY, "PRECISION_COUNTRY")
    )

    precision = models.SmallIntegerField(choices=VALID_PRECISIONS, db_index=True, null=True)

    objects = models.GeoManager()
