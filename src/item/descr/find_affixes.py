import numpy as np
import json
from template_finder import TemplateMatch
from item.corrections import ERROR_MAP
from item.data.affix import Affix
from item.descr.text import clean_str, closest_match, closest_to, find_number
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
    affix_sigil_dict = {**affix_sigil_dict_all["negative"], **affix_sigil_dict_all["positive"]}


def find_affixes(
    img_item_descr: np.ndarray, affix_bullets: list[TemplateMatch], bottom_limit: int, is_sigil: bool = False
) -> tuple[list[Affix] | None, str]:
    affixes: list[Affix] = []

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
    affix_lines = image_to_text(crop_full_affix).text.lower().split("\n")
    affix_lines = [line for line in affix_lines if line]  # remove empty lines
    # split affix text based on distance of affix bullet points
    delta_y_arr = [affix_bullets[i].center[1] - affix_bullets[i - 1].center[1] for i in range(1, len(affix_bullets))]
    delta_y_arr.append(None)
    line_idx = 0
    for dy in delta_y_arr:
        if dy is None:
            combined_lines = "\n".join(affix_lines[line_idx:])
        else:
            closest_value = closest_to(dy, [line_height, line_height * 2, line_height * 3])
            if closest_value == line_height:
                lines_to_add = 1
            elif closest_value == line_height * 2:
                lines_to_add = 2
            else:  # the most lines an affix can have is 3
                lines_to_add = 3
            combined_lines = "\n".join(affix_lines[line_idx : line_idx + lines_to_add])
            line_idx += lines_to_add
        combined_lines = combined_lines.replace("\n", " ")
        for error, correction in ERROR_MAP.items():
            combined_lines = combined_lines.replace(error, correction)
        cleaned_str = clean_str(combined_lines)

        if is_sigil:
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
            affix.loc = [affix_x, affix_bullets[i].center[1]]

    return affixes, ""
