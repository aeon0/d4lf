import time
from utils.misc import wait
from logger import Logger
from cam import Cam
from ui.char_inventory import CharInventory
from ui.inventory_base import InventoryBase
from ui.chest import Chest
from item.find_descr import find_descr
from item.descr.read_descr import read_descr
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.filter import Filter
import keyboard
from utils.custom_mouse import mouse
from utils.window import screenshot
from config import Config


def check_items(inv: InventoryBase):
    occupied, _ = inv.get_item_slots()

    Logger.info(f"Items: {len(occupied)} in {inv.menu_name}")
    start_time = None
    for item in occupied:
        if item.is_junk or item.is_fav:
            continue
        if start_time is not None:
            Logger.debug(f"Runtime (FullItemCheck): {time.time() - start_time:.2f}s")
            Logger.debug("----")
        # Find item descr
        start_time = time.time()
        found = False
        while not found:
            if time.time() - start_time > 6:
                Logger.error("Could not detect item descr. Timeout reached. Continue")
                if img is not None:
                    screenshot("failed_descr_detection", img=img)
                break
            inv.hover_item(item)
            wait(0.15)
            img = Cam().grab()
            start_detect = time.time()
            found, rarity, cropped_descr, _ = find_descr(img, item.center)
            Logger.debug(f"  Runtime (DetectItem): {time.time() - start_detect:.2f}s")
        if not found:
            continue

        start_time_read = time.time()
        # Detect contents of item descr
        item_descr = read_descr(rarity, cropped_descr, False)
        if item_descr is None:
            Logger.info("Retry item detection")
            wait(0.3)
            found, rarity, cropped_descr, _ = find_descr(Cam().grab(), item.center)
            if found:
                item_descr = read_descr(rarity, cropped_descr)
            if item_descr is None:
                continue
        Logger.debug(f"  Runtime (ReadItem): {time.time() - start_time_read:.2f}s")

        # Hardcoded filters
        if rarity == ItemRarity.Common and item_descr.type == ItemType.Material:
            Logger.info(f"Matched: Material")
            continue
        if rarity == ItemRarity.Legendary and item_descr.type == ItemType.Material:
            Logger.info(f"Matched: Extracted Aspect")
            continue
        elif rarity == ItemRarity.Magic and item_descr.type == ItemType.Elixir:
            Logger.info(f"Matched: Elixir")
            continue
        elif rarity in [ItemRarity.Magic, ItemRarity.Common] and item_descr.type != ItemType.Sigil:
            keyboard.send("space")
            wait(0.13, 0.14)
            continue

        # Check if we want to keep the item
        start_filter = time.time()
        res = Filter().should_keep(item_descr)
        matched_any_affixes = len(res.matched) > 0 and len(res.matched[0].matched_affixes) > 0
        Logger.debug(f"  Runtime (Filter): {time.time() - start_filter:.2f}s")
        if not res.keep:
            keyboard.send("space")
            wait(0.13, 0.14)
        elif res.keep and (matched_any_affixes or item_descr.rarity == ItemRarity.Unique):
            Logger.info("Mark as favorite")
            keyboard.send("space")
            wait(0.26, 0.3)
            keyboard.send("space")
            wait(0.13, 0.14)


def run_loot_filter():
    Logger().info("Run Loot filter")
    inv = CharInventory()
    chest = Chest()

    check_tabs = Config().general["check_chest_tabs"]
    if chest.is_open():
        for i in range(check_tabs):
            chest.switch_to_tab(i)
            check_items(chest)
        check_items(inv)
    else:
        if not inv.open():
            screenshot("inventory_not_open", img=Cam().grab())
            Logger.error("Inventory did not open up")
            return
        check_items(inv)
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    Logger().info("Loot Filter done")
