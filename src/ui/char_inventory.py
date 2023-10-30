from config import Config
from logger import Logger
from template_finder import SearchArgs
from ui.menu import ToggleMethod
from ui.inventory_base import InventoryBase
from utils.misc import wait


class CharInventory(InventoryBase):
    def __init__(self):
        super().__init__()
        self.menu_name = "Char_Inventory"
        self.is_open_search_args: SearchArgs = SearchArgs(
            ref=["char_inventory_active", "char_inventory_active_hover"],
            threshold=0.8,
            roi=Config().ui_roi["character_active"],
            use_grayscale=False,
            mode="best",
        )
        self.open_hotkey = Config().char["inventory"]
        self.open_method = ToggleMethod.HOTKEY
        self.close_hotkey = "esc"
        self.close_method = ToggleMethod.HOTKEY

    def should_maintaine(self, max_items: int = 10) -> tuple[bool, int | None]:
        if not self.open():
            Logger.error("Could not open char inventory")
            return False, None
        wait(0.4)
        occupied_slots, _ = self.get_item_slots()
        if not self.close():
            Logger.error("Could not close char inventory")
            return False, len(occupied_slots)
        wait(0.4)
        return len(occupied_slots) > max_items, len(occupied_slots)
