#  -*- coding: UTF8 -*-

import newrelic.agent

from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from api_helios.base import AbstractHeliosEndpoint

from silo_geodata.api import find_best_place, render_place
from silo_geodata.geography.db import Admin1, Place, PostalCode


class GeolocateByPoint(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Finds the closest named place to the point represented by the supplied lat/lon coordinates.

            ** This endpoint is backed by a high performance datastore and can typically run queries in
            ** under 10ms. It's designed to be called multiple times in rapid succession to update the
            ** named location beneath a pin in realtime as the user drags it.

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "latitude": "37.77493",      // Latitude of the point
                    "latitude": "-122.41942"     // Longitude of the point
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",

                        "place": {

                            "precision": "place",
                            "geo_id": 5128581,
                            "postal_id": 780541,
                            "name": "San Francisco, California, San Francisco County, 94199",
                            "latitude": "37.77493",
                            "longitude": "-122.41942",
                            "country_name": "United States"
                        }
                    },
                    "success": true
                }
        """

        # We restrict this endpoint to logged-in users to prevent people using us as a free geocoding service
        target_hid = request.POST.get('target_hid')

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Sanitize latitude
        # =========================================================================

        try:
            # If it can't be mapped to a float, or overflows a float, this will throw an exception
            latitude = float(latitude)

        except:
            return self.render_error(request, code='lat_not_float', status=400)

        if (latitude < -90.0) or (latitude > 90.0):
            # Latitude parameter must be between -90.0 and +90.0
            return self.render_error(request, code='lat_exceeds_bounds', status=400)

        # Sanitize longitude
        # =========================================================================

        try:
            # If it can't be mapped to a float, or overflows a float, this will throw an exception
            longitude = float(longitude)

        except:
            return self.render_error(request, code='lon_not_float', status=400)

        if (longitude < -180.0) or (longitude > 180.0):
            # Longitude parameter must be between -180.0 and +180.0
            return self.render_error(request, code='lon_exceeds_bounds', status=400)

        # STEP 1: FIND CLOSEST ADMIN_1's
        # =========================================================================
        # There are several million "places" in our system, and it takes ~10 seconds to search through
        # all of them. But there are only ~4K admin_1's. So we find the closest admin_1's to the target point

        marker = fromstr('POINT(' + str(longitude) + ' ' + str(latitude) + ')')

        filters = {

            'point__distance_lte': (marker, D(km=1000))
        }

        admin1_ids = Admin1.objects.filter(**filters).values_list('id', flat=True).annotate(

            distance=Distance('point', marker)

        ).order_by('distance')[0:5]

        # STEP 2: FIND CLOSEST PLACES WITHIN RETURNED ADMIN_1's
        # =========================================================================
        # Limiting the search to only the selected admin_1's reduces the number of points that need to be searched
        # by a factor of 1000. We return the closest place to the target point within this search space.

        filters = {

            'admin1__in': list(admin1_ids),
            'point__distance_lte': (marker, D(km=100))
        }

        pre = [

            'country',
            'admin1',
            'admin2',
            'admin3',
            'admin4'
        ]

        places = Place.objects.filter(**filters).prefetch_related(*pre).annotate(

            distance=Distance('point', marker)

        ).order_by('distance')[0:50]

        # Its entirely possible that some places (for example 1000km into the middle of the ocean) may
        # have no place associated with them at all, because they're not part of any country

        if not places:

            return self.render_response(

                request=request,

                data={

                    'viewer_hid': None,
                    'place': None
                }
            )

        else:
            place = find_best_place(marker, places)

        # STEP 3: FIND POSTAL CODE
        # =========================================================================

        filters = {

            'admin1__in': list(admin1_ids),
            'point__distance_lte': (marker, D(km=100))
        }

        postal = PostalCode.objects.filter(**filters).annotate(

            distance=Distance('point', marker)

        ).order_by('distance').first()

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': None,
                'place': render_place(place, postal)
            }
        )
