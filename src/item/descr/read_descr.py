import logging

import numpy as np

from src import TP
from src.config.ui import ResManager
from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.item.descr.find_affixes import find_affixes
from src.item.descr.find_aspect import find_aspect
from src.item.descr.item_type import read_item_type
from src.item.descr.texture import find_affix_bullets, find_aspect_bullet, find_codex_upgrade_icon, find_seperator_short
from src.item.models import Item
from src.utils.window import screenshot

LOGGER = logging.getLogger(__name__)


def read_descr(rarity: ItemRarity, img_item_descr: np.ndarray, show_warnings: bool = True) -> Item | None:
    futures = {}
    base_item = Item(rarity=rarity)

    # Find textures for seperator short on top
    # =========================
    sep_short_match = find_seperator_short(img_item_descr)
    if sep_short_match is None:
        if show_warnings:
            LOGGER.warning("Could not detect item_seperator_short.")
            screenshot("failed_seperator_short", img=img_item_descr)
        return None

    # Find item type and item power / tier list
    # =========================
    item, item_type_str = read_item_type(base_item, img_item_descr, sep_short_match, do_pre_proc=False)
    # In case it was not successful, try with doing image pre-processing
    if item is None:
        item, item_type_str = read_item_type(base_item, img_item_descr, sep_short_match)
    if item is None:
        if show_warnings:
            LOGGER.warning(f"Could not detect ItemPower and ItemType: {item_type_str}")
            screenshot("failed_itempower_itemtype", img=img_item_descr)
        return None

    if item.item_type in [ItemType.Material, ItemType.TemperManual, ItemType.Elixir, ItemType.Incense] or (
        item.rarity in [ItemRarity.Magic, ItemRarity.Common] and item.item_type != ItemType.Sigil
    ):
        return item

    # Find textures for bullets
    # =========================
    affix_bullets = find_affix_bullets(img_item_descr, sep_short_match)
    futures["aspect_bullet"] = (
        TP.submit(find_aspect_bullet, img_item_descr, sep_short_match) if rarity in [ItemRarity.Unique, ItemRarity.Mythic] else None
    )

    # Split affix bullets into inherent and others
    # =========================
    if item.rarity == ItemRarity.Mythic:  # TODO should refactor so we either apply some logic OR we look for separator
        # Just pick the last 4 matches as affixes
        inherent_affix_bullets = affix_bullets[:-4]
        affix_bullets = affix_bullets[-4:]
    elif item.item_type in [ItemType.ChestArmor, ItemType.Helm, ItemType.Gloves, ItemType.Legs]:
        inherent_affix_bullets = []
    elif item.item_type in [ItemType.Ring]:
        inherent_affix_bullets = affix_bullets[:2]
        affix_bullets = affix_bullets[2:]
    elif item.item_type in [ItemType.Sigil]:
        inherent_affix_bullets = affix_bullets[:3]
        affix_bullets = affix_bullets[3:]
    elif item.item_type in [ItemType.Shield]:
        inherent_affix_bullets = affix_bullets[:4]
        affix_bullets = affix_bullets[4:]
    else:
        # default for: Amulets, Boots, All Weapons
        inherent_affix_bullets = affix_bullets[:1]
        affix_bullets = affix_bullets[1:]

    # Find inherent affixes
    # =========================
    is_sigil = item.item_type == ItemType.Sigil

    def _get_inherent():
        line_height = ResManager().offsets.item_descr_line_height
        if len(inherent_affix_bullets) > 0 and len(affix_bullets) > 0:
            bottom_limit = affix_bullets[0].center[1] - int(line_height // 2)
            i_inherent, debug_str = find_affixes(
                img_item_descr=img_item_descr,
                affix_bullets=inherent_affix_bullets,
                bottom_limit=bottom_limit,
                is_sigil=is_sigil,
                is_inherent=True,
            )
            if i_inherent is None:
                i_inherent, debug_str = find_affixes(
                    img_item_descr=img_item_descr,
                    affix_bullets=inherent_affix_bullets,
                    bottom_limit=bottom_limit,
                    is_sigil=is_sigil,
                    is_inherent=True,
                    do_pre_proc_flag=False,
                )
            return i_inherent, debug_str
        return [], ""

    futures["inherent"] = TP.submit(_get_inherent)
    aspect_bullet = futures["aspect_bullet"].result() if futures["aspect_bullet"] is not None else None
    futures["codex_upgrade"] = TP.submit(find_codex_upgrade_icon, img_item_descr, aspect_bullet)

    # Find normal affixes
    # =========================
    def _get_affixes():
        if affix_bullets:
            bottom_limit = affix_bullets[-1].region[1] + affix_bullets[-1].region[3] + ResManager().offsets.item_descr_line_height
        else:
            bottom_limit = img_item_descr.shape[0]
        i_affixes, debug_str = find_affixes(
            img_item_descr=img_item_descr, affix_bullets=affix_bullets, bottom_limit=bottom_limit, is_sigil=is_sigil
        )
        if i_affixes is None:
            i_affixes, debug_str = find_affixes(
                img_item_descr=img_item_descr,
                affix_bullets=affix_bullets,
                bottom_limit=bottom_limit,
                is_sigil=is_sigil,
                do_pre_proc_flag=False,
            )
        return i_affixes, debug_str

    futures["affixes"] = TP.submit(_get_affixes)

    # Find aspects of uniques
    # =========================
    if rarity in [ItemRarity.Unique, ItemRarity.Mythic]:
        item.aspect, debug_str = find_aspect(img_item_descr, aspect_bullet)
        if item.aspect is None:
            item.aspect, debug_str = find_aspect(img_item_descr, aspect_bullet, False)
        if item.aspect is None:
            if show_warnings:
                LOGGER.warning(f"Could not find unique: {debug_str}")
                screenshot("failed_aspect_or_unique", img=img_item_descr)
            return None

    item.affixes, debug_str = futures["affixes"].result()
    if item.affixes is None:
        if show_warnings:
            LOGGER.warning(f"Could not find affix: {debug_str}")
            screenshot("failed_affixes", img=img_item_descr)
        return None

    item.inherent, debug_str = futures["inherent"].result()
    if item.inherent is None:
        if show_warnings:
            LOGGER.warning(f"Could not find inherent: {debug_str}")
            screenshot("failed_inherent", img=img_item_descr)
        return None

    item.codex_upgrade = futures["codex_upgrade"].result()

    return item
