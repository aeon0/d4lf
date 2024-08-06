import logging
import time

import keyboard

from src.cam import Cam
from src.config.loader import IniConfigLoader
from src.config.models import HandleRaresType, ItemRefreshType
from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.item.descr.read_descr import read_descr
from src.item.filter import Filter
from src.item.find_descr import find_descr
from src.ui.char_inventory import CharInventory
from src.ui.chest import Chest
from src.ui.inventory_base import InventoryBase
from src.utils.custom_mouse import mouse
from src.utils.image_operations import compare_histograms
from src.utils.window import screenshot

LOGGER = logging.getLogger(__name__)


def check_items(inv: InventoryBase, force_refresh: ItemRefreshType):
    occupied, _ = inv.get_item_slots()

    if force_refresh == ItemRefreshType.force_with_filter or force_refresh == ItemRefreshType.force_without_filter:
        reset_item_status(occupied, inv)
        occupied, _ = inv.get_item_slots()

    if force_refresh == ItemRefreshType.force_without_filter:
        return

    num_fav = sum(1 for slot in occupied if slot.is_fav)
    num_junk = sum(1 for slot in occupied if slot.is_junk)
    LOGGER.info(f"Items: {len(occupied)} (favorite: {num_fav}, junk: {num_junk}) in {inv.menu_name}")
    start_time = None
    img = None
    for item in occupied:
        if item.is_junk or item.is_fav:
            continue
        if start_time is not None:
            LOGGER.debug(f"Runtime (FullItemCheck): {time.time() - start_time:.2f}s")
            LOGGER.debug("----")
        # Find item descr
        start_time = time.time()
        found = False
        while not found:
            if time.time() - start_time > 6:
                LOGGER.error("Could not detect item descr. Timeout reached. Continue")
                if img is not None:
                    screenshot("failed_descr_detection", img=img)
                break
            inv.hover_item(item)
            time.sleep(0.18)
            img = Cam().grab()
            start_detect = time.time()
            found, rarity, cropped_descr, _ = find_descr(img, item.center)
            if found:
                # To avoid getting an image that is taken while the fade-in animation of the item is showing
                found_check, _, cropped_descr_check, _ = find_descr(Cam().grab(), item.center)
                if found_check:
                    score = compare_histograms(cropped_descr, cropped_descr_check)
                    if score < 0.99:
                        found = False
                        continue
            LOGGER.debug(f"  Runtime (DetectItem): {time.time() - start_detect:.2f}s")
        if not found:
            continue

        start_time_read = time.time()
        # Detect contents of item descr
        item_descr = read_descr(rarity, cropped_descr, False)
        if item_descr is None:
            LOGGER.info("Retry item detection")
            time.sleep(0.3)
            found, rarity, cropped_descr, _ = find_descr(Cam().grab(), item.center)
            if found:
                item_descr = read_descr(rarity, cropped_descr)
            if item_descr is None:
                continue
        LOGGER.debug(f"  Runtime (ReadItem): {time.time() - start_time_read:.2f}s")

        # Hardcoded filters
        if rarity == ItemRarity.Common and item_descr.item_type == ItemType.Material:
            LOGGER.info("Matched: Material")
            continue
        if rarity == ItemRarity.Legendary and item_descr.item_type == ItemType.Material:
            LOGGER.info("Matched: Extracted Aspect")
            continue
        if item_descr.item_type == ItemType.Elixir:
            LOGGER.info("Matched: Elixir")
            continue
        if item_descr.item_type == ItemType.Incense:
            LOGGER.info("Matched: Incense")
            continue
        if item_descr.item_type == ItemType.TemperManual:
            LOGGER.info("Matched: Temper Manual")
            continue
        if rarity in [ItemRarity.Magic, ItemRarity.Common] and item_descr.item_type != ItemType.Sigil:
            keyboard.send("space")
            time.sleep(0.13)
            continue
        if rarity == ItemRarity.Rare and IniConfigLoader().general.handle_rares == HandleRaresType.ignore:
            LOGGER.info("Matched: Rare, ignore Item")
            continue
        if rarity == ItemRarity.Rare and IniConfigLoader().general.handle_rares == HandleRaresType.junk:
            keyboard.send("space")
            time.sleep(0.13)
            continue

        # Check if we want to keep the item
        start_filter = time.time()
        res = Filter().should_keep(item_descr)
        matched_any_affixes = len(res.matched) > 0 and len(res.matched[0].matched_affixes) > 0
        LOGGER.debug(f"  Runtime (Filter): {time.time() - start_filter:.2f}s")
        if not res.keep:
            keyboard.send("space")
            time.sleep(0.13)
        elif (
            res.keep
            and (matched_any_affixes or item_descr.rarity in [ItemRarity.Unique, ItemRarity.Mythic])
            and IniConfigLoader().general.mark_as_favorite
        ):
            LOGGER.info("Mark as favorite")
            keyboard.send("space")
            time.sleep(0.17)
            keyboard.send("space")
            time.sleep(0.13)


def reset_item_status(occupied, inv):
    for item_slot in occupied:
        if item_slot.is_fav:
            inv.hover_item(item_slot)
            keyboard.send("space")
        if item_slot.is_junk:
            inv.hover_item(item_slot)
            keyboard.send("space")
            time.sleep(0.13)
            keyboard.send("space")

    if occupied:
        mouse.move(*Cam().abs_window_to_monitor((0, 0)))


def run_loot_filter(force_refresh: ItemRefreshType = ItemRefreshType.no_refresh):
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    LOGGER.info("Run Loot filter")
    inv = CharInventory()
    chest = Chest()

    if chest.is_open():
        for i in IniConfigLoader().general.check_chest_tabs:
            chest.switch_to_tab(i)
            time.sleep(0.5)
            check_items(chest, force_refresh)
        mouse.move(*Cam().abs_window_to_monitor((0, 0)))
        time.sleep(0.5)
        check_items(inv, force_refresh)
    else:
        if not inv.open():
            screenshot("inventory_not_open", img=Cam().grab())
            LOGGER.error("Inventory did not open up")
            return
        check_items(inv, force_refresh)
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    LOGGER.info("Loot Filter done")
