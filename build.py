import os
import shutil
from pathlib import Path
from src.version import __version__
import argparse
import getpass
from cryptography.fernet import Fernet


parser = argparse.ArgumentParser(description="Build d4lf")
parser.add_argument(
    "-c",
    "--conda_path",
    type=str,
    help="Path to local conda e.g. C:\\Users\\USER\\miniconda3",
    default=f"C:\\Users\\{getpass.getuser()}\\miniconda3",
)
parser.add_argument("-k", "--use_key", action="store_true", help="Will build with encryption key")
args = parser.parse_args()


# clean up
def clean_up():
    # pyinstaller
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("main.spec"):
        os.remove("main.spec")


if __name__ == "__main__":
    release_dir = f"d4lf_v{__version__}"
    print(f"Building version: {__version__}")

    clean_up()

    if os.path.exists(release_dir):
        for path in Path(release_dir).glob("**/*"):
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path)
        shutil.rmtree(release_dir)

    for exe in ["main.py"]:
        key_cmd = " "
        if args.use_key:
            key = Fernet.generate_key().decode("utf-8")
            key_cmd = " --key " + key
        installer_cmd = f"pyinstaller --onefile --distpath {release_dir}{key_cmd} --paths .\\src --paths {args.conda_path}\\envs\\d4lf\\Lib\\site-packages src\\{exe}"
        os.system(installer_cmd)

    os.system(f"cd {release_dir} && mkdir config && cd ..")

    shutil.copy("config/game_1920_1080.ini", f"{release_dir}/config/")
    shutil.copy("config/params.ini", f"{release_dir}/config/")
    shutil.copy("config/filter_affixes.yaml", f"{release_dir}/config/")
    shutil.copy("config/filter_aspects.yaml", f"{release_dir}/config/")
    shutil.copy("README.md", f"{release_dir}/")
    shutil.copytree("assets", f"{release_dir}/assets")
    os.rename(f"{release_dir}/main.exe", f"{release_dir}/d4lf.exe")
    clean_up()
