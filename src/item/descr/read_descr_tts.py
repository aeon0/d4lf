import copy
import logging

import numpy as np
import rapidfuzz

import src.tts
from src import TP
from src.dataloader import Dataloader
from src.item.data.affix import Affix, AffixType
from src.item.data.aspect import Aspect
from src.item.data.item_type import ItemType, is_armor, is_jewelry, is_weapon
from src.item.data.rarity import ItemRarity
from src.item.descr.text import clean_str, closest_match, find_number
from src.item.descr.texture import find_affix_bullets, find_seperator_short, find_seperators_long
from src.item.models import Item
from src.utils.window import screenshot

LOGGER = logging.getLogger(__name__)


def create_item_from_tts(tts_item: list[str]) -> Item | None:
    if tts_item[0] == "Compass":
        return Item(rarity=ItemRarity.Common, item_type=ItemType.Compass)
    if tts_item[0] == "Nightmare Sigil":
        return Item(rarity=ItemRarity.Common, item_type=ItemType.Sigil)

    if any(word in tts_item[0] for word in ["Tribute of"]):
        search_string = tts_item[0].lower()
    else:
        search_string = tts_item[1].lower().replace("ancestral", "").strip()
    item = Item()
    search_string_split = search_string.split(" ")
    res = rapidfuzz.process.extractOne(
        search_string_split[0], [rar.value for rar in ItemRarity], scorer=rapidfuzz.distance.Levenshtein.distance
    )
    try:
        item.rarity = ItemRarity(res[0]) if res else None
    except ValueError:
        return None
    res = rapidfuzz.process.extractOne(
        " ".join(search_string_split[1:]), [it.value for it in ItemType], scorer=rapidfuzz.distance.Levenshtein.distance
    )
    try:
        item.item_type = ItemType(res[0]) if res else None
    except ValueError:
        return None
    for _i, line in enumerate(tts_item):
        if "item power" in line.lower():
            item.power = find_number(line)
            break
    return item


def get_affixes_from_tts_section(tts_section: list[str], item: Item, length: int):
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


def add_affixes_from_tts(tts_section, item, inherent_affix_bullets, affix_bullets):
    affixes = get_affixes_from_tts_section(
        tts_section,
        item,
        len(inherent_affix_bullets)
        + len([x for x in affix_bullets if any(x.name.startswith(s) for s in ["affix", "greater_affix", "rerolled"])]),
    )
    # the first len(inherent_affix_bullets) are inherent affixes
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
            name = closest_match(clean_str(affix), Dataloader().aspect_unique_dict)
            item.aspect = Aspect(
                name=name,
                loc=affix_bullets[i - len(inherent_affix_bullets) - len(affix_bullets)].center,
                text=affix,
                value=find_number(affix),
            )
    return item


def read_descr(img_item_descr: np.ndarray) -> Item | None:
    tts_section = copy.copy(src.tts.LAST_ITEM_SECTION)
    if not tts_section:
        return None
    if (item := create_item_from_tts(tts_section)) is None:
        return None
    if item.item_type in [ItemType.Material, ItemType.TemperManual, ItemType.Elixir, ItemType.Incense] or (
        item.rarity in [ItemRarity.Magic, ItemRarity.Common] and item.item_type != ItemType.Sigil
    ):
        return item

    if (sep_short_match := find_seperator_short(img_item_descr)) is None:
        LOGGER.warning("Could not detect item_seperator_short.")
        screenshot("failed_seperator_short", img=img_item_descr)
        return None
    futures = {}
    futures["sep_long"] = TP.submit(find_seperators_long, img_item_descr, sep_short_match)

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

    return add_affixes_from_tts(tts_section, item, inherent_affix_bullets, affix_bullets)
