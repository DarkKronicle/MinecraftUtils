import json
import csv
from pathlib import Path


class TextureJson:

    __slots__ = ("old_path", "new_path", "name", "model_type")

    def __init__(self, old_path, new_path, name, model_type):
        self.old_path = old_path
        self.new_path = new_path
        self.name = name
        self.model_type = model_type

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.model_type,
            "file": {
                "pre": self.old_path,
                "post": self.new_path
            }
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data):
        return cls(data["file"]["pre"], data["file"]["post"], data["game"]["name"], data["type"])

    @classmethod
    def from_file(cls, file):
        return cls.from_dict(json.loads(file))


class TextureJsonHandler:

    def __init__(self, parent):
        self.parent = Path(str(parent))
        self.textures = []

    def populate_from_csv(self, file):
        csv_reader = csv.reader(file.read_text().split('\n'), delimiter=',')
        line_count = 0
        for row in csv_reader:
            line_count += 1
            if line_count == 1:
                continue
            try:
                self.textures.append(TextureJson(row[1], row[2], row[0], row[3]))
            except IndexError:
                return

    def populate_from_parent(self):
        self.import_dir(self.parent)

    def import_dir(self, directory):
        for c in directory.iterdir():
            if c.is_dir():
                self.import_dir(c)
            else:
                if c.suffix == ".json":
                    self.textures.append(TextureJson.from_dict(json.loads(c.read_text())))

    def save(self):
        for texture in self.textures:
            texture: TextureJson
            name = texture.name.replace(" ", "_")
            folder = '/'.join(texture.new_path.split("/")[0:-1]) + "/"
            to_save = Path(str(self.parent) + '/' + folder + name.split(".")[0] + ".json")
            to_save.parent.mkdir(parents=True, exist_ok=True)
            j = texture.to_json()
            to_save.write_text(j)

    @classmethod
    def default_criteria(cls, texture):
        return True

    def forward_conversion(self, old: Path, new: Path, *, criteria=default_criteria):
        for texture in self.textures:
            if criteria(texture):
                self._convert(texture, old, new, True)

    def _convert(self, texture: TextureJson, old_dir: Path, new_dir: Path, forward=True):
        if forward:
            new = texture.new_path
            old = texture.old_path
        else:
            new = texture.old_path
            old = texture.new_path
        if new is None or old is None:
            # If we don't have one or the other, conversions won't work ;-;
            return
        to_get = Path(str(old_dir) + "/" + old)
        to_go = Path(str(new_dir) + "/" + new)
        to_get.rename(to_go)
