import logging

import numpy as np

from config.helper import singleton
from config.models import UiRoiModel, UiPosModel, UiOffsetsModel, ColorsModel, HSVRangeModel

LOGGER = logging.getLogger("d4lf")

_FHD = (
    (1920, 1080),
    UiOffsetsModel(
        find_bullet_points_width=39,
        find_seperator_short_offset_top=250,
        item_descr_line_height=25,
        item_descr_off_bottom_edge=52,
        item_descr_pad=15,
        item_descr_width=387,
        vendor_center_item_x=616,
    ),
    UiPosModel(
        possible_centers=[
            (1497, 122),
            (1497, 216),
            (1497, 312),
            (1497, 405),
            (1497, 496),
            (1497, 598),
            (1861, 214),
            (1861, 309),
            (1861, 404),
            (1807, 610),
            (1865, 610),
            (1652, 609),
            (1708, 609),
        ],
        window_dimensions=(1920, 1080),
    ),
    UiRoiModel(
        core_skill=np.array([1094, 981, 47, 47]),
        health_slice=np.array([587, 925, 43, 130]),
        hud_detection=np.array([702, 978, 59, 53]),
        mini_map_visible=np.array([1719, 123, 60, 60]),
        rel_descr_search_left=np.array([-455, 0, 60, 880]),
        rel_descr_search_right=np.array([30, 0, 60, 880]),
        rel_fav_flag=np.array([4, 3, 8, 10]),
        rel_skill_cd=np.array([6, 4, 22, 12]),
        skill3=np.array([904, 981, 49, 49]),
        skill4=np.array([967, 981, 47, 47]),
        slots_3x11=np.array([1268, 722, 607, 243]),
        slots_5x10=np.array([46, 269, 612, 486]),
        sort_icon=np.array([1220, 666, 63, 62]),
        stash_menu_icon=np.array([296, 72, 109, 48]),
        tab_slots_6=np.array([150, 142, 400, 51]),
        vendor_text=np.array([100, 391, 94, 22]),
    ),
)


class _ResTransformer:
    def __init__(self, resolution: str):
        self._target_width, self._target_height = map(int, resolution.split("x"))
        self._scale_x = self._target_width / _FHD[0][0]
        self._scale_y = self._target_height / _FHD[0][1]
        self._highest_ratio = 27 / 9

    def _transform(self, value: int) -> int:
        return int(value * self._scale_y)

    def _transform_array(self, value: np.ndarray, scale_only=False) -> np.ndarray:
        new_value = value * self._scale_y
        if scale_only:
            return new_value.astype(int)

        # handle widescreen stretching
        width_org = int(self._scale_y * _FHD[0][0])
        is_right_side = new_value[0] > width_org / 2
        if is_right_side:
            new_value[0] += self._target_width - width_org

        # handle black bars
        aspect_ratio = self._target_width / self._target_height
        if aspect_ratio > self._highest_ratio:
            new_width = int(self._target_height * self._highest_ratio)
            black_bar = (self._target_width - new_width) // 2
            new_value[0] = new_value[0] - black_bar if is_right_side else new_value[0] + black_bar

        return new_value.astype(int)

    def _transform_list_of_tuples(self, value: list[tuple[int, int]]) -> list[tuple[int, int]]:
        res = []
        for v in value:
            res.append(self._transform_tuples(value=v))
        return res

    def _transform_tuples(self, value: tuple[int, int]) -> tuple[int, int]:
        values = self._transform_array(value=np.array(value, dtype=int))
        return int(values[0]), int(values[1])

    def from_fhd(self) -> tuple[UiOffsetsModel, UiPosModel, UiRoiModel]:
        offsets = UiOffsetsModel(
            find_bullet_points_width=self._transform(value=_FHD[1].find_bullet_points_width),
            find_seperator_short_offset_top=self._transform(value=_FHD[1].find_seperator_short_offset_top),
            item_descr_line_height=self._transform(value=_FHD[1].item_descr_line_height),
            item_descr_off_bottom_edge=self._transform(value=_FHD[1].item_descr_off_bottom_edge),
            item_descr_pad=self._transform(value=_FHD[1].item_descr_pad),
            item_descr_width=self._transform(value=_FHD[1].item_descr_width),
            vendor_center_item_x=self._transform(value=_FHD[1].vendor_center_item_x),
        )
        pos = UiPosModel(
            possible_centers=self._transform_list_of_tuples(value=_FHD[2].possible_centers),
            window_dimensions=self._transform_tuples(value=_FHD[2].window_dimensions),
        )
        roi = UiRoiModel(
            core_skill=self._transform_array(value=_FHD[3].core_skill),
            health_slice=self._transform_array(value=_FHD[3].health_slice),
            hud_detection=self._transform_array(value=_FHD[3].hud_detection),
            mini_map_visible=self._transform_array(value=_FHD[3].mini_map_visible),
            rel_descr_search_left=self._transform_array(value=_FHD[3].rel_descr_search_left, scale_only=True),
            rel_descr_search_right=self._transform_array(value=_FHD[3].rel_descr_search_right, scale_only=True),
            rel_fav_flag=self._transform_array(value=_FHD[3].rel_fav_flag, scale_only=True),
            rel_skill_cd=self._transform_array(value=_FHD[3].rel_skill_cd, scale_only=True),
            skill3=self._transform_array(value=_FHD[3].skill3),
            skill4=self._transform_array(value=_FHD[3].skill4),
            slots_3x11=self._transform_array(value=_FHD[3].slots_3x11),
            slots_5x10=self._transform_array(value=_FHD[3].slots_5x10),
            sort_icon=self._transform_array(value=_FHD[3].sort_icon),
            stash_menu_icon=self._transform_array(value=_FHD[3].stash_menu_icon),
            tab_slots_6=self._transform_array(value=_FHD[3].tab_slots_6),
            vendor_text=self._transform_array(value=_FHD[3].vendor_text),
        )
        return offsets, pos, roi


@singleton
class ResManager:
    def __init__(self):
        self._current_resolution = "1920x1080"
        self._offsets = _FHD[1]
        self._pos = _FHD[2]
        self._roi = _FHD[3]

    @property
    def offsets(self) -> UiOffsetsModel:
        return self._offsets

    @property
    def pos(self) -> UiPosModel:
        return self._pos

    @property
    def roi(self) -> UiRoiModel:
        return self._roi

    def set_resolution(self, res: str):
        if res == self._current_resolution:
            return
        self._current_resolution = res
        LOGGER.debug(f"Setting ui resolution to {res}")
        self._offsets, self._pos, self._roi = _ResTransformer(resolution=res).from_fhd()


COLORS = ColorsModel(
    aspect_number=HSVRangeModel(h_s_v_min=np.array([90, 60, 200]), h_s_v_max=np.array([150, 100, 255])),
    cold_imbued=HSVRangeModel(h_s_v_min=np.array([88, 0, 0]), h_s_v_max=np.array([112, 255, 255])),
    legendary_orange=HSVRangeModel(h_s_v_min=np.array([4, 190, 190]), h_s_v_max=np.array([26, 255, 255])),
    material_color=HSVRangeModel(h_s_v_min=np.array([86, 110, 190]), h_s_v_max=np.array([114, 220, 255])),
    poison_imbued=HSVRangeModel(h_s_v_min=np.array([55, 0, 0]), h_s_v_max=np.array([65, 255, 255])),
    shadow_imbued=HSVRangeModel(h_s_v_min=np.array([120, 0, 0]), h_s_v_max=np.array([140, 255, 255])),
    skill_cd=HSVRangeModel(h_s_v_min=np.array([5, 61, 38]), h_s_v_max=np.array([16, 191, 90])),
    unique_gold=HSVRangeModel(h_s_v_min=np.array([4, 45, 125]), h_s_v_max=np.array([26, 155, 250])),
    unusable_red=HSVRangeModel(h_s_v_min=np.array([0, 210, 110]), h_s_v_max=np.array([10, 255, 210])),
)
