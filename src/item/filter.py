import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from config.loader import IniConfigLoader
from config.models import (
    AffixAspectFilterModel,
    AffixFilterCountModel,
    AffixFilterModel,
    AspectFilterType,
    ComparisonType,
    DynamicItemFilterModel,
    ProfileModel,
    SigilFilterModel,
    UniqueModel,
)
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

    def _check_affixes(self, item: Item) -> FilterResult:
        res = FilterResult(False, [])
        if not self.affix_filters:
            return FilterResult(True, [])
        for profile_name, profile_filter in self.affix_filters.items():
            for filter_item in profile_filter:
                filter_name = next(iter(filter_item.root.keys()))
                filter_spec = filter_item.root[filter_name]
                # check item type
                if not self._match_item_type(expected_item_types=filter_spec.itemType, item_type=item.item_type):
                    continue
                # check item power
                if not self._match_item_power(min_power=filter_spec.minPower, item_power=item.power):
                    continue
                # check affixes
                matched_affixes = []
                if filter_spec.affixPool:
                    matched_affixes = self._match_affixes_count(expected_affixes=filter_spec.affixPool, item_affixes=item.affixes)
                    if not matched_affixes:
                        continue
                # check inherent
                matched_inherents = []
                if filter_spec.inherentPool:
                    matched_inherents = self._match_affixes_count(expected_affixes=filter_spec.inherentPool, item_affixes=item.inherent)
                    if not matched_inherents:
                        continue
                all_matches = matched_affixes + matched_inherents
                Logger.info(f"Matched {profile_name}.Affixes.{filter_name}: {all_matches}")
                res.keep = True
                res.matched.append(MatchedFilter(f"{profile_name}.{filter_name}", all_matches))
        return res

    @staticmethod
    def _check_aspect(item: Item) -> FilterResult:
        res = FilterResult(False, [])
        if IniConfigLoader().general.keep_aspects == AspectFilterType.none or (
            IniConfigLoader().general.keep_aspects == AspectFilterType.upgrade and not item.codex_upgrade
        ):
            return res
        Logger.info(f"Matched Aspects that updates codex")
        res.keep = True
        res.matched.append(MatchedFilter("Aspects", did_match_aspect=True))
        return res

    def _check_sigil(self, item: Item) -> FilterResult:
        res = FilterResult(False, [])
        if not self.sigil_filters.items():
            Logger.info("Matched Sigils")
            res.keep = True
            res.matched.append(MatchedFilter("default"))
        for profile_name, profile_filter in self.sigil_filters.items():
            # check item power
            if not self._match_item_power(max_power=profile_filter.maxTier, min_power=profile_filter.minTier, item_power=item.power):
                continue
            # check affix blacklist
            if profile_filter.blacklist and self._match_affixes_sigils(
                expected_affixes=profile_filter.blacklist, sigil_affixes=item.affixes + item.inherent
            ):
                continue
            # check affix whitelist
            if profile_filter.whitelist and not self._match_affixes_sigils(
                expected_affixes=profile_filter.whitelist, sigil_affixes=item.affixes + item.inherent
            ):
                continue
            Logger.info(f"Matched {profile_name}.Sigils")
            res.keep = True
            res.matched.append(MatchedFilter(f"{profile_name}"))
        return res

    def _check_unique_item(self, item: Item) -> FilterResult:
        res = FilterResult(False, [])
        if not self.unique_filters:
            return FilterResult(True, [])
        for profile_name, profile_filter in self.unique_filters.items():
            for filter_item in profile_filter:
                # check item type
                if not self._match_item_type(expected_item_types=filter_item.itemType, item_type=item.item_type):
                    continue
                # check item power
                if not self._match_item_power(min_power=filter_item.minPower, item_power=item.power):
                    continue
                # check aspect
                if not self._match_item_aspect_or_affix(expected_aspect=filter_item.aspect, item_aspect=item.aspect):
                    continue
                # check affixes
                if not self._match_affixes_uniques(expected_affixes=filter_item.affix, item_affixes=item.affixes):
                    continue
                Logger.info(f"Matched {profile_name}.Uniques: {item.aspect.type}")
                res.keep = True
                res.matched.append(MatchedFilter(f"{profile_name}.{item.aspect.type}", did_match_aspect=True))
        return res

    def _did_files_change(self) -> bool:
        if self.last_loaded is None:
            return True
        return any(os.path.getmtime(file_path) > self.last_loaded for file_path in self.all_file_pathes)

    def _match_affixes_count(self, expected_affixes: list[AffixFilterCountModel], item_affixes: list[Affix]) -> list[str]:
        result = []
        for count_group in expected_affixes:
            group_res = []
            for affix in count_group.count:
                matched_item_affix = next((a for a in item_affixes if a.type == affix.name), None)
                if matched_item_affix is not None and self._match_item_aspect_or_affix(affix, matched_item_affix):
                    group_res.append(affix.name)
            if count_group.minCount <= len(group_res) <= count_group.maxCount:
                result.extend(group_res)
            else:  # if one group fails, everything fails
                return []
        return result

    @staticmethod
    def _match_affixes_sigils(expected_affixes: list[str], sigil_affixes: list[Affix]) -> bool:
        return any(a.type in expected_affixes for a in sigil_affixes)

    def _match_affixes_uniques(self, expected_affixes: list[AffixFilterModel], item_affixes: list[Affix]) -> bool:
        for expected_affix in expected_affixes:
            matched_item_affix = next((a for a in item_affixes if a.type == expected_affix.name), None)
            if matched_item_affix is None or not self._match_item_aspect_or_affix(expected_affix, matched_item_affix):
                return False
        return True

    @staticmethod
    def _match_item_aspect_or_affix(expected_aspect: AffixAspectFilterModel | None, item_aspect: Aspect | Affix) -> bool:
        if expected_aspect is None:
            return True
        if expected_aspect.name != item_aspect.type:
            return False
        if expected_aspect.value is not None:
            if item_aspect.value is None:
                return False
            if (expected_aspect.comparison == ComparisonType.larger and item_aspect.value < expected_aspect.value) or (
                expected_aspect.comparison == ComparisonType.smaller and item_aspect.value > expected_aspect.value
            ):
                return False
        return True

    @staticmethod
    def _match_item_power(min_power: int, item_power: int, max_power: int = sys.maxsize) -> bool:
        return min_power <= item_power <= max_power

    @staticmethod
    def _match_item_type(expected_item_types: list[ItemType], item_type: ItemType) -> bool:
        if not expected_item_types:
            return True
        return item_type in expected_item_types

    def load_files(self):
        self.files_loaded = True
        self.affix_filters: dict[str, list[DynamicItemFilterModel]] = dict()
        self.sigil_filters: dict[str, SigilFilterModel] = dict()
        self.unique_filters: dict[str, list[UniqueModel]] = dict()
        profiles: list[str] = IniConfigLoader().general.profiles

        user_dir = os.path.expanduser("~")
        custom_profile_path = Path(f"{user_dir}/.d4lf/profiles")
        params_profile_path = Path(f"config/profiles")
        self.all_file_pathes = []

        errors = False
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
                if config is None:
                    Logger.error(f"Empty YAML file {profile_path}, please remove it")
                    continue

                info_str = f"Loading profile {profile_str}: "
                try:
                    data = ProfileModel(name=profile_str, **config)
                except ValidationError as e:
                    errors = True
                    Logger.error(f"Validation errors in {profile_path}")
                    Logger.error(e)
                    continue

                if data.Affixes:
                    self.affix_filters[data.name] = data.Affixes
                    info_str += "Affixes "
                if data.Sigils:
                    self.sigil_filters[data.name] = data.Sigils
                    info_str += "Sigils "
                if data.Uniques:
                    self.unique_filters[data.name] = data.Uniques
                    info_str += "Uniques"

                Logger.info(info_str)
        if errors:
            Logger.error("Errors occurred while loading profiles, please check the log for details")
            sys.exit(1)
        self.last_loaded = time.time()

    def should_keep(self, item: Item) -> FilterResult:
        if not self.files_loaded or self._did_files_change():
            self.load_files()

        res = FilterResult(False, [])

        if item.item_type is None or item.power is None:
            return res

        if item.item_type == ItemType.Sigil:
            return self._check_sigil(item)

        if item.rarity == ItemRarity.Unique:
            return self._check_unique_item(item)

        if item.rarity != ItemRarity.Unique:
            keep_affixes = self._check_affixes(item)
            if keep_affixes.keep:
                return keep_affixes
            if item.rarity == ItemRarity.Legendary:
                return self._check_aspect(item)

        return res
