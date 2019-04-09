# -*- coding: utf-8 -*-

import json, requests

from django.core.urlresolvers import reverse

from silo_user.user.db import User
from silo_user.user.gender import GenderId


def get_url(route):
    return 'http://localhost:8001' + reverse(route)


def create_test_user():
    session = requests.Session()

    return json.loads(session.post(

        url=get_url('ApiHelios.User.Create'),

        data={

            'email': 'test@example.com',
            'first_name': 'Test',
            'password': '12345678',
            'year': 1910,
            'month': 1,
            'date': 1,
            'gid_is': GenderId.ID_FEMALE,
            'gid_seeking': GenderId.ID_MALE
        }

    ).text)


def login_test_user():
    session = requests.Session()

    result = json.loads(session.post(

        url=get_url('ApiHelios.User.Login'),

        data={

            'email': 'test@example.com',
            'password': '12345678'
        }

    ).text)

    assert result['success'] is True

    viewer_hid = result['data']['viewer_hid']

    return session, viewer_hid
