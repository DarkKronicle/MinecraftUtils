"""
Each pixel becomes a block texture.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from skimage import io


def progress(count, total, status='', bar_len=60):
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    fmt = '[%s] %s%s %s' % (bar, percents, '%', status)
    print('\b' * len(fmt), end='')  # clears the line
    sys.stdout.write(fmt)
    sys.stdout.flush()


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


def fix_channels(img, fix_invert=True, force_trans=-1):
    height, width, channels = img.shape
    pixels = np.int8(img.reshape(width, -1, channels))
    oned = []
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
    ar = ar.reshape(height, -1, channels)
    return ar


def main():
    palette = Path("./to_pixel/palette/")
    images = list(palette.glob("**/*.png"))
    transparent = np.zeros((16, 16, 4))
    colors = {}
    total_palet = len(images)
    current = 1
    for image in images:
        progress(current, total_palet, status='Setting up palette.')
        img = io.imread(image)
        dominant = get_average_color(img)
        colors[dominant] = img
        current += 1
    print("\n")

    to_switch = Path("./to_pixel/convert/")
    to_convert = list(to_switch.glob("**/*.png"))

    total_image = len(to_convert)
    total_start = 0

    problems = []

    for image in to_convert:
        try:
            total_start += 1
            image_name = str(image)
            img = io.imread(image_name)
            img = fix_channels(img, False)
            height, width, channels = img.shape
            if channels < 3:
                print("Not big enough channels")
                continue
            # pixels = np.int8(img.reshape(width, -1, channels))
            pixels = img
            img_rows = []
            img_stitched = None

            total = width * height
            current = 1

            for h in range(height):
                row_image = None
                progress(current, total,
                         status=f'Total: {total_start}/{total_image} Pixels: {current}/{total} - Converting {image}')
                for w in range(width):
                    p = pixels[h, w]
                    r = p[0] % 255
                    g = p[1] % 255
                    b = p[2] % 255
                    a = p[3] % 256
                    if a > 0:
                        color = r, g, b
                        to_get = min_color_diff(color, colors)
                        i = to_get[1]
                        i = i[0:16, 0:16]
                        i = fix_channels(i, force_trans=a)
                    else:
                        i = transparent
                    if row_image is None:
                        row_image = i
                    else:
                        row_image = np.concatenate((row_image, i), axis=1)
                    current += 1

                img_rows.append(row_image)

            for i in img_rows:
                if img_stitched is None:
                    img_stitched = i
                else:
                    img_stitched = np.concatenate((img_stitched, i), axis=0)

            folder = '/'.join(image_name.split("/")[0:-1]) + "/"
            to_save = Path(str("./to_pixel/done") + '/' + folder + image.name)
            to_save.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(to_save), img_stitched)
        except RuntimeError:
            problems.append(str(image))

    print(f"Done! Only problems:" + '\n'.join(problems))


if __name__ == '__main__':
    main()
