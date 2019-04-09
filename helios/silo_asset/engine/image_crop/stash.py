#  -*- coding: UTF8 -*-

from __future__ import division

import os
import time
import warnings
from datetime import datetime

from django.conf import settings
from django.db import transaction
from silo_asset.engine.base.asset import AssetEngine
from silo_asset.item.db import StashedAsset
from sys_base.exceptions import HeliosException
from sys_util.image.math import fit_dimensions
from wand.image import Image


class ImageCroppable(AssetEngine):
    """
        This engine handles croppable images
    """

    # Even though our image library, pgmagick, can read over 190 different file types (you can view the list by
    # running 'identify -list format' in terminal), we only let users upload 16 common formats. We do this because
    # every additional format we allow is probably full of exploits and obscure edge-cases that could burn massive
    # amounts of time while providing little value to users

    IMAGE_FORMATS = ['BMP', 'EPS', 'GIF', 'ICO', 'JPG', 'JPEG', 'JPEG2000', 'PCX', 'PNG', 'PNG8', 'PNG24', 'PNG32',
                     'SVG',
                     'SVGZ', 'TIFF', 'TIFF64']

    # The maximum size in X and Y pixels that an image will be stored at during crop and resizing operations. For
    # example, if set to 4096, the maximum size is 4096 x 4096 pixels. If the user uploaded a 8192 x 2000 pixel
    # image, it would be resized to 4096 x 1000 pixels for image manipulation operations.

    MAX_INTERNAL_IMAGE_SIZE = 8192

    @classmethod
    def stash_item(cls, guid, requester, filehandle, formats, resize_width, resize_height, min_x, min_y):
        """
            ===========================================================================================================
            WARNING: This function AUTOMATICALLY CLOSES file handles passed to it, which causes temporary file handles
            to be DELETED from memory and/or the /tmp folder. If we failed to do this, the server would run out of file
            handles and crash.
            ===========================================================================================================

            Accepts, validates, and prepares an uploaded image for processing using the frontend crop tool. This
            function is intended for use with avatar, hero, and background images. To post image files to the stream,
            use plant_media.engine.document.*

            :param guid: The stash guid to use for the item
            :param requester: The user making the request.
            :param filehandle: A file handle to the uploaded image
            :param formats: Accepted image formats
            :param resize_width: The x-pixels dimension of the cropping canvas in the user's browser
            :param resize_height: The y-pixels dimension of the cropping canvas in the user's browser
            :param min_x: Minimum acceptable source image x-pixels dimension. Images below this limit will be rejected.
            :param min_y: Minimum acceptable source image y-pixels dimension. Images below this limit will be rejected.

            :return: dict

            .. code-block:: python
                {
                    'x': 320,                                # x-value of in-browser cropping image
                    'y': 240,                                # y-value of in-browser cropping image
                    'guid': 'MDzd6Yyow5HVqUyv',              # 16-character alphanumeric GUID for stashed image
                    'file': 'MDzd6Yyow5HVqUyv_BROWSER.jpg',  # Image filename

                    # Full path to file
                    'file': '/mnt/cdn3/stash/pzaQj1meYI2NKUgi_BROWSER.jpg'
                }

            TYPICAL USE
            =====================================================================================================

            GIVEN:

                a) A file handle provided by a POST request, containing an image that is 426 pixels wide
                   and 749 pixels tall
                b) A cropping-canvas size of 700 pixels wide and 400 pixels high
                c) A minimum acceptable image size of 128 pixels wide and 128 pixels high

                .. code-block:: python

                    stash_image(

                        request = <Request>,
                        filehandle = <FileHandle>,
                        resize_width = 700,
                        resize_height = 400,
                        min_x = 128,
                        min_y = 128
                    )

            RETURNS:

                The function will generate a 227 pixel wide by 400 pixel high BROWSER image and a 426 pixel wide by 749
                pixel high MASTER image, and store both files to the scratch folder. The files will persist in the scratch
                folder until they expire (1800 seconds) or they are deleted by another process.

                .. code-block:: python

                    {
                        'x': 227,
                        'y': 400,
                        'guid': 'pzaQj1meYI2NKUgi',
                        'file': 'pzaQj1meYI2NKUgi_BROWSER.jpg',
                        'path': '/mnt/cdn3/scratch/pzaQj1meYI2NKUgi_BROWSER.jpg'
                    }

        """

        # Validate Params
        # ===============================================================================

        # Resize Width
        # --------------------------------

        try:
            resize_width = int(resize_width)

        except:

            filehandle.close()
            raise HeliosException(desc='resize_width is not an int', code='resize_width_not_int')

        # if resize_width < min_x:
        #
        #     filehandle.close()
        #     raise HeliosException(desc='resize_width must be >= min_x', code='invalid_resize_width')

        # Resize Height
        # --------------------------------

        try:
            resize_height = int(resize_height)

        except:

            filehandle.close()
            raise HeliosException(desc='resize_height is not an int', code='resize_height_not_int')

        # if resize_height < min_y:
        #
        #     filehandle.close()
        #     raise HeliosException(desc='resize_height must be >= min_y', code='invalid_resize_height')

        # Read-in the image file
        # ===============================================================================

        start = time.time()

        try:
            temp = Image(file=filehandle)

        except:

            filehandle.close()
            raise HeliosException(desc='Invalid file handle', code='invalid_filehandle')

        # We explicitly analyze the file using ImageMagick via Wand because we cannot trust the user. File
        # extensions are easily changed, content-encoding types can be arbitrarily set, and 'fingerprint strings'
        # are easily spoofed. ImageMagick loads the entire file and validates everything at the binary level
        # before trying to process it. If something is wrong, it *will* catch it.

        if temp.format not in formats:
            filehandle.close()
            raise HeliosException(desc='Invalid original image file format', code='invalid_file_format')

        # Handle animated GIF's by creating a new Image out of the first frame (otherwise Wand will generate
        # potentially hundreds of images, one per frame)

        if temp.animation:

            img = Image(temp.sequence[0])
            temp.close()
            temp = img

        # Handle PDF's and other multi-frame non-animated image types. ImageMagick INCORRECTLY IDENTIFIES
        # PDF files as image type PNG

        elif len(temp.sequence) > 1:

            img = Image(temp.sequence[0])
            temp.close()
            temp = img

        # Validate the source image is large enough
        # ===============================================================================

        temp_x = temp.width
        temp_y = temp.height

        if (temp_x < min_x) or (temp_y < min_y):
            filehandle.close()

            raise HeliosException(

                desc='Source file was smaller than minimum required dimensions',
                code='below_min_dimensions'
            )

        # Generate BROWSER image file
        # ===============================================================================

        if (temp_x <= resize_width) and (temp_y <= resize_height):

            browser_image_x = temp_x
            browser_image_y = temp_y

        else:

            fit_result = fit_dimensions(

                image_x=temp_x,
                image_y=temp_y,
                target_x=resize_width,
                target_y=resize_height
            )

            browser_image_x = fit_result['x']
            browser_image_y = fit_result['y']

        # Create a stash record for the object
        # ===============================================================================

        StashedAsset.objects.create(

            guid=guid,
            requester_id=requester.id,
            engine=AssetEngine.TYPE_IMAGE_CROP,
            worker='BROWSER_IMAGE',
            state=AssetEngine.STATE_STARTED,
            input={},
            progress=0,
            created=datetime.now(),
            updated=datetime.now()
        )

        # Create browser image
        # ===============================================================================

        # Wand throws warnings instead of exceptions if we try to load or manipulate a corrupted file. Setting
        # warnings.filterwarnings to 'error' causes warnings to be raised as exceptions

        prev_warnings_setting = warnings.filterwarnings
        warnings.filterwarnings('error')

        try:

            browser_image = temp.clone()

            # Its important to convert to JPG before doing any operations, because for many images this
            # will increase the image to a 24-bit color space, which produces better results when filtering

            browser_image.convert('jpeg')

            # A JPG compression level of 90 seems to be optimum for our thumbnail sizes. It has almost no effect
            # on the size of images under 96 pixels, but at the 512 pixel size it reduces a typical file size from
            # 160KB to 95KB

            browser_image.compression_quality = 90

            browser_image.resize(

                # See: http://www.dylanbeattie.net/magick/filters/result.html
                width=browser_image_x,
                height=browser_image_y,
                filter='lanczos',
                blur=0.9
            )

        except Warning:

            # If wand raises an exception at this point, the image file is corrupt. We set it to failed
            # to force the user to upload a new file.

            filehandle.close()

            with transaction.atomic():

                asset = StashedAsset.objects.select_for_update().get(guid=guid, worker='BROWSER_IMAGE')

                asset.state = AssetEngine.STATE_FAILED
                asset.updated = datetime.now()
                asset.output = {'desc': 'Corrupt original image file'}

                asset.save()

            raise HeliosException(desc='Corrupt original image file', code='corrupt_original_image_file')

        finally:

            # Restore previous system warnings setting
            warnings.filterwarnings = prev_warnings_setting

        try:
            browser_image_filename = "{}{}_BROWSER.jpg".format(settings.H1_STASH_ROOT, guid)
            browser_image.save(filename=browser_image_filename)

        except:

            filehandle.close()

            # If there's a disk error, set the item to failed. Note that this is kind of a big deal. It
            # probably means someone disconnected a drive.

            with transaction.atomic():

                asset = StashedAsset.objects.select_for_update().get(guid=guid, worker='BROWSER_IMAGE')

                asset.state = AssetEngine.STATE_FAILED
                asset.updated = datetime.now()
                asset.output = {'desc': 'Error writing browser image', 'browser_image': browser_image_filename}

                asset.save()

            raise HeliosException(desc='Error writing browser image to disk', code='error_writing_browser_image')

        # Generate WORKING image file
        # ===============================================================================

        # Wand throws warnings instead of exceptions if we try to load or manipulate a corrupted file. Setting
        # warnings.filterwarnings to 'error' causes warnings to be raised as exceptions

        prev_warnings_setting = warnings.filterwarnings
        warnings.filterwarnings('error')

        if (temp_x <= cls.MAX_INTERNAL_IMAGE_SIZE) and (temp_y <= cls.MAX_INTERNAL_IMAGE_SIZE):

            original_image_x = temp_x
            original_image_y = temp_y

        else:

            fit_result = fit_dimensions(

                image_x=temp_x,
                image_y=temp_y,
                target_x=cls.MAX_INTERNAL_IMAGE_SIZE,
                target_y=cls.MAX_INTERNAL_IMAGE_SIZE
            )

            original_image_x = fit_result['x']
            original_image_y = fit_result['y']

        try:

            # SECURITY IMPLICATIONS. See browser_image code above.
            original_image = temp.clone()
            original_image.convert('jpeg')
            original_image.compression_quality = 90

            original_image.resize(

                width=original_image_x,
                height=original_image_y,
                filter='lanczos',
                blur=0.9
            )

        except Warning:

            # If wand raises an exception at this point, the image file is corrupt. We set it to failed
            # to force the user to upload a new file.

            filehandle.close()

            with transaction.atomic():

                asset = StashedAsset.objects.select_for_update().get(guid=guid, worker='BROWSER_IMAGE')

                asset.state = AssetEngine.STATE_FAILED
                asset.updated = datetime.now()
                asset.output = {'desc': 'Corrupt original image file'}

                asset.save()

            raise HeliosException(desc='Corrupt original image file', code='corrupt_original_image_file')

        finally:

            # Restore previous system warnings setting
            warnings.filterwarnings = prev_warnings_setting

        try:
            original_image_filename = "{}{}_ORIGINAL.jpg".format(settings.H1_STASH_ROOT, guid)
            original_image.save(filename=original_image_filename)

        except:

            # If there's a disk error, set the item to failed. Note that this is kind of a big deal. It
            # probably means someone disconnected a drive.

            filehandle.close()

            with transaction.atomic():

                asset = StashedAsset.objects.select_for_update().get(guid=guid, worker='BROWSER_IMAGE')

                asset.state = AssetEngine.STATE_FAILED
                asset.updated = datetime.now()
                asset.output = {'desc': 'Error writing working image', 'original_image': original_image_filename}

                asset.save()

            raise HeliosException(desc='Error writing original_image file to disk', code='error_writing_original_image')

        temp.close()
        filehandle.close()

        # Update asset with processed image data
        # ===============================================================================

        with transaction.atomic():

            asset = StashedAsset.objects.select_for_update().get(guid=guid, worker='BROWSER_IMAGE')

            asset.state = AssetEngine.STATE_DONE
            asset.updated = datetime.now()

            asset.output = {

                'original_image_x': original_image_x,
                'original_image_y': original_image_y,
                'browser_image_x': browser_image_x,
                'browser_image_y': browser_image_y,
                'browser_image_filename': browser_image_filename,
                'original_image_filename': original_image_filename,
                'browser_image_time': (time.time() - start)
            }

            asset.save()

        return {

            'original_image_x': original_image_x,
            'original_image_y': original_image_y,
            'x': browser_image_x,
            'y': browser_image_y,
            'guid': guid,
            'file': guid + '_BROWSER.jpg',
            'path': browser_image_filename
        }

    @classmethod
    def crop_item(cls, guid, x1, y1, x2, y2, aspect_ratio_x, aspect_ratio_y, tolerance=0.01):
        """
            Crops a stashed image created with silo_media.engine.image.main.stash_image() to the specified
            coordinates and saves the modified file back to the stash.

            * Coordinates are based on the small BROWSER image but are scaled to the full-size MASTER image.
            * Coordinates emulate Python array slicing: cropping from 100 to 201 will produce a 100 pixel result.
            * The cropped file will have the same base GUID as the source image

            :param guid: guid of the stashed image to crop

            :param x1: x-value of the upper-left coordinate to crop from
            :param y1: y-value of the upper-left coordinate to crop from
            :param x2: x-value of the lower-right coordinate to crop to
            :param y2: y-value of the lower-right coordinate to crop to

            :param aspect_ratio_x: x-pixels value used to calculate cropped image aspect ratio
            :param aspect_ratio_y: y-pixels value used to calculate cropped image aspect ratio

            :param tolerance: If the aspect ratio defined by ((x2 - x1) / (y2 - y1)) deviates from the aspect ratio
                   defined by (aspect_ratio_x / aspect_ratio_y) by more than tolerance, an exception will be raised.

                   1) Tolerance should never be 0 due to floating-point rounding errors.
                   2) When used for generating Profile images, from sys_util.image.thumbnail.create_child_images()
                      will re-crop the image generated by this function to precisely match the aspect ratio of the
                      given image type (avatar, hero, etc)

            :return: dict

            .. code-block:: python
                {
                    'x': 320,                                # x-value of cropped image
                    'y': 240,                                # y-value of cropped image
                    'guid': 'MDzd6Yyow5HVqUyv',              # 16-character alphanumeric GUID for stashed image
                    'file': 'MDzd6Yyow5HVqUyv_CROPPED.jpg',  # Cropped image filename

                    # Full path to file
                    'file': '/mnt/cdn3/stash/MDzd6Yyow5HVqUyv_CROPPED.jpg'
                }

            TYPICAL USE
            =====================================================================================================

            GIVEN:

                a) A stashed image with GUID 'UZrvAY7Fxn145Bh6' that has a BROWSER image size of 700 pixels
                   wide and 400 pixels tall, and a MASTER image size of 1400 pixels wide and 800 pixels tall
                b) Upper-left cropping coordinate of (x1=100, y1=50)
                c) Lower-left cropping coordinate of (x2=601, y2=351)

                .. code-block:: python

                    crop_stashed_image(

                        guid = 'UZrvAY7Fxn145Bh6',
                        x1 = 100,
                        y1 = 50,
                        x2 = 601,
                        y2 = 351
                    )

            RETURNS:

                The supplied coordinates represent a 500 pixel wide by 300 pixel tall image cropped from the BROWSER
                image. Because the MASTER image in this example is exactly twice the size of the BROWSER image, the
                CROPPED image will be 1000 pixels wide and 600 pixels tall. Upon successfully creating the cropped
                image, the function WILL DELETE THE BROWSER IMAGE AND THE MASTER IMAGE FROM THE STASH.

                .. code-block:: python
                    {
                        'x': 1000,                               # x-value of cropped image
                        'y': 600,                                # y-value of cropped image
                        'guid': 'UZrvAY7Fxn145Bh6',              # 16-character alphanumeric GUID for stashed image
                        'file': 'UZrvAY7Fxn145Bh6_CROPPED.jpg',  # Cropped image filename

                        # Full path to file
                        'file': '/mnt/cdn3/stash/UZrvAY7Fxn145Bh6_CROPPED.jpg'
                    }

        """

        assert ((aspect_ratio_x > 0) and (aspect_ratio_y > 0))
        assert (tolerance > 0.0)

        # Validate input parameters
        # ===============================================================================

        try:
            guid = str(guid)

        except:
            raise HeliosException(desc='guid is not a string', code='guid_not_string')

        if len(guid) != 16:
            raise HeliosException(desc='guid is not valid', code='invalid_guid')

        try:
            x1 = float(x1)
            y1 = float(y1)
            x2 = float(x2)
            y2 = float(y2)

        except:

            # This can't be done as a loop because Python doesn't have dynamic variable creation in classes,
            # and copy-pasting 4 boilerplate try-catch blocks makes the code too cluttered

            raise HeliosException(desc='one or more coords is not an int', code='crop_coords_not_int')

        if (x1 < 0) or (y1 < 0) or (x2 <= x1) or (y2 <= y1):  # This statement also traps (x2 <= 0) and (y2 <= 0)

            raise HeliosException(

                desc='Invalid crop coordinates: x2 must be > x1, y2 must be > y1, and no coordinate can be negative',
                code='invalid_crop_coords'
            )

        cropped_ratio = ((x2 - x1) / (y2 - y1))
        required_ratio = (aspect_ratio_x / aspect_ratio_y)

        if abs(cropped_ratio - required_ratio) > tolerance:
            raise HeliosException(

                desc='Invalid aspect ratio. Cropped: {}, Required: {}'.format(str(cropped_ratio), str(required_ratio)),
                code='invalid_aspect_ratio'
            )

        # Fetch the stashed item from the DB
        # ===============================================================================

        start = time.time()

        with transaction.atomic():

            asset = StashedAsset.objects.select_for_update().filter(guid=guid).first()

            if not asset:
                raise HeliosException(desc='Requested guid does not exist', code='nonexistent_guid')

            if asset.engine != AssetEngine.TYPE_IMAGE_CROP:
                raise HeliosException(desc='Incompatible item type', code='incompatible_item_type')

            if asset.state == AssetEngine.STATE_FAILED:
                raise HeliosException(desc='Requested guid failed processing', code='guid_failed')

            if (asset.state != AssetEngine.STATE_DONE) or (asset.worker != 'BROWSER_IMAGE'):
                raise HeliosException(desc='Requested guid is locked by another worker', code='guid_locked')

            # If we were able to grab the item, immediately mark it as STATE_STARTED to block
            # other threads. Normally you would add a thread id to the lock and have a system that
            # checks if threads are still alive, but a simple "something is using this item right now"
            # flag is sufficient for now.

            asset.state = AssetEngine.STATE_STARTED
            asset.worker = 'PROFILE_IMAGE'

            # Move the results of the previous worker into the 'input' field

            asset.input = {

                'original_image_x': asset.output['original_image_x'],
                'original_image_y': asset.output['original_image_y'],
                'original_image_filename': asset.output['original_image_filename'],

                'browser_image_x': asset.output['browser_image_x'],
                'browser_image_y': asset.output['browser_image_y'],
                'browser_image_filename': asset.output['browser_image_filename'],
                'browser_image_time': asset.output['browser_image_time']
            }

            asset.updated = datetime.now()

            asset.save()

        # Process the item
        # ===============================================================================
        # NOTE: queries below do not need to use transactions. We have already locked the item from other
        # threads by setting asset.state_thumbgen = AssetEngine.STATE_STARTED, and we are only processing
        # with one thread (other engines are multi-threaded)

        try:
            working_image = Image(filename=asset.input['original_image_filename'])

            working_x = working_image.width
            working_y = working_image.height

        except:

            # If there's a disk error, set the item to failed. Note that this is kind of a big deal. It
            # probably means someone disconnected a drive.

            with transaction.atomic():

                asset = StashedAsset.objects.select_for_update().get(guid=guid, worker='PROFILE_IMAGE')

                asset.updated = datetime.now()
                asset.output = {'desc': 'Error reading original_image file'}
                asset.state = AssetEngine.STATE_FAILED
                asset.save()

            raise HeliosException(desc='Missing original_thumb file', code='missing_original_thumb_file')

        # Snap coordinates
        # ===============================================================================

        if x1 < 0.5:
            x1 = 0

        if y1 < 0.5:
            y1 = 0

        if x2 > asset.input['browser_image_x']:
            x2 = asset.input['browser_image_x']

        if y2 > asset.input['browser_image_y']:
            y2 = asset.input['browser_image_y']

        # Generate cropped image file
        # ===============================================================================

        scale = working_x / asset.input['browser_image_x']

        # The int(), min(), and max() calls handle floating-point math errors, ensuring that the results are
        # integer values and within the bounds of the image.

        crop_x1 = int(max(0, round((x1 * scale))))
        crop_y1 = int(max(0, round((y1 * scale))))

        crop_x2 = int(min(round((x2 * scale)), working_x))
        crop_y2 = int(min(round((y2 * scale)), working_y))

        # Wand throws warnings instead of exceptions if we try to load or manipulate a corrupted file. Setting
        # warnings.filterwarnings to 'error' causes warnings to be raised as exceptions

        prev_warnings_setting = warnings.filterwarnings
        warnings.filterwarnings('error')

        try:
            # Note that we don't need to convert to JPG format and set compression quality here, because that was
            # already done when the working image was stashed. The cropped_image inherits these settings.

            cropped_image = working_image.clone()
            cropped_image.crop(crop_x1, crop_y1, crop_x2, crop_y2)

        except Warning:

            # If wand raises an exception at this point, the image file is corrupt. We set it to failed
            # to force the user to upload a new file.

            asset.updated = datetime.now()
            asset.output = {'desc': 'Corrupt original_image file'}
            asset.state = AssetEngine.STATE_FAILED
            asset.save()

            raise HeliosException(desc='Corrupt original_thumb file', code='corrupt_original_thumb_file')

        finally:

            # Restore previous system warnings setting
            warnings.filterwarnings = prev_warnings_setting

        cropped_image_filename = "{}{}_CROPPED.jpg".format(settings.H1_STASH_ROOT, guid)

        # NOTE: We allow the user to repeatedly generate cropped files from the MASTER image until
        # they get one that they like. This is why we delete the current cropped image file, if it exists.

        try:
            os.remove(cropped_image_filename)

        except OSError:
            pass

        try:
            cropped_image.save(filename=cropped_image_filename)

        except:

            # If there's a disk error, set the item to failed. Note that this is kind of a big deal. It
            # probably means someone disconnected a drive.

            asset.updated = datetime.now()
            asset.output = {'desc': 'Error writing CROPPED file to disk', 'filename': cropped_image_filename}
            asset.state = AssetEngine.STATE_FAILED
            asset.save()

            raise HeliosException(desc='Error writing CROPPED file to disk', code='error_writing_cropped_file')

        working_image.close()

        # Update asset to release our lock
        # ===============================================================================

        asset.updated = datetime.now()

        asset.output = {

            'original_image_x': asset.output['original_image_x'],
            'original_image_y': asset.output['original_image_y'],
            'original_image_filename': asset.output['original_image_filename'],

            'browser_image_x': asset.output['browser_image_x'],
            'browser_image_y': asset.output['browser_image_y'],
            'browser_image_filename': asset.output['browser_image_filename'],
            'browser_image_time': asset.output['browser_image_time'],

            'cropped_image': cropped_image_filename,
            'cropped_image_x': crop_x2 - crop_x1,
            'cropped_image_y': crop_y2 - crop_y1,
            'cropped_image_time': (time.time() - start)
        }

        asset.state = AssetEngine.STATE_DONE
        asset.save()

        return {

            'x': crop_x2 - crop_x1,
            'y': crop_y2 - crop_y1,
            'guid': guid,
            'file': guid + '_CROPPED.jpg',
            'path': cropped_image_filename
        }
