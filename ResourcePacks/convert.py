import os
from pathlib import Path

import ResourcePacks.texture_json as tjson


class ConversionHandler:

    def __init__(self, texture_parent):
        self.textures = tjson.TextureJsonHandler(texture_parent)

    def import_file(self, file):
        self.textures.populate_from_csv(file)
        self.textures.save()

    def import_json(self):
        self.textures.populate_from_parent()


def main():
    cwd = os.getcwd()
    texture_parent = Path(cwd + "/resources")
    handler = ConversionHandler(texture_parent)
    handler.import_file(Path(str(cwd) + '/theflatsheet.csv'))


if __name__ == '__main__':
    main()
