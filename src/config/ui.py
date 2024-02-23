import logging

from numpy import array, ndarray

from config.helper import singleton
from config.models import UiRoi, UiPos, UiOffsets, Colors, HSVRange

LOGGER = logging.getLogger("d4lf")

_FHD = (
    UiOffsets(
        find_bullet_points_width=39,
        find_seperator_short_offset_top=250,
        item_descr_line_height=25,
        item_descr_off_bottom_edge=52,
        item_descr_pad=15,
        item_descr_width=387,
        vendor_center_item_x=616,
    ),
    UiPos(
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
    UiRoi(
        core_skill=array([1094, 981, 47, 47]),
        health_slice=array([587, 925, 43, 130]),
        hud_detection=array([702, 978, 59, 53]),
        mini_map_visible=array([1719, 123, 60, 60]),
        rel_descr_search_left=array([-455, 0, 60, 880]),
        rel_descr_search_right=array([30, 0, 60, 880]),
        rel_fav_flag=array([4, 3, 8, 10]),
        rel_skill_cd=array([6, 4, 22, 12]),
        skill3=array([904, 981, 49, 49]),
        skill4=array([967, 981, 47, 47]),
        slots_3x11=array([1268, 722, 607, 243]),
        slots_5x10=array([46, 269, 612, 486]),
        sort_icon=array([1220, 666, 63, 62]),
        stash_menu_icon=array([296, 72, 109, 48]),
        tab_slots_6=array([150, 142, 400, 51]),
        vendor_text=array([100, 391, 94, 22]),
    ),
)


class _ResTransformer:
    def __init__(self, factor: float = 1, width: int | None = None, black_bars: tuple[int, int] | None = None):
        self.factor = factor
        self.width = width
        self.black_bars = black_bars

    def __transform(self, value: int) -> int:
        return int(value * self.factor)

    def __transform_array(self, value: ndarray, scaly_only=False) -> ndarray:
        scaled_value = value * self.factor
        if self.width is not None and not scaly_only:
            width_org = int(self.factor * 1920)
            is_right_side = scaled_value[0] > width_org / 2
            if is_right_side:
                scaled_value[0] += self.width - width_org
            if self.black_bars is not None:
                offset = self.black_bars[1] if is_right_side else self.black_bars[0]
                scaled_value[0] += offset
        return scaled_value.astype(int)

    def __transform_list_of_tuples(self, value: list[tuple[int, int]]) -> list[tuple[int, int]]:
        res = []
        for v in value:
            res.append(self.__transform_tuples(value=v))
        return res

    def __transform_tuples(self, value: tuple[int, int]) -> tuple[int, int]:
        values = self.__transform_array(value=array(value, dtype=int))
        return int(values[0]), int(values[1])

    def from_fhd(self) -> tuple[UiOffsets, UiPos, UiRoi]:
        offsets = UiOffsets(
            find_bullet_points_width=self.__transform(value=_FHD[0].find_bullet_points_width),
            find_seperator_short_offset_top=self.__transform(value=_FHD[0].find_seperator_short_offset_top),
            item_descr_line_height=self.__transform(value=_FHD[0].item_descr_line_height),
            item_descr_off_bottom_edge=self.__transform(value=_FHD[0].item_descr_off_bottom_edge),
            item_descr_pad=self.__transform(value=_FHD[0].item_descr_pad),
            item_descr_width=self.__transform(value=_FHD[0].item_descr_width),
            vendor_center_item_x=self.__transform(value=_FHD[0].vendor_center_item_x),
        )
        pos = UiPos(
            possible_centers=self.__transform_list_of_tuples(value=_FHD[1].possible_centers),
            window_dimensions=self.__transform_tuples(value=_FHD[1].window_dimensions),
        )
        roi = UiRoi(
            core_skill=self.__transform_array(value=_FHD[2].core_skill),
            health_slice=self.__transform_array(value=_FHD[2].health_slice),
            hud_detection=self.__transform_array(value=_FHD[2].hud_detection),
            mini_map_visible=self.__transform_array(value=_FHD[2].mini_map_visible),
            rel_descr_search_left=self.__transform_array(value=_FHD[2].rel_descr_search_left, scaly_only=True),
            rel_descr_search_right=self.__transform_array(value=_FHD[2].rel_descr_search_right, scaly_only=True),
            rel_fav_flag=self.__transform_array(value=_FHD[2].rel_fav_flag, scaly_only=True),
            rel_skill_cd=self.__transform_array(value=_FHD[2].rel_skill_cd, scaly_only=True),
            skill3=self.__transform_array(value=_FHD[2].skill3),
            skill4=self.__transform_array(value=_FHD[2].skill4),
            slots_3x11=self.__transform_array(value=_FHD[2].slots_3x11),
            slots_5x10=self.__transform_array(value=_FHD[2].slots_5x10),
            sort_icon=self.__transform_array(value=_FHD[2].sort_icon),
            stash_menu_icon=self.__transform_array(value=_FHD[2].stash_menu_icon),
            tab_slots_6=self.__transform_array(value=_FHD[2].tab_slots_6),
            vendor_text=self.__transform_array(value=_FHD[2].vendor_text),
        )
        return offsets, pos, roi


@singleton
class ResManager:
    def __init__(self):
        self._offsets = _FHD[0]
        self._pos = _FHD[1]
        self._roi = _FHD[2]
        self.transformers = {
            "1920x1080": _ResTransformer(),
            "2560x1080": _ResTransformer(width=2560),
            "2560x1440": _ResTransformer(factor=4.0 / 3.0),
            "2560x1600": _ResTransformer(factor=40.0 / 27.0, width=2560),
            "3440x1440": _ResTransformer(factor=4.0 / 3.0, width=3440),
            "3840x1080": _ResTransformer(width=3840, black_bars=(300, -300)),
            "3840x1600": _ResTransformer(factor=40.0 / 27.0, width=3840),
            "3840x2160": _ResTransformer(factor=2),
            "5120x1440": _ResTransformer(factor=4.0 / 3.0, width=5120, black_bars=(400, -400)),
        }

    @property
    def offsets(self) -> UiOffsets:
        return self._offsets

    @property
    def pos(self) -> UiPos:
        return self._pos

    @property
    def roi(self) -> UiRoi:
        return self._roi

    def set_resolution(self, res: str):
        if res not in self.transformers:
            raise ValueError(f"Resolution {res} not supported")
        LOGGER.debug(f"Setting ui resolution to {res}")
        self._offsets, self._pos, self._roi = self.transformers[res].from_fhd()


COLORS = Colors(
    aspect_number=HSVRange(h_s_v_min=array([90, 60, 200]), h_s_v_max=array([150, 100, 255])),
    cold_imbued=HSVRange(h_s_v_min=array([88, 0, 0]), h_s_v_max=array([112, 255, 255])),
    legendary_orange=HSVRange(h_s_v_min=array([4, 190, 190]), h_s_v_max=array([26, 255, 255])),
    material_color=HSVRange(h_s_v_min=array([86, 110, 190]), h_s_v_max=array([114, 220, 255])),
    poison_imbued=HSVRange(h_s_v_min=array([55, 0, 0]), h_s_v_max=array([65, 255, 255])),
    shadow_imbued=HSVRange(h_s_v_min=array([120, 0, 0]), h_s_v_max=array([140, 255, 255])),
    skill_cd=HSVRange(h_s_v_min=array([5, 61, 38]), h_s_v_max=array([16, 191, 90])),
    unique_gold=HSVRange(h_s_v_min=array([4, 45, 125]), h_s_v_max=array([26, 155, 250])),
    unusable_red=HSVRange(h_s_v_min=array([0, 210, 110]), h_s_v_max=array([10, 255, 210])),
)
