#  -*- coding: UTF8 -*-

from datetime import datetime

from django.contrib.gis.geos import fromstr
from django.db import transaction

from silo_geodata.cache.db import IpCache
from silo_geodata.geography.db import Admin1, Admin2, Admin3, Admin4, Country, Place

from silo_user.location.db import Location
from silo_user.user.db import User

from silo_geodata.api import render_location
from sys_base.exceptions import HeliosException


def get_user_location(user):
    """
        Fetches a User's Location

        :param user: a User object
        :return: Dict containing location data
    """

    prefetch = ['country', 'admin1', 'admin2', 'admin3', 'admin4', 'place']

    location = Location.objects.prefetch_related(*prefetch).filter(owner=user).first()

    if not location:
        # Some users don't have a location set. The right way to fix this is to set a random location
        # for the user during the signup process if they don't set their real location. But as a
        # quick workaround, we'll just return a location in New York City for these users

        location = IpCache.objects.filter(place_id=5128581).prefetch_related(*prefetch).first()

    return render_location(location)


def set_user_location(user, keys, context):
    """
        Sets a User's Location

        :param user: a User object
        :param keys: dict of keys of geodata information
        :param context: one of ['normal', 'geolocated', 'random']

        :return: object Location object
    """

    # Sanitize
    # =========================================================================

    # 'precision'
    # ---------------------------

    precision = str(keys['precision'])

    if precision not in ['point', 'place', 'admin4', 'admin3', 'admin2', 'admin1', 'country']:
        raise HeliosException(desc='invalid precision parameter', code='invalid_precision_type')

    clean_precision = {

        'point': Location.PRECISION_POINT,
        'place': Location.PRECISION_PLACE,
        'admin4': Location.PRECISION_ADMIN4,
        'admin3': Location.PRECISION_ADMIN3,
        'admin2': Location.PRECISION_ADMIN2,
        'admin1': Location.PRECISION_ADMIN1,
        'country': Location.PRECISION_COUNTRY

    }[precision]

    # 'geo_id'
    # ---------------------------

    try:
        geo_id = int(keys['geo_id'])

    except:
        raise HeliosException(desc='geo_id parameter is not an int', code='geo_id_not_int')

    if (geo_id < 1) or (geo_id > 2 ** 32):
        raise HeliosException(desc='geo_id parameter must be between 1 and maxint', code='geo_id_exceeds_bounds')

    # 'context'
    # ---------------------------

    if context not in ['normal', 'geolocated', 'random']:
        raise HeliosException(desc='invalid context parameter', code='invalid_context')

    clean_context = {

        'normal': Location.CONTEXT_NORMAL,
        'geolocated': Location.CONTEXT_GEOLOCATED,
        'random': Location.CONTEXT_RANDOM

    }[context]

    # 'latitude' / 'longitude'
    # ---------------------------

    if precision == 'point':

        if ('latitude' not in keys) or ('longitude' not in keys):
            raise HeliosException(

                desc='latitude and longitude parameters must be set when specifying a point',
                code='missing_lat_lon'
            )

        try:
            latitude = float(keys['latitude'])

        except:
            raise HeliosException(desc='latitude parameter is not a float', code='lat_not_float')

        if (latitude < -90.0) or (latitude > 90.0):
            raise HeliosException(

                desc='latitude parameter must be between -90.0 and +90.0', code='lat_exceeds_bounds'
            )

        try:
            longitude = float(keys['longitude'])

        except:
            raise HeliosException(desc='longitude parameter is not a float', code='lon_not_float')

        if (longitude < -180.0) or (longitude > 180.0):
            raise HeliosException(

                desc='longitude parameter must be between -180.0 and +180.0', code='lon_exceeds_bounds'
            )

    else:

        latitude = None
        longitude = None

    # Process each level of precision
    # =========================================================================

    # IMPORTANT: when a user doesn't specify their location with 'point' precision, we transcribe the weighted
    # centroid lat/long coordinates of the location's place/admin4/admin3/admin2/admin1/country into the user's
    # location record so that user locations can be searched by lat/lon: "Find all the people within a X kilometer
    # radius of New York City"

    place = None
    admin1 = None
    admin2 = None
    admin3 = None
    admin4 = None

    if (precision == 'point') or (precision == 'place'):

        place_obj = Place.objects.filter(id=geo_id).first()

        if not place_obj:
            raise HeliosException(desc='Specified place does not exist', code='nonexistent_place')

        loc_latitude = latitude if latitude else place_obj.latitude
        loc_longitude = longitude if longitude else place_obj.longitude

        place = place_obj
        admin1 = place_obj.admin1
        admin2 = place_obj.admin2
        admin3 = place_obj.admin3
        admin4 = place_obj.admin4
        country = place_obj.country
        latitude = loc_latitude
        longitude = loc_longitude
        point = fromstr('POINT(' + str(loc_longitude) + ' ' + str(loc_latitude) + ')')

    elif precision == 'admin4':

        admin4_obj = Admin4.objects.filter(id=geo_id).first()

        if not admin4_obj:
            raise HeliosException(desc='Specified admin4 geo_id does not exist', code='nonexistent_admin4')

        admin1 = admin4_obj.admin1
        admin2 = admin4_obj.admin2
        admin3 = admin4_obj.admin3
        admin4 = admin4_obj
        country = admin4_obj.country
        latitude = admin4_obj.latitude
        longitude = admin4_obj.longitude
        point = admin4_obj.point

    elif precision == 'admin3':

        admin3_obj = Admin3.objects.filter(id=geo_id).first()

        if not admin3_obj:
            raise HeliosException(desc='Specified admin3 geo_id does not exist', code='nonexistent_admin3')

        admin1 = admin3_obj.admin1
        admin2 = admin3_obj.admin2
        admin3 = admin3_obj
        country = admin3_obj.country
        latitude = admin3_obj.latitude
        longitude = admin3_obj.longitude
        point = admin3_obj.point

    elif precision == 'admin2':

        admin2_obj = Admin2.objects.filter(id=geo_id).first()

        if not admin2_obj:
            raise HeliosException(desc='Specified admin2 geo_id does not exist', code='nonexistent_admin2')

        admin1 = admin2_obj.admin1
        admin2 = admin2_obj
        country = admin2_obj.country
        latitude = admin2_obj.latitude
        longitude = admin2_obj.longitude
        point = admin2_obj.point

    elif precision == 'admin1':

        admin1_obj = Admin1.objects.filter(id=geo_id).first()

        if not admin1_obj:
            raise HeliosException(desc='Specified admin1 geo_id does not exist', code='nonexistent_admin1')

        admin1 = admin1_obj
        country = admin1_obj.country
        latitude = admin1_obj.latitude
        longitude = admin1_obj.longitude
        point = admin1_obj.point

    else:

        country_obj = Country.objects.filter(id=geo_id).first()

        if not country_obj:
            raise HeliosException(desc='Specified country geo_id does not exist', code='nonexistent_country')

        country = country_obj

        # NOTE: the "country" level records in the geodata silo don't have lat/lon coordinates yet,
        # so this function will crash if someone tries to use it

        latitude = country_obj.latitude
        longitude = country_obj.longitude
        point = country_obj.point

    with transaction.atomic():

        user_location = Location.objects.select_for_update().filter(owner=user).first()

        if user_location:

            user_location.place = place
            user_location.admin1 = admin1
            user_location.admin2 = admin2
            user_location.admin3 = admin3
            user_location.admin4 = admin4
            user_location.country = country
            user_location.latitude = latitude
            user_location.longitude = longitude
            user_location.point = point

            user_location.context = clean_context
            user_location.precision = clean_precision
            user_location.updated = datetime.now()

            user_location.save()

        else:

            user_location = Location.objects.create(

                place=place,
                admin1=admin1,
                admin2=admin2,
                admin3=admin3,
                admin4=admin4,
                country=country,
                latitude=latitude,
                longitude=longitude,
                point=point,
                context=clean_context,
                precision=clean_precision,
                created=datetime.now(),
                updated=datetime.now()
            )

            # Update the User object's location

            owner = User.objects.select_for_update().filter(id=user.id).first()
            owner.location = user_location
            owner.save()

    return user_location
