import keyboard
import traceback
from cam import Cam
from config import Config
from ui.hud import Hud
from utils.misc import wait
from logger import Logger


def run_rogue_tb():
    hud = Hud()

    Logger.info("Starting Rogue TB Script")
    while True:
        img = Cam().grab()
        if hud.is_ingame(img):
            ready4 = hud.is_skill_ready(img)
            imbued = hud.is_imbued(img)
            if not imbued:
                if ready4:
                    keyboard.send("r")
        wait(0.1, 0.15)


if __name__ == "__main__":
    try:
        from utils.window import start_detecting_window

        start_detecting_window()
        while not Cam().is_offset_set():
            wait(0.2)
        run_rogue_tb()
    except:
        traceback.print_exc()
        print("Press Enter to exit ...")
        input()
