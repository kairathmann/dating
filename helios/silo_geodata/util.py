# -*- coding: utf-8 -*-

import json, requests, sys
import newrelic.agent

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.gis.geos import fromstr
from django.db import transaction

from requests.utils import default_user_agent

from sys_base.exceptions import HeliosException

from silo_geodata.cache.db import IpCache
from silo_geodata.geography.db import Country, Admin1, Admin2, Admin3, Admin4, Place


@newrelic.agent.function_trace()
def fetch_ip_location(ip):
    """
        Fetches location information for a given ip address. If this function is passed an unroutable IP address,
        it will return a location somewhere in New York City.

        :param ip: (string) IPv4 or IPv6 address to check

        :return: object <silo_geodata.IpCache> with all child objects pre-fetched
    """

    # ####################################################################################################
    # NOTE: HEAVY error-checking and EXTENSIVE error-handling of MaxMind's responses is required. In a test
    # of 20,000 ip addresses on 2015-03-26, about 1% of responses failed with one of the following:
    #
    # "Timed-out", "HTTPS error", "4xx or 5xx error", "Empty response", "Invalid JSON"
    #
    # IP addresses that generate an erroneous response will often return valid data if tried again later
    # ####################################################################################################

    prefetch = ['country', 'admin1', 'admin2', 'admin3', 'admin4', 'place']

    # Handle unroutable IP addresses
    # ====================================================================================================

    # Can I do this with Regex? Yes. Should I do this with Regex? ...probably not.
    # https://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses

    newrelic.agent.add_custom_parameter('ip', ip)

    # Localhost is not routable

    if ip == '127.0.0.1':

        routable = False

    elif ':' in ip:

        tokens = ip.split(':')

        # According to Wikipedia (https://en.wikipedia.org/wiki/IPv6_address#IPv6_address_space)
        # ...CIDR fc00::/7 is the reserved IPv6 address block, which translates to the range:
        # fc00:0:0:0:0:0:0:0 - fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff

        if (str(tokens[0][0]) == 'f') and ((str(tokens[0][1]) == 'c') or (str(tokens[0][1]) == 'd')):

            routable = False

        else:
            routable = True

    else:

        tokens = ip.split('.')

        if int(tokens[0]) == 10:

            # 10.0.0.0 - 10.255.255.255
            routable = False

        elif (int(tokens[0]) == 172) and (int(tokens[1]) >= 16) and (int(tokens[1]) <= 31):

            # 172.16.0.0 - 172.31.255.255
            routable = False

        elif (int(tokens[0]) == 192) and (int(tokens[1]) == 168):

            # 192.168.0.0 - 192.168.255.255
            routable = False

        else:
            routable = True

    # If the IP is non-routable, return a cache entry for New York City, of which there are hundreds

    if not routable:
        return IpCache.objects.filter(place_id=5128581).prefetch_related(*prefetch).first()

    # Fetch the IP's cache record, if it exists
    # ====================================================================================================

    raise_exception = False

    with transaction.atomic():

        cache_entry = IpCache.objects.select_for_update().filter(ip=ip).prefetch_related(*prefetch).first()

        if cache_entry:

            # If the cache has a valid entry, update its usage metrics and return the row

            if cache_entry.valid:

                cache_entry.hits += 1
                cache_entry.last_hit = datetime.now()
                cache_entry.save()

                return cache_entry

            # If the cache entry is invalid, but is more than 4 hours old, delete it so it will
            # be fetched again. MaxMind often throws an error for an IP address then returns valid
            # data for the same IP address a few hours later

            elif (cache_entry.created + timedelta(hours=4)) < datetime.now():

                cache_entry.delete()

            # Otherwise, update its usage metrics, then fail the request

            else:

                cache_entry.hits += 1
                cache_entry.last_hit = datetime.now()
                cache_entry.save()

                raise_exception = True

    if raise_exception:
        raise HeliosException(desc='MaxMind API Error', code='api_error')

    # If the IP address doesn't have a cache entry, fetch it from MaxMind
    # ====================================================================================================

    fail_count = 0
    success = False

    while fail_count <= 3:

        fail_count += 1

        try:

            response = requests.get(

                url="https://geoip.maxmind.com/geoip/v2.1/insights/{}".format(ip),
                auth=(settings.MAXMIND_LOGIN, settings.MAXMIND_PASS),
                headers={

                    'Accept': 'application/json',

                    # Its important to set the user_agent
                    'User-Agent': 'GeoIP2 Python Client v%s (%s)' % ('2.1.0', default_user_agent())
                },

                # Requests MUST be time-limited. If the remote server never responds due to packets
                # being dropped, the timeout stops the process from infinitely blocking.

                timeout=10
            )

            if response.status_code == 200:

                raw_result = json.loads(response.text)
                success = True
                break

            # Handle the MaxMind API returning 400 and 500 class errors

            else:

                raw_result = {

                    'failure_type': 'bad_status',
                    'code': response.status_code,
                    'raw_result': json.loads(response.text)
                }

        # Handle requests raising an exception (timeout, malformed JSON response, SSL problem)

        except Exception as e:

            raw_result = {

                'failure_type': 'requests_exception',
                'error': str(e)
            }

    # If there was a failure accessing MaxMind, set a fail record and raise an exception
    # ====================================================================================================

    if not success:

        with transaction.atomic():

            # Even though we PREVIOUSLY checked if a cache entry exists for this IP address, we have to check AGAIN
            # inside a transaction because MaxMind's API can introduce 10's of seconds of lag between when we ran the
            # initial check and when we actually reach this block of code. This was previously causing about 5% of
            # calls to fail, so its actually a big deal.

            if not IpCache.objects.filter(ip=ip).exists():
                IpCache.objects.create(

                    ip=ip,
                    created=datetime.now(),
                    raw_result=raw_result,
                    hits=1,
                    valid=False
                )

        raise HeliosException(desc='MaxMind API Error', code='api_error')

    # Try to Parse the API result
    # ====================================================================================================

    try:

        fields = parse_maxmind_response(raw_result)

        with transaction.atomic():

            # Even though we PREVIOUSLY checked if a cache entry exists for this IP address, we have to check AGAIN
            # inside a transaction because MaxMind's API can introduce 10's of seconds of lag between when we ran the
            # initial check and when we actually reach this block of code. This was previously causing about 5% of
            # calls to fail, so its actually a big deal.

            if not IpCache.objects.filter(ip=ip).exists():
                IpCache.objects.create(

                    valid=True,
                    ip=ip,
                    user_type=fields['user_type'],
                    country=fields['country'],
                    admin1=fields['admin1'],
                    admin2=fields['admin2'],
                    admin3=fields['admin3'],
                    admin4=fields['admin4'],
                    place=fields['place'],
                    latitude=fields['latitude'],
                    longitude=fields['longitude'],
                    point=fields['point'],
                    loc_accuracy=fields['loc_accuracy'],
                    created=datetime.now(),
                    hits=1,
                    raw_result=raw_result,
                    code=fields['code']
                )

        # Reload the record we created, fetching all of its child objects

        return IpCache.objects.filter(ip=ip).prefetch_related(*prefetch).first()


    # If the result failed to parse, set a fail record and raise an exception
    # ====================================================================================================

    except HeliosException as e:

        if e.code in [

            'missing_traits', 'missing_country', 'missing_user_type', 'missing_location', 'missing_accuracy_radius',
            'lat_not_float', 'lat_exceeds_bounds', 'lon_not_float', 'lon_exceeds_bounds', 'accuracy_not_int',
            'accuracy_exceeds_bounds', 'invalid_user_type', 'city_id_not_int', 'city_id_exceeds_bounds',
            'country_id_not_int', 'country_id_exceeds_bounds', 'nonexistent_country_id', 'malformed_subdiv_dict',
            'subdiv_id_not_int', 'subdiv_id_exceeds_bounds'
        ]:

            with transaction.atomic():

                # Even though we PREVIOUSLY checked if a cache entry exists for this IP address, we have to check AGAIN
                # inside a transaction because MaxMind's API can introduce 10's of seconds of lag between when we ran the
                # initial check and when we actually reach this block of code. This was previously causing about 5% of
                # calls to fail, so its actually a big deal.

                if not IpCache.objects.filter(ip=ip).exists():
                    IpCache.objects.create(

                        ip=ip,
                        created=datetime.now(),
                        raw_result={'raw_result': raw_result, 'error': e.code},
                        hits=1,
                        valid=False
                    )

            raise HeliosException(desc='MaxMind API Error', code='api_error')

        else:
            exc_info = sys.exc_info()
            raise exc_info[0], exc_info[1], exc_info[2]


def parse_maxmind_response(record):
    """
        Parses a reponse from MaxMind's API, and converts it to a dict.

        :param record: response from MaxMind
        :return: place dict
    """

    # ####################################################################################################
    # NOTE: HEAVY error-checking and EXTENSIVE error-handling of MaxMind's responses is required. In a test
    # of 20,000 ip addresses on 2015-03-26, about 1% of responses contained invalid data.
    # ####################################################################################################

    if 'traits' not in record:
        raise HeliosException(desc='missing traits dict', code='missing_traits')

    if 'country' not in record:
        raise HeliosException(desc='missing country dict', code='missing_country')

    if 'user_type' not in record['traits']:
        raise HeliosException(desc='missing user_type dict', code='missing_user_type')

    if 'location' not in record:
        raise HeliosException(desc='missing location dict', code='missing_location')

    if 'accuracy_radius' not in record['location']:
        raise HeliosException(desc='missing accuracy_radius', code='missing_accuracy_radius')

    result = {}

    # Latitude
    # =======================================================================

    try:
        latitude = float(record['location']['latitude'])

    except:
        raise HeliosException(desc='latitude parameter is not a float', code='lat_not_float')

    if (latitude < -90.0) or (latitude > 90.0):
        raise HeliosException(

            desc='latitude parameter must be between -90.0 and +90.0', code='lat_exceeds_bounds'
        )

    # Longitude
    # =======================================================================

    try:
        longitude = float(record['location']['longitude'])

    except:
        raise HeliosException(desc='longitude parameter is not a float', code='lon_not_float')

    if (longitude < -180.0) or (longitude > 180.0):
        raise HeliosException(

            desc='longitude parameter must be between -180.0 and +180.0', code='lon_exceeds_bounds'
        )

    result['latitude'] = latitude
    result['longitude'] = longitude
    result['point'] = fromstr('POINT(' + str(longitude) + ' ' + str(latitude) + ')')

    # Accuracy
    # =======================================================================

    try:
        accuracy_radius = int(record['location']['accuracy_radius'])

    except:
        raise HeliosException(desc='Accuracy parameter is not an int', code='accuracy_not_int')

    if (accuracy_radius < 0) or (accuracy_radius > 20000):
        raise HeliosException(desc='Accuracy parameter must be between 0 and 20000.', code='accuracy_exceeds_bounds')

    result['loc_accuracy'] = accuracy_radius

    # User Type
    # =======================================================================

    lut = {

        'business': IpCache.TYPE_BUSINESS,
        'cafe': IpCache.TYPE_CAFE,
        'cellular': IpCache.TYPE_CELLULAR,
        'college': IpCache.TYPE_COLLEGE,
        'content_delivery_network': IpCache.TYPE_CDN,
        'dialup': IpCache.TYPE_DIALUP,
        'government': IpCache.TYPE_GOVERNMENT,
        'hosting': IpCache.TYPE_HOSTING,
        'library': IpCache.TYPE_LIBRARY,
        'military': IpCache.TYPE_MILITARY,
        'residential': IpCache.TYPE_RESIDENTIAL,
        'router': IpCache.TYPE_ROUTER,
        'school': IpCache.TYPE_SCHOOL,
        'search_engine_spider': IpCache.TYPE_SPIDER,
        'traveler': IpCache.TYPE_TRAVELER
    }

    if record['traits']['user_type'] not in lut:
        raise HeliosException(

            desc='Invalid user type: {}'.format(record['traits']['user_type']),
            code='invalid_user_type'
        )

    result['user_type'] = lut[record['traits']['user_type']]

    # If a city id is included in the response, use it to fetch known-good results from our DB
    # ==============================================================================================================

    if 'city' in record:

        try:
            city_id = int(record['city']['geoname_id'])

        except:
            raise HeliosException(desc='city_id parameter is not an int', code='city_id_not_int')

        if (city_id < 0) or (city_id > 2 ** 32):
            raise HeliosException(desc='city_id parameter must be between 0 and maxint.', code='city_id_exceeds_bounds')

        prefetch = ['country', 'admin1', 'admin2', 'admin3', 'admin4']

        place = Place.objects.filter(id=city_id).prefetch_related(*prefetch).first()

        if place:
            result['place'] = place

            result['country'] = place.country

            result['admin1'] = place.admin1
            result['admin2'] = place.admin2
            result['admin3'] = place.admin3
            result['admin4'] = place.admin4

            result['code'] = place.code

            return result

    # If no city was returned in the API call, or if we weren't able to fetch a Place record due to our database
    # being stale and not having a geo_id that MaxMind is referring to, disassemble the API response and generate
    # the most accurate records possible. It is NOT practical to add new entries to our geodata silo based on data
    # returned by MaxMind's API because:
    #
    # 1) The 'city' data returned by the API doesn't include centroid lat/lon coordinates, and we can't
    #    use the 'location' lat/lon coordinates because these are different from the city centroid
    #
    # 2) The 'city' data doesn't include population data, which is needed for ranking search results
    #
    # 3) The 'city' data doesn't include an ASCII version of the place name, and there's no way to guarantee
    #    we convert the unicode name to ASCII exactly the same way geonames does
    #
    # 4) The 'subdivisions' data doesn't include the admin level (1-4) of each entity. There's no guarantee
    #    that the admin entries exist in our database or are even valid (there are invalid entries in geonames)

    result['place'] = None

    # ...LOG PLACE NOT IN DATABASE

    # Country
    # =======================================================================

    try:
        country_id = int(record['country']['geoname_id'])

    except:
        raise HeliosException(desc='country_id parameter is not an int', code='country_id_not_int')

    if (country_id < 0) or (country_id > 2 ** 32):
        raise HeliosException(desc='country_id parameter must be between 0 and maxint.',
                              code='country_id_exceeds_bounds')

    country = Country.objects.filter(id=country_id).first()

    if not country:
        raise HeliosException(

            desc='Invalid country id: {}'.format(record['traits']['user_type']),
            code='nonexistent_country_id'
        )

    # Admin 1 -> Admin 4
    # =======================================================================

    if 'subdivisions' not in record:

        admin_1 = None
        admin_2 = None
        admin_3 = None
        admin_4 = None

    else:

        geo_ids = []

        for sub in record['subdivisions']:

            if 'geoname_id' not in sub:
                raise HeliosException(desc='malformed subdivisions dict', code='malformed_subdiv_dict')

            try:
                geo_id = int(sub['geoname_id'])

            except:
                raise HeliosException(desc='subdiv_id not an int', code='subdiv_id_not_int')

            if (geo_id < 0) or (geo_id > 2 ** 32):
                raise HeliosException(desc='subdiv_id parameter must be between 0 and maxint.',
                                      code='subdiv_id_exceeds_bounds')

            geo_ids.append(geo_id)

        admin_1 = Admin1.objects.filter(id__in=geo_ids).first()
        admin_2 = Admin2.objects.filter(id__in=geo_ids).first()
        admin_3 = Admin3.objects.filter(id__in=geo_ids).first()
        admin_4 = Admin4.objects.filter(id__in=geo_ids).first()

        if not (admin_1 or admin_2 or admin_3 or admin_4):
            pass

            # ...LOG ADMIN AREA NOT IN DATABASE

    # Assemble Record
    # =======================================================================

    result['country'] = country

    result['admin1'] = admin_1
    result['admin2'] = admin_2
    result['admin3'] = admin_3
    result['admin4'] = admin_4

    if admin_4:
        result['code'] = 'PPLA4'

    elif admin_3:
        result['code'] = 'PPLA3'

    elif admin_2:
        result['code'] = 'PPLA2'

    elif admin_1:
        result['code'] = 'PPLA1'

    else:
        result['code'] = None

    return result


def preload_cache():
    """
        A testing and bootstrapping function that preloads silo_geodate.IpCache with records from a text file,
        where each line is of the form:

        "cardinality", "ip_address"

        EXAMPLE:

            274, 8.8.8.8
            10973, 1.2.3.4

        The text file is generated by parsing Nginx logs using the Linux commands below. It easily handles 5GB+
        of logs in a single run.

        1) Unzip the log files
            'gunzip *.gz'

        2) Concatenate the files together
            'cat $(ls -t) > concat.txt'

        3) Extract the IP's
            'cat concat.txt | awk '{print $1}' | sort -r | uniq -c > unique_ips.txt'
    """

    with open('/mnt/CDN2/data/geonames/unique_ips.txt') as f:
        content = f.read().splitlines()

    tick = 0

    for line in content:

        tick += 1

        if tick % 10 == 0:
            print tick
        tokens = line.split()

        ip = tokens[1]

        try:
            result = fetch_ip_location(ip)

            print result.id

        except HeliosException as e:

            print e
