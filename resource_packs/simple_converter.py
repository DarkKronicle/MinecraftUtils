from pathlib import Path

import cv2
from tqdm import tqdm

from resource_packs.image_builder import ImageBuilder
import numpy as np
from skimage import io
from colorama import Fore
import resource_packs


def convert(pixel_func, to_convert, to_save):
    to_switch = to_convert
    to_convert_files = list(to_switch.glob("**/*.png"))

    total_start = 0

    problems = []
    pbar = tqdm(to_convert_files, unit=' images',
                bar_format="%s{l_bar}%s{bar}%s{r_bar}%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, Fore.RESET),
                smoothing=0.1)
    for image in pbar:
        try:
            pbar.set_description_str(f"Processing {image.name}")
            total_start += 1
            image_name = str(image)
            img = io.imread(image_name)
            builder = ImageBuilder(img, fix_invert=True)
            for p in builder:
                a = p[3] % 256
                if a > 0:
                    i = p
                    i = pixel_func(i)
                else:
                    i = builder.transparent

                builder.add(i)

            img_stitched = builder.build()
            to_save_to = resource_packs.get_path(image, to_convert, to_save)
            cv2.imwrite(str(to_save_to), np.float32(img_stitched))
        except RuntimeError as e:
            # REMOVE IF DEBUGGING ^
            if isinstance(e, KeyboardInterrupt):
                return
            problems.append(str(image))

    if len(problems) == 0:
        print("No problems! Awesome!")
    else:
        print(f"Done! Only problems:" + '\n'.join(problems))
