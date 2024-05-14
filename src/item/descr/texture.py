import numpy as np

from config.data import COLORS
from config.ui import ResManager
from template_finder import search, TemplateMatch
from utils.image_operations import crop, color_filter


def find_seperator_short(img_item_descr: np.ndarray) -> TemplateMatch:
    refs = ["item_seperator_short_rare", "item_seperator_short_legendary"]
    roi = [0, 0, img_item_descr.shape[1], ResManager().offsets.find_seperator_short_offset_top]
    if not (sep_short := search(refs, img_item_descr, 0.68, roi, True, mode="all", do_multi_process=False)).success:
        return None
    sorted_matches = sorted(sep_short.matches, key=lambda match: match.center[1])
    sep_short_match = sorted_matches[0]
    return sep_short_match


def _gen_roi_bullets(sep_short_match: TemplateMatch, img_height: int):
    roi_bullets = [0, sep_short_match.center[1], ResManager().offsets.find_bullet_points_width + 20, img_height]
    return roi_bullets


def find_affix_bullets(img_item_descr: np.ndarray, sep_short_match: TemplateMatch) -> list[TemplateMatch]:
    # TODO small font greater/tempered affix bullet template fallback
    img_height = img_item_descr.shape[0]
    roi_bullets = _gen_roi_bullets(sep_short_match, img_height)
    if not (
        affix_bullets := search(
            [
                "affix_bullet_point_medium",
                "greater_affix_bullet_point_medium",
                "tempered_affix_bullet_point_medium",
                "rerolled_bullet_point_medium",
            ],
            img_item_descr,
            0.85,
            roi_bullets,
            True,
            mode="all",
        )
    ).success:
        if not (
            affix_bullets := search(["affix_bullet_point", "rerolled_bullet_point"], img_item_descr, 0.85, roi_bullets, True, mode="all")
        ).success:
            return []
    affix_bullets.matches = sorted(affix_bullets.matches, key=lambda match: match.center[1])
    return affix_bullets.matches


def find_empty_sockets(img_item_descr: np.ndarray, sep_short_match: TemplateMatch) -> list[TemplateMatch]:
    img_height = img_item_descr.shape[0]
    roi_bullets = _gen_roi_bullets(sep_short_match, img_height)
    empty_sockets = search("empty_socket", img_item_descr, 0.85, roi_bullets, True, mode="all")
    empty_sockets.matches = sorted(empty_sockets.matches, key=lambda match: match.center[1])
    return empty_sockets.matches


def find_aspect_bullet(img_item_descr: np.ndarray, sep_short_match: TemplateMatch) -> TemplateMatch | None:
    img_height = img_item_descr.shape[0]
    roi_bullets = _gen_roi_bullets(sep_short_match, img_height)
    if not (
        aspect_bullets := search(
            ["aspect_bullet_point_medium", "unique_bullet_point_medium"], img_item_descr, 0.8, roi_bullets, True, mode="first"
        )
    ).success:
        if not (
            aspect_bullets := search(["aspect_bullet_point", "unique_bullet_point"], img_item_descr, 0.8, roi_bullets, True, mode="first")
        ).success:
            return None
    return aspect_bullets.matches[0]


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


def find_codex_upgrade_icon(img_item_descr: np.ndarray) -> bool:
    # TODO small font template fallback
    return search(["codex_upgrade_icon_medium"], img_item_descr, 0.8, use_grayscale=True, mode="first").success
