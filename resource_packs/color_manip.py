import enum
from functools import partial
import resource_packs.image_manipulation as images
import resource_packs.simple_converter as simple
from colorsys import rgb_to_hls, hls_to_rgb


def set_invert(i):
    i[0] = 255 - i[0]
    i[1] = 255 - i[1]
    i[2] = 255 - i[2]
    return i


def set_grayscale(i):
    gray = images.get_gray(i[0], i[1], i[2])
    i[0] = gray
    i[1] = gray
    i[2] = gray
    return i


custom_r = 2
custom_g = 72
custom_b = 233

blueh, bluel, blues = rgb_to_hls(custom_r / 255.0, custom_g / 255.0, custom_b / 255.0)


def set_color(r, g, b):
    global blueh, bluel, blues, custom_r, custom_g, custom_b
    custom_r = r
    custom_g = g
    custom_b = b

    blueh, bluel, blues = rgb_to_hls(custom_r / 255.0, custom_g / 255.0, custom_b / 255.0)


def set_custom(i):
    h1, l1, s1 = rgb_to_hls(i[0] / 255.0, i[1] / 255.0, i[2] / 255.0)
    h1 = blueh
    r, g, b = hls_to_rgb(h1, l1, s1)
    i[2] = int(r * 255)
    i[1] = int(g * 255)
    i[0] = int(b * 255)
    return i


class ColorPresets(enum.Enum):
    invert = partial(set_invert)
    grayscale = partial(set_grayscale)
    custom = partial(set_custom)


def convert(color_preset, to_convert, to_save):
    simple.convert(color_preset, to_convert, to_save)
