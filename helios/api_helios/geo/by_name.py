#  -*- coding: UTF8 -*-

import newrelic.agent

from api_helios.base import AbstractHeliosEndpoint

from silo_geodata.api import render_place
from silo_geodata.geography.db import Place

from sys_base.api import parse_search_string


class GeolocateByName(AbstractHeliosEndpoint):

    @newrelic.agent.function_trace()
    def post(self, request, **kwargs):
        """
            Finds up to 'max_results' places matching 'search_name'.

            ** This endpoint is backed by a high performance datastore and can typically run queries in
            ** under 10ms. It's designed to be called multiple times in rapid succession for implementing
            ** autocomplete functionality.

            :param request: HTTP request containing

            .. code-block:: javascript
                {
                    "search_str": "San Fr",     // String to match against. Must be in UTF-8.
                    "max_results": "20"         // Max number of results to return
                }

            :return: JSON object

            .. code-block:: javascript
                {
                    "data": {

                        "viewer_hid": "b3665ea5",

                        "results": [

                            {
                                "precision": "place",
                                "geo_id": 5128581,
                                "name": "San Francisco, California, San Francisco County",
                                "latitude": "37.77493",
                                "longitude": "-122.41942",
                                "country_name": "United States"
                            },
                            {
                                "precision": "place",
                                "geo_id": 3493146,
                                "name": "San Francisco de Macoris, Provincia Duarte",
                                "latitude": "19.30099",
                                "longitude": "-70.25259",
                                "country_name": "Dominican Republic"
                            }
                        ]
                    },
                    "success": true
                }
        """

        # We restrict this endpoint to logged-in users to prevent people using us as a free geocoding service
        target_hid = request.POST.get('target_hid')

        search_str = request.POST.get('search_str')
        max_results = request.POST.get('max_results', 10)

        upstream = self.get_upstream_for_user(request, target_hid=target_hid)

        if not self.viewer_logged_in(upstream):
            return self.render_error(request, code='login_required', status=401)

        elif not upstream['target_user']:
            return self.render_error(request, code='nonexistent_user', status=400)

        if not (upstream['root_active'] or upstream['target_is_viewer']):
            return self.render_error(request, code='access_denied', status=403)

        # Sanitize search_name
        # =========================================================================

        tokens = parse_search_string(search_str)

        if len(tokens) < 1:
            return self.render_error(request, code='search_str_empty', status=400)

        # Sanitize max_results
        # =========================================================================

        try:
            max_results = int(max_results)

        except:
            return self.render_error(request, code='max_results_not_int', status=400)

        if (max_results < 1) or (max_results > 1000):
            return self.render_error(request, code='max_results_exceeds_bounds', status=400)

        filters = {

            'fulltext_chain__ft_phrase_startswith': tokens
        }

        pre = [

            'country',
            'admin1',
            'admin2',
            'admin3',
            'admin4'
        ]

        places = list(Place.objects.filter(**filters).prefetch_related(*pre).order_by('-population')[0:max_results])

        # Return JSON response
        # =======================================================================

        return self.render_response(

            request=request,

            data={

                'viewer_hid': None,
                'results': [render_place(place) for place in places]
            }
        )
