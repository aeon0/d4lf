import time
import numpy as np
from logger import Logger
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.models import Item
from utils.window import screenshot
from config import Config

from item.descr.texture import find_seperator_short, find_affix_bullets, find_aspect_bullet, find_empty_sockets
from item.descr.item_type import read_item_type
from item.descr.find_affixes import find_affixes
from item.descr.find_aspect import find_aspect


def read_descr(rarity: ItemRarity, img_item_descr: np.ndarray, show_warnings: bool = True) -> Item | None:
    item = Item(rarity)

    # Find textures for seperator short on top
    # =========================
    sep_short_match = find_seperator_short(img_item_descr)
    if sep_short_match is None:
        if show_warnings:
            Logger.warning("Could not detect item_seperator_short.")
            screenshot("failed_seperator_short", img=img_item_descr)
        return None

    # Find item type and item power / tier list
    # =========================
    item, item_type_str = read_item_type(item, img_item_descr, sep_short_match)
    if item is None:
        if show_warnings:
            Logger.warning(f"Could not detect ItemPower and ItemType: {item_type_str}")
            screenshot("failed_itempower_itemtype", img=img_item_descr)
        return None

    if item.type == ItemType.Material or (item.rarity in [ItemRarity.Magic, ItemRarity.Common] and item.type != ItemType.Sigil):
        return item

    # Find textures for bullets and sockets
    # =========================
    affix_bullets = find_affix_bullets(img_item_descr, sep_short_match)
    aspect_bullet = find_aspect_bullet(img_item_descr, sep_short_match) if rarity in [ItemRarity.Legendary, ItemRarity.Unique] else None
    empty_sockets = find_empty_sockets(img_item_descr, sep_short_match)

    # Split affix bullets into inherent and others
    # =========================
    if item.type in [ItemType.Armor, ItemType.Helm, ItemType.Gloves]:
        inhernet_affixe_bullets = []
    elif item.type in [ItemType.Ring, ItemType.Sigil]:
        inhernet_affixe_bullets = affix_bullets[:2]
        affix_bullets = affix_bullets[2:]
    elif item.type in [ItemType.Shield]:
        inhernet_affixe_bullets = affix_bullets[:4]
        affix_bullets = affix_bullets[4:]
    else:
        # default for: Pants, Amulets, Boots, All Weapons
        inhernet_affixe_bullets = affix_bullets[:1]
        affix_bullets = affix_bullets[1:]

    # Find inherent affixes
    # =========================
    is_sigil = item.type == ItemType.Sigil
    line_height = Config().ui_offsets["item_descr_line_height"]
    if len(inhernet_affixe_bullets) > 0 and len(affix_bullets) > 0:
        bottom_limit = affix_bullets[0].center[1] - int(line_height // 2)
        item.inherent, _ = find_affixes(img_item_descr, inhernet_affixe_bullets, bottom_limit, is_sigil)
        if item.inherent is None:
            if show_warnings:
                Logger.warning(f"Could not find inherent: {debug_str}")
                screenshot("failed_inherent", img=img_item_descr)
            return None

    # Find normal affixes
    # =========================
    if aspect_bullet is not None:
        bottom_limit = aspect_bullet.center[1]
    elif len(empty_sockets) > 0:
        bottom_limit = empty_sockets[0].center[1]
    else:
        bottom_limit = img_item_descr.shape[0]
    item.affixes, debug_str = find_affixes(img_item_descr, affix_bullets, bottom_limit, is_sigil)
    if item.affixes is None:
        if show_warnings:
            Logger.warning(f"Could not find affix: {debug_str}")
            screenshot("failed_affixes", img=img_item_descr)
        return None

    # Find aspects & uniques
    # =========================
    if rarity in [ItemRarity.Legendary, ItemRarity.Unique]:
        item.aspect, debug_str = find_aspect(img_item_descr, aspect_bullet, item.type, item.rarity)
        if item.aspect is None:
            if show_warnings:
                Logger.warning(f"Could not find aspect/unique: {debug_str}")
                screenshot("failed_aspect_or_unique", img=img_item_descr)
            return None

    return item
