from pathlib import Path

import inquirer
import resource_packs.color_manip as color
import resource_packs as rp
from functools import wraps
import resource_packs.all_one as one


def store_func(func, *args, **kwargs):
    wraps(func)

    def new_func(*newargs, **newkwargs):
        return func(*(args + newargs), **({**kwargs,  **newkwargs}))

    return new_func


def all_for_one(to_convert, to_save):
    questions = [
        inquirer.Path("palette", path_type=inquirer.Path.FILE,
                      message="What file will be the palette?", default="assets/convert/cobblestone.png"),
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


def main():
    """
    MAKE SURE YOU RUN THIS IN A TERMINAL.
    It will break (for example) using PyCharms' default running instance.
    (If using PyCharm) you can set 'Emulate Terminal' to true.
    """
    options = {
        'Grayscale': store_func(color.convert, color.ColorPresets.grayscale.value),
        'Invert': store_func(color.convert, color.ColorPresets.invert.value),
        'Blue': store_func(color.convert, color.ColorPresets.blue.value),
        'All One': all_for_one
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
