#  -*- coding: UTF8 -*-

import random

from django.template.loader import get_template
from silo_user.user.view.base import UserAsBase


class UserAsTile(UserAsBase):
    RENDER = {

        'desktop': {

            'template': 'silo_user/user/view/tpl_desktop/tile/items.html',

            'css_head': {

                'src': [

                    'sys_base/ui/css_desktop/fonts.css',
                    'sys_base/control/css_desktop/tile/items.css',
                    'silo_user/user/view/css_desktop/tile.css'
                ]
            },

            'js_head': {

                'lib': [

                    'jquery/jquery-1.12.0.js'
                ],

                'src': [

                    'sys_base/control/js_desktop/tile/items.js'
                ]
            }
        },

        'mobile': {'template': '', 'css_head': {}, 'js_head': {}}
    }

    def __init__(self, universe, viewer, **kwargs):
        self.universe = universe

        self.org = kwargs.get('org', None)
        self.viewed_user = kwargs.get('viewed_user', None)

        self.followed_ids = kwargs.get('followed_ids', [])

        self.viewer = viewer
        self.followed_ids = kwargs.get('followed_ids', [])

        self.prefix = kwargs.get('prefix', None)
        self.avatar_req_x = kwargs.get('avatar_req_x', 96)
        self.avatar_req_y = kwargs.get('avatar_req_y', 96)

    def select_related_cols(self):
        cols = [

            'job',
            'location__country',
            'location__admin1',
            'location__admin2',
            'location__admin3',
            'location__admin4',
            'location__place'
        ]

        return [self.prefix + '__' + col for col in cols] if self.prefix else cols

    def only_cols(self):
        cols = [

            'slug',
            'first_name',
            'last_name',
            'hid',
            'avatar_prefix',
            'avatar_size',
            'job__title',
            'job__employer',
            'location__country__alpha3',
            'location__admin1__code',
            'location__admin1__name',
            'location__admin2__name',
            'location__admin3__name',
            'location__admin4__name',
            'location__place__name'
        ]

        return [self.prefix + '__' + col for col in cols] if self.prefix else cols

    def render_iframe_html(self, target, items_page, total_items, items):
        """
            Renders a HTML blob for this schema instance

            :return: rendered HTML blob for this schema instance
        """

        template = get_template(self.RENDER['desktop']['template'])

        return template.render({

            'CSS_HEAD': self.enqueue_css_head(target),
            'JS_HEAD': self.enqueue_js_head(target),

            'TOTAL': total_items,
            'ITEMS_PAGE': items_page,

            'ITEMS': [{

                'NAME': user.first_name + ' ' + user.last_name,
                'URL': user.get_relative_url(),
                'AVATAR': self.build_avatar(user),
                'JOB': self.build_job(user),
                'LOCATION': self.build_location(user),
                'ACTIONS': self.build_actions(user),

                'DELAY': "{0:.1f}".format(random.choice([x * .1 for x in range(0, 5)]))

            } for user in items]
        })
