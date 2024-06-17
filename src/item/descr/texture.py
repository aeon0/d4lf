import math

import numpy as np

from src.config.data import COLORS
from src.config.ui import ResManager
from src.template_finder import TemplateMatch, search
from src.utils.image_operations import color_filter, crop


def find_seperator_short(img_item_descr: np.ndarray) -> TemplateMatch:
    refs = ["item_seperator_short_rare", "item_seperator_short_legendary"]
    roi = [0, 0, img_item_descr.shape[1], ResManager().offsets.find_seperator_short_offset_top]
    if not (sep_short := search(refs, img_item_descr, 0.62, roi, True, mode="all", do_multi_process=False)).success:
        return None
    sorted_matches = sorted(sep_short.matches, key=lambda match: match.center[1])
    return sorted_matches[0]


def _filter_outliers(template_matches: list[TemplateMatch]) -> list[TemplateMatch]:
    # Extract center[0] values
    centers_x = [tm.center[0] for tm in template_matches]
    # Calculate the median
    if not centers_x:
        return []
    target_center_x = np.min(centers_x)
    # Filter out the outliers
    return [tm for tm in template_matches if abs(tm.center[0] - target_center_x) < 1.2 * tm.region[2]]


def _gen_roi_bullets(sep_short_match: TemplateMatch, img_height: int):
    return [0, sep_short_match.center[1], ResManager().offsets.find_bullet_points_width + 20, img_height]


def _find_bullets(
    img_item_descr: np.ndarray, sep_short_match: TemplateMatch, template_list: list[str], threshold: float, mode: str
) -> list[TemplateMatch]:
    img_height = img_item_descr.shape[0]
    roi_bullets = _gen_roi_bullets(sep_short_match, img_height)
    all_templates = [f"{x}_medium" for x in template_list] + template_list
    all_bullets = search(
        ref=all_templates,
        inp_img=img_item_descr,
        threshold=threshold,
        roi=roi_bullets,
        use_grayscale=True,
        mode=mode,
    )
    if not all_bullets.success:
        return []
    all_bullets.matches = _filter_outliers(all_bullets.matches)
    # go through the matches and filter out the ones that are too close to each other. only keep the one with higher probability
    matches_dict = {}
    for match in all_bullets.matches:
        match_exists = False
        for center in matches_dict:
            if math.sqrt((center[0] - match.center[0]) ** 2 + (center[1] - match.center[1]) ** 2) <= 5:
                if match.score > matches_dict[center].score:
                    matches_dict[center] = match
                match_exists = True
                break
        if not match_exists:
            matches_dict[match.center] = match
    filtered_matches = list(matches_dict.values())
    return sorted(filtered_matches, key=lambda match: match.center[1])


def find_affix_bullets(img_item_descr: np.ndarray, sep_short_match: TemplateMatch) -> list[TemplateMatch]:
    return _find_bullets(
        img_item_descr=img_item_descr,
        sep_short_match=sep_short_match,
        template_list=["affix_bullet_point", "greater_affix_bullet_point", "rerolled_bullet_point", "tempered_affix_bullet_point"],
        threshold=0.8,
        mode="all",
    )


def find_empty_sockets(img_item_descr: np.ndarray, sep_short_match: TemplateMatch) -> list[TemplateMatch]:
    empty_sockets = _find_bullets(
        img_item_descr=img_item_descr,
        sep_short_match=sep_short_match,
        template_list=["empty_socket"],
        threshold=0.8,
        mode="all",
    )
    return sorted(empty_sockets, key=lambda match: match.center[1])


def find_aspect_bullet(img_item_descr: np.ndarray, sep_short_match: TemplateMatch) -> TemplateMatch | None:
    aspect_bullets = _find_bullets(
        img_item_descr=img_item_descr,
        sep_short_match=sep_short_match,
        template_list=["aspect_bullet_point", "unique_bullet_point"],
        threshold=0.8,
        mode="first",
    )
    return aspect_bullets[0] if aspect_bullets else None


def find_aspect_search_area(img_item_descr: np.ndarray, aspect_bullet: TemplateMatch) -> list[int]:
    line_height = ResManager().offsets.item_descr_line_height
    img_height, img_width = img_item_descr.shape[:2]
    offset_x = aspect_bullet.center[0] + int(line_height // 5)
    top = aspect_bullet.center[1] - int(line_height * 0.8)
    roi_aspect = [offset_x, top, int(img_width * 0.99) - offset_x, int(img_height * 0.95) - top]
    cropped_bottom = crop(img_item_descr, roi_aspect)
    filtered, _ = color_filter(cropped_bottom, COLORS.unique_gold, False)
    bounding_values = np.nonzero(filtered)
    if len(bounding_values[0]) > 0:
        roi_aspect[3] = bounding_values[0].max() + int(line_height * 0.4)
    return roi_aspect


def find_codex_upgrade_icon(img_item_descr: np.ndarray, aspect_bullet: TemplateMatch) -> bool:
    top_limit = img_item_descr.shape[0] // 2
    right_limit = img_item_descr.shape[1] // 2
    if aspect_bullet is not None:
        top_limit = aspect_bullet.center[1]
    cut_item_descr = img_item_descr[top_limit:, :right_limit]
    # TODO small font template fallback
    result = search(["codex_upgrade_icon_medium"], cut_item_descr, 0.78, use_grayscale=True, mode="first")
    if not result.success:
        result = search(["codex_upgrade_icon"], cut_item_descr, 0.78, use_grayscale=True, mode="first")
    return result.success
