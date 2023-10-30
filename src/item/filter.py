from item.models import Item
import yaml
import json
from logger import Logger
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity


affix_dict = dict()
with open("assets/affixes.json", "r") as f:
    affix_dict = json.load(f)

aspect_dict = dict()
with open("assets/aspects.json", "r") as f:
    aspect_dict = json.load(f)

with open("config/filter_affix.yaml") as f:
    config = yaml.safe_load(f)
    filters = config["Filters"]
    # Sanity check on the item types
    for filter_dict in filters:
        for filter_name, filter_data in filter_dict.items():
            user_item_types = [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
            invalid_types = []
            for val in user_item_types:
                try:
                    ItemType(val)
                except ValueError:
                    invalid_types.append(val)
            if invalid_types:
                Logger.warning(f"Warning: Invalid ItemTypes in filter {filter_name}: {', '.join(invalid_types)}")
    # Sanity check on the affixes
    for filter_dict in filters:
        for filter_name, filter_data in filter_dict.items():
            user_affix_pool = [filter_data["affixPool"]] if isinstance(filter_data["affixPool"], str) else filter_data["affixPool"]
            invalid_affixes = []
            if user_affix_pool is None:
                continue
            for affix in user_affix_pool:
                affix_name = affix if isinstance(affix, str) else affix[0]
                if affix_name not in affix_dict:
                    invalid_affixes.append(affix_name)
            if invalid_affixes:
                Logger.warning(f"Warning: Invalid Affixes in filter {filter_name}: {', '.join(invalid_affixes)}")

with open("config/filter_aspect.yaml") as f:
    config = yaml.safe_load(f)
    filter_aspects = config["Aspects"]
    # Sanity check on the aspects
    if filter_aspects is not None:
        invalid_aspects = []
        user_aspect_pool = [filter_aspects] if isinstance(filter_aspects, str) else filter_aspects
        for aspect in user_aspect_pool:
            aspect_name = aspect if isinstance(aspect, str) else aspect[0]
            if aspect_name not in aspect_dict:
                invalid_aspects.append(aspect_name)
        if invalid_aspects:
            Logger.warning(f"Warning: Invalid Aspect: {', '.join(invalid_aspects)}")


def should_keep(item: Item):
    if filter_aspects is None and item.rarity is ItemRarity.Legendary:
        Logger.info(f"Matched. Any Aspect.")
        return True

    if item.rarity is ItemRarity.Unique:
        Logger.info(f"Matched. Unique.")
        return True

    for filter_dict in filters:
        for filter_name, filter_data in filter_dict.items():
            filter_item_types = [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
            filter_min_power = filter_data["minPower"]
            filter_affix_pool = [filter_data["affixPool"]] if isinstance(filter_data["affixPool"], str) else filter_data["affixPool"]
            filter_min_affix_count = filter_data["minAffixCount"]

            if item.type.value not in filter_item_types or (item.power is not None and item.power < filter_min_power):
                continue

            matching_affix_count = 0
            if filter_affix_pool is not None:
                for affix in filter_affix_pool:
                    name, *rest = affix if isinstance(affix, list) else [affix]
                    threshold = rest[0] if rest else None
                    condition = rest[1] if len(rest) > 1 else "larger"

                    item_affix_value = next((a.value for a in item.affixes if a.type == name), None)

                    if item_affix_value is not None:
                        if (
                            threshold is None
                            or (condition == "larger" and item_affix_value >= threshold)
                            or (condition == "smaller" and item_affix_value <= threshold)
                        ):
                            matching_affix_count += 1
                    elif any(a.type == name for a in item.affixes):
                        matching_affix_count += 1

            if matching_affix_count >= filter_min_affix_count:
                Logger.info(f"Matched with affix filter: {filter_name}")
                return True

            if item.aspect:
                for filter_data in filter_aspects:
                    filter_aspect_pool = [filter_data] if isinstance(filter_data, str) else filter_data
                    for aspect in filter_aspect_pool:
                        aspect_name, *rest = aspect if isinstance(aspect, list) else [aspect]
                        threshold = rest[0] if rest else None
                        condition = rest[1] if len(rest) > 1 else "larger"

                        if item.aspect.type == aspect_name:
                            if (
                                threshold is None
                                or item.aspect.value is None
                                or (condition == "larger" and item.aspect.value >= threshold)
                                or (condition == "smaller" and item.aspect.value <= threshold)
                            ):
                                Logger.info(f"Matched with aspect filter: {filter_name}")
                                return True

    return False
