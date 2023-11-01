from config import Config
from logger import Logger
from ui.menu import ToggleMethod
from ui.inventory_base import InventoryBase
from cam import Cam
from utils.misc import wait
from template_finder import SearchArgs
from utils.custom_mouse import mouse


class Chest(InventoryBase):
    def __init__(self):
        super().__init__(5, 10)
        self.menu_name = "Chest"
        self.is_open_search_args = SearchArgs(ref="stash_menu_icon", threshold=0.8, roi="stash_menu_icon", use_grayscale=True)
        self.close_hotkey = "esc"
        self.close_method = ToggleMethod.HOTKEY
        self.curr_tab = 0

    @staticmethod
    def switch_to_tab(tab_idx) -> bool:
        Logger.info(f"Switch Stash Tab to: {tab_idx}")
        if tab_idx > 4:
            return False
        x, y, w, h = Config().ui_roi["tab_slots_5"]
        section_length = w // 5
        centers = [(x + (i + 0.5) * section_length, y + h // 2) for i in range(5)]
        mouse.move(*Cam().window_to_monitor(centers[tab_idx]), randomize=2)
        wait(0.5)
        mouse.click("left")
        wait(1)
        return True
