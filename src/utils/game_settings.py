import os

from config.loader import IniConfigLoader


def is_fontsize_ok() -> bool:
    custom_path = IniConfigLoader().general.local_prefs_path
    user_dir = os.path.expanduser("~")
    default_path = f"{user_dir}\\Documents\\Diablo IV/LocalPrefs.txt"
    file_path = custom_path if custom_path != "" else default_path
    if not os.path.exists(file_path):
        return True
    try:
        with open(file_path) as file:
            file_content = file.read()
            if 'FontScale "0"' not in file_content:
                return False
    except PermissionError:
        return True
    return True
