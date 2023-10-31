import numpy as np
from copy import copy
from item.data.rarity import ItemRarity
from config import Config
from template_finder import SearchArgs
from utils.image_operations import crop
from utils.roi_operations import fit_roi_to_window_size

# TODO: Add common itemrarity
map_template_rarity = {
    "item_unique_top_left": ItemRarity.Unique,
    "item_rare_top_left": ItemRarity.Rare,
    "item_leg_top_left": ItemRarity.Legendary,
    "item_magic_top_left": ItemRarity.Magic,
}


def find_descr(img: np.ndarray, anchor: tuple[int, int]) -> tuple[bool, tuple[int, int], ItemRarity, np.ndarray]:
    item_descr_width, _ = Config().ui_offsets["item_descr"]
    _, window_height = Config().ui_pos["window_dimensions"]

    refs = ["item_unique_top_left", "item_rare_top_left", "item_leg_top_left", "item_magic_top_left"]
    res = None

    roi_left = copy(Config().ui_roi["rel_descr_search_left"])
    roi_left[0] += anchor[0]
    ok, roi_left = fit_roi_to_window_size(roi_left, Config().ui_pos["window_dimensions"])
    if ok:
        res = SearchArgs(ref=refs, roi=roi_left, threshold=0.93, mode="best").detect()
    if res is not None and not res.success:
        roi_right = copy(Config().ui_roi["rel_descr_search_right"])
        roi_right[0] += anchor[0]
        ok, roi_right = fit_roi_to_window_size(roi_right, Config().ui_pos["window_dimensions"])
        if ok:
            res = SearchArgs(ref=refs, roi=roi_right, threshold=0.93, mode="best").detect()

    if res is not None and res.success:
        match = res.matches[0]
        rarity = map_template_rarity[match.name.lower()]
        # find equipe template
        equip_roi = [match.region[0] - 30, match.region[1], item_descr_width, window_height]
        equip = SearchArgs(ref=["item_descr_equip", "item_descr_equip_inactive"], roi=equip_roi, threshold=0.78)
        if (res_equip := equip.detect()).success:
            _, off_bottom_of_descr = Config().ui_offsets["equip_to_bottom"]
            equip_match = res_equip.matches[0]
            crop_roi = [
                match.region[0],
                match.region[1],
                item_descr_width,
                equip_match.center[1] - off_bottom_of_descr - match.region[1],
            ]
            croped_descr = crop(img, crop_roi)
            return True, match.center, rarity, croped_descr

    return False, None, None, None
