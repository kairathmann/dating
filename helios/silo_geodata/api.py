# -*- coding: utf-8 -*-

import sys

from silo_geodata.cache.db import IpCache
from silo_geodata.util import fetch_ip_location

from sys_base.exceptions import HeliosException

from sys_util.geodata.name import render_name_chain_obj


def get_place_by_ip(ip):
    """
        Returns parsed geolocation data for a given IP address. If this function is passed an unroutable IP address,
        it will return a location somewhere in New York City.

        :param ip: (string) IPv4 or IPv6 address to check

        :return:
    """

    try:
        location = fetch_ip_location(ip)

    except HeliosException as e:

        if e.code in ['api_error']:

            # If MaxMind's API isn't working properly, return a random location somewhere in New York City
            # to avoid breaking the front-end UI. This is a better strategy than displaying a "Location Unknown"
            # screen, because a user might choose to leave their location in such a state whereas if we put them
            # in clearly the *wrong* location, they'll be annoyed and drag the map to where they actually are

            prefetch = ['country', 'admin1', 'admin2', 'admin3', 'admin4', 'place']

            location = IpCache.objects.filter(place_id=5128581).prefetch_related(*prefetch).first()

        else:
            exc_info = sys.exc_info()
            raise exc_info[0], exc_info[1], exc_info[2]

    return render_location(location)


def find_best_place(origin, places):
    """
        Given an origin location and a list of place records, finds the best matching place

        :param origin: a GEOS Point object
        :param places: list of Place objects
        :return: best Place object
    """

    # print "\nLIST: =========================================="
    #
    # for location in places:
    #
    #     test = 'CODE: ' + location.code + ', POP: ' + str(location.population) + ', LAT: ' + str(location.latitude) + ', LON: ' + str(location.longitude)
    #
    #     test += ', NAME: ' + location.name
    #
    #     if location.admin4:
    #         test += ', ADMIN 4: ' + location.admin4.name
    #
    #     if location.admin3:
    #         test += ', ADMIN 3: ' + location.admin3.name
    #
    #     if location.admin2:
    #         test += ', ADMIN 2: ' + location.admin2.name
    #
    #     if location.admin1:
    #         test += ', ADMIN 1: ' + location.admin1.name
    #
    #     print test

    # ATTEMPT 1: Return the closest populated place
    # =======================================================================================

    populated_places = [place for place in places if place.population > 0]

    if populated_places:

        sorted(populated_places, key=lambda x: origin.distance(x.point), reverse=True)

        return populated_places[0]


    # ATTEMPT 2: Ascend through the featude code heirarchy and find the closest place within
    # the first level that matches
    # =======================================================================================

    else:

        for feature_code in ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLX', 'PPLC',
                             'PPLL', 'PPLF', 'PPLS', 'PPLG', 'ADMD', 'ADM2', 'ADM3']:

            matching_places = [place for place in places if place.code == feature_code]

            if matching_places:
                sorted(matching_places, key=lambda x: origin.distance(x.point), reverse=True)

                return matching_places[0]


def render_location(location):
    """
        Renders a location record into a dict suitable for display by the site's front-end
        :param location:
        :return: Rendered location dict
    """

    result = {

        'name': render_name_chain_obj(

            base_name=location.place.asciiname if location.place else '',
            location=location
        ),

        'country_name': location.country.name
    }

    if location.place:

        result['geo_id'] = location.place.id

        if (location.latitude != location.place.latitude) or (location.longitude != location.place.longitude):

            result['precision'] = 'point'
            result['latitude'] = location.latitude
            result['longitude'] = location.longitude

        else:

            result['precision'] = 'place'
            result['latitude'] = location.place.latitude
            result['longitude'] = location.place.longitude

    else:

        if location.admin4:

            result['precision'] = 'admin4'
            result['geo_id'] = location.admin4.id

            result['latitude'] = location.admin4.latitude
            result['longitude'] = location.admin4.longitude

        elif location.admin3:

            result['precision'] = 'admin3'
            result['geo_id'] = location.admin3.id

            result['latitude'] = location.admin3.latitude
            result['longitude'] = location.admin3.longitude

        elif location.admin2:

            result['precision'] = 'admin2'
            result['geo_id'] = location.admin2.id

            result['latitude'] = location.admin2.latitude
            result['longitude'] = location.admin2.longitude

        elif location.admin1:

            result['precision'] = 'admin1'
            result['geo_id'] = location.admin1.id

            result['latitude'] = location.admin1.latitude
            result['longitude'] = location.admin1.longitude

        else:

            result['precision'] = 'country'
            result['geo_id'] = location.country.id

            result['latitude'] = location.country.latitude
            result['longitude'] = location.country.longitude

    return result


def render_place(place, postal=None):
    """
        Renders a place result into a dict

        :param place: Place result object to render
        :param postal: Postal result object to render

        :return: dict of place data
    """

    data = {

        'precision': 'place',
        'geo_id': place.id,
        'latitude': place.latitude,
        'longitude': place.longitude,
        'country_name': place.country.name
    }

    name = render_name_chain_obj(place.asciiname, place)

    if postal:
        data['postal_id'] = postal.id
        name += u", " + postal.postalcode

    data['name'] = name

    return data
