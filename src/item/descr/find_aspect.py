import numpy as np
import json
from config import Config
from template_finder import TemplateMatch
from item.descr.aspect_num_idx import ASPECT_NUMBER_AT_IDX1, ASPECT_NUMBER_AT_IDX2
from item.data.aspect import Aspect
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.descr.text import clean_str, closest_match, find_number
from utils.image_operations import crop
from template_finder import TemplateMatch
from utils.ocr.read import image_to_text
from item.descr.texture import find_aspect_search_area
from logger import Logger
from dataloader import Dataloader


def find_aspect(
    img_item_descr: np.ndarray, aspect_bullet: TemplateMatch, item_type: ItemType, rarity: ItemRarity
) -> tuple[Aspect | None, str]:
    if aspect_bullet is None:
        return None, ""

    roi_aspect = find_aspect_search_area(img_item_descr, aspect_bullet, rarity)
    img_full_aspect = crop(img_item_descr, roi_aspect)
    # cv2.imwrite("img_full_aspect.png", img_full_aspect)
    concatenated_str = image_to_text(img_full_aspect).text.lower().replace("\n", " ")
    cleaned_str = clean_str(concatenated_str)

    if rarity == ItemRarity.Legendary:
        found_key = closest_match(cleaned_str, Dataloader().aspect_dict)
        snoids = Dataloader().aspect_snoids
    else:
        found_key = closest_match(cleaned_str, Dataloader().aspect_unique_dict)
        snoids = Dataloader().aspect_unique_snoids

    if found_key is None:
        return None, cleaned_str

    if snoids[found_key] in ASPECT_NUMBER_AT_IDX1:
        idx = 1
    elif snoids[found_key] in ASPECT_NUMBER_AT_IDX2:
        idx = 2
    else:
        idx = 0
    found_value = find_number(concatenated_str, idx)

    # Scale the aspect down to the canonical range if found on an item that scales it up
    if found_value is not None and rarity == ItemRarity.Legendary:
        if item_type is ItemType.Amulet:
            found_value /= 1.5
        # Possibly add Bow and Crossbow if those scale it up as well
        if item_type in [
            ItemType.Bow,
            ItemType.Crossbow2H,
            ItemType.Axe2H,
            ItemType.Sword2H,
            ItemType.Mace2H,
            ItemType.Scythe,
            ItemType.Polearm,
            ItemType.Staff,
        ]:
            found_value /= 2

    Logger.debug(f"{found_key}: {found_value}")

    # Rapid detects 19 as 199 often
    if found_key == "rapid_aspect" and found_value == 199:
        found_value = 19
    loc = [aspect_bullet.center[0], aspect_bullet.center[1] - 2]
    return Aspect(found_key, found_value, concatenated_str, loc), cleaned_str
