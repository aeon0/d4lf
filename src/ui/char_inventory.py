from config import Config
from template_finder import SearchArgs
from ui.menu import ToggleMethod
from ui.inventory_base import InventoryBase


class CharInventory(InventoryBase):
    def __init__(self):
        super().__init__()
        self.menu_name = "Char_Inventory"
        self.is_open_search_args: SearchArgs = SearchArgs(
            ref=["sort_icon", "sort_icon_hover"],
            threshold=0.8,
            roi=Config().ui_roi["sort_icon"],
            use_grayscale=False,
        )
        self.open_hotkey = Config().char["inventory"]
        self.open_method = ToggleMethod.HOTKEY
        self.close_hotkey = "esc"
        self.close_method = ToggleMethod.HOTKEY
