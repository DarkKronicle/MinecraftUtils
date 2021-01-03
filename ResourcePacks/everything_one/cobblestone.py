from pathlib import Path
import ResourcePacks.image_manipulation as images

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


def main():
    palette = images.fix_channels(io.imread(Path(PALETTE_FILE)), force_trans=255)
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
            img = images.fix_channels(img, False)
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
                            gray = images.get_gray(p[0], p[1], p[2])
                            brightness = images.clamp(1 + (0.5 - (gray / 255)) / 1, 0.7, 1.3)
                            new = images.adjust_color_lightness(i[0], i[1], i[2], brightness)
                            i[0] = new[0]
                            i[1] = new[1]
                            i[2] = new[2]
                        if MAP_COLOR:
                            new = images.map_sat(i[0], i[1], i[2], p[2], p[1], p[0])
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

            folder = '/'.join(image_name.split("/")[2:-1]) + "/"
            to_save = Path(str("./to_pixel/done") + '/' + folder + image.name)
            to_save.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(to_save), img_stitched)
        except Exception as e:
            # REMOVE IF DEBUGGING ^
            if isinstance(e, KeyboardInterrupt):
                return
            problems.append(str(image))

    print(f"Done! Only problems:" + '\n'.join(problems))


if __name__ == '__main__':
    main()
