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
    unique_filters = dict()
    with open("assets/affixes.json", "r") as f:
        affix_dict = json.load(f)
    with open("assets/aspects.json", "r") as f:
        aspect_dict = json.load(f)
    files_loaded = False
    all_file_pathes = []
    last_loaded = None

    _initialized: bool = False
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Filter, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def check_item_types(filters):
        for filter_dict in filters:
            for filter_name, filter_data in filter_dict.items():
                user_item_types = [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
                if user_item_types is None:
                    Logger.warning(f"Warning: Missing itemtype in {filter_name}")
                    continue
                invalid_types = []
                for val in user_item_types:
                    try:
                        ItemType(val)
                    except ValueError:
                        invalid_types.append(val)
                if invalid_types:
                    Logger.warning(f"Warning: Invalid ItemTypes in filter {filter_name}: {', '.join(invalid_types)}")

    @staticmethod
    def check_affixes(filters, affix_dict):
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

    def load_files(self):
        self.files_loaded = True
        self.affix_filters = dict()
        self.aspect_filters = dict()
        self.unique_filters = dict()
        profiles: list[str] = Config().general["profiles"]

        user_dir = os.path.expanduser("~")
        custom_profile_path = Path(f"{user_dir}/.d4lf/profiles")
        params_profile_path = Path(f"config/profiles")
        self.all_file_pathes = []

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

            self.all_file_pathes.append(profile_path)
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
                    self.check_item_types(self.affix_filters[profile_str])
                    # Sanity check on the affixes
                    self.check_affixes(self.affix_filters[profile_str], self.affix_dict)

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

                if config is not None and "Uniques" in config:
                    info_str += "Uniques"
                    self.unique_filters[profile_str] = config["Uniques"]
                    if config["Uniques"] is None:
                        Logger.error(f"Empty Uniques section in {profile_str}. Remove it")
                        return
                    # Sanity check on the item types
                    self.check_item_types(self.unique_filters[profile_str])
                    # Sanity check on the affixes
                    self.check_affixes(self.unique_filters[profile_str], self.affix_dict)

                Logger.info(info_str)

        self.last_loaded = time.time()

    def _did_files_change(self) -> bool:
        if self.last_loaded is None:
            return True

        for file_path in self.all_file_pathes:
            if os.path.getmtime(file_path) > self.last_loaded:
                return True
        return False

    def should_keep(self, item: Item) -> tuple[bool, bool, list[str], str]:
        if not self.files_loaded or self._did_files_change():
            self.load_files()

        if item.type is None or item.power is None:
            return False, False, [], ""

        if item.rarity != ItemRarity.Unique:
            for profile_str, affix_filter in self.affix_filters.items():
                for filter_dict in affix_filter:
                    for filter_name, filter_data in filter_dict.items():
                        filter_item_types = (
                            [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
                        )
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
                            affix_debug_msg = [name for name in matched_affixes]
                            Logger.info(f"Matched {profile_str}.{filter_name}: {affix_debug_msg}")
                            return True, True, matched_affixes, f"{profile_str}.{filter_name}"

        if item.aspect and item.rarity != ItemRarity.Unique:
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
                            return True, False, [], f"{profile_str}.Aspects"

        if item.rarity == ItemRarity.Unique:
            for profile_str, unique_filter in self.unique_filters.items():
                for filter_dict in unique_filter:
                    for filter_name, filter_data in filter_dict.items():
                        filter_item_types = filter_data["itemType"]
                        filter_min_power = filter_data["minPower"]
                        filter_affix_pool = (
                            [filter_data["affixPool"]] if isinstance(filter_data["affixPool"], str) else filter_data["affixPool"]
                        )
                        filter_min_affix_count = len(filter_affix_pool)  # all have to match

                        matched_affixes = []
                        found_affixes = []
                        if filter_affix_pool is not None:
                            for affix in filter_affix_pool:
                                name, *rest = affix if isinstance(affix, list) else [affix]
                                threshold = rest[0] if rest else None
                                condition = rest[1] if len(rest) > 1 else "larger"

                                item_affix_value = next((a.value for a in item.affixes if a.type == name), None)

                                if any(a.type == name for a in item.affixes):
                                    found_affixes.append(name)

                                if item_affix_value is not None:
                                    if (
                                        threshold is None
                                        or (condition == "larger" and item_affix_value >= threshold)
                                        or (condition == "smaller" and item_affix_value <= threshold)
                                    ):
                                        matched_affixes.append(name)
                                elif any(a.type == name for a in item.affixes):
                                    matched_affixes.append(name)

                        item_type_ok = item.type.value in filter_item_types
                        item_power_ok = item.power is None or filter_min_power is None or item.power >= filter_min_power
                        if (
                            (filter_min_affix_count is None or len(matched_affixes) >= filter_min_affix_count)
                            and item_type_ok
                            and item_power_ok
                        ):
                            av = filter_data["aspectValue"] if "aspectValue" in filter_data else None
                            if av is not None:
                                rest = filter_data if isinstance(filter_data["aspectValue"], list) else [filter_data["aspectValue"]]
                                threshold = rest[0] if rest else None
                                condition = rest[1] if len(rest) > 1 else "larger"

                                aspect_ok = (
                                    item.aspect is None
                                    or item.aspect.value is None
                                    or threshold is None
                                    or (condition == "larger" and item.aspect.value >= threshold)
                                    or (condition == "smaller" and item.aspect.value <= threshold)
                                )

                                if aspect_ok:
                                    Logger.info(f"Matched {profile_str}.{filter_name}")
                                    return True, True, [], f"{profile_str}.{filter_name}"
                            else:
                                return True, True, [], f"{profile_str}.{filter_name}"

                        if filter_min_affix_count is not None and len(found_affixes) >= filter_min_affix_count:
                            return False, False, [], f"{profile_str}.{filter_name}"

            if not Config().general["whitelist_uniques"]:
                # We didnt find any match to that unique, if whitelist is false we return True
                return True, True, [], "unique.no_config"

        return False, False, [], ""
