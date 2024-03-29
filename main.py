from pathlib import Path

import inquirer
from tqdm import tqdm

import resource_packs.color_manip as color
import resource_packs as rp
from functools import wraps
import resource_packs.all_one as one
import resource_packs.color_manip as cm
import resource_packs.block_pixels as bp
from PIL import Image


def store_func(func, *args, **kwargs):
    wraps(func)

    def new_func(*newargs, **newkwargs):
        return func(*(args + newargs), **({**kwargs,  **newkwargs}))

    return new_func


def one_for_all(to_convert, to_save):
    questions = [
        inquirer.Path("palette", path_type=inquirer.Path.FILE,
                      message="What file will be the palette?", default="assets/cobblestone.png"),
        inquirer.Confirm(
            "brightness", message="Map brightness?"
                      ),
        inquirer.Confirm(
            "transparency", message="Map transparency?"
        ),
        inquirer.Confirm(
            "color", message="Map color?"
        )
    ]
    answers = inquirer.prompt(questions)
    one.all_one(answers['palette'], to_convert, to_save, answers['brightness'], answers['transparency'], answers['color'])


def pixel_blocks(to_convert, to_save):
    questions = [
        inquirer.Path("palette", path_type=inquirer.Path.DIRECTORY,
                      message="What directory will contain the palette images?", default="assets/palette/"),
        inquirer.Text(
            "palette_res", message="What resolution are the palette images?", default=16
        )
    ]
    answers = inquirer.prompt(questions)
    res = int(answers['palette_res'])
    bp.pixel_per_block((res, res), answers['palette'], to_save, to_convert)


def custom(to_convert, to_save):
    questions = [
        inquirer.Text(
            "r", message="What's the R value?"
        ),
        inquirer.Text(
            "g", message="Whats the G value?"
        ),
        inquirer.Text(
            "b", message="Whats the B value?"
        )
    ]
    answers = inquirer.prompt(questions)
    cm.set_color(int(answers['r']), int(answers['g']), int(answers['b']))
    color.convert(color.ColorPresets.custom.value, to_convert, to_save)


def png_all(to_convert, to_save):
    directory = Path(to_convert)
    file_types = ('*.png', '*.jpg', '*.webp', '*.jpeg')
    images = []
    for file_type in file_types:
        images.extend(directory.glob("**/{}".format(file_type)))
    for image in tqdm(images):
        im = Image.open(str(image)).convert('RGB')
        im.save(rp.get_path(Path(str(image.parent) + '/' + image.stem + '.png'), to_convert, to_save), 'png')

def main():
    """
    MAKE SURE YOU RUN THIS IN A TERMINAL.
    It will break (for example) using PyCharms' default running instance.
    (If using PyCharm) you can set 'Emulate Terminal' to true.
    """
    options = {
        'PNG Everything': png_all,
        'Grayscale': store_func(color.convert, color.ColorPresets.grayscale.value),
        'Invert': store_func(color.convert, color.ColorPresets.invert.value),
        'Custom Color': custom,
        'One for All': one_for_all,
        'Pixel Blocks': pixel_blocks,
        'Copy .mcmeta': rp.copy_mcmeta,
        'Shuffle': store_func(color.convert, color.ColorPresets.shuffle.value)
    }

    questions = [
        inquirer.List("action", message="What do you want to do?",
                      choices=options.keys()
                      ),
        inquirer.Path("to_convert", path_type=inquirer.Path.DIRECTORY,
                      message="What folder do you want to convert?", default="assets/convert/"),
        inquirer.Path("to_save", path_type=inquirer.Path.DIRECTORY,
                      message="What folder do you want the results to be?", default="assets/done/"),
    ]
    answers = inquirer.prompt(questions)
    rp.to_save = Path(answers['to_save'])
    rp.to_convert = Path(answers['to_convert'])

    func = answers['action']
    options[func](to_save=rp.to_save, to_convert=rp.to_convert)


if __name__ == '__main__':
    main()
