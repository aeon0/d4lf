import os
from utils.misc import wait


def get_setting_folder() -> str:
    folder = f"C:\\Users\\{os.getlogin()}\\Documents\\Diablo IV"
    if not folder:
        assert f"Could not find setting folder at {folder}"
    return folder


def is_fontsize_ok() -> bool:
    file_path = f"{get_setting_folder()}/LocalPrefs.txt"
    with open(file_path, "r") as file:
        file_content = file.read()
        if 'FontScale "0"' not in file_content:
            return False
    return True
