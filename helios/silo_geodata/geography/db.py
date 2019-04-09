#  -*- coding: UTF8 -*-

from django.contrib.gis.db import models

from sys_base.fields.field_fulltext import VectorField


class Country(models.Model):
    """
        Stores Country objects. We store these in a separate table to speed up searches, because in many cases
        we're just searching for the name of a country. This table contains many columns we're unlikely to use
        in the near future. They exist to make it easier to import new data into our system.

        Example: "United States of America"
    """

    # Geonames id of this object
    id = models.PositiveIntegerField(primary_key=True)

    # ISO numeric country code
    iso = models.PositiveSmallIntegerField(db_index=True)

    # ISO 2-letter country code. Example: "US"
    alpha2 = models.CharField(max_length=2, db_index=True)

    # ISO 3-letter country code. Example: "USA"
    alpha3 = models.CharField(max_length=3, db_index=True)

    # FIPS code for country, if exists
    fips = models.CharField(max_length=2, null=True, db_index=True)

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # Name of the country (ascii)
    name = models.TextField(max_length=200, db_index=True)

    # The vector outline of the place. We use MultiPolygonField because there are plenty of places that
    # consist of multiple chunks of land. Example: https://en.wikipedia.org/wiki/Hawaii. Note that we
    # do not have polygon outlines for every place on earth.

    shape = models.MultiPolygonField(null=True)

    # Area of country in km^2
    area = models.BigIntegerField(db_index=True)

    # Population of country
    population = models.BigIntegerField(db_index=True)

    # Regex for validating a postal code within the country
    postal_regex = models.CharField(max_length=200, null=True)

    # Postgres GIN fulltext search field
    fulltext = VectorField(null=True)


class TimeZone(models.Model):
    """
        Stores global time zones
    """

    # Timezone id
    id = models.AutoField(primary_key=True)

    # Country that owns this Admin1 area
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Name of time zone
    name = models.TextField(max_length=40, db_index=True)

    # GMT offset on 1st of January
    gmt_offset = models.DecimalField(max_digits=3, decimal_places=1)

    # DST offset to gmt on 1st of July (of the current year)
    dst_offset = models.DecimalField(max_digits=3, decimal_places=1)

    # Raw offset, without DST
    raw_offset = models.DecimalField(max_digits=3, decimal_places=1)


class Admin1(models.Model):
    """
        Stores Admin Level 1 (state/province/territory) objects. We store these in a separate table to speed
        up searches, because in many cases we're just searching for the name of a state. See: http://www.gadm.org/maps

        Example: "The State of California" (in "United States of America")
    """

    # Geonames id of this object
    id = models.PositiveIntegerField(primary_key=True)

    # Name of the Admin 1 division (utf8). Example: "State of California"
    name = models.TextField(max_length=200, db_index=True)

    # Name of the Admin 1 division in plain ascii characters. Example: "State of California"
    asciiname = models.TextField(max_length=200, db_index=True)

    # ISO 2-letter country code. Example: "US"
    alpha2 = models.CharField(max_length=2, db_index=True)

    # Either FIPS code or ISO code depending on Country. Example: "CA" for "State of California"
    code = models.CharField(max_length=20, db_index=True)

    # Country that owns this Admin1 area
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # The vector outline of the place. We use MultiPolygonField because there are plenty of places that
    # consist of multiple chunks of land. Example: https://en.wikipedia.org/wiki/Hawaii. Note that we
    # do not have polygon outlines for every place on earth.

    shape = models.MultiPolygonField(null=True)

    # Population of admin area
    population = models.BigIntegerField(db_index=True)

    # Elevation, in meters. Can have negative values because some places are below sea level
    elevation = models.IntegerField(db_index=True)

    # Time zone of this admin area
    timezone = models.ForeignKey('silo_geodata.TimeZone', db_index=True)

    # When the record was last updated
    updated = models.DateField(db_index=True)

    # Postgres GIN fulltext search field
    fulltext = VectorField(null=True)

    objects = models.GeoManager()


class Admin2(models.Model):
    """
        Stores Admin Level 2 (county/division/parish) objects. We store these in a separate table to speed up searches,
        because in many cases we're just searching for data at this level. See: http://www.gadm.org/maps

        Example: "Fresno County", (in "The State of California", in "United States of America")
    """

    # Geonames id of this object
    id = models.PositiveIntegerField(primary_key=True)

    # Name of geographical point (utf8)
    name = models.TextField(max_length=200, db_index=True)

    # Name of geographical point in plain ascii characters
    asciiname = models.TextField(max_length=200, db_index=True)

    # ISO 2-letter country code. Example: "US"
    alpha2 = models.CharField(max_length=2, db_index=True)

    # ISO code for this Admin2 area
    code = models.CharField(max_length=200, db_index=True)

    # Country that owns this Admin2 area
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Admin1 area that owns this Admin2 area, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True)

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # The vector outline of the place. We use MultiPolygonField because there are plenty of places that
    # consist of multiple chunks of land.

    shape = models.MultiPolygonField(null=True)

    # Population of admin area
    population = models.BigIntegerField(db_index=True)

    # Elevation, in meters. Can have negative values because some places are below sea level
    elevation = models.IntegerField(db_index=True)

    # Time zone of this admin area
    timezone = models.ForeignKey('silo_geodata.TimeZone', db_index=True)

    # When the record was last updated
    updated = models.DateField(db_index=True)

    # Postgres GIN fulltext search field
    fulltext = VectorField(null=True)

    objects = models.GeoManager()


class Admin3(models.Model):
    """
        Stores Admin Level 3 objects. We store these in a separate table to speed up searches, because in
        many cases we're just searching for data at this level. See: http://www.gadm.org/maps

        Example:

    """

    # Geonames id of this object
    id = models.PositiveIntegerField(primary_key=True)

    # Name of geographical point (utf8)
    name = models.TextField(max_length=200, db_index=True)

    # Name of geographical point in plain ascii characters
    asciiname = models.TextField(max_length=200, db_index=True)

    # ISO 2-letter country code. Example: "US"
    alpha2 = models.CharField(max_length=2, db_index=True)

    # ISO code for this Admin3 area
    code = models.CharField(max_length=20, db_index=True)

    # Country that owns this Admin2 area
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Admin1 area that owns this Admin3 area, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True)

    # Admin2 area that owns this Admin3 area, if relationship exists
    admin2 = models.ForeignKey('silo_geodata.Admin2', null=True, db_index=True)

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # The vector outline of the place. We use MultiPolygonField because there are plenty of places that
    # consist of multiple chunks of land.

    shape = models.MultiPolygonField(null=True)

    # Population of admin area
    population = models.BigIntegerField(db_index=True)

    # Elevation, in meters. Can have negative values because some places are below sea level
    elevation = models.IntegerField(db_index=True)

    # Time zone of this admin area
    timezone = models.ForeignKey('silo_geodata.TimeZone', db_index=True)

    # When the record was last updated
    updated = models.DateField(db_index=True)

    # Postgres GIN fulltext search field
    fulltext = VectorField(null=True)

    objects = models.GeoManager()


class Admin4(models.Model):
    """
        Stores Admin Level 4 objects. We store these in a separate table to speed up searches, because in
        many cases we're just searching for data at this level. See: http://www.gadm.org/maps

        Example:
    """

    # Geonames id of this object
    id = models.PositiveIntegerField(primary_key=True)

    # Name of geographical point (utf8)
    name = models.TextField(max_length=200, db_index=True)

    # Name of geographical point in plain ascii characters
    asciiname = models.TextField(max_length=200, db_index=True)

    # ISO 2-letter country code. Example: "US"
    alpha2 = models.CharField(max_length=2, db_index=True)

    # ISO code for this Admin3 area
    code = models.CharField(max_length=20, db_index=True)

    # Country that owns this Admin2 area
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Admin1 area that owns this Admin3 area, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True)

    # Admin2 area that owns this Admin3 area, if relationship exists
    admin2 = models.ForeignKey('silo_geodata.Admin2', null=True, db_index=True)

    # Admin3 area that owns this Admin4 area, if relationship exists
    admin3 = models.ForeignKey('silo_geodata.Admin3', null=True, db_index=True)

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # The vector outline of the place. We use MultiPolygonField because there are plenty of places that
    # consist of multiple chunks of land.

    shape = models.MultiPolygonField(null=True)

    # Population of admin area
    population = models.BigIntegerField(db_index=True)

    # Elevation, in meters. Can have negative values because some places are below sea level
    elevation = models.IntegerField(db_index=True)

    # Time zone of this admin area
    timezone = models.ForeignKey('silo_geodata.TimeZone', db_index=True)

    # When the record was last updated
    updated = models.DateField(db_index=True)

    # Postgres GIN fulltext search field
    fulltext = VectorField(null=True)

    objects = models.GeoManager()


class Place(models.Model):
    """
        A populated place. Typically a city or town.

        Example: "Manhattan", (in "New York County" in "The State of New York", in "United States of America") - note
        that each borough in New York City is it's own state county.
    """

    # Geonames id of this object
    id = models.PositiveIntegerField(primary_key=True)

    # Name of geographical point (utf8)
    name = models.TextField(max_length=200, db_index=True)

    # Name of geographical point in plain ascii characters
    asciiname = models.TextField(max_length=200, db_index=True)

    # ISO 2-letter country code. Example: "US"
    alpha2 = models.CharField(max_length=2, db_index=True)

    # ISO code for this Admin3 area
    code = models.CharField(max_length=20, db_index=True)

    # Country that owns this Admin1 area
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Admin1 area that owns this Admin2 area, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True)

    # Admin2 area that owns this Admin3 area, if relationship exists
    admin2 = models.ForeignKey('silo_geodata.Admin2', null=True, db_index=True)

    # Admin3 area that owns this Admin4 area, if relationship exists
    admin3 = models.ForeignKey('silo_geodata.Admin3', null=True, db_index=True)

    # Admin4 area that owns this place, if relationship exists
    admin4 = models.ForeignKey('silo_geodata.Admin4', null=True, db_index=True)

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # The vector outline of the place. We use MultiPolygonField because there are plenty of places that
    # consist of multiple chunks of land.

    shape = models.MultiPolygonField(null=True)

    # Population of admin area
    population = models.BigIntegerField(db_index=True)

    # Elevation, in meters. Can have negative values because some places are below sea level
    elevation = models.IntegerField(db_index=True)

    # Time zone of this admin area
    timezone = models.ForeignKey('silo_geodata.TimeZone', db_index=True)

    # When the record was last updated
    updated = models.DateField(db_index=True)

    # Postgres GIN fulltext search field for JUST the name of this place
    fulltext = VectorField(null=True)

    # Postgres GIN fulltext search field for the entire NAME CHAIN up to the country
    fulltext_chain = VectorField(null=True)

    objects = models.GeoManager()


class AltName(models.Model):
    """
        Alternate names for places, typically in a different language. For example, Americans call it "Beijing", but
        the people that live there call it "北京", or "京" for short, or "北平" in other dialects. Etc. We use this
        table to find places when a user enters one of the alternate names.
    """

    # Geonames alternatename id of this object
    id = models.PositiveIntegerField(primary_key=True)

    # Country that owns this altname
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # Admin1 area that owns this altname, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True)

    # City object this alternate name references
    place = models.ForeignKey('silo_geodata.Place', db_index=True)

    # ISO-639 language code 2- or 3-characters; 4-characters 'post' for postal codes
    # and 'iata','icao' and faac for airport codes, fr_1793 for French Revolution names,  abbr for abbreviation, link for a website, varchar(7)
    iso_language = models.TextField(max_length=200, null=True, db_index=True)

    # Alternate name or name variant
    name = models.TextField(max_length=200, db_index=True)

    # '1', if this alternate name is an official/preferred name
    is_preferred = models.NullBooleanField(null=True, db_index=True)

    # '1', if this is a short name like 'California' for 'State of California'
    is_short = models.NullBooleanField(null=True, db_index=True)

    # '1', if this alternate name is a colloquial or slang term
    is_colloquial = models.NullBooleanField(null=True, db_index=True)

    # '1', if this alternate name is historic and was used in the past
    is_historic = models.NullBooleanField(null=True, db_index=True)

    # Postgres GIN fulltext search field
    fulltext = VectorField(null=True)


class PostalCode(models.Model):
    """
        A postal code representing an area within a populated place
    """

    # Unique object id
    id = models.AutoField(primary_key=True)

    # Country that owns this postal code area
    country = models.ForeignKey('silo_geodata.Country', db_index=True)

    # ISO 2-letter country code. Example: "US"
    alpha2 = models.CharField(max_length=2, db_index=True)

    # Postal code string
    postalcode = models.TextField(max_length=20, db_index=True)

    # UTF8 name of the postal area
    placename = models.TextField(max_length=180, db_index=True)

    # Admin1 area that owns this Admin3 area, if relationship exists
    admin1 = models.ForeignKey('silo_geodata.Admin1', null=True, db_index=True)

    # Admin2 area that owns this Admin3 area, if relationship exists
    admin2 = models.ForeignKey('silo_geodata.Admin2', null=True, db_index=True)

    # Admin3 area that owns this Admin4 area, if relationship exists
    admin3 = models.ForeignKey('silo_geodata.Admin3', null=True, db_index=True)

    # Latitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    latitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # Longitude in decimal degrees (wgs84). 5 digits after decimal = 1.1 meter resolution
    longitude = models.DecimalField(max_digits=8, decimal_places=5, db_index=True)

    # PostGIS data point corresponding to the lat/lon coordinates
    point = models.PointField(geography=False, spatial_index=True)

    # The vector outline of the place. We use MultiPolygonField because there are plenty of places that
    # consist of multiple chunks of land.

    shape = models.MultiPolygonField(null=True)

    # Accuracy 0 to 6 where 0 is nonexistent and 6 is a centroid (source data's explanation is unclear)
    accuracy = models.PositiveSmallIntegerField(db_index=True)

    # Postgres GIN fulltext search field
    fulltext = VectorField(null=True)

    objects = models.GeoManager()
