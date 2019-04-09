#  -*- coding: UTF8 -*-

from __future__ import division

import newrelic.agent
import os
import sys

import sys_util.image.thumbnail as thumbnail
from django.db import connection, transaction
from silo_asset.engine.image_crop.stash import ImageCroppable
from silo_asset.item.db import StashedAsset
from sys_base.exceptions import HeliosException


class ProfileImage(object):
    """
        Provides image management methods for profiles
    """

    # Entity Images
    # =================================================================

    AVATAR_SIZES = [

        {'id': 1, 'x': 32, 'y': 32},
        {'id': 2, 'x': 48, 'y': 48},
        {'id': 3, 'x': 64, 'y': 64},
        {'id': 4, 'x': 96, 'y': 96},
        {'id': 5, 'x': 128, 'y': 128},
        {'id': 6, 'x': 192, 'y': 192},
        {'id': 7, 'x': 256, 'y': 256},
        {'id': 8, 'x': 384, 'y': 384},
        {'id': 9, 'x': 512, 'y': 512}
    ]

    # MIN_SIZE is used by the stash to decide whether or not to accept an image file a user uploads for a
    # given type of profile image

    AVATAR_MIN_SIZE = {'id': 7, 'x': 256, 'y': 256}

    # MAX_SIZE is used by the stash to decide whether or not to downsample an image file a user uploads for a
    # given type of profile image

    AVATAR_MAX_SIZE = {'id': 9, 'x': 512, 'y': 512}

    @classmethod
    @newrelic.agent.function_trace()
    def set_avatar_from_stash(cls, profile_id, guid, x1, y1, x2, y2):
        """
            Replaces a profile's avatar image with the stash image represented by 'guid', generating all necessary
            child sizes. See plant_media.engines.profile.core.crop_stashed_profile_image() for detailed usage examples.

            :param profile_id: id of the profile profile to modify.
            :param guid: Stash guid representing an image.
            :param x1: x-value of the upper-left coordinate to crop from
            :param y1: y-value of the upper-left coordinate to crop from
            :param x2: x-value of the lower-right coordinate to crop to
            :param y2: y-value of the lower-right coordinate to crop to

            :return: New maximum avatar size id.
        """

        ImageCroppable.crop_item(

            guid=guid,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            aspect_ratio_x=cls.AVATAR_SIZES[-1]['x'],
            aspect_ratio_y=cls.AVATAR_SIZES[-1]['y']
        )

        with transaction.atomic():  # Note select_for_update() calls

            profile = cls.objects.select_for_update().filter(id=profile_id).first()

            if not profile:
                raise HeliosException(desc='profile_id does not exist', code='nonexistent_profile_id')

            asset = StashedAsset.objects.select_for_update().get(guid=guid)

            if not asset:
                raise HeliosException(desc='Requested stash_guid does not exist', code='nonexistent_stash_guid')

            cls._set_avatar_from_file(profile, asset.output['cropped_image'])
            asset.delete()

        return cls.get_avatar_url(profile)

    @newrelic.agent.function_trace()
    def _set_avatar_from_file(self, original_image):
        """
            Creates a set of avatar thumbnails for a profile using the supplied original_image file. If the profile
            already has a set of avatar thumbnails, they will overwritten. This function can only be used inside an
            atomic transaction block, on a profile which has been locked using .select_for_update()

            :param original_image: An image to set as the profile avatar.
            :return: id of largest avatar size created.
        """

        prefix_base = thumbnail.generate_thumbnail_prefix()

        size_id = self._set_image_from_file(

            original_image=original_image,
            old_prefix=(str(self.avatar_prefix) + '_avatar') if self.avatar_prefix else None,
            old_size=self.avatar_size,
            sizes=self.AVATAR_SIZES,
            new_prefix=prefix_base + '_avatar'
        )

        self.avatar_prefix = prefix_base
        self.avatar_size = size_id
        self.avatar_set = True
        self.save()

        return size_id

    @newrelic.agent.function_trace()
    def _set_image_from_file(self, original_image, old_prefix, old_size, sizes, new_prefix):
        """
            Creates a set of thumbnails for a profile 'avatar' image using the supplied
            original_image file. If the profile already has a set of thumbnails for the specified image type, they
            will overwritten. This function is used to wrap self._create_or_update_image() to handle automatically
            creating the profile's assets folder.

            :param original_image: An file to set as the specified image
        """

        # This assertion blocks a race condition whereby two requests in rapid succession try to modify the
        # same files on the CDN. Wrapping it in an update transaction blocks the second request until the
        # first one completes, and enforces the lock across the entire server cluster.

        assert connection.in_atomic_block, "This method can only be used within a transaction"

        if os.path.exists(self._assets_path):

            created_assets_folder = False

        else:

            created_assets_folder = True

            try:
                os.makedirs(self._assets_path, 0755)

            except:
                raise HeliosException(desc='Error creating assets folder', code='error_creating_assets_folder')

        try:
            return self._create_or_update_image(original_image, old_prefix, old_size, sizes, new_prefix)


        except HeliosException:

            # If we created a profile folder for this entity and have to abort, we also have to delete
            # the profile folder we just created

            if created_assets_folder:
                os.rmdir(self._assets_path)

            # Bubble exception, preserving stacktrace
            exc_info = sys.exc_info()
            raise exc_info[0], exc_info[1], exc_info[2]

    @newrelic.agent.function_trace()
    def _create_or_update_image(self, original_image, old_prefix, old_size, sizes, new_prefix):
        """
            Creates a set of thumbnails for this profile using the supplied original_image file. If the post already
            has a set of thumbnails, they will overwritten.

            :param original_image: An file to set as the specified image
        """

        # Create new master and child images
        # =================================================================

        try:

            thumbnail.create_master_image(

                media_path=self._assets_path,
                prefix=new_prefix,
                suffix='MASTER',
                original_image=original_image,
                valid_formats=ImageCroppable.IMAGE_FORMATS,
                min_x=sizes[0]['x'],
                min_y=sizes[0]['y']
            )

            size_id, cropped_x, cropped_y = thumbnail.create_child_images(

                media_path=self._assets_path,
                prefix=new_prefix,
                original_image=original_image,
                valid_formats=ImageCroppable.IMAGE_FORMATS,
                sizes=sizes,
                mode='crop'
            )

        except HeliosException as e:

            # If create_child_images() has reached the point where it can throw a 'corrupt_original_image_file'
            # exception, we need to delete any files it managed to write

            if e.code == 'corrupt_original_image_file':
                thumbnail.delete_master_image(

                    media_path=self._assets_path,
                    prefix=new_prefix,
                    suffix='MASTER'
                )

                thumbnail.delete_child_images(

                    media_path=self._assets_path,
                    prefix=new_prefix,

                    # Feed it the largest possible avatar size, to ensure all files are cleared
                    max_size=sizes[-1],

                    sizes=sizes
                )

            # Bubble the exception, preserving stacktrace (this will abort the transaction)
            exc_info = sys.exc_info()
            raise exc_info[0], exc_info[1], exc_info[2]

        # Delete the old master and child images, if they exist
        # =================================================================

        if old_prefix:
            thumbnail.delete_master_image(

                media_path=self._assets_path,
                prefix=old_prefix,
                suffix='MASTER'
            )

            thumbnail.delete_child_images(

                media_path=self._assets_path,
                prefix=old_prefix,
                max_size=old_size,
                sizes=sizes
            )

        return size_id
