import time
import cv2
from utils.misc import wait
from logger import Logger
from cam import Cam
from ui.char_inventory import CharInventory
from item.find_descr import find_descr
from utils.roi_operations import compare_tuples
from item.read_descr import read_descr
from item.data.rarity import ItemRarity
from item.filter import should_keep
import keyboard
from utils.custom_mouse import mouse


def run_loot_filter():
    Logger().info("Run Loot filter")
    inv = CharInventory()
    while True:
        if not inv.is_open():
            inv.open()
        occupied, _ = inv.get_item_slots()
        last_item_center = None

        for item in occupied:
            # Find item descr
            start_time = time.time()
            found = False
            while not found:
                if time.time() - start_time > 6:
                    Logger.error("Could not detect item descr. Timeout reached. Continue")
                    break
                inv.hover_item(item)
                wait(0.4)
                img = Cam().grab()
                found, top_left_center, rarity, croped_descr = find_descr(img, item.center)
                if found:
                    # Sometimes we go to the next item, but the previous one still shows
                    if last_item_center is not None and compare_tuples(top_left_center, last_item_center, 5):
                        found = False
                        Logger.warning("Detected no updated item, move cursor keep searching.")
                        continue
                    last_item_center = top_left_center
            if not found:
                continue

            # Hardcoded rarity filters
            if rarity == ItemRarity.Unique:
                Logger.info("Matched unique.")
                continue
            if rarity in [ItemRarity.Common, ItemRarity.Magic]:
                Logger.info(f"Discard item of rarity: {rarity}")
                keyboard.send("space")
                wait(0.15, 0.18)
                continue

            # Detect contents of item descr
            item = read_descr(rarity, croped_descr)
            if item is None:
                Logger.warning("Failed to read properties. Keeping it.")
                continue

            # Check if we want to keep the item
            if not should_keep(item):
                keyboard.send("space")
                wait(0.15, 0.18)

        break
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    Logger().info("Loot Filter done")
