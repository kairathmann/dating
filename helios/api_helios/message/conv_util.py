#  -*- coding: UTF8 -*-

from silo_user.user.db import User

from silo_user.user.imgix_service import ImgixService

class ConversationUtil(object):
    """
    Utility class for conversations.
    """

    NAME_DELETED = "Deleted"

    @staticmethod
    def calc_partner(conversation, target_user):
        """
            Finds the User to display beside a Conversation in List View
        """
        if conversation.sender == target_user:
            return conversation.recipient
        else:
            return conversation.sender

    @staticmethod
    def avatar(partner, width, height):
	imgix_service = ImgixService()
	return imgix_service.build_avatar_url(partner, width, height)

    @staticmethod
    def first_name(partner):
        if partner.is_deleted:
            return ConversationUtil.NAME_DELETED
        else:
            return partner.first_name

    @staticmethod
    def gender(partner):
        if partner.is_deleted:
            return User.ID_OTHER
        else:
            return partner.gid_is
