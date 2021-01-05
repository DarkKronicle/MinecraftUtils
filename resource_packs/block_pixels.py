from pathlib import Path

import cv2
import numpy as np
from skimage import io
from tqdm import tqdm
from colorama import Fore

import resource_packs
import resource_packs.image_manipulation as images


def pixel_per_block(palette_res, to_palette, to_save, to_convert):
    palette = Path(to_palette)
    palette_images = list(palette.glob("**/*.png"))
    transparent = np.zeros((palette_res[0], palette_res[1], 4))
    colors = {}
    current = 1
    pbar = tqdm(palette_images)
    for image in pbar:
        pbar.set_description("Setting up palette...")
        img = io.imread(image)
        dominant = images.get_average_color(img)
        colors[dominant] = img
        current += 1

    to_switch = to_convert
    to_convert_to = list(to_switch.glob("**/*.png"))

    total_image = len(to_convert_to)
    total_start = 0

    problems = []

    for image in to_convert_to:
        try:
            total_start += 1
            image_name = str(image)
            img = io.imread(image_name)
            img = images.fix_channels(img, False)
            height, width, channels = img.shape
            if channels < 3:
                print("Not big enough channels")
                continue
            pixels = img
            img_rows = []
            img_stitched = None

            total = width * height
            current = 1
            num = f"Image: {total_start}/{total_image}"
            with tqdm(total=total, unit=' pixels',
                      bar_format="%s{l_bar}%s{bar}%s| Pixel: {n_fmt}/{total_fmt} %s {postfix} [{elapsed}<{"
                                 "remaining}, {rate_fmt}]%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, num, Fore.RESET),
                      smoothing=0.1,
                      desc=f"Processing {image.name}") \
                    as pbar:

                for h in range(height):
                    row_image = None
                    for w in range(width):
                        pbar.update()
                        p = pixels[h, w]
                        r = p[0] % 255
                        g = p[1] % 255
                        b = p[2] % 255
                        a = p[3] % 256
                        if a > 0:
                            color = r, g, b
                            to_get = images.min_color_diff(color, colors)
                            i = to_get[1]
                            i = i[0:palette_res[0], 0:palette_res[1]]
                            i = images.fix_channels(i, force_trans=a)
                        else:
                            i = transparent
                        if row_image is None:
                            row_image = i
                        else:
                            row_image = np.concatenate((row_image, i), axis=1)
                        current += 1

                    img_rows.append(row_image)
                pbar.set_description_str(f"Saving {image.name}")
                for i in img_rows:
                    if img_stitched is None:
                        img_stitched = i
                    else:
                        img_stitched = np.concatenate((img_stitched, i), axis=0)

                to_save_to = resource_packs.get_path(image, to_convert, to_save)
                cv2.imwrite(str(to_save_to), img_stitched)
                pbar.set_description_str(f"Done with {image.name}!")
        except Exception as e:
            # REMOVE IF DEBUGGING ^
            if isinstance(e, KeyboardInterrupt):
                return
            problems.append(str(image))

    if len(problems) != 0:
        print(f"Done! Only problems:" + '\n'.join(problems))
    else:
        print("Done! No problems! POG CHAMP!")

