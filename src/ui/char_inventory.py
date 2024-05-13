from config.loader import IniConfigLoader
from config.ui import ResManager
from template_finder import SearchArgs
from ui.inventory_base import InventoryBase
from ui.menu import ToggleMethod


class CharInventory(InventoryBase):
    def __init__(self):
        super().__init__()
        self.menu_name = "Char_Inventory"
        self.is_open_search_args: SearchArgs = SearchArgs(
            ref=["sort_icon", "sort_icon_hover"],
            threshold=0.8,
            roi=ResManager().roi.sort_icon,
            use_grayscale=False,
        )
        self.open_hotkey = IniConfigLoader().char.inventory
        self.open_method = ToggleMethod.HOTKEY
        self.close_hotkey = "esc"
        self.close_method = ToggleMethod.HOTKEY
        self.delay = 1  # Needed as they added a "fad-in" for the items
