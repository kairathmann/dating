import imgix

import settings
from silo_user.user.gender_id import GenderId

class ImgixService:
    def __init__(self):
        self.builder = imgix.UrlBuilder(settings.IMGIX_SOURCE, sign_key=settings.IMGIX_SIGN_KEY, use_https=True)

    def build_unknown_user_avatar_url(self, user, width, height):
        if user.is_deleted:
            return self.builder.create_url("avatar/default_other.png", {'w': width, 'h': height})

        if user.gid_is == GenderId.ID_MALE:
            return self.builder.create_url("avatar/default_male.png", {'w': width, 'h': height})
        if user.gid_is == GenderId.ID_FEMALE:
            return self.builder.create_url("avatar/default_female.png", {'w': width, 'h': height})
        if user.gid_is == GenderId.ID_OTHER:
            return self.builder.create_url("avatar/default_other.png", {'w': width, 'h': height})

    def build_avatar_url(self, user, width, height):
        if user.is_deleted or not user.avatar_set:
            return self.build_unknown_user_avatar_url(user, width, height)

        return self.builder.create_url("avatar/%s.jpg"%user.hid, {'w': width, 'h': height})
