#  -*- coding: UTF8 -*-

from __future__ import division

import newrelic.agent


def parse_cropper_form(request, browser_x, browser_y):
    """
        Ingests image cropping parameters from a POST request, returning the cropping coordinates for
        a User or Org profile image

        :param request: the current request
        :param browser_x: x-pixels measurement of the image that the crop coordinates are referenced against
        :param browser_y: y-pixels measurement of the image that the crop coordinates are referenced against

        :return: dict of cropping coordinates
    """

    resize_width = request.POST.get('resize_width')
    resize_height = request.POST.get('resize_height')
    container_x = request.POST.get('container_x')
    container_y = request.POST.get('container_y')

    x1 = request.POST.get('x1')
    y1 = request.POST.get('y1')
    x2 = request.POST.get('x2')
    y2 = request.POST.get('y2')

    newrelic.agent.add_custom_parameter('resize_width', resize_width)
    newrelic.agent.add_custom_parameter('resize_height', resize_height)
    newrelic.agent.add_custom_parameter('container_x', container_x)
    newrelic.agent.add_custom_parameter('container_y', container_y)
    newrelic.agent.add_custom_parameter('x1', x1)
    newrelic.agent.add_custom_parameter('y1', y1)
    newrelic.agent.add_custom_parameter('x2', x2)
    newrelic.agent.add_custom_parameter('y2', y2)

    resize_width_clean = abs(float(resize_width))
    resize_height_clean = abs(float(resize_height))
    container_x_clean = abs(float(container_x))
    container_y_clean = abs(float(container_y))

    if container_x_clean > resize_width_clean:

        x_shift = (container_x_clean - resize_width_clean) / 2
        y_shift = 0

    else:
        x_shift = 0
        y_shift = (container_y_clean - resize_height_clean) / 2

    # Due to floating point rounding errors, small values close to zero (0.00000000000000000002) will
    # sometimes flip negative. We flip these small values positive again to prevent the profile asset
    # crop functions from raising an exception.

    x1_offset = abs(float(x1) - x_shift)
    y1_offset = abs(float(y1) - y_shift)
    x2_offset = abs(float(x2) - x_shift)
    y2_offset = abs(float(y2) - y_shift)

    x1_pct = x1_offset / resize_width_clean
    y1_pct = y1_offset / resize_height_clean
    x2_pct = x2_offset / resize_width_clean
    y2_pct = y2_offset / resize_height_clean

    x1_crop = x1_pct * browser_x
    y1_crop = y1_pct * browser_y
    x2_crop = x2_pct * browser_x
    y2_crop = y2_pct * browser_y

    # This block is used to debug the platform every time something goes wrong with
    # the frontend JS cropper
    # ================================================================================

    # print 'stash_guid: ' + stash_guid
    # print 'resize_width: ' + str(resize_width)
    # print 'resize_height: ' + str(resize_height)
    # print 'resize_width_clean: ' + str(resize_width_clean)
    # print 'resize_height_clean: ' + str(resize_height_clean)
    # print 'x1: ' + str(x1)
    # print 'y1: ' + str(y1)
    # print 'x2: ' + str(x2)
    # print 'y2: ' + str(y2)
    # print 'x_shift: ' + str(x_shift)
    # print 'y_shift: ' + str(y_shift)
    # print 'x1_offset: ' + str(x1_offset)
    # print 'y1_offset: ' + str(y1_offset)
    # print 'x2_offset: ' + str(x2_offset)
    # print 'y2_offset: ' + str(y2_offset)
    # print 'x1_pct: ' + str(x1_pct)
    # print 'y1_pct: ' + str(y1_pct)
    # print 'x2_pct: ' + str(x2_pct)
    # print 'y2_pct: ' + str(y2_pct)
    # print 'browser_x: ' + str(preview_data['browser_x'])
    # print 'browser_y: ' + str(preview_data['browser_y'])
    # print 'x1_crop: ' + str(x1_crop)
    # print 'y1_crop: ' + str(y1_crop)
    # print 'x2_crop: ' + str(x2_crop)
    # print 'y2_crop: ' + str(y2_crop)

    return {

        'x1': x1_crop,
        'y1': y1_crop,
        'x2': x2_crop,
        'y2': y2_crop
    }
