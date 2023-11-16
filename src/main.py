import os
from utils.window import start_detecting_window
from beautifultable import BeautifulTable
import logging
import os
from pathlib import Path
import traceback
from utils.process_handler import safe_exit
from version import __version__
from config import Config
from logger import Logger
from utils.misc import wait
from cam import Cam
from overlay import Overlay
import keyboard
from utils.game_settings import is_fontsize_ok
from item.filter import Filter


def main():
    start_detecting_window()
    while not Cam().is_offset_set():
        wait(0.2)

    # Create folders for logging stuff
    user_dir = os.path.expanduser("~")
    config_dir = Path(f"{user_dir}/.d4lf")
    for dir_name in ["log/screenshots", config_dir, config_dir / "profiles"]:
        os.makedirs(dir_name, exist_ok=True)

    file_path = config_dir / "params.ini"
    if not file_path.exists():
        file_path.touch()

    if Config().advanced_options["log_lvl"] == "info":
        Logger.init(logging.INFO)
    elif Config().advanced_options["log_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown log_lvl {Config().advanced_options['log_lvl']}. Must be one of [info, debug]")

    if not is_fontsize_ok():
        Logger.warning("You do not have your font size set to small! The lootfilter might not work as intended.")

    Logger.info(f"Adapt your custom configs in: {config_dir}")

    Filter().load_files()
    overlay = None

    print(f"============ D4 Loot Filter {__version__} ============")
    table = BeautifulTable()
    table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
    table.rows.append([Config().advanced_options["run_scripts"], "Run/Stop Vision Filter"])
    table.rows.append([Config().advanced_options["run_filter"], "Run/Stop Auto Filter"])
    table.rows.append([Config().advanced_options["exit_key"], "Exit"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    keyboard.add_hotkey(Config().advanced_options["run_scripts"], lambda: overlay.run_scripts() if overlay is not None else None)
    keyboard.add_hotkey(Config().advanced_options["run_filter"], lambda: overlay.filter_items() if overlay is not None else None)
    keyboard.add_hotkey(Config().advanced_options["exit_key"], lambda: safe_exit())

    overlay = Overlay()
    overlay.run()


if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
        print("Press Enter to exit ...")
        input()
