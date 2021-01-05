import resource_packs.image_manipulation as images
import numpy as np


class ImageBuilder:

    def __init__(self, image, *, fix_invert=True, scale=1):
        self.image = images.fix_channels(image, fix_invert=fix_invert)
        self.height, self.width, _ = self.image.shape
        self.scale = scale
        self.shape = (self.scale, 4)
        self.queue = []

    def build(self):
        arr = np.array(self.queue, dtype=object)
        return np.float32(arr.reshape((self.height, self.width, 4)))

    def add(self, arr):
        self.queue.extend(list(arr))

    def __getitem__(self, *args):
        return self.image[args]

    @property
    def transparent(self):
        if self.scale == 1:
            return np.zeros(4)
        return np.zeros(self.scale, 4)

    def __iter__(self):
        for h in range(self.height):
            for w in range(self.width):
                yield self.image[h, w].copy()

    def packed(self):
        """
        Used to get current x value and y value
        """
        for h in range(self.height):
            for w in range(self.width):
                yield w, h, self.image[h, w].copy()
