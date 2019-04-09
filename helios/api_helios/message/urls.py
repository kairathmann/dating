# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from .conv_create import ConversationCreate
from .conv_retrieve_active import ConversationRetrieveActive
from .conv_retrieve_bids import ConversationRetrieveBids
from .conv_retrieve_single import ConversationRetrieveSingle
from .message_create import MessageCreate
from .bubble_create_link import BubbleCreateLink

urlpatterns = [

    url(r'^conversation/', include([

        url(r'^create/$', ConversationCreate.as_view(), name='ApiHelios.Message.Conv.Create'),
        url(r'^retrieve/active/$', ConversationRetrieveActive.as_view(), name='ApiHelios.Message.Conv.RetrieveActive'),
        url(r'^retrieve/bids/$', ConversationRetrieveBids.as_view(), name='ApiHelios.Message.Conv.RetrieveBids'),
        url(r'^retrieve/single/$', ConversationRetrieveSingle.as_view(), name='ApiHelios.Message.Conv.RetrieveSingle')
    ])),

    url(r'^message/', include([
        url(r'^bubble/$', BubbleCreateLink.as_view(), name='ApiHelios.Message.Bubble.Link'),
        url(r'^create/$', MessageCreate.as_view(), name='ApiHelios.Message.Message.Create')
    ]))
]
