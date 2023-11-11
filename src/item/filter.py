from item.models import Item
import yaml
import json
import os
import time
from pathlib import Path
from logger import Logger
from config import Config
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity


class Filter:
    affix_filters = dict()
    aspect_filters = dict()
    with open("assets/affixes.json", "r") as f:
        affix_dict = json.load(f)
    with open("assets/aspects.json", "r") as f:
        aspect_dict = json.load(f)
    files_loaded = False

    _initialized: bool = False
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Filter, cls).__new__(cls)
        return cls._instance

    def load_files(self):
        self.files_loaded = True
        profiles: list[str] = Config().general["profiles"]

        user = os.getlogin()
        custom_profile_path = Path(f"C:/Users/{user}/.d4lf/profiles")
        params_profile_path = Path(f"config/profiles")

        for profile_str in profiles:
            custom_file_path = custom_profile_path / f"{profile_str}.yaml"
            params_file_path = params_profile_path / f"{profile_str}.yaml"
            if custom_file_path.is_file():
                profile_path = custom_file_path
            elif params_file_path.is_file():
                profile_path = params_file_path
            else:
                Logger.error(f"Could not load profile {profile_str}. Checked: {custom_file_path}, {params_file_path}")
                continue

            with open(profile_path) as f:
                try:
                    config = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    if hasattr(e, "problem_mark"):
                        mark = e.problem_mark
                        Logger.error(f"Error in the YAML file {profile_path} at position: (line {mark.line + 1}, column {mark.column + 1})")
                    else:
                        Logger.error(f"Error in the YAML file {profile_path}: {e}")
                    continue
                except Exception as e:
                    Logger.error(f"An unexpected error occurred loading YAML file {profile_path}: {e}")
                    continue

                info_str = f"Loading profile {profile_str}: "

                if config is not None and "Affixes" in config:
                    info_str += "Affixes "
                    self.affix_filters[profile_str] = config["Affixes"]
                    if config["Affixes"] is None:
                        Logger.error(f"Empty Affixes section in {profile_str}. Remove it")
                        return
                    # Sanity check on the item types
                    for filter_dict in self.affix_filters[profile_str]:
                        for filter_name, filter_data in filter_dict.items():
                            user_item_types = (
                                [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
                            )
                            invalid_types = []
                            for val in user_item_types:
                                try:
                                    ItemType(val)
                                except ValueError:
                                    invalid_types.append(val)
                            if invalid_types:
                                Logger.warning(f"Warning: Invalid ItemTypes in filter {filter_name}: {', '.join(invalid_types)}")
                    # Sanity check on the affixes
                    for filter_dict in self.affix_filters[profile_str]:
                        for filter_name, filter_data in filter_dict.items():
                            user_affix_pool = (
                                [filter_data["affixPool"]] if isinstance(filter_data["affixPool"], str) else filter_data["affixPool"]
                            )
                            invalid_affixes = []
                            if user_affix_pool is None:
                                continue
                            for affix in user_affix_pool:
                                affix_name = affix if isinstance(affix, str) else affix[0]
                                if affix_name not in self.affix_dict:
                                    invalid_affixes.append(affix_name)
                            if invalid_affixes:
                                Logger.warning(f"Warning: Invalid Affixes in filter {filter_name}: {', '.join(invalid_affixes)}")

                if config is not None and "Aspects" in config:
                    info_str += "Aspects "
                    self.aspect_filters[profile_str] = config["Aspects"]
                    if config["Aspects"] is None:
                        Logger.error(f"Empty Aspects section in {profile_str}. Remove it")
                        return
                    invalid_aspects = []
                    for aspect in self.aspect_filters[profile_str]:
                        aspect_name = aspect if isinstance(aspect, str) else aspect[0]
                        if aspect_name not in self.aspect_dict:
                            invalid_aspects.append(aspect_name)
                    if invalid_aspects:
                        Logger.warning(f"Warning: Invalid Aspect: {', '.join(invalid_aspects)}")

                Logger.info(info_str)

    def should_keep(self, item: Item) -> tuple[bool, bool, list[str]]:
        if not self.files_loaded:
            self.load_files()

        if item.rarity is ItemRarity.Unique:
            Logger.info(f"Matched: Unique")
            return True, False, []

        for profile_str, affix_filter in self.affix_filters.items():
            for filter_dict in affix_filter:
                for filter_name, filter_data in filter_dict.items():
                    filter_item_types = [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
                    filter_min_power = filter_data["minPower"]
                    filter_affix_pool = (
                        [filter_data["affixPool"]] if isinstance(filter_data["affixPool"], str) else filter_data["affixPool"]
                    )
                    filter_min_affix_count = filter_data["minAffixCount"]

                    if item.type.value not in filter_item_types or (
                        item.power is not None and filter_min_power is not None and item.power < filter_min_power
                    ):
                        continue

                    matched_affixes = []
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
                                    matched_affixes.append(name)
                            elif any(a.type == name for a in item.affixes):
                                matched_affixes.append(name)

                    if filter_min_affix_count is None or len(matched_affixes) >= filter_min_affix_count:
                        affix_debug_msg = [affix.type for affix in item.affixes]
                        Logger.info(f"Matched {profile_str}.{filter_name}: {affix_debug_msg}")
                        return True, True, matched_affixes

        if item.aspect:
            for profile_str, aspect_filter in self.aspect_filters.items():
                for filter_data in aspect_filter:
                    aspect_name, *rest = filter_data if isinstance(filter_data, list) else [filter_data]
                    threshold = rest[0] if rest else None
                    condition = rest[1] if len(rest) > 1 else "larger"

                    if item.aspect.type == aspect_name:
                        if (
                            threshold is None
                            or item.aspect.value is None
                            or (condition == "larger" and item.aspect.value >= threshold)
                            or (condition == "smaller" and item.aspect.value <= threshold)
                        ):
                            Logger.info(f"Matched {profile_str}.Aspects: [{item.aspect.type}, {item.aspect.value}]")
                            return True, False, []

        return False, False, []
