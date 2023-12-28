import numpy as np
from item.models import Item, ItemRarity, ItemType
from utils.ocr.read import image_to_text
from utils.image_operations import crop, color_filter
from template_finder import TemplateMatch
from config import Config
from item.corrections import ERROR_MAP


def read_item_type(item: Item, img_item_descr: np.ndarray, sep_short_match: TemplateMatch) -> tuple[Item | None, str]:
    # Item Type and Item Power
    # =====================================
    # start_power = time.time()
    rarity = item.rarity
    _, img_width, _ = img_item_descr.shape
    roi_top = [0, 0, int(img_width * 0.74), sep_short_match.center[1]]
    crop_top = crop(img_item_descr, roi_top)
    concatenated_str = image_to_text(crop_top).text.lower().replace("\n", " ")

    if "sigil" in concatenated_str and "tier" in concatenated_str:
        # process sigil
        item.type = ItemType.Sigil
    elif rarity in [ItemRarity.Common, ItemRarity.Legendary]:
        # We check if it is a material
        mask, _ = color_filter(crop_top, Config().colors[f"material_color"], False)
        mean_val = np.mean(mask)
        if mean_val > 2.0:
            item.type = ItemType.Material
            return item, concatenated_str
        elif rarity == ItemRarity.Common:
            return item, concatenated_str

    if item.type == ItemType.Sigil:
        item.power = _find_sigil_tier(concatenated_str)
    else:
        item = _find_item_power_and_type(item, concatenated_str)

    if item.type is None:
        masked_red, _ = color_filter(crop_top, Config().colors[f"unusable_red"], False)
        crop_top[masked_red == 255] = [235, 235, 235]
        concatenated_str = image_to_text(crop_top).text.lower().replace("\n", " ")
        item = _find_item_power_and_type(item, concatenated_str)

    if item.rarity != ItemRarity.Magic and (item.power is None or item.type is None):
        return None, concatenated_str

    return item, concatenated_str
    # print("Runtime (start_power): ", time.time() - start_power)


def _find_item_power_and_type(item: Item, concatenated_str: str) -> Item:
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
            if item_power_numbers[0].isdigit() and item_power_numbers[1].isdigit():
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
    if "two-handed" in concatenated_str or "two- handed" in concatenated_str:
        if item.type == ItemType.Sword:
            item.type = ItemType.Sword2H
        elif item.type == ItemType.Mace:
            item.type = ItemType.Mace2H
        elif item.type == ItemType.Scythe:
            item.type = ItemType.Scythe2H
        elif item.type == ItemType.Axe:
            item.type = ItemType.Axe2H
    return item


def _find_sigil_tier(concatenated_str: str) -> int:
    idx = None
    for error, correction in ERROR_MAP.items():
        concatenated_str = concatenated_str.replace(error, correction)
    if "tier" in concatenated_str:
        idx = concatenated_str.index("tier")
    if idx is not None:
        following_word = concatenated_str[idx:].split()[1]
        if following_word.isdigit():
            return int(following_word)
    return None
