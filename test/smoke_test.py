import time

import cv2

from cam import Cam
from item.data.rarity import ItemRarity
from item.descr.read_descr import read_descr
from item.filter import Filter
from item.find_descr import find_descr


def test_smoke():
    res = (2560, 1440)
    anchor = (1723, 1012)
    Cam().update_window_pos(0, 0, *res)
    img = cv2.imread("test/assets/item/find_descr_legendary_1440p.png")
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
    filter = Filter()
    res = filter.should_keep(item_descr)
    print("Runtime (full): ", time.time() - start, res.keep)
