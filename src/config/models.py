"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

import enum
from pathlib import Path
from typing import List

import numpy
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from pydantic_numpy import np_array_pydantic_annotated_typing
from pydantic_numpy.model import NumpyModel

from config.helper import key_must_exist
from item.data.item_type import ItemType


class ComparisonType(enum.StrEnum):
    larger = enum.auto()
    smaller = enum.auto()


class _IniBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True, str_to_lower=True)


class AffixAspectFilterModel(BaseModel):
    name: str
    value: float | None = None
    comparison: ComparisonType = ComparisonType.larger

    @field_validator("name")
    def name_must_exist(cls, name: str) -> str:
        import dataloader  # This on module level would be a circular import, so we do it lazy for now

        if name not in dataloader.Dataloader().affix_dict.keys() and name not in dataloader.Dataloader().aspect_unique_dict.keys():
            raise ValueError(f"affix {name} does not exist")
        return name

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


class AdvancedOptionsModel(_IniBaseModel):
    exit_key: str
    log_lvl: str = "info"
    process_name: str = "Diablo IV.exe"
    run_filter: str
    run_scripts: str
    scripts: list[str]

    @model_validator(mode="after")
    def key_must_be_unique(self) -> "AdvancedOptionsModel":
        keys = [self.exit_key, self.run_filter, self.run_scripts]
        if len(set(keys)) != len(keys):
            raise ValueError(f"hotkeys must be unique")
        return self

    @field_validator("run_scripts", "run_filter", "exit_key")
    def key_must_exist(cls, k: str) -> str:
        return key_must_exist(k)

    @field_validator("log_lvl")
    def log_lvl_must_exist(cls, k: str) -> str:
        if k not in ["debug", "info", "warning", "error", "critical"]:
            raise ValueError("log level does not exist")
        return k


class CharModel(_IniBaseModel):
    inventory: str

    @field_validator("inventory")
    def key_must_exist(cls, k: str) -> str:
        return key_must_exist(k)


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


class General(_IniBaseModel):
    check_chest_tabs: list[int]
    hidden_transparency: float
    language: str = "enUS"
    local_prefs_path: Path | None
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
        if not 0.01 <= v <= 1:
            raise ValueError("must be in [0.01, 1]")
        return v

    @field_validator("local_prefs_path")
    def path_must_exist(cls, v: Path | None) -> Path | None:
        if v is not None and not v.exists():
            raise ValueError("path does not exist")
        return v


class HSVRangeModel(_IniBaseModel):
    h_s_v_min: np_array_pydantic_annotated_typing(dimensions=1)
    h_s_v_max: np_array_pydantic_annotated_typing(dimensions=1)

    def __getitem__(self, index):
        # TODO added this to not have to change much of the other code. should be fixed some time
        if index == 0:
            return self.h_s_v_min
        elif index == 1:
            return self.h_s_v_max
        else:
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
    def values_in_range(cls, v: numpy.ndarray) -> numpy.ndarray:
        if not len(v) == 3:
            raise ValueError("must be h,s,v")
        if not -179 <= v[0] <= 179:
            raise ValueError("must be in [-179, 179]")
        if not all(0 <= x <= 255 for x in v[1:3]):
            raise ValueError("must be in [0, 255]")
        return v


class SigilModel(BaseModel):
    minTier: int = 0
    maxTier: int = 100
    blacklist: list[str] = []
    whitelist: list[str] = []

    @model_validator(mode="after")
    def blacklist_whitelist_must_be_unique(self) -> "SigilModel":
        errors = [item for item in self.blacklist if item in self.whitelist]
        if errors:
            raise ValueError(f"blacklist and whitelist must not overlap: {errors}")
        return self

    @field_validator("maxTier")
    def max_tier_in_range(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("must be in [0, 100]")
        return v

    @field_validator("minTier")
    def min_tier_in_range(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("must be in [0, 100]")
        return v

    @field_validator("blacklist", "whitelist")
    def name_must_exist(cls, names: list[str]) -> list[str]:
        import dataloader  # This on module level would be a circular import, so we do it lazy for now

        errors = []
        for name in names:
            if name not in dataloader.Dataloader().affix_sigil_dict.keys():
                errors.append(name)
        if errors:
            raise ValueError(f"The following affixes/dungeons do not exist: {errors}")
        return names


class UniqueModel(BaseModel):
    affix: list[AffixAspectFilterModel] = []
    aspect: AffixAspectFilterModel = None
    itemType: list[ItemType] = []
    minPower: int = 0

    @field_validator("itemType", mode="before")
    def parse_item_type(cls, data: str | list[str]) -> list[str]:
        if isinstance(data, str):
            return [data]
        return data


class ProfileModel(BaseModel):
    name: str
    Sigils: SigilModel | None = None
    Uniques: List[UniqueModel] = []


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
