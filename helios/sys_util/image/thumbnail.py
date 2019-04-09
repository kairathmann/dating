#  -*- coding: UTF8 -*-

from __future__ import division

import os
import random
import warnings

from sys_base.exceptions import HeliosException
from sys_util.image.math import fit_dimensions, zoom_dimensions
from wand.image import Image


def generate_thumbnail_prefix():
    """
        Generates a random prefix string for a thumbnail file. This is used for cache busting when an object's
        thumbnail is updated.

        :return: A random 8-character alphanumeric string
    """

    return ''.join([random.choice('0123456789abcdef') for x in range(8)])


def create_master_image(media_path, prefix, suffix, original_image, valid_formats, min_x=None, min_y=None):
    """
        Generates a master image in JPG format for original_image, then copies it to the CDN. A master image is
        the largest possible image we can generate for a media item. Its used to regenerate the post's thumbnails
        as the child thumbnail sizes needed change as the platform evolves.

        NOTE: Running this method on an image that has already been JPG compressed, as is done when we set a
        profile's avatar via crop_stashed_image(), will not harm image quality. The file will run through the
        JPG encoder untouched.

        :param media_path: Filesystem path to the folder to write the thumbnail images to.
        :param prefix: The prefix to prepend to the filename.
        :param suffix: The suffix to append to the filename.
        :param original_image: The source image to generate a master image from
        :param valid_formats: List of valid media formats. This is NOT the same as the file extension.
        :param min_x: Exception raised if the original_image width is below this value. Set to None to bypass.
        :param min_y: Exception raised if the original_image height is below this value. Set to None to bypass.

        :return: (pixels_x, pixely_y) dimensions of saved master image
    """

    # Fetch the master image file from disk
    # ====================================================================================

    # Ensure the filename is encoded as ASCII. The database stores strings as UTF8, and if
    # we pass a UTF8 encoded string to the filesystem, it will raise an exception

    try:
        ascii_filename = original_image.encode('ascii', 'replace')

    except:
        raise HeliosException(desc='Filename could not be converted to ASCII', code='invalid_filename')

    try:
        original = Image(filename=ascii_filename)

        original_x = original.width
        original_y = original.height

    except:
        raise HeliosException(desc='Error reading source image from disk', code='error_reading_file')

    # We explicitly analyze the file using ImageMagick via Wand because we cannot trust the user. File
    # extensions are easily changed, content-encoding types can arbitrarily set, and 'fingerprint strings'
    # are easily spoofed. ImageMagick loads the entire file and validates everything at the binary level
    # before trying to process it. If something is wrong, it *will* catch it.

    if original.format not in valid_formats:
        original.close()
        raise HeliosException(desc='Invalid original image file format', code='invalid_file_format')

    # Handle animated GIF's by creating a new Image out of the first frame (otherwise Wand will generate
    # potentially hundreds of images, one per frame)

    if original.animation:

        temp = Image(original.sequence[0])
        original.close()
        original = temp

    # Handle PDF's and other multi-frame non-animated image types. ImageMagick INCORRECTLY IDENTIFIES
    # PDF files as image type PNG

    elif len(original.sequence) > 1:

        temp = Image(original.sequence[0])
        original.close()
        original = temp

    x_below_limit = (min_x and (original_x < min_x))
    y_below_limit = (min_y and (original_y < min_y))

    if x_below_limit or y_below_limit:
        original.close()

        raise HeliosException(

            desc='Below min size. MIN_X: {}, X: {}, MIN_Y: {}, Y: {}'.format(min_x, original_x, min_y, original_y),
            code='below_min_size'
        )

    # Wand throws warnings instead of exceptions if we try to load or manipulate a corrupted file. Setting
    # warnings.filterwarnings to 'error' causes warnings to be raised as exceptions

    prev_warnings_setting = warnings.filterwarnings
    warnings.filterwarnings('error')

    try:
        cdn_master = original.clone()
        cdn_master.convert('jpeg')

        # Small changes in JPG compression quality make huge differences in image file size when the file size is
        # large. Increasing compression_quality from 90 to 95 could triple the size of a 3MB file.

        cdn_master.compression_quality = 90

    except Warning:
        raise HeliosException(desc='Corrupt original image file', code='corrupt_original_image_file')

    finally:
        original.close()
        warnings.filterwarnings = prev_warnings_setting  # Restore previous system warnings setting

    try:
        cdn_master_filename = "{}{}_{}.jpg".format(media_path, prefix, suffix)
        cdn_master.save(filename=cdn_master_filename)
        cdn_master.close()

    except:
        raise HeliosException(desc='Error saving master image', code='error_saving_master_image')

    return original_x, original_y


def create_child_images(media_path, mode, prefix, original_image, valid_formats, sizes, tolerance=0.6):
    """
        Given an image file, generates a set of thumbnail images up to the maximum thumbnail size
        that can be rendered from the file and saves the thumbnails to original_image.

        :param media_path: Filesystem path to the folder to write the thumbnail images to.
        :param mode: Crop or bound the image. One of ['crop', 'bound']
        :param prefix: The prefix to prepend to the filename.
        :param original_image: The image to generate thumbnails from
        :param valid_formats: List of valid media formats. This is NOT the same as the file extension.

        :param sizes: A list of sizes to create. Typically supplied by the silo class (eg: sys_base.Profile). Each
               size is an object of the form {'id':<ID>,'x':<X>,'y':<Y>}.

        :param tolerance: If the original image size is within (tolerance * thumb_size), it will be upsampled
               to thumb_size instead of being skipped.

        :return: (pixels_x, pixely_y) dimensions of the largest thumbnail image generated.
    """

    assert media_path
    assert mode in ['crop', 'bound']
    assert prefix
    assert original_image
    assert (tolerance >= 0) and (tolerance <= 1.0)

    # Fetch the original image file from disk
    # ====================================================================================

    try:
        # Ensure the filename is encoded as ASCII. The database stores strings as UTF8, and if
        # we pass a UTF8 encoded string to the filesystem, it will raise an exception

        ascii_filename = original_image.encode('ascii', 'replace')

    except:
        raise HeliosException(desc='Filename could not be converted to ASCII', code='invalid_filename')

    try:
        original = Image(filename=ascii_filename)

    except:
        raise HeliosException(desc='Error reading source image from disk', code='error_reading_filename')

    # We explicitly analyze the file using ImageMagick via Wand because we cannot trust the user. File
    # extensions are easily changed, content-encoding types can arbitrarily set, and 'fingerprint strings'
    # are easily spoofed. ImageMagick loads the entire file and validates everything at the binary level
    # before trying to process it. If something is wrong, it *will* catch it.

    if original.format not in valid_formats:
        original.close()
        raise HeliosException(desc='Invalid original image file format', code='invalid_file_format')

    # Handle animated GIF's by creating a new Image out of the first frame (otherwise Wand will generate
    # potentially hundreds of images, one per frame)

    if original.animation:

        temp = Image(original.sequence[0])
        original.close()
        original = temp

    # Handle PDF's and other multi-frame non-animated image types. ImageMagick INCORRECTLY IDENTIFIES
    # PDF files as image type PNG

    elif len(original.sequence) > 1:

        temp = Image(original.sequence[0])
        original.close()
        original = temp

    # Generate thumbs
    # ====================================================================================

    # Creating thumbnail images and writing them to a locally attached drive takes milliseconds. There's no
    # point in doing it asynchronously. Iterate through each image size, saving a thumbnail if the base image
    # is larger than the desired thumbnail size

    original_x = original.width
    original_y = original.height

    max_id_matched = None
    max_x_matched = None
    max_y_matched = None

    for size in sizes:

        if (original_x < (tolerance * size['x'])) or (original_y < (tolerance * size['y'])):
            break

        # Wand throws warnings instead of exceptions if we try to load or manipulate a corrupted file. Setting
        # warnings.filterwarnings to 'error' causes warnings to be raised as exceptions

        prev_warnings_setting = warnings.filterwarnings
        warnings.filterwarnings('error')

        try:

            max_id_matched = size['id']

            # WARNING: do not try to "optimize" this algorithm by creating each successively smaller thumbnail
            # from the thumbnail created before it, instead of the original. Although doing so would be faster because
            # less total pixels need to be processed, running the image through potentially dozens of resizing and
            # compression steps would cause severe generation loss. See: https://en.wikipedia.org/wiki/Generation_loss

            thumb = original.clone()

            # Its important to convert to JPG before doing any operations, because for many images this
            # will increase the image to a 24-bit color space, which produces better results when filtering

            thumb.convert('jpg')

            # A JPG compression level of 95 seems to be optimum for our thumbnail sizes. If set lower than this,
            # small thumbnail sizes become excessively noisy. To the user, this looks like the image is 'mushy',
            # but its not the same as a blurry image. You can see the problem by zooming-in to an image in your
            # web browser or viewing it at a high level of zoom in an image editor.

            thumb.compression_quality = 95

            # NOTE: Wand also offers a third resizing algorithm called "liquid_resize" which uses seam-carving to
            # try and selectively discard parts of the image. It works well on images with large empty areas, but
            # with zoomed-in images of people's faces, the results are proper nightmare fuel. As such, we
            # don't use this algorithm.

            if mode == 'crop':

                crop_data = zoom_dimensions(

                    image_x=original_x,
                    image_y=original_y,
                    min_x=size['x'],
                    min_y=size['y'],
                    max_x=size['x'],
                    max_y=size['y']
                )

                thumb.resize(

                    # See: http://www.dylanbeattie.net/magick/filters/result.html
                    width=crop_data['scale']['x'],
                    height=crop_data['scale']['y'],
                    filter='lanczos',
                    blur=0.9
                )

                thumb.crop(

                    crop_data['crop']['x1'], crop_data['crop']['y1'],
                    crop_data['crop']['x2'], crop_data['crop']['y2']
                )

                max_x_matched = size
                max_y_matched = size


            elif mode == 'bound':

                bound_data = fit_dimensions(

                    image_x=original_x,
                    image_y=original_y,
                    target_x=size['x'],
                    target_y=size['y']
                )

                thumb.resize(

                    # See: http://www.dylanbeattie.net/magick/filters/result.html
                    width=bound_data['x'],
                    height=bound_data['y'],
                    filter='lanczos',
                    blur=0.9
                )

                max_x_matched = bound_data['x']
                max_y_matched = bound_data['y']


        except Warning:

            # If wand raises an exception during any of the crop or resize operations, the image
            # file is corrupt

            raise HeliosException(desc='Corrupt original_image file', code='corrupt_original_image_file')

        finally:

            # Restore previous system warnings setting
            warnings.filterwarnings = prev_warnings_setting

        # Save the thumb
        # ====================================================================================

        try:
            thumb_filename = "{}{}_{}.jpg".format(media_path, prefix, str(size['id']))
            thumb.save(filename=thumb_filename)

        except:
            raise HeliosException(desc='Error saving image to disk', code='error_saving_to_disk')

    original.close()

    # The loop will break when it hits the maximum thumbnail size that can be generated using the
    # source image. We return this value.

    return max_id_matched, max_x_matched, max_y_matched


def delete_master_image(media_path, prefix, suffix):
    """
        Deletes the master thumbnail image corresponding to media_path and prefix

        :param media_path: Filesystem path to the folder to delete the thumbnail images from.
        :param prefix: The prefix to prepend to the filename
        :param suffix: The suffix to append to the filename.
    """

    filename = "{}{}_{}.jpg".format(media_path, prefix, suffix)

    try:
        os.remove(filename)

    except OSError:
        pass


def delete_child_images(media_path, prefix, max_size, sizes):
    """
        Deletes all child image files in media_path with the supplied prefix string, up to max_size.

        :param media_path: Filesystem path to the folder to delete the thumbnail images from.
        :param prefix: The prefix to prepend to the filename.
        :param max_size: Largest size present in the folder.

        :param sizes: A list of sizes to delete. Typically supplied by the silo class (eg: sys_base.Profile). Each
               size is an object of the form {'id':<ID>,'x':<X>,'y':<Y>}.
    """

    # NOTE: what we'd ideally like to do is something called an 'atomic delete', where either *all* of the
    # target files get deleted or *none* of the target files get deleted. Unfortunately, the filesystems
    # we have available to us on the server don't support transactions. If the system had to be extremely
    # reliable, we would first create a backup copy of each file, then delete the target files, then delete
    # the backup copies; and if something went wrong while deleting the target files, we'd 'roll-back' the
    # operation by restoring all of the deleted files from the backups.
    #
    # We probably don't need that level of reliability at this point, so instead the code below just steamrollers
    # through any exceptions it encounters. The downside of this is that cloud filesystems aren't 100% reliable,
    # and over time, glitches with filesystem operations will cause orphan files to slowly accumulate.

    for size in sizes:

        if max_size >= size['id']:

            filename = "{}{}_{}.jpg".format(media_path, prefix, str(size['id']))

            try:
                os.remove(filename)

            except OSError:
                pass
