import copy
import logging

import numpy as np
import rapidfuzz

import src.tts
from src import TP
from src.config import AFFIX_COMPARISON_CHARS
from src.dataloader import Dataloader
from src.item.data.affix import Affix, AffixType
from src.item.data.aspect import Aspect
from src.item.data.item_type import ItemType, is_armor, is_consumable, is_jewelry, is_mapping, is_socketable, is_weapon
from src.item.data.rarity import ItemRarity
from src.item.descr.text import clean_str, closest_match, find_number
from src.item.descr.texture import find_affix_bullets, find_seperator_short, find_seperators_long
from src.item.models import Item
from src.template_finder import TemplateMatch
from src.utils.window import screenshot

LOGGER = logging.getLogger(__name__)


def _add_affixes_from_tts_mixed(
    tts_section: list[str], item: Item, inherent_affix_bullets: list[TemplateMatch], affix_bullets: list[TemplateMatch]
) -> Item:
    affixes = _get_affixes_from_tts_section(
        tts_section,
        item,
        len(inherent_affix_bullets)
        + len([x for x in affix_bullets if any(x.name.startswith(s) for s in ["affix", "greater_affix", "rerolled"])]),
    )
    for i, affix in enumerate(affixes):
        if i < len(inherent_affix_bullets):
            name = rapidfuzz.process.extractOne(
                clean_str(affix), list(Dataloader().affix_dict), scorer=rapidfuzz.distance.Levenshtein.distance
            )
            item.inherent.append(
                Affix(
                    name=name[0],
                    loc=inherent_affix_bullets[i].center,
                    text=affix,
                    type=AffixType.inherent,
                    value=find_number(affix),
                )
            )
        elif i < len(inherent_affix_bullets) + len(affix_bullets):
            name = rapidfuzz.process.extractOne(
                clean_str(affix), list(Dataloader().affix_dict), scorer=rapidfuzz.distance.Levenshtein.distance
            )
            if affix_bullets[i - len(inherent_affix_bullets)].name.startswith("greater_affix"):
                a_type = AffixType.greater
            elif affix_bullets[i - len(inherent_affix_bullets)].name.startswith("rerolled"):
                a_type = AffixType.rerolled
            else:
                a_type = AffixType.normal
            item.affixes.append(
                Affix(
                    name=name[0],
                    loc=affix_bullets[i - len(inherent_affix_bullets)].center,
                    text=affix,
                    type=a_type,
                    value=find_number(affix),
                )
            )
        else:
            name = closest_match(clean_str(affix)[:AFFIX_COMPARISON_CHARS], Dataloader().aspect_unique_dict)
            item.aspect = Aspect(
                name=name,
                loc=affix_bullets[i - len(inherent_affix_bullets) - len(affix_bullets)].center,
                text=affix,
                value=find_number(affix),
            )
    return item


def _add_affixes_from_tts(tts_section: list[str], item: Item) -> Item:
    inherent_num = 0
    affixes_num = 3 if item.rarity == ItemRarity.Legendary else 4
    if is_weapon(item.item_type) or item.item_type in [ItemType.Amulet, ItemType.Boots]:
        inherent_num = 1
    elif item.item_type in [ItemType.Ring]:
        inherent_num = 2
    elif item.item_type in [ItemType.Shield]:
        inherent_num = 4
    affixes = _get_affixes_from_tts_section(tts_section, item, inherent_num + affixes_num)
    for i, affix in enumerate(affixes):
        if i < inherent_num:
            name = rapidfuzz.process.extractOne(
                clean_str(affix), list(Dataloader().affix_dict), scorer=rapidfuzz.distance.Levenshtein.distance
            )
            item.inherent.append(
                Affix(
                    name=name[0],
                    text=affix,
                    type=AffixType.inherent,
                    value=find_number(affix),
                )
            )
        elif i < inherent_num + affixes_num:
            name = rapidfuzz.process.extractOne(
                clean_str(affix), list(Dataloader().affix_dict), scorer=rapidfuzz.distance.Levenshtein.distance
            )
            item.affixes.append(
                Affix(
                    name=name[0],
                    text=affix,
                    type=AffixType.normal,
                    value=find_number(affix),
                )
            )
        else:
            name = closest_match(clean_str(affix)[:AFFIX_COMPARISON_CHARS], Dataloader().aspect_unique_dict)
            item.aspect = Aspect(
                name=name,
                text=affix,
                value=find_number(affix),
            )
    return item


def _create_base_item_from_tts(tts_item: list[str]) -> Item | None:
    if tts_item[0].startswith(src.tts.ItemIdentifiers.COMPASS.value):
        return Item(rarity=ItemRarity.Common, item_type=ItemType.Compass)
    if tts_item[0].startswith(src.tts.ItemIdentifiers.NIGHTMARE_SIGIL.value):
        return Item(rarity=ItemRarity.Common, item_type=ItemType.Sigil)
    if tts_item[0].startswith(src.tts.ItemIdentifiers.TRIBUTE.value):
        item = Item(item_type=ItemType.Tribute)
        search_string_split = tts_item[1].split(" ")
        item.rarity = _get_item_rarity(search_string_split[0])
        return item
    if tts_item[0].startswith(src.tts.ItemIdentifiers.WHISPERING_KEY.value):
        return Item(item_type=ItemType.Consumable)
    if any(tts_item[1].lower().endswith(x) for x in ["summoning"]):
        return Item(item_type=ItemType.Material)
    if any(tts_item[1].lower().endswith(x) for x in ["gem"]):
        return Item(item_type=ItemType.Gem)
    if "rune of" in tts_item[1].lower():
        item = Item(item_type=ItemType.Rune)
        search_string_split = tts_item[1].lower().split(" rune of ")
        item.rarity = _get_item_rarity(search_string_split[0])
        return item
    item = Item()
    if tts_item[1].lower().endswith("elixir"):
        item.item_type = ItemType.Elixir
    elif tts_item[1].lower().endswith("incense"):
        item.item_type = ItemType.Incense
    elif any(tts_item[1].lower().endswith(x) for x in ["consumable", "scroll"]):
        item.item_type = ItemType.Consumable
    if is_consumable(item.item_type):
        search_string_split = tts_item[1].split(" ")
        item.rarity = _get_item_rarity(search_string_split[0])
        return item

    search_string = tts_item[1].lower().replace("ancestral", "").strip()
    search_string_split = search_string.split(" ")
    item.rarity = _get_item_rarity(search_string_split[0])
    item.item_type = _get_item_type(" ".join(search_string_split[1:]))
    for _i, line in enumerate(tts_item):
        if "item power" in line.lower():
            item.power = int(find_number(line))
            break
    return item


def _get_affixes_from_tts_section(tts_section: list[str], item: Item, length: int):
    if item.rarity in [ItemRarity.Mythic, ItemRarity.Unique]:
        length += 1
    dps = None
    item_power = None
    masterwork = None
    start = 0
    for i, line in enumerate(tts_section):
        if "masterwork" in line.lower():
            masterwork = i
        if "item power" in line.lower():
            item_power = i
        if "damage per second" in line.lower():
            dps = i
    base_value = masterwork if masterwork else item_power
    if is_weapon(item.item_type):
        start = dps + 2
    elif is_jewelry(item.item_type):
        start = base_value
    elif is_armor(item.item_type):
        start = base_value + 1
    elif item.item_type == ItemType.Shield:
        start = base_value + 3
    start += 1
    return tts_section[start : start + length]


def _get_item_rarity(data: str) -> ItemRarity | None:
    res = rapidfuzz.process.extractOne(data, [rar.value for rar in ItemRarity], scorer=rapidfuzz.distance.Levenshtein.distance)
    try:
        return ItemRarity(res[0]) if res else None
    except ValueError:
        return None


def _get_item_type(data: str):
    res = rapidfuzz.process.extractOne(data, [it.value for it in ItemType], scorer=rapidfuzz.distance.Levenshtein.distance)
    try:
        return ItemType(res[0]) if res else None
    except ValueError:
        return None


def _is_codex_upgrade(tts_section: list[str], item: Item) -> bool:
    return any("upgrades an aspect in the codex of power on salvage" in line.lower() for line in tts_section)


def read_descr_mixed(img_item_descr: np.ndarray) -> Item | None:
    tts_section = copy.copy(src.tts.LAST_ITEM)
    if not tts_section:
        return None
    if (item := _create_base_item_from_tts(tts_section)) is None:
        return None
    if any(
        [
            is_consumable(item.item_type),
            is_mapping(item.item_type),
            is_socketable(item.item_type),
            item.item_type in [ItemType.Material, ItemType.Tribute],
        ]
    ):
        return item
    if all([not is_armor(item.item_type), not is_jewelry(item.item_type), not is_weapon(item.item_type)]):
        return None

    if (sep_short_match := find_seperator_short(img_item_descr)) is None:
        LOGGER.warning("Could not detect item_seperator_short.")
        screenshot("failed_seperator_short", img=img_item_descr)
        return None
    futures = {"sep_long": TP.submit(find_seperators_long, img_item_descr, sep_short_match)}

    affix_bullets = find_affix_bullets(img_item_descr, sep_short_match)
    sep_long_match = futures["sep_long"].result() if futures["sep_long"] is not None else None
    if sep_long_match is None:
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
    else:
        # check how many affix bullets are below the long separator. if there are more below, then the long separator is the inherent separator.
        inherent_sep = (None, 0)
        for sep in sep_long_match:
            candidate = (sep, len([True for bullet in affix_bullets if bullet.center[1] > sep.center[1]]))
            if candidate[1] > inherent_sep[1]:
                inherent_sep = candidate
        if inherent_sep[0] is None:
            number_inherents = 0
        else:
            number_inherents = len([True for bullet in affix_bullets if bullet.center[1] < inherent_sep[0].center[1]])
        inherent_affix_bullets = affix_bullets[:number_inherents]
        affix_bullets = affix_bullets[number_inherents:]

    item.codex_upgrade = _is_codex_upgrade(tts_section, item)

    return _add_affixes_from_tts_mixed(tts_section, item, inherent_affix_bullets, affix_bullets)


def read_descr() -> Item | None:
    tts_section = copy.copy(src.tts.LAST_ITEM)
    if not tts_section:
        return None
    if (item := _create_base_item_from_tts(tts_section)) is None:
        return None
    if any(
        [
            is_consumable(item.item_type),
            is_mapping(item.item_type),
            is_socketable(item.item_type),
            item.item_type in [ItemType.Material, ItemType.Tribute],
        ]
    ):
        return item
    if all([not is_armor(item.item_type), not is_jewelry(item.item_type), not is_weapon(item.item_type)]):
        return None

    item.codex_upgrade = _is_codex_upgrade(tts_section, item)
    return _add_affixes_from_tts(tts_section, item)
