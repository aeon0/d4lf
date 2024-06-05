"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

import enum
import sys

import numpy as np
from pydantic import BaseModel, ConfigDict, RootModel, field_validator, model_validator
from pydantic_numpy import np_array_pydantic_annotated_typing
from pydantic_numpy.model import NumpyModel

from src.config.helper import check_greater_than_zero, validate_hotkey
from src.item.data.item_type import ItemType


class AspectFilterType(enum.StrEnum):
    all = enum.auto()
    none = enum.auto()
    upgrade = enum.auto()


class HandleRaresType(enum.StrEnum):
    filter = enum.auto()
    ignore = enum.auto()
    junk = enum.auto()


class MoveItemsType(enum.StrEnum):
    everything = enum.auto()
    junk = enum.auto()
    non_favorites = enum.auto()


class ComparisonType(enum.StrEnum):
    larger = enum.auto()
    smaller = enum.auto()


class _IniBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True, str_to_lower=True)


def _parse_item_type(data: str | list[str]) -> list[str]:
    if isinstance(data, str):
        return [data]
    return data


class AffixAspectFilterModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    value: float | None = None
    comparison: ComparisonType = ComparisonType.larger

    @model_validator(mode="before")
    def parse_data(cls, data: str | list[str] | list[str | float] | dict[str, str | float]) -> dict[str, str | float]:
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            return {"name": data}
        if isinstance(data, list):
            if not data or len(data) > 3:
                raise ValueError("list, cannot be empty or larger than 3 items")
            result = {}
            if len(data) >= 1:
                result["name"] = data[0]
            if len(data) >= 2:
                result["value"] = data[1]
            if len(data) == 3:
                result["comparison"] = data[2]
            return result
        raise ValueError("must be str or list")


class AffixFilterModel(AffixAspectFilterModel):
    @field_validator("name")
    def name_must_exist(cls, name: str) -> str:
        from src.dataloader import Dataloader  # This on module level would be a circular import, so we do it lazy for now

        if name not in Dataloader().affix_dict:
            raise ValueError(f"affix {name} does not exist")
        return name


class AffixFilterCountModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    count: list[AffixFilterModel] = []
    maxCount: int = sys.maxsize
    minCount: int = 0
    minGreaterAffixCount: int = 0

    @field_validator("minCount", "minGreaterAffixCount", "maxCount")
    def count_validator(cls, v: int) -> int:
        return check_greater_than_zero(v)

    @model_validator(mode="after")
    def model_validator(self) -> "AffixFilterCountModel":
        # If minCount and maxCount are not set, we assume that the lengths of the count list is the only thing that matters.
        # To not show up in the model.dict() we need to remove them from the model_fields_set property
        if "minCount" not in self.model_fields_set and "maxCount" not in self.model_fields_set:
            self.minCount = len(self.count)
            self.maxCount = len(self.count)
            self.model_fields_set.remove("minCount")
            self.model_fields_set.remove("maxCount")
        if self.minCount > self.maxCount:
            raise ValueError("minCount must be smaller than maxCount")
        return self


class AspectUniqueFilterModel(AffixAspectFilterModel):
    @field_validator("name")
    def name_must_exist(cls, name: str) -> str:
        from src.dataloader import Dataloader  # This on module level would be a circular import, so we do it lazy for now

        if name not in Dataloader().aspect_unique_dict:
            raise ValueError(f"affix {name} does not exist")
        return name


class AdvancedOptionsModel(_IniBaseModel):
    exit_key: str
    log_lvl: str = "info"
    move_to_chest: str
    move_to_inv: str
    process_name: str = "Diablo IV.exe"
    run_filter: str
    run_filter_force_refresh: str
    run_scripts: str
    scripts: list[str]

    @model_validator(mode="after")
    def key_must_be_unique(self) -> "AdvancedOptionsModel":
        keys = [self.exit_key, self.move_to_chest, self.move_to_inv, self.run_filter, self.run_filter_force_refresh, self.run_scripts]
        if len(set(keys)) != len(keys):
            raise ValueError("hotkeys must be unique")
        return self

    @field_validator("exit_key", "move_to_chest", "move_to_inv", "run_filter", "run_filter_force_refresh", "run_scripts")
    def key_must_exist(cls, k: str) -> str:
        return validate_hotkey(k)

    @field_validator("log_lvl")
    def log_lvl_must_exist(cls, k: str) -> str:
        if k not in ["debug", "info", "warning", "error", "critical"]:
            raise ValueError("log level does not exist")
        return k


class CharModel(_IniBaseModel):
    inventory: str

    @field_validator("inventory")
    def key_must_exist(cls, k: str) -> str:
        return validate_hotkey(k)


class ColorsModel(_IniBaseModel):
    aspect_number: "HSVRangeModel"
    cold_imbued: "HSVRangeModel"
    legendary_orange: "HSVRangeModel"
    material_color: "HSVRangeModel"
    poison_imbued: "HSVRangeModel"
    shadow_imbued: "HSVRangeModel"
    skill_cd: "HSVRangeModel"
    unique_gold: "HSVRangeModel"
    unusable_red: "HSVRangeModel"


class BrowserType(enum.StrEnum):
    edge = enum.auto()
    chrome = enum.auto()
    firefox = enum.auto()


class GeneralModel(_IniBaseModel):
    browser: BrowserType = BrowserType.chrome
    check_chest_tabs: list[int]
    full_dump: bool = False
    handle_rares: HandleRaresType = HandleRaresType.filter
    hidden_transparency: float
    keep_aspects: AspectFilterType = AspectFilterType.upgrade
    language: str = "enUS"
    move_to_inv_item_type: MoveItemsType = MoveItemsType.non_favorites
    move_to_stash_item_type: MoveItemsType = MoveItemsType.non_favorites
    profiles: list[str]
    run_vision_mode_on_startup: bool

    @field_validator("check_chest_tabs", mode="after")
    def check_chest_tabs_index(cls, v: list[int]) -> list[int]:
        return sorted([int(x) - 1 for x in v])

    @field_validator("language")
    def language_must_exist(cls, v: str) -> str:
        if v not in ["enUS"]:
            raise ValueError("language not supported")
        return v

    @field_validator("hidden_transparency")
    def transparency_in_range(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("must be in [0, 1]")
        return v


class HSVRangeModel(_IniBaseModel):
    h_s_v_min: np_array_pydantic_annotated_typing(dimensions=1)
    h_s_v_max: np_array_pydantic_annotated_typing(dimensions=1)

    def __getitem__(self, index):
        # TODO added this to not have to change much of the other code. should be fixed some time
        if index == 0:
            return self.h_s_v_min
        if index == 1:
            return self.h_s_v_max
        raise IndexError("Index out of range")

    @model_validator(mode="after")
    def check_interval_sanity(self) -> "HSVRangeModel":
        if self.h_s_v_min[0] > self.h_s_v_max[0]:
            raise ValueError(f"invalid hue range [{self.h_s_v_min[0]}, {self.h_s_v_max[0]}]")
        if self.h_s_v_min[1] > self.h_s_v_max[1]:
            raise ValueError(f"invalid saturation range [{self.h_s_v_min[1]}, {self.h_s_v_max[1]}]")
        if self.h_s_v_min[2] > self.h_s_v_max[2]:
            raise ValueError(f"invalid value range [{self.h_s_v_min[2]}, {self.h_s_v_max[2]}]")
        return self

    @field_validator("h_s_v_min", "h_s_v_max")
    def values_in_range(cls, v: np.ndarray) -> np.ndarray:
        if not len(v) == 3:
            raise ValueError("must be h,s,v")
        if not -179 <= v[0] <= 179:
            raise ValueError("must be in [-179, 179]")
        if not all(0 <= x <= 255 for x in v[1:3]):
            raise ValueError("must be in [0, 255]")
        return v


class ItemFilterModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    affixPool: list[AffixFilterCountModel] = []
    inherentPool: list[AffixFilterCountModel] = []
    itemType: list[ItemType] = []
    minGreaterAffixCount: int = 0
    minPower: int = 0

    @field_validator("minPower")
    def check_min_power(cls, v: int) -> int:
        return check_greater_than_zero(v)

    @field_validator("minGreaterAffixCount")
    def min_greater_affix_in_range(cls, v: int) -> int:
        if not 0 <= v <= 3:
            raise ValueError("must be in [0, 3]")
        return v

    @field_validator("itemType", mode="before")
    def parse_item_type(cls, data: str | list[str]) -> list[str]:
        return _parse_item_type(data)


DynamicItemFilterModel = RootModel[dict[str, ItemFilterModel]]


class SigilConditionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    condition: list[str] = []

    @model_validator(mode="before")
    def parse_data(cls, data: str | list[str] | list[str | float] | dict[str, str | float]) -> dict[str, str | float]:
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            return {"name": data}
        if isinstance(data, list):
            if not data:
                raise ValueError("list cannot be empty")
            result = {}
            if len(data) >= 1:
                result["name"] = data[0]
            if len(data) >= 2:
                result["condition"] = data[1:]
            return result
        raise ValueError("must be str or list")

    @field_validator("condition", "name")
    def name_must_exist(cls, names_in: str | list[str]) -> str | list[str]:
        from src.dataloader import Dataloader  # This on module level would be a circular import, so we do it lazy for now

        names = [names_in] if isinstance(names_in, str) else names_in
        errors = [name for name in names if name not in Dataloader().affix_sigil_dict]
        if errors:
            raise ValueError(f"The following affixes/dungeons do not exist: {errors}")
        return names_in


class SigilFilterModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    blacklist: list[SigilConditionModel] = []
    maxTier: int = sys.maxsize
    minTier: int = 0
    whitelist: list[SigilConditionModel] = []

    @model_validator(mode="after")
    def data_integrity(self) -> "SigilFilterModel":
        errors = [item for item in self.blacklist if item in self.whitelist]
        if errors:
            raise ValueError(f"blacklist and whitelist must not overlap: {errors}")
        if self.minTier > self.maxTier:
            raise ValueError("minTier must be smaller than maxTier")
        return self

    @field_validator("minTier", "maxTier")
    def min_max_tier_in_range(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("must be in [0, 100]")
        return v


class UniqueModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    affix: list[AffixFilterModel] = []
    aspect: AspectUniqueFilterModel = None
    itemType: list[ItemType] = []
    minGreaterAffixCount: int = 0
    minPower: int = 0

    @field_validator("minPower")
    def check_min_power(cls, v: int) -> int:
        return check_greater_than_zero(v)

    @field_validator("minGreaterAffixCount")
    def count_validator(cls, v: int) -> int:
        return check_greater_than_zero(v)

    @field_validator("itemType", mode="before")
    def parse_item_type(cls, data: str | list[str]) -> list[str]:
        return _parse_item_type(data)


class ProfileModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    Affixes: list[DynamicItemFilterModel] = []
    Sigils: SigilFilterModel | None = None
    Uniques: list[UniqueModel] = []


class UiOffsetsModel(_IniBaseModel):
    find_bullet_points_width: int
    find_seperator_short_offset_top: int
    item_descr_line_height: int
    item_descr_off_bottom_edge: int
    item_descr_pad: int
    item_descr_width: int
    vendor_center_item_x: int


class UiPosModel(_IniBaseModel):
    possible_centers: list[tuple[int, int]]
    window_dimensions: tuple[int, int]


class UiRoiModel(NumpyModel):
    core_skill: np_array_pydantic_annotated_typing(dimensions=1)
    health_slice: np_array_pydantic_annotated_typing(dimensions=1)
    hud_detection: np_array_pydantic_annotated_typing(dimensions=1)
    mini_map_visible: np_array_pydantic_annotated_typing(dimensions=1)
    rel_descr_search_left: np_array_pydantic_annotated_typing(dimensions=1)
    rel_descr_search_right: np_array_pydantic_annotated_typing(dimensions=1)
    rel_fav_flag: np_array_pydantic_annotated_typing(dimensions=1)
    rel_skill_cd: np_array_pydantic_annotated_typing(dimensions=1)
    skill3: np_array_pydantic_annotated_typing(dimensions=1)
    skill4: np_array_pydantic_annotated_typing(dimensions=1)
    slots_3x11: np_array_pydantic_annotated_typing(dimensions=1)
    slots_5x10: np_array_pydantic_annotated_typing(dimensions=1)
    sort_icon: np_array_pydantic_annotated_typing(dimensions=1)
    stash_menu_icon: np_array_pydantic_annotated_typing(dimensions=1)
    tab_slots_6: np_array_pydantic_annotated_typing(dimensions=1)
    vendor_text: np_array_pydantic_annotated_typing(dimensions=1)
