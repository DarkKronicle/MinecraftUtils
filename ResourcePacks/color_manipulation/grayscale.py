from pathlib import Path

import cv2
import numpy as np
from skimage import io
from tqdm import tqdm
from colorama import Fore

import ResourcePacks.image_manipulation as images
from ResourcePacks.image_builder import ImageBuilder

CONVERT_PATH = "./to_pixel/convert"


def main():
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
            builder = ImageBuilder(img, fix_invert=False)
            for p in builder:
                a = p[3] % 256
                if a > 0:
                    # If we don't copy, it actually gets modified.
                    i = p
                    # Calculate grayscale and set it
                    gray = images.get_gray(p[0], p[1], p[2])
                    i[0] = gray
                    i[1] = gray
                    i[2] = gray
                    i[3] = a
                else:
                    i = builder.transparent

                builder.add(i)

            img_stitched = builder.build()
            folder = '/'.join(image_name.split("/")[2:-1]) + "/"
            to_save = Path(str("./to_pixel/done") + '/' + folder + image.name)
            to_save.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(to_save), np.float32(img_stitched))
        except RuntimeError as e:
            # REMOVE IF DEBUGGING ^
            if isinstance(e, KeyboardInterrupt):
                return
            problems.append(str(image))

    if len(problems) == 0:
        print("No problems! Awesome!")
    else:
        print(f"Done! Only problems:" + '\n'.join(problems))


if __name__ == '__main__':
    main()
