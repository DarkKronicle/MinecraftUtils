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
    rgb_arr = i[[0, 1, 2]].transpose((1, 2, 0)) / 255
    hsv_arr = matc.rgb_to_hsv(rgb_arr).transpose((2, 0, 1))
    hsv_arr[0] = np.full(shape[1:], blueh)
    r, g, b = matc.hsv_to_rgb(hsv_arr.transpose((1, 2, 0))).transpose((2, 0, 1))
    i[2] = r * 255
    i[1] = g * 255
    i[0] = b * 255
    return i


def set_shuffle(i):
    i = i.transpose((1, 2, 0))
    height, width, chan = i.shape
    i = i.reshape((-1, chan))
    if chan == 18:
        np.random.shuffle(i[i[3] > 0])
    else:
        np.random.shuffle(i)
    return i.reshape(height, width, chan).transpose((2, 0, 1))


def set_brightness(i, brightness):
    rgb_arr = i[[0, 1, 2]].transpose((1, 2, 0)) / 255
    hsv_arr = matc.rgb_to_hsv(rgb_arr).transpose((2, 0, 1))
    hsv_arr[2] = hsv_arr[2] * brightness
    hsv_arr[2, hsv_arr[2] > 1] = 1
    hsv_arr[2, hsv_arr[2] < 0] = 0
    r, g, b = matc.hsv_to_rgb(hsv_arr.transpose((1, 2, 0))).transpose((2, 0, 1))
    i[0] = r * 255
    i[1] = g * 255
    i[2] = b * 255
    return i


def set_hue(base, copy):
    # Grab the base HSV values
    base_rgb_arr = base[[0, 1, 2]].transpose((1, 2, 0)) / 255
    base_hsv_arr = matc.rgb_to_hsv(base_rgb_arr).transpose((2, 0, 1))

    # Grab the HSV values to edit
    rgb_arr = copy[[0, 1, 2]].transpose((1, 2, 0)) / 255
    hsv_arr = matc.rgb_to_hsv(rgb_arr).transpose((2, 0, 1))

    # Set the second to the first
    hsv_arr[0] = base_hsv_arr[0]
    hsv_arr[2] = (hsv_arr[2] + base_hsv_arr[2]) / 2
    hsv_arr[1] = (hsv_arr[1] + base_hsv_arr[1]) / 2
    r, g, b = matc.hsv_to_rgb(hsv_arr.transpose((1, 2, 0))).transpose((2, 0, 1))
    copy[0] = r * 255
    copy[1] = g * 255
    copy[2] = b * 255
    return copy


class ColorPresets(enum.Enum):
    invert = partial(set_invert)
    grayscale = partial(set_grayscale)
    custom = partial(set_custom)
    shuffle = partial(set_shuffle)


def convert(color_preset, to_convert, to_save):
    simple.convert(color_preset, to_convert, to_save)
