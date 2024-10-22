import logging
import time

import keyboard

import src.item.descr.read_descr_tts
import src.scripts.loot_filter
import src.scripts.loot_filter_tts
from src.cam import Cam
from src.config.loader import IniConfigLoader
from src.config.models import ItemRefreshType
from src.ui.char_inventory import CharInventory
from src.ui.chest import Chest
from src.utils.custom_mouse import mouse
from src.utils.window import screenshot

LOGGER = logging.getLogger(__name__)


def mark_as_junk():
    keyboard.send("space")
    time.sleep(0.13)


def mark_as_favorite():
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


def run_loot_filter(force_refresh: ItemRefreshType = ItemRefreshType.no_refresh, tts: bool = False):
    LOGGER.info("Run Loot filter")
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    check_items = src.scripts.loot_filter_tts.check_items if tts else src.scripts.loot_filter.check_items

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
