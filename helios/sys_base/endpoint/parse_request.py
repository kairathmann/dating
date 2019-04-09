# -*- coding: utf-8 -*-

import json

from app_org.ajax.core.rate_limit import check_endpoint_rate

from sys_base.exceptions import GETRequestException, JSONRequestException, POSTRequestException


def parse_json_request(request, required_keys, must_be_authenticated, rate_limit=None):
    # Trap the client sending an invalid JSON object, because it will throw an exception

    try:
        data = json.loads(request.body)

    except:

        raise JSONRequestException(

            desc='Client sent an invalid JSON object',
            code=400
        )

    # Check for missing keys

    missing_keys = [key for key in required_keys if key not in data]

    if missing_keys:
        raise JSONRequestException(

            desc='Missing JSON keys: ' + ', '.join(missing_keys),
            code=400
        )

    # Rate-limit the client if necessary

    if rate_limit:

        rate_ok = check_endpoint_rate(

            request,
            endpoint=rate_limit['endpoint'],
            max_1s=rate_limit['max_1s'],
            max_60s=rate_limit['max_60s'],
            max_3600s=rate_limit['max_3600s']
        )

        if not rate_ok:
            raise JSONRequestException(

                desc='Too many requests',
                code=429
            )

    if must_be_authenticated and not request.user.is_authenticated():
        raise JSONRequestException(

            desc='You must be authenticated to use this endpoint',
            code=401
        )

    return data


def parse_post_request(request, required_keys, must_be_authenticated, rate_limit=None):
    # Check for missing keys

    missing_keys = [key for key in required_keys if key not in request.POST]

    if missing_keys:
        raise POSTRequestException(

            desc='Missing POST keys: ' + ', '.join(missing_keys),
            code=400
        )

    # Rate-limit the client if necessary

    if rate_limit:

        rate_ok = check_endpoint_rate(

            request,
            endpoint=rate_limit['endpoint'],
            max_1s=rate_limit['max_1s'],
            max_60s=rate_limit['max_60s'],
            max_3600s=rate_limit['max_3600s']
        )

        if not rate_ok:
            raise POSTRequestException(

                desc='Too many requests',
                code=429
            )

    if must_be_authenticated and not request.user.is_authenticated():
        raise POSTRequestException(

            desc='You must be authenticated to use this endpoint',
            code=401
        )

    return request.POST


def parse_get_request(request, required_keys, must_be_authenticated, rate_limit=None):
    # Check for missing keys

    missing_keys = [key for key in required_keys if key not in request.GET]

    if missing_keys:
        raise GETRequestException(

            desc='Missing GET keys: ' + ', '.join(missing_keys),
            code=400
        )

    # Rate-limit the client if necessary

    if rate_limit:

        rate_ok = check_endpoint_rate(

            request,
            endpoint=rate_limit['endpoint'],
            max_1s=rate_limit['max_1s'],
            max_60s=rate_limit['max_60s'],
            max_3600s=rate_limit['max_3600s']
        )

        if not rate_ok:
            raise GETRequestException(

                desc='Too many requests',
                code=429
            )

    if must_be_authenticated and not request.user.is_authenticated():
        raise GETRequestException(

            desc='You must be authenticated to use this endpoint',
            code=401
        )

    return request.GET
