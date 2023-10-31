import keyboard
import os
import threading
from utils.window import find_and_set_window_position
from beautifultable import BeautifulTable
import logging
import traceback
from utils.process_handler import safe_exit
from version import __version__
from config import Config
from logger import Logger
from loot_filter import run_loot_filter


def main():
    find_and_set_window_position()

    # Create folders for logging stuff
    for dir_name in ["log/screenshots", "log/error"]:
        os.makedirs(dir_name, exist_ok=True)

    if Config().advanced_options["log_lvl"] == "info":
        Logger.init(logging.INFO)
    elif Config().advanced_options["log_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown log_lvl {Config().advanced_options['log_lvl']}. Must be one of [info, debug]")

    print(f"============ D4 Loot Filter {__version__} ============")
    table = BeautifulTable()
    table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
    table.rows.append([Config().advanced_options["run_key"], "Run Loot Filter"])
    table.rows.append([Config().advanced_options["exit_key"], "Stop"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    keyboard.add_hotkey(Config().advanced_options["run_key"], lambda: threading.Thread(target=run_loot_filter, daemon=True).start())
    keyboard.add_hotkey(Config().advanced_options["exit_key"], lambda: safe_exit())
    keyboard.wait()


if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()
