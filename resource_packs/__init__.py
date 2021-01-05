from pathlib import Path


def get_path(file: Path, firstdir, seconddir):
    folder = str(file.parents[0]).replace(str(firstdir), "") + "/"
    to_save_to = Path(str(seconddir) + '/' + folder + file.name)
    to_save_to.parent.mkdir(parents=True, exist_ok=True)
    return to_save_to
