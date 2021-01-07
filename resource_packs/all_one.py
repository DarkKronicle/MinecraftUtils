from math import ceil
from pathlib import Path
import resource_packs.image_manipulation as images
import resource_packs.color_manip as color

import cv2
import resource_packs
from skimage import io
from tqdm import tqdm
from colorama import Fore
import numpy as np


def all_one(palette_file, to_convert, to_save, map_brightness, map_transparency, map_color):
    palette = images.fix_channels(io.imread(Path(palette_file)), force_trans=255)
    # We want to get the width/height so that we don't get any index errors.
    p_height, p_width, _ = palette.shape
    palette = palette # .transpose((2, 0, 1))

    to_switch = Path(to_convert)
    to_convert_to = list(to_switch.glob("**/*.png"))

    total_start = 0

    problems = []
    pbar = tqdm(to_convert_to, unit=' images',
                bar_format="%s{l_bar}%s{bar}%s{r_bar}%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, Fore.RESET),
                smoothing=0.1)
    for image in pbar:
        try:
            total_start += 1
            image_name = str(image)
            img = io.imread(image_name)
            shape = img.shape
            if len(shape) == 2:
                img = img[:, :, np.newaxis]
                shape = img.shape
            img = img.transpose((2, 0, 1))
            if len(img) == 1:
                img = np.array([img[0], img[0], img[0], np.full(img.shape[1:], 255)])
            elif len(img) == 3:
                img = np.array([img[2], img[1], img[0], np.full(img.shape[1:], 255)])
            else:
                img = img[[2, 1, 0, 3]]
            # We tile it a certain amount and then crop it when we're done.
            height_tile = ceil(shape[0] / p_height)
            width_tile = ceil(shape[1] / p_width)
            edited_img = np.tile(palette, (height_tile, width_tile, 1))
            edited_img = edited_img[:shape[0], :shape[1], :].transpose((2, 0, 1))

            # Length of image shows if it has alpha.
            if map_transparency and len(img) == 4:
                edited_img[3] = img[3]
            if map_brightness:
                gray = images.get_gray(img[0], img[1], img[2])
                brightness = 1 + (0.5 - (gray / 255)) / 1
                brightness[brightness > 1.3] = 1.3
                brightness[brightness < 0.7] = 0.7
                new = color.set_brightness(edited_img, brightness)
                edited_img[0] = new[0]
                edited_img[1] = new[1]
                edited_img[2] = new[2]
            if map_color:
                new = color.set_hue(img, edited_img)
                edited_img[0] = new[0]
                edited_img[1] = new[1]
                edited_img[2] = new[2]

            img_stitched = edited_img.transpose((1, 2, 0))

            to_save_to = resource_packs.get_path(image, to_convert, to_save)
            cv2.imwrite(str(to_save_to), img_stitched)
        except RuntimeError as e:
            # REMOVE IF DEBUGGING ^
            if isinstance(e, KeyboardInterrupt):
                return
            problems.append(str(image))

    if len(problems) == 0:
        print("LETS GO! NO ERRORS.")
    else:
        print(f"Done! Only problems:" + '\n'.join(problems))
