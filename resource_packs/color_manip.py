import enum
from functools import partial
import resource_packs.image_manipulation as images
import resource_packs.simple_converter as simple
from colorsys import rgb_to_hsv
import matplotlib.colors as matc
import numpy as np


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

blueh, blues, bluev = rgb_to_hsv(custom_r / 255.0, custom_g / 255.0, custom_b / 255.0)


def set_color(r, g, b):
    global blueh, bluel, blues, custom_r, custom_g, custom_b
    custom_r = r
    custom_g = g
    custom_b = b

    blueh, blues, bluev = rgb_to_hsv(custom_r / 255.0, custom_g / 255.0, custom_b / 255.0)


def set_custom(i):
    shape = i.shape
    rgb_arr = i[[0, 1, 2]].transpose((1, 2, 0))
    hsv_arr = matc.rgb_to_hsv(rgb_arr).transpose((2, 0, 1))
    hsv_arr[0] = np.full(shape[1:], blueh)
    r, g, b = matc.hsv_to_rgb(hsv_arr.transpose((1, 2, 0))).transpose((2, 0, 1))
    i[2] = r
    i[1] = g
    i[0] = b
    return i


class ColorPresets(enum.Enum):
    invert = partial(set_invert)
    grayscale = partial(set_grayscale)
    custom = partial(set_custom)


def convert(color_preset, to_convert, to_save):
    simple.convert(color_preset, to_convert, to_save)
