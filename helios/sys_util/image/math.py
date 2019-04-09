#  -*- coding: UTF8 -*-

from __future__ import division


def zoom_dimensions(image_x, image_y, min_x, min_y, max_x, max_y):
    """
        Given any possible combination of source image dimensions and max/min target image dimensions,
        calculates the X and Y values that the source image must be scaled to and the (X1,Y1), (X2,Y2)
        coordinates the scaled target image must be cropped to in order to satisfy the supplied constraints.

        To fit an image to an arbitrary bounding-box without cropping it, use math.fit_dimensions()

        :param image_x: source image x-pixels (width)
        :param image_y: source image y-pixels (height)
        :param min_x: minimum acceptable target image x-pixels
        :param min_y: minimum acceptable target image y-pixels
        :param max_x: maximum acceptable target image x-pixels
        :param max_y: maximum acceptable target image y-pixels

        :return: dict

        .. code-block:: python
            {
                'scale': {
                    'x': 125,   # x-value to scale target image to
                    'y': 60     # y-value to scale target image to
                },
                'crop': {
                    'x1': 20,   # x1 coordinate to crop scaled target image to
                    'y1': 0,    # y1 coordinate to crop scaled target image to
                    'x2': 100,  # x2 coordinate to crop scaled target image to
                    'y2': 58    # y2 coordinate to crop scaled target image to
                }
            }

        TYPICAL USE
        =====================================================================================================

        GIVEN:

            a) An input image that is 275 pixels WIDE and 94 pixels HIGH
            b) A desired thumbnail size of 128 pixels WIDE and 96 pixels HIGH that must be COMPLETELY filled,
               DISCARDING part of the source image if necessary

            .. code-block:: python

                zoom_dimensions(
                    image_x = 275,
                    image_y = 94,
                    min_x = 128,
                    min_y = 96,
                    max_x = 128,
                    max_y = 96
                )

        RETURNS:

            Regardless of whether the source image is larger or smaller than the target image, the function
            will return the correct scale and crop parameters.

            .. code-block:: python

                {
                    'scale': {
                        'x': 281,
                        'y': 96,
                    },
                    'crop': {
                        'x1': 77,
                        'y1': 0,
                        'x2': 205,
                        'y2': 96
                    }
                }

        YOU MUST:

            a) Scale the target image to 281 pixels WIDE and 96 pixels HIGH
            b) Crop the scaled target image from coordinates (x=77,y=0) to (x=205,y=96) to produce final result

    """

    # If necessary, scale the image so it meets the min_x and min_y parameters

    if image_x < min_x:
        scale_factor = min_x / image_x
        image_x = round(image_x * scale_factor)
        image_y = round(image_y * scale_factor)

    if image_y < min_y:
        scale_factor = min_y / image_y
        image_x = round(image_x * scale_factor)
        image_y = round(image_y * scale_factor)

    # If the image exceeds *both* the max_x and max_y parameters, scale the image so that the dimension
    # closest to its max value parameter meets the max value parameter

    if (image_x > max_x) and (image_y > max_y):
        ratio_x = image_x / max_x
        ratio_y = image_y / max_y

        scale_factor = min(ratio_x, ratio_y)

        image_x = round(image_x / scale_factor)
        image_y = round(image_y / scale_factor)

    # Calculate the crop parameters

    mask_x = min(max_x, image_x)
    crop_x1 = round((image_x - mask_x) / 2)
    crop_x2 = crop_x1 + mask_x

    mask_y = min(max_y, image_y)
    crop_y1 = round((image_y - mask_y) / 2)
    crop_y2 = crop_y1 + mask_y

    return {

        'scale': {

            'x': int(image_x),
            'y': int(image_y)
        },

        'crop': {

            'x1': int(crop_x1),
            'y1': int(crop_y1),
            'x2': int(crop_x2),
            'y2': int(crop_y2)
        }
    }


def fit_dimensions(image_x, image_y, target_x, target_y):
    """
        Given any possible combination of source image dimensions and max target image dimensions, calculates the
        X and Y values that the source image must be scaled to in order to cover the largest possible area within
        the target dimensions WITHOUT cropping the source image.

        To completely fill a bounding-box while cropping the source image if necessary, use math.zoom_dimensions()

        :param image_x: source image x-pixels (width)
        :param image_y: source image y-pixels (height)
        :param target_x: maximum acceptable target image x-pixels
        :param target_y: maximum acceptable target image y-pixels

        :return: dict

        .. code-block:: python
            {
                'x': 125,   # x-value to scale target image to
                'y': 60     # y-value to scale target image to
            }

        TYPICAL USE
        =====================================================================================================

        GIVEN:

            a) An input image that is 275 pixels WIDE and 94 pixels HIGH
            b) A bounding box that is 128 pixels WIDE and 320 pixels TALL that the source image must be scaled
               to fit within

            .. code-block:: python

                fit_dimensions(
                    image_x = 275,
                    image_y = 94,
                    target_x = 128,
                    target_y = 320
                )

        RETURNS:

            Regardless of whether the source image is larger or smaller than the target image, the function
            will return the correct scale and crop parameters.

            .. code-block:: python

                {
                    'x': 128,
                    'y': 43
                }

        YOU MUST:

            a) Scale the target image to 128 pixels WIDE and 43 pixels HIGH

    """

    scale = min((target_x / image_x), (target_y / image_y))

    return {

        'x': int(image_x * scale),
        'y': int(image_y * scale)
    }
