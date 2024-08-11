import time

import cv2

from src.cam import Cam
from src.config import BASE_DIR
from src.item.data.rarity import ItemRarity
from src.item.descr.read_descr import read_descr
from src.item.filter import Filter
from src.item.find_descr import find_descr

BASE_PATH = BASE_DIR / "tests/assets/item"


def test_smoke():
    res = (1920, 1080)
    anchor = (1450, 761)
    Cam().update_window_pos(0, 0, *res)
    img = cv2.imread(f"{BASE_PATH}/unknown/find_descr_rare_1080p.png")
    start = time.time()
    found, rarity, cropped_descr, _ = find_descr(img, anchor)
    print("Runtime (detect): ", time.time() - start)
    assert found
    if rarity == ItemRarity.Unique:
        return
    if rarity in [ItemRarity.Common, ItemRarity.Magic]:
        return
    item_descr = read_descr(rarity, cropped_descr)
    assert item_descr is not None
    test_filter = Filter()
    res = test_filter.should_keep(item_descr)
    print("Runtime (full): ", time.time() - start, res.keep)
