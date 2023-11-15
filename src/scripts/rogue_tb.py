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
            ready3 = hud.is_skill_ready(img, "skill3")
            imbued = hud.is_imbued(img)
            # Logger.debug(f"imbued: {imbued} s3: {ready3} s4: {ready4}")
            if not imbued:
                if ready4:
                    keyboard.send(Config().char["skill4"])
                    Logger.debug("Casting imbuement (skill4)")
                elif ready3:
                    keyboard.send(Config().char["skill3"])
                    Logger.debug("Casting imbuement (skill3)")
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
