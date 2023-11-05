import cv2
import time
from item.find_descr import find_descr
from item.read_descr import read_descr
from item.filter import Filter
from item.data.rarity import ItemRarity
from cam import Cam
from config import Config
from template_finder import stored_templates


def test_smoke():
    res = (2560, 1440)
    anchor = (1723, 1012)
    Cam().update_window_pos(0, 0, *res)
    Config().load_data()
    stored_templates.cache_clear()
    img = cv2.imread("test/assets/item/find_descr_legendary_1440p.png")
    start = time.time()
    found, _, rarity, cropped_descr = find_descr(img, anchor)
    print("Runtime (detect): ", time.time() - start)
    assert found
    if rarity == ItemRarity.Unique:
        return
    if rarity in [ItemRarity.Common, ItemRarity.Magic]:
        return
    item_descr = read_descr(rarity, cropped_descr)
    assert item_descr is not None
    filter = Filter()
    keep = filter.should_keep(item_descr)
    print("Runtime (full): ", time.time() - start, keep)
