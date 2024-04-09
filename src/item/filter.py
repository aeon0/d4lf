import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from config.loader import IniConfigLoader
from config.models import ProfileModel, UniqueModel, SigilModel, AffixAspectFilterModel, ComparisonType
from dataloader import Dataloader
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item
from logger import Logger


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
    def _check_item_types(filters):
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
    def _check_affix_pool(affix_pool, affix_dict, filter_name):
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
        self.sigil_filters: dict[str, SigilModel] = dict()
        self.unique_filters: dict[str, list[UniqueModel]] = dict()
        profiles: list[str] = IniConfigLoader().general.profiles

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
                    if config["Affixes"] is None:
                        Logger.error(f"Empty Affixes section in {profile_str}. Remove it")
                        return
                    self.affix_filters[profile_str] = config["Affixes"]
                    # Sanity check on the item types
                    self._check_item_types(self.affix_filters[profile_str])
                    # Sanity check on the affixes
                    for filter_dict in self.affix_filters[profile_str]:
                        for filter_name, filter_data in filter_dict.items():
                            if "affixPool" in filter_data:
                                self._check_affix_pool(filter_data["affixPool"], Dataloader().affix_dict, filter_name)
                            else:
                                filter_data["affixPool"] = []
                            if "inherentPool" in filter_data:
                                self._check_affix_pool(filter_data["inherentPool"], Dataloader().affix_dict, filter_name)

                if config is not None and "Sigils" in config:
                    info_str += "Sigils "
                    data = ProfileModel(name=profile_str, **config)
                    if data.Sigils is None:
                        Logger.error(f"Empty Sigils section in {profile_str}. Remove it")
                        return
                    self.sigil_filters[data.name] = data.Sigils

                if config is not None and "Aspects" in config:
                    info_str += "Aspects "
                    if config["Aspects"] is None:
                        Logger.error(f"Empty Aspects section in {profile_str}. Remove it")
                        return
                    self.aspect_filters[profile_str] = config["Aspects"]
                    invalid_aspects = []
                    for aspect in self.aspect_filters[profile_str]:
                        aspect_name = aspect if isinstance(aspect, str) else aspect[0]
                        if aspect_name not in Dataloader().aspect_dict:
                            invalid_aspects.append(aspect_name)
                    if invalid_aspects:
                        Logger.warning(f"Warning: Invalid Aspect: {', '.join(invalid_aspects)}")

                if config is not None and "Uniques" in config:
                    info_str += "Uniques"
                    data = ProfileModel(name=profile_str, **config)
                    if not data.Uniques:
                        Logger.error(f"Empty Uniques section in {profile_str}. Remove it")
                        return
                    self.unique_filters[data.name] = data.Uniques

                Logger.info(info_str)

        self.last_loaded = time.time()

    def _did_files_change(self) -> bool:
        if self.last_loaded is None:
            return True
        return any(os.path.getmtime(file_path) > self.last_loaded for file_path in self.all_file_pathes)

    @staticmethod
    def _check_item_aspect(expected_aspect: AffixAspectFilterModel, item_aspect: Aspect) -> bool:
        if expected_aspect.name != item_aspect.type:
            return False
        if expected_aspect.value is not None:
            if item_aspect.value is None:
                return False
            if not (expected_aspect.comparison == ComparisonType.larger and item_aspect.value >= expected_aspect.value) or (
                    expected_aspect.comparison == ComparisonType.smaller and item_aspect.value <= expected_aspect.value
            ):
                return False
        return True

    @staticmethod
    def _check_item_power(min_power: int, item_power: int, max_power: int = sys.maxsize) -> bool:
        return min_power <= item_power <= max_power

    @staticmethod
    def _check_item_type(expected_item_types: list[ItemType], item_type: ItemType) -> bool:
        return item_type in expected_item_types

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

    def _check_non_unique_item(self, item: Item) -> FilterResult:
        # TODO replace me next league
        res = FilterResult(False, [])
        if item.rarity != ItemRarity.Unique and item.type != ItemType.Sigil:
            for profile_str, affix_filter in self.affix_filters.items():
                for filter_dict in affix_filter:
                    for filter_name, filter_data in filter_dict.items():
                        filter_min_affix_count = (
                            filter_data["minAffixCount"]
                            if "minAffixCount" in filter_data and filter_data["minAffixCount"] is not None
                            else 0
                        )
                        max_power = filter_data["maxPower"] if "maxPower" in filter_data and filter_data["maxPower"] is not None else 9999
                        min_power = filter_data["minPower"] if "minPower" in filter_data and filter_data["minPower"] is not None else 1
                        power_ok = self._check_item_power(max_power=max_power, min_power=min_power, item_power=item.power)
                        if "itemType" not in filter_data:
                            type_ok = True
                        else:
                            filter_item_type_list = [
                                ItemType(val)
                                for val in (
                                    [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
                                )
                            ]
                            type_ok = self._check_item_type(filter_item_type_list, item.type)
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
                            Logger.info(f"Matched {profile_str}.Affixes.{filter_name}: {affix_debug_msg}")
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
        return res

    def _check_sigil(self, item: Item) -> FilterResult:
        res = FilterResult(False, [])
        if (
                len(self.sigil_filters.items()) == 0
        ):  # in this intermedia version there are no profiles with Sigils = None since they would have been filtered on load
            res.keep = True
            res.matched.append(MatchedFilter(""))
        for profile_name, profile_filter in self.sigil_filters.items():
            # check item power
            if not self._check_item_power(max_power=profile_filter.maxTier, min_power=profile_filter.minTier, item_power=item.power):
                continue
            # check affix TODO
            if profile_filter.blacklist and self._match_affixes(profile_filter["blacklist"], item.affixes + item.inherent):
                continue
            if profile_filter.whitelist and not self._match_affixes(profile_filter["whitelist"], item.affixes + item.inherent):
                continue
            Logger.info(f"Matched {profile_name}.Sigils")
            res.keep = True
            res.matched.append(MatchedFilter(f"{profile_name}"))
        return res

    def _check_unique_item(self, item: Item) -> FilterResult:
        res = FilterResult(False, [])
        for profile_name, profile_filter in self.unique_filters.items():
            for filter_item in profile_filter:
                # check item type
                if not self._check_item_type(expected_item_types=filter_item.itemType, item_type=item.type):
                    continue
                # check item power
                if not self._check_item_power(min_power=filter_item.minPower, item_power=item.power):
                    continue
                # check aspect
                if (
                        item.aspect is None
                        or filter_item.aspect is None
                        or not self._check_item_aspect(expected_aspect=filter_item.aspect, item_aspect=item.aspect)
                ):
                    continue
                # check affixes TODO
                filter_item.setdefault("affixPool", [])
                matched_affixes = self._match_affixes([] if "affixPool" not in filter_item else filter_item["affixPool"], item.affixes)
                if len(matched_affixes) != len(filter_item["affixPool"]):
                    continue
                Logger.info(f"Matched {profile_name}.Uniques: {item.aspect.type}")
                res.keep = True
                res.matched.append(MatchedFilter(f"{profile_name}.{item.aspect.type}", did_match_aspect=True))
        return res

    def should_keep(self, item: Item) -> FilterResult:
        if not self.files_loaded or self._did_files_change():
            self.load_files()

        res = FilterResult(False, [])

        if item.type is None or item.power is None:
            return res

        if item.type == ItemType.Sigil:
            return self._check_sigil(item)

        if item.rarity != ItemRarity.Unique and item.type != ItemType.Sigil:
            return self._check_non_unique_item(item)

        if item.rarity == ItemRarity.Unique:
            return self._check_unique_item(item)

        return res
