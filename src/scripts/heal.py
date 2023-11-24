import keyboard
import traceback
from cam import Cam
from config import Config
from ui.hud import Hud
from ui.char_inventory import CharInventory
from utils.misc import wait
from logger import Logger


def heal():
    hud = Hud()
    inv = CharInventory()
    Logger.info("Starting Heal Script")
    while True:
        img = Cam().grab()
        if hud.is_ingame(img) and not inv.is_open():
            health = hud.get_health(img)
            if health < 0.8:
                keyboard.send("tab")
                Logger.debug(f"Healing {health}")

        wait(0.3, 0.35)


if __name__ == "__main__":
    try:
        from utils.window import start_detecting_window

        start_detecting_window()
        while not Cam().is_offset_set():
            wait(0.2)
        heal()
    except:
        traceback.print_exc()
        print("Press Enter to exit ...")
        input()
