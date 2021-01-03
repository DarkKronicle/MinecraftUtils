"""
Each pixel becomes a block texture.
"""
import time
from colorsys import rgb_to_hls, hls_to_rgb
from pathlib import Path

import cv2
import numpy as np
from skimage import io
from tqdm import tqdm
from colorama import Fore

PALETTE_FILE = "./to_pixel/palette/cobblestone.png"
CONVERT_PATH = "./to_pixel/convert"
MAP_BRIGHTNESS = True
MAP_TRANSPARENCY = True
MAP_COLOR = True


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


def main():
    palette = fix_channels(io.imread(Path(PALETTE_FILE)), force_trans=255)
    # We want to get the width/height so that we don't get any index errors.
    p_height, p_width, _ = palette.shape
    transparent = np.zeros((4))

    to_switch = Path(CONVERT_PATH)
    to_convert = list(to_switch.glob("**/*.png"))

    total_start = 0

    problems = []
    pbar = tqdm(to_convert, unit=' images',
                bar_format="%s{l_bar}%s{bar}%s{r_bar}%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, Fore.RESET),
                smoothing=0.1)
    for image in pbar:
        try:
            pbar.set_description_str(f"Processing {image.name}")
            total_start += 1
            image_name = str(image)
            img = io.imread(image_name)
            # We want everything to be 4 channels.
            img = fix_channels(img, False)
            height, width, channels = img.shape
            if channels < 3:
                # This should never happend
                print("Not big enough channels")
                continue
            pixels = img
            img_rows = []
            img_stitched = None

            for h in range(height):
                row_image = None
                for w in range(width):
                    p = pixels[h, w]
                    if MAP_TRANSPARENCY:
                        a = p[3] % 256
                    else:
                        a = 255
                    if a > 0:
                        # If we don't copy, it actually gets modified by KEEP_BRIGHT.
                        i = palette[h % p_height, w % p_width].copy()
                        if MAP_BRIGHTNESS:
                            # We still want to somewhat know what we're looking at.
                            # Does slow it down, but it's not too bad.
                            gray = (0.3 * p[0]) + (0.59 * p[1]) + (0.11 * p[2])
                            brightness = clamp(1 + (0.5 - (gray / 255)) / 1, 0.7, 1.3)
                            new = adjust_color_lightness(i[0], i[1], i[2], brightness)
                            i[0] = new[0]
                            i[1] = new[1]
                            i[2] = new[2]
                        if MAP_COLOR:
                            new = map_sat(i[0], i[1], i[2], p[2], p[1], p[0])
                            i[0] = new[0]
                            i[1] = new[1]
                            i[2] = new[2]
                        i[3] = a
                    else:
                        i = transparent
                    i = i.reshape((1, 1, 4))
                    if row_image is None:
                        row_image = i
                    else:
                        row_image = np.concatenate((row_image, i), axis=1)

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
        except RuntimeError as e:
            # REMOVE IF DEBUGGING ^
            if isinstance(e, KeyboardInterrupt):
                return
            problems.append(str(image))

    print(f"Done! Only problems:" + '\n'.join(problems))


if __name__ == '__main__':
    main()
