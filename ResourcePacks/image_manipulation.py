from colorsys import rgb_to_hls, hls_to_rgb

import numpy as np
import cv2
from skimage import io


def get_gray(r, g, b):
    return (0.3 * r) + (0.59 * g) + (0.11 * b)


def adjust_color_lightness(r, g, b, factor):
    h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    l = max(min(l * factor, 1.0), 0.0)
    r, g, b = hls_to_rgb(h, l, s)
    return int(r * 255), int(g * 255), int(b * 255)


def map_sat(r1, g1, b1, r2, g2, b2):
    h1, l1, s1 = rgb_to_hls(r1 / 255, g1 / 255, b1 / 255)
    h2, l2, s2 = rgb_to_hls(r2 / 255, g2 / 255, b2 / 255)
    r3, g3, b3 = hls_to_rgb(h2, l1, (s1 + s2) / 2)
    return int(r3 * 255), int(g3 * 255), int(b3 * 255)


def clamp(num, min_num, max_num):
    # 0 1 5
    if min_num <= num <= max_num:
        return num
    if min_num > num:
        return min_num
    if max_num < num:
        return max_num


def fix_channels(img, fix_invert=True, force_trans=-1):
    try:
        height, width, channels = img.shape
    except ValueError:
        height, width = img.shape
        channels = 1
    pixels = np.int8(img.reshape(width, -1, channels))
    oned = []
    if channels == 1:
        for w in range(width):
            for h in range(height):
                pixel = pixels[w, h] % 255
                if force_trans < 0:
                    force_trans = 255
                oned.extend([pixel, pixel, pixel, force_trans])
    else:
        for w in range(width):
            # oned = []
            for h in range(height):
                if channels == 4 and force_trans < 0:
                    pixel = pixels[w, h]
                    if fix_invert:
                        oned.extend([pixel[2] % 255, pixel[1] % 255, pixel[0] % 255, pixel[3] % 256])
                    else:
                        oned.extend([pixel[0] % 255, pixel[1] % 255, pixel[2] % 255, pixel[3] % 256])
                else:
                    pixel = pixels[w, h]
                    if force_trans < 0:
                        force_trans = 255
                    if fix_invert:
                        oned.extend([pixel[2] % 255, pixel[1] % 255, pixel[0] % 255, force_trans])
                    else:
                        oned.extend([pixel[0] % 255, pixel[1] % 255, pixel[2] % 255, force_trans])
        # last.append(oned)
    ar = np.array(oned)
    ar = ar.reshape(height, -1, 4)
    return ar


def get_dominant_color(filename):
    img = io.imread(filename)

    img = fix_channels(img)

    pixels = np.float32(img.reshape(-1, 4))

    n_colors = 3
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    dominant = palette[np.argmax(counts)]
    return dominant[0], dominant[1], dominant[2]


def get_average_color(img):
    img = img[:, :, :-1]
    height, width, channels = img.shape
    if channels < 2:
        return None
    average = img.mean(axis=0).mean(axis=0)
    r = average[0]
    g = average[1]
    if len(average) > 2:
        b = average[2]
    else:
        b = 0
    return r, g, b


# https://stackoverflow.com/questions/3565108/which-is-most-accurate-way-to-distinguish-one-of-8-colors/3565191#3565191
def rgb_to_ycc(r, g, b):  # http://bit.ly/1blFUsF
    y = .299 * r + .587 * g + .114 * b
    cb = 128 - .168736 * r - .331364 * g + .5 * b
    cr = 128 + .5 * r - .418688 * g - .081312 * b
    return y, cb, cr


def to_ycc(color):
    """ converts color tuples to floats and then to yuv """
    return rgb_to_ycc(*[x / 255.0 for x in color])


def color_dist(c1, c2):
    """ returns the squared euklidian distance between two color vectors in yuv space """
    return sum((a - b) ** 2 for a, b in zip(to_ycc(c1), to_ycc(c2)))


def min_color_diff(color_to_match, colors):
    """ returns the `(distance, color_name)` with the minimal distance to `colors`"""
    return min(  # overal best is the best match to any color:
        (color_dist(color_to_match, test), colors[test])  # (distance to `test` color, color name)
        for test in colors)