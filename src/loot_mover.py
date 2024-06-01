from src.cam import Cam
from src.config.loader import IniConfigLoader
from src.config.models import MoveItemsType
from src.logger import Logger
from src.ui.char_inventory import CharInventory
from src.ui.chest import Chest
from src.utils.custom_mouse import mouse


def move_items_to_stash():
    Logger().info("Move inventory items to stash")

    inv = CharInventory()
    chest = Chest()

    if chest.is_open():
        occupied_inv, _ = inv.get_item_slots()

        for i in IniConfigLoader().general.check_chest_tabs:
            chest.switch_to_tab(i)

            _, empty_chest = chest.get_item_slots()

            if len(empty_chest) == 0:
                continue

            move_items(inv, occupied_inv, len(empty_chest))

            if len(occupied_inv) == 0:
                break

        mouse.move(*Cam().abs_window_to_monitor((0, 0)))
        Logger().info("Completed move")
    else:
        Logger().error("Moving items only works if stash is open")


def move_items_to_inventory():
    Logger().info("Move stash items to inventory")

    inv = CharInventory()
    chest = Chest()

    if chest.is_open():
        _, empty_inv = inv.get_item_slots()
        empty_slot_count = len(empty_inv)

        for i in IniConfigLoader().general.check_chest_tabs:
            chest.switch_to_tab(i)

            occupied_chest, _ = chest.get_item_slots()

            Logger().debug(
                f"Stash tab {i} - Number of stash items: {len(occupied_chest)} - Number of empty inventory " f"spaces: {empty_slot_count}"
            )

            item_move_count = move_items(inv, occupied_chest, empty_slot_count)
            empty_slot_count = empty_slot_count - item_move_count
            Logger().debug(f"Moved {item_move_count} items, now have {empty_slot_count} empty slots left.")

            if empty_slot_count < 1:
                break

        mouse.move(*Cam().abs_window_to_monitor((0, 0)))
        Logger().info("Completed move")
    else:
        Logger().error("Moving items only works if stash is open")


def move_items(inv, occupied, num_to_move):
    item_move_count = 0
    handled_items = []
    for item in occupied:
        handled_items.append(item)

        move_item_type = IniConfigLoader().general.move_item_type
        if (
            (move_item_type == MoveItemsType.junk and item.is_junk)
            or (move_item_type == MoveItemsType.non_favorites and not item.is_fav)
            or move_item_type == MoveItemsType.everything
        ):
            inv.hover_item(item)
            mouse.click("right")
            item_move_count = item_move_count + 1

        if item_move_count == num_to_move:
            break

    for handled_item in handled_items:
        occupied.remove(handled_item)

    return item_move_count
