#  -*- coding: UTF8 -*-

from django.db import models
from silo_user.user.db import User


class ExitSurvey(models.Model):
    COMMENT_MAX_LENGTH = 500

    # The user that created this exit survey
    user = models.ForeignKey('silo_user.User')

    # The state that the user changed to
    state = models.SmallIntegerField(choices=User.USER_STATES)

    # When this exit survey was created
    created = models.DateTimeField(auto_now_add=True)

    # Reason flags
    reason1 = models.BooleanField()
    reason2 = models.BooleanField()
    reason3 = models.BooleanField()
    reason4 = models.BooleanField()
    reason5 = models.BooleanField()

    # Comment
    comment = models.CharField(max_length=COMMENT_MAX_LENGTH, null=True)
