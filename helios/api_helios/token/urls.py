# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from .luna_get_balance import LunaGetBalance
from .luna_list_trans_all import LunaListTransfersAll
from .qtum_get_in_address import QtumGetInAddress
from .qtum_list_trans_in import QtumListTransfersIn
from .qtum_list_trans_out import QtumListTransfersOut
from .qtum_network_sync import QtumNetworkSync
from .qtum_send_trans_out import QtumSendTransOut

urlpatterns = [

    url(r'^luna/', include([

        url(r'^get_balance/$', LunaGetBalance.as_view(), name='ApiHelios.Token.Luna.GetBalance'),
        url(r'^list_trans_all/$', LunaListTransfersAll.as_view(), name='ApiHelios.Token.Luna.ListTransAll')
    ])),

    url(r'^qtum/', include([

        url(r'^get_in_address/$', QtumGetInAddress.as_view(), name='ApiHelios.Token.Qtum.GetInAddress'),
        url(r'^list_trans_in/$', QtumListTransfersIn.as_view(), name='ApiHelios.Token.Qtum.ListTransIn'),
        url(r'^list_trans_out/$', QtumListTransfersOut.as_view(), name='ApiHelios.Token.Qtum.ListTransOut'),
        url(r'^network_sync/$', QtumNetworkSync.as_view(), name='ApiHelios.Token.Qtum.NetworkSync'),
        url(r'^send_trans_out/$', QtumSendTransOut.as_view(), name='ApiHelios.Token.Qtum.SendTransOut')
    ])),
]
