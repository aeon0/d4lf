from item.models import Item
from dataclasses import dataclass, field
import yaml
import json
import os
import time
from pathlib import Path
from logger import Logger
from config import Config
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.data.affix import Affix


@dataclass
class MatchedFilter:
    profile: str
    matched_affixes: list[str] = field(default_factory=list)
    did_match_aspect: bool = False


@dataclass
class FilterResult:
    keep: bool
    matched: list[MatchedFilter]


class Filter:
    affix_filters = dict()
    aspect_filters = dict()
    unique_filters = dict()
    sigil_filters = dict()
    with open("assets/affixes.json", "r") as f:
        affix_dict = json.load(f)
    with open("assets/aspects.json", "r") as f:
        aspect_dict = json.load(f)
    with open("assets/aspects_unique.json", "r") as f:
        aspect_unique_dict = json.load(f)
    with open("assets/sigils.json", "r") as f:
        sigil_dict_all = json.load(f)
        sigil_dict = {**sigil_dict_all["negative"], **sigil_dict_all["positive"], **sigil_dict_all["inherent"]}

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
    def check_affix_pool(affix_pool, affix_dict, filter_name):
        user_affix_pool = affix_pool
        invalid_affixes = []
        if user_affix_pool is None:
            return
        for affix in user_affix_pool:
            if isinstance(affix, dict) and "any_of" in affix:
                affix_list = affix["any_of"] if affix["any_of"] is not None else []
            else:
                affix_list = [affix]
            for a in affix_list:
                affix_name = a if isinstance(a, str) else a[0]
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
            with open(profile_path, encoding="utf-8") as f:
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
                    for filter_dict in self.affix_filters[profile_str]:
                        for filter_name, filter_data in filter_dict.items():
                            if "affixPool" in filter_data:
                                self.check_affix_pool(filter_data["affixPool"], self.affix_dict, filter_name)
                            else:
                                filter_data["affixPool"] = []
                            if "inherentPool" in filter_data:
                                self.check_affix_pool(filter_data["inherentPool"], self.affix_dict, filter_name)

                if config is not None and "Sigils" in config:
                    info_str += "Sigils "
                    self.sigil_filters[profile_str] = config["Sigils"]
                    if config["Sigils"] is None:
                        Logger.error(f"Empty Sigils section in {profile_str}. Remove it")
                        return
                    # Sanity check on the sigil affixes
                    if "blacklist" not in self.sigil_filters[profile_str]:
                        self.sigil_filters[profile_str]["blacklist"] = []
                    self.check_affix_pool(self.sigil_filters[profile_str]["blacklist"], self.sigil_dict, f"{profile_str}.Sigils")

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
                    # Sanity check for unique aspects
                    invalid_uniques = []
                    for unique in self.unique_filters[profile_str]:
                        if "aspect" not in unique:
                            Logger.warning(f"Warning: Unique missing mandatory 'aspect' field in {profile_str} profile")
                            continue
                        unique_name = unique["aspect"] if isinstance(unique["aspect"], str) else unique["aspect"][0]
                        if unique_name not in self.aspect_unique_dict:
                            invalid_uniques.append(unique_name)
                        elif "affixPool" in unique:
                            self.check_affix_pool(unique["affixPool"], self.affix_dict, unique_name)
                    if invalid_uniques:
                        Logger.warning(f"Warning: Invalid Unique: {', '.join(invalid_uniques)}")

                Logger.info(info_str)

        self.last_loaded = time.time()

    def _did_files_change(self) -> bool:
        if self.last_loaded is None:
            return True

        for file_path in self.all_file_pathes:
            if os.path.getmtime(file_path) > self.last_loaded:
                return True
        return False

    def _check_sigil_tier(self, filter_data: dict, item: Item) -> bool:
        min_tier = filter_data["minTier"] if "minTier" in filter_data and filter_data["minTier"] is not None else 0
        max_tier = filter_data["maxTier"] if "maxTier" in filter_data and filter_data["maxTier"] is not None else 9999
        return min_tier <= item.power <= max_tier

    def _check_power(self, filter_data: dict, item: Item) -> bool:
        filter_min_power = filter_data["minPower"] if "minPower" in filter_data else None
        item_power_ok = item.power is None or filter_min_power is None or item.power >= filter_min_power
        return item_power_ok

    def _check_item_type(self, filter_data: dict, item: Item) -> bool:
        if "itemType" not in filter_data or filter_data["itemType"] is None:
            filter_item_types = None
        else:
            filter_item_types = [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
        item_type_ok = item.type is None or filter_item_types is None or item.type.value in filter_item_types
        return item_type_ok

    def _match_affixes(self, filter_affix_pool: list, item_affix_pool: list[Affix]) -> list:
        item_affix_pool = item_affix_pool[:]
        matched_affixes = []
        if filter_affix_pool is None:
            return matched_affixes
        filter_affix_pool = [filter_affix_pool] if isinstance(filter_affix_pool, str) else filter_affix_pool

        for affix in filter_affix_pool:
            if isinstance(affix, dict) and "any_of" in affix:
                any_of_matched = self._match_affixes(affix["any_of"], item_affix_pool)
                if len(any_of_matched) > 0:
                    name = any_of_matched[0]
                    item_affix_pool = [a for a in item_affix_pool if a.type != name]
                    matched_affixes.append(name)
            else:
                name, *rest = affix if isinstance(affix, list) else [affix]
                threshold = rest[0] if rest else None
                condition = rest[1] if len(rest) > 1 else "larger"

                item_affix_value = next((a.value for a in item_affix_pool if a.type == name), None)
                if item_affix_value is not None:
                    if (
                        threshold is None
                        or (isinstance(condition, str) and condition == "larger" and item_affix_value >= threshold)
                        or (isinstance(condition, str) and condition == "smaller" and item_affix_value <= threshold)
                    ):
                        item_affix_pool = [a for a in item_affix_pool if a.type != name]
                        matched_affixes.append(name)
                elif any(a.type == name for a in item_affix_pool):
                    item_affix_pool = [a for a in item_affix_pool if a.type != name]
                    matched_affixes.append(name)
        return matched_affixes

    def should_keep(self, item: Item) -> FilterResult:
        if not self.files_loaded or self._did_files_change():
            self.load_files()

        res = FilterResult(False, [])

        if item.type is None or item.power is None:
            return res

        # Filter Sigils
        if item.type == ItemType.Sigil:
            if len(self.sigil_filters.items()) == 0:
                res.keep = True
                res.matched.append(MatchedFilter(""))
            for profile_str, filter_data in self.sigil_filters.items():
                tier_ok = self._check_sigil_tier(filter_data, item)
                if not tier_ok:
                    continue
                matched_blacklist_affixes = self._match_affixes(filter_data["blacklist"], item.affixes)
                matched_blacklist_inherent_affixes = self._match_affixes(filter_data["blacklist"], item.inherent)
                if (len(matched_blacklist_affixes) + len(matched_blacklist_inherent_affixes)) == 0:
                    res.keep = True
                    res.matched.append(MatchedFilter(f"{profile_str}.Sigil"))

        # Filter Magic, Rare, Legendary
        if item.rarity != ItemRarity.Unique and item.type != ItemType.Sigil:
            for profile_str, affix_filter in self.affix_filters.items():
                for filter_dict in affix_filter:
                    for filter_name, filter_data in filter_dict.items():
                        filter_min_affix_count = (
                            filter_data["minAffixCount"]
                            if "minAffixCount" in filter_data and filter_data["minAffixCount"] is not None
                            else 0
                        )
                        power_ok = self._check_power(filter_data, item)
                        type_ok = self._check_item_type(filter_data, item)
                        if not power_ok or not type_ok:
                            continue
                        matched_affixes = self._match_affixes(filter_data["affixPool"], item.affixes)
                        affixes_ok = filter_min_affix_count is None or len(matched_affixes) >= filter_min_affix_count
                        inherent_ok = True
                        matched_inherent = []
                        if "inherentPool" in filter_data:
                            matched_inherent = self._match_affixes(filter_data["inherentPool"], item.inherent)
                            inherent_ok = len(matched_inherent) > 0
                        if affixes_ok and inherent_ok:
                            all_matched_affixes = matched_affixes + matched_inherent
                            affix_debug_msg = [name for name in all_matched_affixes]
                            Logger.info(f"Matched {profile_str}.{filter_name}: {affix_debug_msg}")
                            res.keep = True
                            res.matched.append(MatchedFilter(f"{profile_str}.{filter_name}", all_matched_affixes))

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
                                or (isinstance(condition, str) and condition == "larger" and item.aspect.value >= threshold)
                                or (isinstance(condition, str) and condition == "smaller" and item.aspect.value <= threshold)
                            ):
                                Logger.info(f"Matched {profile_str}.Aspects: [{item.aspect.type}, {item.aspect.value}]")
                                res.keep = True
                                res.matched.append(MatchedFilter(f"{profile_str}.Aspects", did_match_aspect=True))

        # Filter Uniques
        if item.rarity == ItemRarity.Unique:
            for profile_str, unique_filter in self.unique_filters.items():
                for filter_dict in unique_filter:
                    unique_name, *rest = filter_dict["aspect"] if isinstance(filter_dict["aspect"], list) else [filter_dict["aspect"]]
                    threshold = rest[0] if rest else None
                    condition = rest[1] if len(rest) > 1 else "larger"

                    if item.aspect.type == unique_name:
                        if (
                            threshold is None
                            or item.aspect.value is None
                            or (isinstance(condition, str) and condition == "larger" and item.aspect.value >= threshold)
                            or (isinstance(condition, str) and condition == "smaller" and item.aspect.value <= threshold)
                        ):
                            filter_affix_pool = [] if "affixPool" not in filter_dict else filter_dict["affixPool"]
                            filter_min_affix_count = len(filter_affix_pool) if filter_affix_pool is not None else 0
                            power_ok = self._check_power(filter_dict, item)
                            if not power_ok:
                                continue
                            matched_affixes = self._match_affixes(filter_affix_pool, item.affixes)
                            if filter_min_affix_count is None or len(matched_affixes) >= filter_min_affix_count:
                                Logger.info(f"Matched {profile_str}.Unique: [{item.aspect.type}, {item.aspect.value}]")
                                res.keep = True
                                res.matched.append(MatchedFilter(f"{profile_str}.{item.aspect.type}", did_match_aspect=True))

        return res
