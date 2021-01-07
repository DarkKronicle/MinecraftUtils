from pathlib import Path
from colorama import Fore
import shutil
from tqdm import tqdm


def get_path(file: Path, firstdir, seconddir):
    folder = str(file.parents[0]).replace(str(firstdir), "") + "/"
    to_save_to = Path(str(seconddir) + '/' + folder + file.name)
    to_save_to.parent.mkdir(parents=True, exist_ok=True)
    return to_save_to


def copy_mcmeta(to_convert, to_save):
    mcmetas = list(Path(to_convert).glob("**/*.mcmeta"))
    pbar = tqdm(mcmetas, unit=' files',
                bar_format="%s{l_bar}%s{bar}%s{r_bar}%s" % (Fore.BLUE, Fore.WHITE, Fore.BLUE, Fore.RESET),
                smoothing=0.1, desc="Copying .mcmeta files.")
    for m in pbar:
        to_save_to = get_path(m, to_convert, to_save)
        shutil.copy(m, to_save_to)
