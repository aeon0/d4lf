"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

from pathlib import Path

import numpy
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from pydantic_numpy import np_array_pydantic_annotated_typing
from pydantic_numpy.model import NumpyModel

from config.helper import key_must_exist


class _IniBase(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True, str_to_lower=True)


class AdvancedOptions(_IniBase):
    exit_key: str
    log_lvl: str = "info"
    process_name: str = "Diablo IV.exe"
    run_filter: str
    run_scripts: str
    scripts: list[str]

    @model_validator(mode="after")
    def key_must_be_unique(self) -> "AdvancedOptions":
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


class Char(_IniBase):
    inventory: str

    @field_validator("inventory")
    def key_must_exist(cls, k: str) -> str:
        return key_must_exist(k)


class Colors(_IniBase):
    aspect_number: "HSVRange"
    cold_imbued: "HSVRange"
    legendary_orange: "HSVRange"
    material_color: "HSVRange"
    poison_imbued: "HSVRange"
    shadow_imbued: "HSVRange"
    skill_cd: "HSVRange"
    unique_gold: "HSVRange"
    unusable_red: "HSVRange"


class General(_IniBase):
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


class HSVRange(_IniBase):
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
    def check_interval_sanity(self) -> "HSVRange":
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


class UiOffsets(_IniBase):
    find_bullet_points_width: int
    find_seperator_short_offset_top: int
    item_descr_line_height: int
    item_descr_off_bottom_edge: int
    item_descr_pad: int
    item_descr_width: int
    vendor_center_item_x: int


class UiPos(_IniBase):
    possible_centers: list[tuple[int, int]]
    window_dimensions: tuple[int, int]


class UiRoi(NumpyModel):
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
