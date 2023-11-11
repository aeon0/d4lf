import numpy as np
import time
import cv2
from logger import Logger
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.models import Item
from template_finder import search
from utils.ocr.read import image_to_text
from utils.image_operations import crop, color_filter
from utils.window import screenshot
import re
import json
from rapidfuzz import process
from config import Config


# Some aspects have their variable number as second (number_idx_1) or third (number_idx_2)
ASPECT_NUMBER_AT_IDX1 = [
    "frostbitten_aspect",
    "aspect_of_artful_initiative",
    "aspect_of_noxious_ice",
    "elementalists_aspect",
    "snowveiled_aspect",
    "aspect_of_might",
    "assimilation_aspect",
    "exploiters_aspect",
    "aspect_of_audacity",
    "ghostwalker_aspect",
    "aspect_of_slaughter",
    "aspect_of_tempering_blows",
    "aspect_of_ancestral_charge",
    "aspect_of_encroaching_wrath",
    "brawlers_aspect",
    "devilish_aspect",
    "earthstrikers_aspect",
    "steadfast_berserkers_aspect",
    "windlasher_aspect",
    "bear_clan_berserkers_aspect",
    "aspect_of_mending_stone",
    "aspect_of_metamorphic_stone",
    "aspect_of_the_stampede",
    "aspect_of_the_trampled_earth",
    "lightning_dancers_aspect",
    "raw_might_aspect",
    "aspect_of_decay",
    "osseous_gale_aspect",
    "rotting_aspect",
    "aspect_of_exposed_flesh",
    "coldbringers_aspect",
    "aspect_of_uncanny_treachery",
    "aspect_of_lethal_dusk",
    "enshrouding_aspect",
    "aspect_of_arrow_storms",
    "aspect_of_bursting_venoms",
    "aspect_of_pestilent_points",
    "aspect_of_synergy",
    "icy_alchemists_aspect",
    "toxic_alchemists_aspect",
    "trickshot_aspect",
    "snowguards_aspect",
    "aspect_of_frozen_orbit",
    "serpentine_aspect",
]
ASPECT_NUMBER_AT_IDX2 = [
    "aspect_of_retribution",
    "aspect_of_serration",
    "aspect_of_untimely_death",
]

ERROR_MAP = {
    "thoms": "thorns",
    "seythe": "scythe",
    "@arbarian": "(barbarian",
    "two-handed!": "two-handed",
    "two-handed.": "two-handed",
}

affix_dict = dict()
with open("assets/affixes.json", "r") as f:
    affix_dict = json.load(f)

aspect_dict = dict()
with open("assets/aspects.json", "r") as f:
    aspect_dict = json.load(f)


def _closest_match(target, candidates, min_score=89):
    keys, values = zip(*candidates.items())
    result = process.extractOne(target, values)
    if result and result[1] >= min_score:
        matched_key = keys[values.index(result[0])]
        return matched_key
    return None


def _closest_to(value, choices):
    return min(choices, key=lambda x: abs(x - value))


def _find_number(s, idx: int = 0):
    s = re.sub(r",", "", s)  # remove commas because of large numbers having a comma seperator
    matches = re.findall(r"[+-]?(\d+\.\d+|\.\d+|\d+\.?|\d+)\%?", s)
    if "Up to a 5%" in s:
        number = matches[1] if len(matches) > 1 else None
    else:
        number = matches[idx] if matches and len(matches) > idx else None
    if number is not None:
        return float(number.replace("+", "").replace("%", ""))
    return None


def _remove_text_after_first_keyword(text, keywords):
    for keyword in keywords:
        match = re.search(re.escape(keyword), text)
        if match:
            return text[: match.start()]
    return text


def _clean_str(s):
    cleaned_str = re.sub(r"(\+)?\d+(\.\d+)?%?", "", s)  # Remove numbers and trailing % or preceding +
    cleaned_str = re.sub(r"[\[\]+\-:%\']", "", cleaned_str)  # Remove [ and ] and leftover +, -, %, :, '
    cleaned_str = re.sub(
        r"\((rogue|barbarian|druid|sorcerer|necromancer) only\)", "", cleaned_str
    )  # this is not included in our affix table
    cleaned_str = _remove_text_after_first_keyword(cleaned_str, ["requires level", "requires lev", "account", "sell value"])
    cleaned_str = re.sub(
        r"(scroll up|account bound|requires level|sell value|durability|barbarian|rogue|sorceress|druid|necromancer|not useable|by your class|by your clas)",
        "",
        cleaned_str,
    )  # Remove new terms
    cleaned_str = " ".join(cleaned_str.split())  # Remove extra spaces
    return cleaned_str


def read_descr(rarity: ItemRarity, img_item_descr: np.ndarray) -> Item:
    item = Item(rarity)
    img_height, img_width, _ = img_item_descr.shape
    line_height = Config().ui_offsets["item_descr_line_height"]

    # Detect textures (1)
    # =====================================
    start_tex_1 = time.time()
    refs = ["item_seperator_short_rare", "item_seperator_short_legendary"]
    roi = [0, 0, img_item_descr.shape[1], Config().ui_offsets["find_seperator_short_offset_top"]]
    if not (sep_short := search(refs, img_item_descr, 0.68, roi, True, mode="all", do_multi_process=False)).success:
        Logger.warning("Could not detect item_seperator_short.")
        screenshot("failed_seperator_short", img=img_item_descr)
        return None
    sorted_matches = sorted(sep_short.matches, key=lambda match: match.center[1])
    sep_short_match = sorted_matches[0]
    # print("-----")
    # print("Runtime (start_tex_1): ", time.time() - start_tex_1)

    # Item Type and Item Power
    # =====================================
    start_power = time.time()
    roi_top = [0, 0, int(img_width * 0.74), sep_short_match.center[1]]
    crop_top = crop(img_item_descr, roi_top)
    if rarity in [ItemRarity.Common, ItemRarity.Legendary]:
        # We check if it is a material
        mask, _ = color_filter(crop_top, Config().colors[f"material_color"], False)
        mean_val = np.mean(mask)
        if mean_val > 2.0:
            item.type = ItemType.Material
            return item
        elif rarity == ItemRarity.Common:
            return item
    concatenated_str = image_to_text(crop_top).text.lower().replace("\n", " ")
    idx = None
    # TODO: Handle common mistakes nicer
    if "item power" in concatenated_str:
        idx = concatenated_str.index("item power")
    elif "ttem power" in concatenated_str:
        idx = concatenated_str.index("ttem power")
    elif "item" in concatenated_str:
        idx = concatenated_str.index("item")
    if idx is not None:
        preceding_word = concatenated_str[:idx].split()[-1]
        if preceding_word.isdigit():
            item.power = int(preceding_word)
        elif "+" in preceding_word:
            item_power_numbers = preceding_word.split("+")
            item.power = int(item_power_numbers[0]) + int(item_power_numbers[1])
    max_length = 0
    last_char_idx = 0
    for error, correction in ERROR_MAP.items():
        concatenated_str = concatenated_str.replace(error, correction)
    for item_type in ItemType:
        if (found_idx := concatenated_str.rfind(item_type.value)) != -1:
            tmp_idx = found_idx + len(item_type.value)
            if tmp_idx >= last_char_idx and len(item_type.value) > max_length:
                item.type = item_type
                last_char_idx = tmp_idx
                max_length = len(item_type.value)
    # common mistake is that "Armor" is on a seperate line and can not be detected properly
    if item.type is None:
        if "chest" in concatenated_str or "armor" in concatenated_str:
            item.type = ItemType.Armor
    # common mistake that two-handed can not be added to the weapon type
    if "two-handed" in concatenated_str:
        if item.type == ItemType.Sword:
            item.type = ItemType.Sword2H
        if item.type == ItemType.Mace:
            item.type = ItemType.Mace2H
        if item.type == ItemType.Scythe:
            item.type = ItemType.Scythe2H
        if item.type == ItemType.Axe:
            item.type = ItemType.Axe2H

    if rarity == ItemRarity.Magic:
        return item

    if item.power is None or item.type is None:
        Logger().warning(f"Could not detect ItemPower and ItemType: {concatenated_str}")
        screenshot("failed_itempower_itemtype", img=img_item_descr)
        return None
    # print("Runtime (start_power): ", time.time() - start_power)

    # Detect textures (2)
    # =====================================
    start_tex_2 = time.time()
    roi_bullets = [0, sep_short_match.center[1], Config().ui_offsets["find_bullet_points_width"] + 20, img_height]
    if not (affix_bullets := search("affix_bullet_point", img_item_descr, 0.91, roi_bullets, True, mode="all")).success:
        if not (affix_bullets := search("affix_bullet_point_medium", img_item_descr, 0.87, roi_bullets, True, mode="all")).success:
            Logger.warning("Could not detect affix_bullet_points.")
            screenshot("failed_affix_bullet_points", img=img_item_descr)
            return None
    affix_bullets.matches = sorted(affix_bullets.matches, key=lambda match: match.center[1])
    # Depending on the item type we have to remove some of the topmost affixes as they are fixed
    remove_top_most = 1
    if item.type in [ItemType.Armor, ItemType.Helm, ItemType.Gloves]:
        remove_top_most = 0
    elif item.type in [ItemType.Ring]:
        remove_top_most = 2
    elif item.type in [ItemType.Shield]:
        remove_top_most = 4
    else:
        # default for: Pants, Amulets, Boots, All Weapons
        remove_top_most = 1
    affix_bullets.matches = affix_bullets.matches[remove_top_most:]
    if len(affix_bullets.matches) > 4:
        Logger.debug("Still too many bullet points, removing so we have only 4 left")
        affix_bullets.matches = affix_bullets.matches[-4:]
    empty_sockets = search("empty_socket", img_item_descr, 0.87, roi_bullets, True, mode="all")
    empty_sockets.matches = sorted(empty_sockets.matches, key=lambda match: match.center[1])
    refs = ["aspect_bullet_point", "aspect_bullet_point_medium"]
    aspect_bullets = search(refs, img_item_descr, 0.87, roi_bullets, True, mode="first")
    if rarity == ItemRarity.Legendary and not aspect_bullets.success:
        Logger.warning("Could not detect aspect_bullet for a legendary item.")
        screenshot("failed_aspect_bullet", img=img_item_descr)
        return None
    # print("Runtime (start_tex_2): ", time.time() - start_tex_2)

    # Affixes
    # =====================================
    start_affix = time.time()
    # Affix starts at first bullet point
    affix_start = [affix_bullets.matches[0].center[0] + line_height // 4, affix_bullets.matches[0].center[1] - int(line_height * 0.7)]
    # Affix ends at aspect bullet or empty sockets
    bottom_limit = 0
    if rarity == ItemRarity.Legendary:
        bottom_limit = aspect_bullets.matches[0].center[1]
    elif len(empty_sockets.matches) > 0:
        bottom_limit = empty_sockets.matches[0].center[1]
    if bottom_limit < affix_start[1]:
        bottom_limit = img_height
    # Calc full region of all affixes
    affix_width = img_width - affix_start[0]
    affix_height = bottom_limit - affix_start[1] - int(line_height * 0.4)
    full_affix_region = [*affix_start, affix_width, affix_height]
    crop_full_affix = crop(img_item_descr, full_affix_region)
    # cv2.imwrite("crop_full_affix.png", crop_full_affix)
    affix_lines = image_to_text(crop_full_affix).text.lower().split("\n")
    affix_lines = [line for line in affix_lines if line]  # remove empty lines
    # split affix text based on distance of affix bullet points
    delta_y_arr = [
        affix_bullets.matches[i].center[1] - affix_bullets.matches[i - 1].center[1] for i in range(1, len(affix_bullets.matches))
    ]
    delta_y_arr.append(None)
    line_idx = 0
    for dy in delta_y_arr:
        if dy is None:
            combined_lines = "\n".join(affix_lines[line_idx:])
        else:
            closest_value = _closest_to(dy, [line_height, line_height * 2, line_height * 3])
            if closest_value == line_height:
                lines_to_add = 1
            elif closest_value == line_height * 2:
                lines_to_add = 2
            else:  # closest_value == 75
                lines_to_add = 3
            combined_lines = "\n".join(affix_lines[line_idx : line_idx + lines_to_add])
            line_idx += lines_to_add
        combined_lines = combined_lines.replace("\n", " ")
        for error, correction in ERROR_MAP.items():
            combined_lines = combined_lines.replace(error, correction)
        cleaned_str = _clean_str(combined_lines)

        found_key = _closest_match(cleaned_str, affix_dict)
        found_value = _find_number(combined_lines)

        if found_key is not None:
            item.affixes.append(Affix(found_key, found_value, combined_lines))
        else:
            Logger.warning(f"Could not find affix: {cleaned_str}")
            screenshot("failed_affixes", img=img_item_descr)
            return None
    # print("Runtime (start_affix): ", time.time() - start_affix)

    # Aspect
    # =====================================
    start_aspect = time.time()
    if rarity == ItemRarity.Legendary:
        ab = aspect_bullets.matches[0].center
        bottom_limit = empty_sockets.matches[0].center[1] if len(empty_sockets.matches) > 0 else img_height
        dx_offset = line_height // 4
        dy_offset = int(line_height * 0.7)
        dy = bottom_limit - ab[1]
        roi_full_aspect = [ab[0] + dx_offset, ab[1] - dy_offset, img_width - ab[0] - dx_offset - 1, dy]
        img_full_aspect = crop(img_item_descr, roi_full_aspect)
        # cv2.imwrite("img_full_aspect.png", img_full_aspect)
        concatenated_str = image_to_text(img_full_aspect).text.lower().replace("\n", " ")
        cleaned_str = _clean_str(concatenated_str)
        found_key = _closest_match(cleaned_str, aspect_dict, min_score=77)

        if found_key in ASPECT_NUMBER_AT_IDX1:
            idx = 1
        elif found_key in ASPECT_NUMBER_AT_IDX2:
            idx = 2
        else:
            idx = 0
        found_value = _find_number(concatenated_str, idx)

        # Scale the aspect down to the canonical range if found on an item that scales it up
        if found_value is not None:
            if item.type is ItemType.Amulet:
                found_value /= 1.5
            # Possibly add Bow and Crossbow if those scale it up as well
            if item.type in [
                ItemType.Bow,
                ItemType.Crossbow,
                ItemType.Axe2H,
                ItemType.Sword2H,
                ItemType.Mace2H,
                ItemType.Scythe,
                ItemType.Polearm,
                ItemType.Staff,
            ]:
                found_value /= 2

        if found_key is not None:
            # Rapid detects 19 as 199
            if found_key == "rapid_aspect" and found_value == 199:
                found_value = 19
            item.aspect = Aspect(found_key, found_value, concatenated_str)
        else:
            Logger.warning(f"Could not find aspect: {cleaned_str}")
            screenshot("failed_aspect", img=img_item_descr)
            return None
    # print("Runtime (start_aspect): ", time.time() - start_aspect)

    return item
