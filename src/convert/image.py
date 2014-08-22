#!/usr/bin/env python

# Copyright (C) 2010  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from PIL import Image, ImageDraw


class ImageFlags:
    def __init__(self):
        pass

    Orient = 1 << 0
    Resize = 1 << 1
    Frame = 1 << 2
    Quantize = 1 << 3


class KindleData:

    def __init__(self):
        pass

    Palette4 = [
        0x00, 0x00, 0x00,
        0x55, 0x55, 0x55,
        0xaa, 0xaa, 0xaa,
        0xff, 0xff, 0xff
    ]

    Palette15a = [
        0x00, 0x00, 0x00,
        0x11, 0x11, 0x11,
        0x22, 0x22, 0x22,
        0x33, 0x33, 0x33,
        0x44, 0x44, 0x44,
        0x55, 0x55, 0x55,
        0x66, 0x66, 0x66,
        0x77, 0x77, 0x77,
        0x88, 0x88, 0x88,
        0x99, 0x99, 0x99,
        0xaa, 0xaa, 0xaa,
        0xbb, 0xbb, 0xbb,
        0xcc, 0xcc, 0xcc,
        0xdd, 0xdd, 0xdd,
        0xff, 0xff, 0xff,
    ]

    Palette15b = [
        0x00, 0x00, 0x00,
        0x11, 0x11, 0x11,
        0x22, 0x22, 0x22,
        0x33, 0x33, 0x33,
        0x44, 0x44, 0x44,
        0x55, 0x55, 0x55,
        0x77, 0x77, 0x77,
        0x88, 0x88, 0x88,
        0x99, 0x99, 0x99,
        0xaa, 0xaa, 0xaa,
        0xbb, 0xbb, 0xbb,
        0xcc, 0xcc, 0xcc,
        0xdd, 0xdd, 0xdd,
        0xee, 0xee, 0xee,
        0xff, 0xff, 0xff,
    ]

    Palette16 = [
        0x00, 0x00, 0x00,
        0x11, 0x11, 0x11,
        0x22, 0x22, 0x22,
        0x33, 0x33, 0x33,
        0x44, 0x44, 0x44,
        0x55, 0x55, 0x55,
        0x66, 0x66, 0x66,
        0x77, 0x77, 0x77,
        0x88, 0x88, 0x88,
        0x99, 0x99, 0x99,
        0xaa, 0xaa, 0xaa,
        0xbb, 0xbb, 0xbb,
        0xcc, 0xcc, 0xcc,
        0xdd, 0xdd, 0xdd,
        0xee, 0xee, 0xee,
        0xff, 0xff, 0xff,
    ]

    Profiles = {
        'Kindle 1': ((600, 800), Palette4),
        'Kindle 2': ((600, 800), Palette15a),
        'Kindle 3': ((600, 800), Palette15a),
        'Kindle 4': ((600, 800), Palette15b),
        'Kindle 5': ((758, 1024), Palette16),
        'Kindle DX': ((824, 1200), Palette15a),
        'Kindle DXG': ((824, 1200), Palette15a)
    }


def quantize_image(image, palette):
    colors = len(palette) / 3
    if colors < 256:
        palette += palette[:3] * (256 - colors)

    pal_img = Image.new('P', (1, 1))
    pal_img.putpalette(palette)

    return image.quantize(palette=pal_img)


def resize_image(image, size):
    width_dev, height_dev = size
    width_img, height_img = image.size

    if width_img <= width_dev and height_img <= height_dev:
        return image

    ratio_img = float(width_img) / float(height_img)
    ratio_width = float(width_img) / float(width_dev)
    ratio_height = float(height_img) / float(height_dev)

    if ratio_width > ratio_height:
        width_img = width_dev
        height_img = int(width_dev / ratio_img)
    elif ratio_width < ratio_height:
        height_img = height_dev
        width_img = int(height_dev * ratio_img)
    else:
        width_img, height_img = size

    return image.resize((width_img, height_img), Image.ANTIALIAS)


def format_image(image):
    if image.mode == 'RGB':
        return image
    return image.convert('RGB')


def orient_image(image, size):
    width_dev, height_dev = size
    width_img, height_img = image.size

    if (width_img > height_img) != (width_dev > height_dev):
        return image.rotate(90, Image.BICUBIC, True)

    return image


def frame_image(image, foreground, background, size):
    width_dev, height_dev = size
    width_img, height_img = image.size

    paste_pt = (
        max(0, (width_dev - width_img) / 2),
        max(0, (height_dev - height_img) / 2)
    )

    corner1 = (
        paste_pt[0] - 1,
        paste_pt[1] - 1
    )

    corner2 = (
        paste_pt[0] + width_img + 1,
        paste_pt[1] + height_img + 1
    )

    image_bg = Image.new(image.mode, size, background)
    image_bg.paste(image, paste_pt)

    draw = ImageDraw.Draw(image_bg)
    draw.rectangle([corner1, corner2], outline=foreground)

    return image_bg


def convert_image(source, target, device, flags):
    try:
        size, palette = KindleData.Profiles[device]
    except KeyError:
        raise RuntimeError('Unexpected output device %s' % device)

    try:
        image = Image.open(source)
    except IOError:
        raise RuntimeError('Cannot read image file %s' % source)

    image = format_image(image)
    if flags & ImageFlags.Orient:
        image = orient_image(image, size)
    if flags & ImageFlags.Resize:
        image = resize_image(image, size)
    if flags & ImageFlags.Frame:
        image = frame_image(image, tuple(palette[:3]), tuple(palette[-3:]), size)
    if flags & ImageFlags.Quantize:
        image = quantize_image(image, palette)

    try:
        image.save(target)
    except IOError:
        raise RuntimeError('Cannot write image file %s' % target)
