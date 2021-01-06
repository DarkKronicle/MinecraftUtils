from collections import OrderedDict
from pathlib import Path

import cv2
import numpy as np
from skimage import io
from tqdm import tqdm
from colorama import Fore

import resource_packs
import resource_packs.image_manipulation as images
from resource_packs.image_builder import ImageBuilder


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
            builder = ImageBuilder(img, fix_invert=False, scale=palette_res[0])
            height, width, channels = img.shape
            if channels < 3:
                print("Not big enough channels")
                continue

            num = f"Image: {total_start}/{total_image}"
            pbar = tqdm(list(builder.packed()), unit=' pixels',
                        bar_format="%s{l_bar}%s{bar}%s| Pixel: {n_fmt}/{total_fmt} %s {postfix} [{elapsed}<{"
                                   "remaining}, {rate_fmt}]%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, num, Fore.RESET),
                        smoothing=0.1,
                        desc=f"Processing {image.name}")

            img_processed = {}
            img_list = []
            old_h = 0
            for w, h, p in pbar:
                if old_h != h:
                    old_h = h
                    for he in range(palette_res[1]):
                        for i in img_list:
                            builder.add(i[he])
                    img_list.clear()
                pbar.update()
                r = p[0] % 255
                g = p[1] % 255
                b = p[2] % 255
                a = p[3] % 256
                if a > 0:
                    color = r, g, b
                    to_get = img_processed.get(color)
                    if to_get is None:
                        to_get = images.min_color_diff(color, colors)[1]
                        to_get = to_get[0:palette_res[0], 0:palette_res[1]]
                        img_processed[r, g, b] = to_get
                    i = to_get
                    i = images.fix_channels(i, force_trans=a)
                else:
                    i = transparent
                img_list.append(i)

            for he in range(palette_res[1]):
                for i in img_list:
                    builder.add(i[he])

            pbar.set_description_str(f"Saving {image.name}")
            arr = np.array(builder.queue, dtype=object)
            arr = np.float32(arr.reshape((-1, 4)))
            img_stitched = np.float32(arr.reshape((builder.height * builder.scale, builder.width * builder.scale, 4)))

            to_save_to = resource_packs.get_path(image, to_convert, to_save)
            cv2.imwrite(str(to_save_to), img_stitched)
            pbar.set_description_str(f"Done with {image.name}!")
        except RuntimeError as e:
            # REMOVE IF DEBUGGING ^
            if isinstance(e, KeyboardInterrupt):
                return
            problems.append(str(image))

    if len(problems) != 0:
        print(f"Done! Only problems:" + '\n'.join(problems))
    else:
        print("Done! No problems! POG CHAMP!")
