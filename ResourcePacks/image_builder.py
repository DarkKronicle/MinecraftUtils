import ResourcePacks.image_manipulation as images
import numpy as np


class ImageBuilder:

    def __init__(self, image, *, fix_invert=True, scale=1):
        self.image = images.fix_channels(image, fix_invert=fix_invert)
        self.height, self.width, _ = self.image.shape
        self.scale = scale
        self.shape = (self.scale, 4)
        self.array = None

    def build(self):
        return self.array.reshape((self.height, self.width, 4))

    def add(self, arr):
        arr = arr.reshape(self.shape)
        if self.array is None:
            self.array = arr
        else:
            self.array = np.concatenate((self.array, arr))

    def __getitem__(self, *args):
        return self.image[args]

    @property
    def transparent(self):
        if self.scale == 1:
            return np.zeros(4)
        return np.zeros(self.scale, 4)

    def __iter__(self):
        count = 0
        for h in range(self.height):
            for w in range(self.width):
                count += 1
                yield self.image[h, w].copy()

