import cv2
import numpy as np
from skimage import io
from tqdm import tqdm
from colorama import Fore

import resource_packs as packs
import resource_packs.image_manipulation as images
from resource_packs.image_builder import ImageBuilder
from sklearn.neighbors import KDTree


class BlockPixel:

    def __init__(self, block_handler, image):
        self.block_handler = block_handler
        self.image = image
        self.image_name = str(image)
        self.img = self._get_img()
        self.builder = ImageBuilder(self.img, fix_invert=False, scale=self.block_handler.palette_res[0])

    def _get_img(self):
        return io.imread(self.image_name)

    def _check_img(self):
        height, width, channels = self.img.shape
        if channels < 3:
            return False
        return True

    def convert(self):
        if not self._check_img():
            print('Not enough channels for: ' + self.image_name)
            return

        pbar = self.block_handler.setup_progress(self.builder, self.image)

        cached_colors = {}
        img_list = []
        old_h = 0
        for w, h, p in pbar:
            if old_h != h:
                old_h = h
                for he in range(self.block_handler.palette_res[1]):
                    for i in img_list:
                        self.builder.add(i[he])
                img_list.clear()
            pbar.update()

            a = p[3] % 256
            if a == 0:
                img_list.append(self.block_handler.transparent)
                continue

            r = p[0] % 255
            g = p[1] % 255
            b = p[2] % 255
            color = r, g, b
            to_get = cached_colors.get(color)
            to_get = None
            if to_get is None:
                to_get = self.block_handler.get_closest(*color)
                to_get = to_get[0:self.block_handler.palette_res[0], 0:self.block_handler.palette_res[1]]
                cached_colors[color] = to_get
            i = to_get
            i = images.fix_channels(i, force_trans=a)
            img_list.append(i)

        for he in range(self.block_handler.palette_res[1]):
            for i in img_list:
                self.builder.add(i[he])
        self.save(pbar)

    def save(self, pbar):
        pbar.set_description_str(f"Saving {self.image.name}")
        arr = np.array(self.builder.queue, dtype=object)
        arr = np.float32(arr.reshape((-1, 4)))
        img_stitched = np.float32(arr.reshape((self.builder.height * self.builder.scale, self.builder.width * self.builder.scale, 4)))

        to_save_to = packs.get_path(self.image, self.block_handler.to_convert, self.block_handler.to_save)
        cv2.imwrite(str(to_save_to), img_stitched)
        pbar.set_description_str(f"Done with {self.image.name}!")


class BlockPixelHandler:

    def __init__(self, palette_res, to_palette, to_save, to_convert):
        self.palette_res = palette_res
        self.to_palette = to_palette
        self.to_save = to_save
        self.to_convert = to_convert
        self.transparent = np.zeros((palette_res[0], palette_res[1], 4))
        self.color_img = []
        self.color_list = []
        self.problems = []
        self.total_image = 0
        self.total_start = 0
        self.tree: KDTree = None

    def setup_palette(self):
        current = 1
        pbar = tqdm(packs.get_img_files(self.to_palette))
        for image in pbar:
            pbar.set_description("Setting up palette...")
            img = io.imread(image)
            dominant = images.rgb_to_ycc(*images.get_average_color(img))
            self.color_list.append(dominant)
            self.color_img.append(img)
            current += 1
        self.color_list = np.array(self.color_list)
        self.tree = KDTree(self.color_list, leaf_size=100)

    def get_closest(self, r, g, b):
        color = np.array([images.rgb_to_ycc(r, g, b)])
        i = self.tree.query(color, k=1, return_distance=False)[0][0]
        return self.color_img[i]

    def convert_all(self):
        self.setup_palette()
        to_convert_to = packs.get_img_files(self.to_convert)
        self.total_image = len(to_convert_to)
        self.total_start = 0
        for image in to_convert_to:
            try:
                self.total_start += 1
                img = BlockPixel(self, image)
                img.convert()
            except RuntimeError as e:
                if isinstance(e, KeyboardInterrupt):
                    return
                self.problems.append(str(image))

        if len(self.problems) != 0:
            print(f"Done! Only problems:" + '\n'.join(self.problems))
        else:
            print("Done! No problems! POG CHAMP!")

    def setup_progress(self, builder, image):
        num = f"Image: {self.total_start}/{self.total_image}"
        return tqdm(list(builder.packed()), unit=' pixels',
                    bar_format="%s{l_bar}%s{bar}%s| Pixel: {n_fmt}/{total_fmt} %s {postfix} [{elapsed}<{"
                               "remaining}, {rate_fmt}]%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, num, Fore.RESET),
                    smoothing=0.1,
                    desc=f"Processing {image.name}")


def pixel_per_block(palette_res, to_palette, to_save, to_convert):
    block = BlockPixelHandler(palette_res, to_palette, to_save, to_convert)
    block.convert_all()

