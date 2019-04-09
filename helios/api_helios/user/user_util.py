#  -*- coding: UTF8 -*-

class UserUtil(object):
    """
    Utility class for users.
    """

    @staticmethod
    def is_complete(user):
        """
        Returns whether the user is complete. Should be used for assigning the state.
        :param user: User.
        :return: True if the user is complete; False otherwise.
        """
        return (
            user.dob
            and user.gid_is
            and user.gid_seeking
            and user.seeking_age_from
            and user.seeking_age_to
            and user.first_name
        )
