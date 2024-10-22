import logging
import time

import keyboard

import src.item.descr.read_descr_tts
from src.cam import Cam
from src.config.loader import IniConfigLoader
from src.config.models import HandleRaresType, ItemRefreshType, UnfilteredUniquesType
from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.item.filter import Filter
from src.scripts.common import mark_as_favorite, mark_as_junk, reset_item_status
from src.ui.char_inventory import CharInventory
from src.ui.chest import Chest
from src.ui.inventory_base import InventoryBase
from src.utils.custom_mouse import mouse
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
    for item in occupied:
        if item.is_junk or item.is_fav:
            continue
        inv.hover_item(item)
        time.sleep(0.15)
        img = Cam().grab()
        item_descr = None
        try:
            item_descr = src.item.descr.read_descr_tts.read_description()
            LOGGER.debug(f"Parsed item based on TTS: {item_descr}")
        except Exception:
            screenshot("tts_error", img=img)
            LOGGER.exception(f"Error in TTS read_descr. {src.tts.LAST_ITEM=}")
        if item_descr is None:
            LOGGER.info("Retry item detection")
            time.sleep(0.3)
            try:
                item_descr = src.item.descr.read_descr_tts.read_description()
                LOGGER.debug(f"Parsed item based on TTS: {item_descr}")
            except Exception:
                screenshot("tts_error", img=img)
                LOGGER.exception(f"Error in TTS read_descr. {src.tts.LAST_ITEM=}")
        if item_descr is None:
            continue

        # Hardcoded filters
        if item_descr.rarity == ItemRarity.Common and item_descr.item_type == ItemType.Material:
            LOGGER.info("Matched: Material")
            continue
        if item_descr.rarity == ItemRarity.Legendary and item_descr.item_type == ItemType.Material:
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
        if item_descr.rarity in [ItemRarity.Magic, ItemRarity.Common] and item_descr.item_type != ItemType.Sigil:
            keyboard.send("space")
            time.sleep(0.13)
            continue
        if item_descr.rarity == ItemRarity.Rare and IniConfigLoader().general.handle_rares == HandleRaresType.ignore:
            LOGGER.info("Matched: Rare, ignore Item")
            continue
        if item_descr.rarity == ItemRarity.Rare and IniConfigLoader().general.handle_rares == HandleRaresType.junk:
            keyboard.send("space")
            time.sleep(0.13)
            continue

        # Check if we want to keep the item
        start_filter = time.time()
        res = Filter().should_keep(item_descr)
        matched_any_affixes = len(res.matched) > 0 and len(res.matched[0].matched_affixes) > 0
        LOGGER.debug(f"  Runtime (Filter): {time.time() - start_filter:.2f}s")

        # Uniques have special handling. If they have an aspect specifically called out by a profile they are treated
        # like any other item. If not, and there are no non-aspect filters, then they are handled by the handle_uniques
        # property
        if item_descr.rarity == ItemRarity.Unique:
            if not res.keep:
                mark_as_junk()
            elif res.keep:
                if res.all_unique_filters_are_aspects and not res.unique_aspect_in_profile:
                    if IniConfigLoader().general.handle_uniques == UnfilteredUniquesType.favorite:
                        mark_as_favorite()
                elif IniConfigLoader().general.mark_as_favorite:
                    mark_as_favorite()
        else:
            if not res.keep:
                mark_as_junk()
            elif (
                res.keep
                and (matched_any_affixes or item_descr.rarity == ItemRarity.Mythic or item_descr.item_type == ItemType.Sigil)
                and IniConfigLoader().general.mark_as_favorite
            ):
                mark_as_favorite()


def run_loot_filter(force_refresh: ItemRefreshType = ItemRefreshType.no_refresh):
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    LOGGER.info("Run Loot filter")
    inv = CharInventory()
    chest = Chest()

    if chest.is_open():
        for i in IniConfigLoader().general.check_chest_tabs:
            chest.switch_to_tab(i)
            time.sleep(0.4)
            check_items(chest, force_refresh)
        mouse.move(*Cam().abs_window_to_monitor((0, 0)))
        time.sleep(0.4)
        check_items(inv, force_refresh)
    else:
        if not inv.open():
            screenshot("inventory_not_open", img=Cam().grab())
            LOGGER.error("Inventory did not open up")
            return
        check_items(inv, force_refresh)
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    LOGGER.info("Loot Filter done")
