import numpy as np
from copy import copy
from item.data.rarity import ItemRarity
from config import Config
from template_finder import search
from utils.image_operations import crop
from utils.roi_operations import fit_roi_to_window_size


map_template_rarity = {
    "item_unique_top_left": ItemRarity.Unique,
    "item_rare_top_left": ItemRarity.Rare,
    "item_leg_top_left": ItemRarity.Legendary,
    "item_magic_top_left": ItemRarity.Magic,
    "item_common_top_left": ItemRarity.Common,
}


def find_descr(img: np.ndarray, anchor: tuple[int, int]) -> tuple[bool, ItemRarity, np.ndarray, tuple[int, int], tuple[int, int, int, int]]:
    item_descr_width = Config().ui_offsets["item_descr_width"]
    item_descr_pad = Config().ui_offsets["item_descr_pad"]
    _, window_height = Config().ui_pos["window_dimensions"]

    refs = list(map_template_rarity.keys())
    res = None

    roi_left = copy(Config().ui_roi["rel_descr_search_left"])
    roi_left[0] += anchor[0]
    ok, roi_left = fit_roi_to_window_size(roi_left, Config().ui_pos["window_dimensions"])
    if ok:
        res = search(ref=refs, inp_img=img, roi=roi_left, threshold=0.8, mode="best")
    if res is not None and not res.success:
        roi_right = copy(Config().ui_roi["rel_descr_search_right"])
        roi_right[0] += anchor[0]
        ok, roi_right = fit_roi_to_window_size(roi_right, Config().ui_pos["window_dimensions"])
        if ok:
            res = search(ref=refs, inp_img=img, roi=roi_right, threshold=0.8, mode="best")

    if res is not None and res.success:
        match = res.matches[0]
        rarity = map_template_rarity[match.name.lower()]
        # find equipe template
        offset_top = int(window_height * 0.03)
        roi_y = match.region[1] + offset_top
        search_height = window_height - roi_y - offset_top
        roi = [match.region[0], roi_y, item_descr_width, search_height]
        res_bottom = search(ref=["item_bottom_edge"], inp_img=img, roi=roi, threshold=0.73, mode="best")

        refs = ["item_seperator_short_rare", "item_seperator_short_legendary"]
        sep_short = search(refs, img, 0.68, roi, True, mode="first", do_multi_process=False)

        if res_bottom.success and sep_short.success:
            off_bottom_of_descr = Config().ui_offsets["item_descr_off_bottom_edge"]
            equip_match = res_bottom.matches[0]
            crop_roi = [
                match.region[0] + item_descr_pad,
                match.region[1] + item_descr_pad,
                item_descr_width - 2 * item_descr_pad,
                equip_match.center[1] - off_bottom_of_descr - match.region[1],
            ]
            croped_descr = crop(img, crop_roi)
            return True, rarity, croped_descr, match.center, crop_roi

    return False, None, None, None, None
