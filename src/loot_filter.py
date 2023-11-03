import time
from utils.misc import wait
from logger import Logger
from cam import Cam
from ui.char_inventory import CharInventory
from ui.inventory_base import InventoryBase
from ui.chest import Chest
from item.find_descr import find_descr
from utils.roi_operations import compare_tuples
from item.read_descr import read_descr
from item.data.rarity import ItemRarity
from item.filter import should_keep
import keyboard
from utils.custom_mouse import mouse
from utils.window import screenshot
from config import Config


def check_items(inv: InventoryBase):
    occupied, _ = inv.get_item_slots()
    Logger.info(f"Found {len(occupied)} items in {inv.menu_name}. Checking them.")
    last_item_center = None
    start_time = None
    for item in occupied:
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
            wait(0.35)
            img = Cam().grab()
            found, top_left_center, rarity, cropped_descr = find_descr(img, item.center)
            if found:
                # Sometimes we go to the next item, but the previous one still shows
                if last_item_center is not None and compare_tuples(top_left_center, last_item_center, 5):
                    found = False
                    Logger.warning("Detected no updated item, move cursor keep searching.")
                    continue
                last_item_center = top_left_center
        if not found:
            continue
        Logger.debug(f"  Runtime (DetectItem): {time.time() - start_time:.2f}s")
        # Hardcoded rarity filters
        if rarity == ItemRarity.Unique:
            Logger.info("Matched: unique")
            continue
        if rarity in [ItemRarity.Common, ItemRarity.Magic]:
            Logger.info(f"Discard item of rarity: {rarity}")
            keyboard.send("space")
            wait(0.15, 0.18)
            continue
        start_time_read = time.time()
        # Detect contents of item descr
        item_descr = read_descr(rarity, cropped_descr)
        if item_descr is None:
            Logger.warning("Failed to read properties. Keeping it")
            continue
        Logger.debug(f"  Runtime (ReadItem): {time.time() - start_time_read:.2f}s")

        # Check if we want to keep the item
        if not should_keep(item_descr):
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
    elif not inv.is_open():
        inv.open()
    if not inv.is_open():
        screenshot("inventory_not_open", img=Cam().grab())
        Logger.error("Inventory did not open up")
        return
    check_items(inv)
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    Logger().info("Loot Filter done")
