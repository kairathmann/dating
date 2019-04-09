#  -*- coding: UTF8 -*-

from django.contrib.postgres.fields import JSONField
from django.db import models
from silo_asset.engine.base.asset import AssetEngine


class StashedAsset(models.Model):
    """
        Stores individual tasks associated with processing a stashed item
    """

    # The item's guid. We use random GUID's to prevent attackers from stealing other user's stashed items by
    # simply counting-up from their own item id (had we used this as the stash key) and claiming the item

    guid = models.CharField(max_length=16, db_index=True)

    # The User that created this stashed asset. This lets us get in touch with people who are having large
    # numbers of items fail on them. In the future this will be used with websockets to create a callback
    # notification instead of having the browser poll the server.

    requester = models.ForeignKey('silo_user.User', related_name='requester_stashed_assets')

    # NOTE: for several fields below, we store states and ID's as strings instead of ints. While this is less
    # efficient than storing them as ints, it has zero performance impact because there will be, at most, 100 items
    # in the table at any given time. Storing these items as strings makes them much easier to debug.

    engine = models.CharField(db_index=True, max_length=16)

    # Engines can name their workers whatever they want. Trying to enforce an enumerated
    # list of worker names in the Task model would break modularity

    worker = models.CharField(db_index=True, max_length=32)

    # The current state of this worker
    state = models.CharField(db_index=True, max_length=16, choices=AssetEngine.VALID_STATES)

    # The input data for this task
    input = JSONField(default=dict)

    # The output data for this task
    output = JSONField(default=dict)

    # The completion percentage of this task
    progress = models.PositiveSmallIntegerField(db_index=True)

    # When the task was initially created
    created = models.DateTimeField(db_index=True)

    # When the task was last modified
    updated = models.DateTimeField(db_index=True)
