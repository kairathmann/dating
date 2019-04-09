# -*- coding: utf-8 -*-
from django.conf.urls import url

from .avatar_crop import UserAvatarCrop
from .avatar_stash import UserAvatarStash
from .avatar_upload import UserAvatarUpload
from .create import UserCreate
from .disable_delete import UserDelete
from .disable_delete import UserDisable
from .login import Login
from .logout import Logout
from .retrieve_edit import UserRetrieveForEdit
from .retrieve_self import UserRetrieveForSelf
from .retrieve_single import UserRetrieveForSingle
from .retrieve_recommend import UserRetrieveForRecommend, UserRetrieveForSkipped
from .update_daily_inbox_limit import UserUpdateDailyInboxLimit
from .update_pass import UserUpdatePass
from .update_profile import UserUpdateProfile
from .update_reaction_unmatch import UserUpdateReactionUnmatch

urlpatterns = [

    url(r'^avatar/crop/$', UserAvatarCrop.as_view(), name='ApiHelios.User.AvatarCrop'),
    url(r'^avatar/stash/$', UserAvatarStash.as_view(), name='ApiHelios.User.AvatarStash'),
    url(r'^avatar/upload/$', UserAvatarUpload.as_view(), name='ApiHelios.User.AvatarUpload'),

    url(r'^create/$', UserCreate.as_view(), name='ApiHelios.User.Create'),

    url(r'^delete/$', UserDelete.as_view(), name='ApiHelios.User.Delete'),
    url(r'^disable/$', UserDisable.as_view(), name='ApiHelios.User.Disable'),

    url(r'^login/$', Login.as_view(), name='ApiHelios.User.Login'),
    url(r'^logout/$', Logout.as_view(), name='ApiHelios.User.Logout'),

    url(r'^retrieve/edit/$', UserRetrieveForEdit.as_view(), name='ApiHelios.User.RetrieveEdit'),
    url(r'^retrieve/self/$', UserRetrieveForSelf.as_view(), name='ApiHelios.User.RetrieveSelf'),
    url(r'^retrieve/single/$', UserRetrieveForSingle.as_view(), name='ApiHelios.User.RetrieveSingle'),
    url(r'^retrieve/recommend/$', UserRetrieveForRecommend.as_view(), name='ApiHelios.User.RetrieveRecommend'),
    url(r'^retrieve/skipped/$', UserRetrieveForSkipped.as_view(), name='ApiHelios.User.RetrieveSkipped'),

    url(r'^update/daily_inbox_limit/$', UserUpdateDailyInboxLimit.as_view(),
        name='ApiHelios.User.UpdateDailyInboxLimit'),
    url(r'^update/pass/$', UserUpdatePass.as_view(), name='ApiHelios.User.UpdatePass'),
    url(r'^update/profile/$', UserUpdateProfile.as_view(), name='ApiHelios.User.UpdateProfile'),
    url(r'^update/reaction/unmatch/$', UserUpdateReactionUnmatch.as_view(),
        name='ApiHelios.User.UpdateReactionUnmatch'),
]
