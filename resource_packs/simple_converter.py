from pathlib import Path

import cv2
from tqdm import tqdm

from resource_packs.image_builder import ImageBuilder
import time
import numpy as np
from skimage import io
from colorama import Fore
import resource_packs
from functools import wraps


def pixel_func_wrapper(pixel_func):
    wraps(pixel_func)

    def func(arr):
        arrlen = len(arr)
        shape = arr.shape
        if arrlen == 1:
            return pixel_func(np.array([arr[0], arr[0], arr[0], np.full(shape[1:], 255)]))
        elif arrlen == 3:
            shape = arr.shape
            return pixel_func(np.array([arr[2], arr[1], arr[0], np.full(shape[1:], 255)]))
        else:
            return pixel_func(arr[[2, 1, 0, 3]])

    return func


def convert(pixel_func, to_convert, to_save):
    pixel_func = pixel_func_wrapper(pixel_func)
    to_switch = to_convert
    to_convert_files = list(to_switch.glob("**/*.png"))

    problems = []
    pbar = tqdm(to_convert_files, unit=' images',
                bar_format="%s{l_bar}%s{bar}%s{r_bar}%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, Fore.RESET),
                smoothing=0.1)

    for image in pbar:
        try:
            image_name = str(image)
            img = io.imread(image_name)
            if len(img.shape) == 2:
                img = img[:, :, np.newaxis]
            img = img.transpose((2, 0, 1))
            img = pixel_func(img)
            img_stitched = img.transpose((1, 2, 0))
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
