import time

import cv2
from cam import Cam
from item.data.rarity import ItemRarity
from item.descr.read_descr import read_descr
from item.filter import Filter
from item.find_descr import find_descr


def test_smoke():
    res = (1920, 1080)
    anchor = (1450, 761)
    Cam().update_window_pos(0, 0, *res)
    img = cv2.imread("tests/assets/item/find_descr_rare_1080p.png")
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
