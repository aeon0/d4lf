import numpy as np
import time
from config import Config
from template_finder import search, TemplateMatch


def find_seperator_short(img_item_descr: np.ndarray) -> TemplateMatch:
    # Detect textures (1)
    # =====================================
    start_tex_1 = time.time()
    refs = ["item_seperator_short_rare", "item_seperator_short_legendary"]
    roi = [0, 0, img_item_descr.shape[1], Config().ui_offsets["find_seperator_short_offset_top"]]
    if not (sep_short := search(refs, img_item_descr, 0.68, roi, True, mode="all", do_multi_process=False)).success:
        return None
    sorted_matches = sorted(sep_short.matches, key=lambda match: match.center[1])
    sep_short_match = sorted_matches[0]
    # print("-----")
    # print("Runtime (start_tex_1): ", time.time() - start_tex_1)
    return sep_short_match
