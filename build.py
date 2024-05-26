import argparse
import getpass
import os
import shutil
from pathlib import Path

from cryptography.fernet import Fernet

from src.version import __version__

EXE_NAME = "d4lf.exe"


def build(use_key: bool, release_dir: Path):
    clean_up()
    if release_dir.exists():
        shutil.rmtree(release_dir)
    key_cmd = " "
    if use_key:
        key = Fernet.generate_key().decode("utf-8")
        key_cmd = " --key " + key
    installer_cmd = f"pyinstaller --clean --onefile --distpath {release_dir}{key_cmd} --paths .\\src --paths {ARGS.conda_path}\\envs\\d4lf\\Lib\\site-packages src\\main.py"
    os.system(installer_cmd)
    (release_dir / "main.exe").rename(release_dir / EXE_NAME)


# clean up
def clean_up():
    # pyinstaller
    if (build_dir := Path("build")).exists():
        shutil.rmtree(build_dir)
    if (p := Path("main.spec")).exists():
        p.unlink()


def copy_additional_resources(release_dir: Path):
    shutil.copy("README.md", release_dir)
    shutil.copytree("assets", release_dir / "assets")
    shutil.copytree("config", release_dir / "config")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Build d4lf")
    PARSER.add_argument(
        "-c",
        "--conda_path",
        type=str,
        help="Path to local conda e.g. C:\\Users\\USER\\miniconda3",
        default=f"C:\\Users\\{getpass.getuser()}\\miniconda3",
    )
    PARSER.add_argument("-k", "--use_key", action="store_true", help="Will build with encryption key")
    ARGS = PARSER.parse_args()

    print(f"Building version: {__version__}")
    RELEASE_DIR = Path(f"d4lf_v{__version__}")

    build(use_key=ARGS.use_key, release_dir=RELEASE_DIR)
    copy_additional_resources(RELEASE_DIR)
