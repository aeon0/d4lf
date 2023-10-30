import os
import shutil
from pathlib import Path
from src.version import __version__
import argparse
import getpass
import random
from cryptography.fernet import Fernet
import string


parser = argparse.ArgumentParser(description="Build d4h")
parser.add_argument("-v", "--version", type=str, help="New release version e.g. 0.4.2", default="")
parser.add_argument(
    "-c",
    "--conda_path",
    type=str,
    help="Path to local conda e.g. C:\\Users\\USER\\miniconda3",
    default=f"C:\\Users\\{getpass.getuser()}\\miniconda3",
)
parser.add_argument("-r", "--random_name", action="store_true", help="Will generate a random name for the exe")
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
    release_dir = f"d4h_v{__version__}"
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
        installer_cmd = f"pyinstaller --onefile --distpath {release_dir}{key_cmd} --paths .\\src --paths {args.conda_path}\\envs\\d4h\\Lib\\site-packages src\\{exe}"
        os.system(installer_cmd)

    os.system(f"cd {release_dir} && mkdir config && cd ..")

    with open(f"{release_dir}/config/custom.ini", "w") as f:
        f.write("; Add parameters you want to overwrite from param.ini here")
    shutil.copy("config/game.ini", f"{release_dir}/config/")
    shutil.copy("config/params.ini", f"{release_dir}/config/")
    shutil.copy("config/options.ini", f"{release_dir}/config/")
    shutil.copy("README.md", f"{release_dir}/")
    shutil.copytree("assets", f"{release_dir}/assets")
    clean_up()

    if args.random_name:
        print("Generate random names")
        new_name = "".join(random.choices(string.ascii_letters, k=random.randint(6, 14)))
        os.rename(f"{release_dir}/main.exe", f"{release_dir}/{new_name}.exe")
