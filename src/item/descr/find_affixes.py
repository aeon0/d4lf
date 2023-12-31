import numpy as np
import json
from template_finder import TemplateMatch
from item.corrections import ERROR_MAP
from item.data.affix import Affix
from item.descr.text import clean_str, closest_match, closest_to, find_number, remove_text_after_first_keyword
from config import Config
from utils.image_operations import crop
from template_finder import TemplateMatch
from utils.ocr.read import image_to_text


affix_dict = dict()
with open("assets/affixes.json", "r") as f:
    affix_dict = json.load(f)

affix_sigil_dict = dict()
with open("assets/sigils.json", "r") as f:
    affix_sigil_dict_all = json.load(f)
    affix_sigil_dict = {**affix_sigil_dict_all["negative"], **affix_sigil_dict_all["positive"], **affix_sigil_dict_all["inherent"]}


def split_into_paragraphs(
    affix_lines: list[str],
    line_pos: list[any],
    affix_bullets: list[TemplateMatch],
    threshold: int,
    offset_y_affix_bullets: int,
):
    paragraphs = []
    current_paragraph = ""

    for text, pos in zip(affix_lines, line_pos):
        # Check if any bullet point is close to the line
        is_bullet_close = any(abs(pos[1]["y"] - (bullet.center[1] - offset_y_affix_bullets)) < threshold for bullet in affix_bullets)
        if is_bullet_close:
            if current_paragraph:
                paragraphs.append(current_paragraph)
            current_paragraph = text
        else:
            current_paragraph += f" {text}"

    if current_paragraph:
        paragraphs.append(current_paragraph.strip())

    return paragraphs


def is_within_tolerance(num1, num2, tolerance=1):
    return


def filter_affix_lines(affix_lines: list[str], line_pos: list[any]) -> tuple[list[str], list[any]]:
    filtered_affix_lines = []
    filtered_line_pos = []
    unique_lines = {}
    curr_ly = None
    for i, line in enumerate(line_pos):
        lx = line[1]["x"]
        ly = line[1]["y"]
        if curr_ly is not None and abs(curr_ly - ly) <= 2:
            ly = curr_ly
        if ly not in unique_lines or lx < unique_lines[ly][0]:
            unique_lines[ly] = (lx, i)
        curr_ly = ly
    for _, (_, i) in unique_lines.items():
        filtered_affix_lines.append(affix_lines[i])
        filtered_line_pos.append(line_pos[i])
    return filtered_affix_lines, filtered_line_pos


def find_affixes(
    img_item_descr: np.ndarray, affix_bullets: list[TemplateMatch], bottom_limit: int, is_sigil: bool = False
) -> tuple[list[Affix] | None, str]:
    affixes: list[Affix] = []
    if len(affix_bullets) == 0:
        return affixes, ""

    # Affix starts at first bullet point
    img_width = img_item_descr.shape[1]
    line_height = Config().ui_offsets["item_descr_line_height"]
    affix_top_left = [affix_bullets[0].center[0] + line_height // 4, affix_bullets[0].center[1] - int(line_height * 0.7)]

    # Calc full region of all affixes
    affix_width = img_width - affix_top_left[0]
    affix_height = bottom_limit - affix_top_left[1] - int(line_height * 0.4)
    full_affix_region = [*affix_top_left, affix_width, affix_height]
    crop_full_affix = crop(img_item_descr, full_affix_region)
    # cv2.imwrite("crop_full_affix.png", crop_full_affix)
    do_pre_proc = False if is_sigil else True
    res, line_pos = image_to_text(crop_full_affix, line_boxes=True, do_pre_proc=do_pre_proc)
    affix_lines = res.text.lower().split("\n")
    affix_lines = [line for line in affix_lines if line]  # remove empty lines
    if len(affix_lines) != len(line_pos):
        return None, "affix_lines and line_pos not same length"
    # filter lines that have the same y-coordinate by choosing the smallest x-coordinate. Remove from affix_lines and line_pos
    affix_lines, line_pos = filter_affix_lines(affix_lines, line_pos)
    paragraphs = split_into_paragraphs(affix_lines, line_pos, affix_bullets, int(line_height // 2), full_affix_region[1])

    for combined_lines in paragraphs:
        for error, correction in ERROR_MAP.items():
            combined_lines = combined_lines.replace(error, correction)
        cleaned_str = clean_str(combined_lines)

        if is_sigil:
            # A bit of a hack to match the locations...
            if len(affix_bullets) == 2:
                cleaned_str = remove_text_after_first_keyword(cleaned_str, [" in "])
            found_key = closest_match(cleaned_str, affix_sigil_dict)
        else:
            found_key = closest_match(cleaned_str, affix_dict)
        found_value = find_number(combined_lines)

        if found_key is not None:
            affixes.append(Affix(found_key, found_value, combined_lines))
        else:
            return None, f"[cleaned]: {cleaned_str}, [raw]: {combined_lines}"

    # Add location to the found_values
    affix_x = affix_bullets[0].center[0]
    for i, affix in enumerate(affixes):
        if len(affix_bullets) > i:
            affix.loc = [affix_x, affix_bullets[i].center[1] - 2]

    return affixes, ""
