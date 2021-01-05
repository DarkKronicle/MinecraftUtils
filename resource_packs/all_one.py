from pathlib import Path
import resource_packs.image_manipulation as images
from resource_packs.image_builder import ImageBuilder

import cv2
import resource_packs
from skimage import io
from tqdm import tqdm
from colorama import Fore


def all_one(palette_file, to_convert, to_save, map_brightness, map_transparency, map_color):
    palette = images.fix_channels(io.imread(Path(palette_file)), force_trans=255)
    # We want to get the width/height so that we don't get any index errors.
    p_height, p_width, _ = palette.shape

    to_switch = Path(to_convert)
    to_convert_to = list(to_switch.glob("**/*.png"))

    total_start = 0

    problems = []
    pbar = tqdm(to_convert_to, unit=' images',
                bar_format="%s{l_bar}%s{bar}%s{r_bar}%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, Fore.RESET),
                smoothing=0.1)
    for image in pbar:
        try:
            pbar.set_description_str(f"Processing {image.name}")
            total_start += 1
            image_name = str(image)
            img = io.imread(image_name)
            builder = ImageBuilder(img)
            for w, h, p in builder.packed():
                if map_transparency:
                    a = p[3] % 256
                else:
                    a = 255
                if a > 0:
                    # If we don't copy, it actually gets modified by KEEP_BRIGHT.
                    i = palette[h % p_height, w % p_width].copy()
                    if map_brightness:
                        # We still want to somewhat know what we're looking at.
                        # Does slow it down, but it's not too bad.
                        gray = images.get_gray(p[0], p[1], p[2])
                        brightness = images.clamp(1 + (0.5 - (gray / 255)) / 1, 0.7, 1.3)
                        new = images.adjust_color_lightness(i[0], i[1], i[2], brightness)
                        i[0] = new[0]
                        i[1] = new[1]
                        i[2] = new[2]
                    if map_color:
                        new = images.map_sat(i[0], i[1], i[2], p[2], p[1], p[0])
                        i[0] = new[0]
                        i[1] = new[1]
                        i[2] = new[2]
                    i[3] = a
                else:
                    i = builder.transparent
                builder.add(i)

            img_stitched = builder.build()

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
