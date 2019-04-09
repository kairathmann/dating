#  -*- coding: UTF8 -*-

import newrelic.agent

from api_helios.base import AbstractHeliosEndpoint

from silo_geodata.api import get_place_by_ip

from sys_base.api import get_client_ip


class GeolocateByIP(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Returns the most precise location data possible for a given IP address. When run on a dev box (where the
            client is connecting from within a local network and as such has an unroutable IP address), this endpoint
            will return a location somewhere in New York City.

            :param request: JSON object {}

            :return: JSON object

            There are six possible levels of precision, "point" is the most precise, and "country" is the least
            precise: ["point", "place", "admin4", "admin3", "admin2", "admin1", "country"]

            CASE 1 - POINT PRECISION
            ====================================================================================
            When the endpoint returns a "point" precision record, the "latitude", and "longitude" coordinates
            are significant. When calling SetUserLocation, with this data, you must send "geo_id", "precision",
            "latitude", and "longitude"

            .. code-block:: javascript

                {
                    "geo_id": 5128581,
                    "precision": "point",
                    "longitude": -74.00520,
                    "latitude": 40.72140,
                    "country_name": "United States",
                    "place_name": "New York City, New York"
                }

            CASE 2 - ALL OTHER LEVELS OF PRECISION
            ====================================================================================
            When the endpoint returns a record that has any precision other than "point", the "latitude", and
            "longitude" coordinates are simply the weighted centroid of the geodata object being returned, and
            as such are already stored in the database. When calling SetUserLocation, with the record, you
            only have to send "geo_id" and "precision"

            .. code-block:: javascript

                {
                    "geo_id": 2968815,
                    "precision": "admin2",
                    "longitude": -74.0,
                    "latitude": 40.7,
                    "country_name": "United States",
                    "place_name": "New York City, New York"
                }
        """

        # We restrict this endpoint to logged-in users to prevent people using us as a free geolocation service
        target_hid = request.POST.get('target_hid')

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': None,
                'place': get_place_by_ip(get_client_ip(request))
            }
        )
