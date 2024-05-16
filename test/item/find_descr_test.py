import time

import cv2
import pytest

from cam import Cam
from item.data.rarity import ItemRarity
from item.find_descr import find_descr

BASE_PATH = "test/assets/item"


@pytest.mark.parametrize(
    "img_res, input_img, anchor, expected_success, expected_top_left, expected_rarity",
    [
        ((1920, 1080), f"{BASE_PATH}/find_descr_rare_1080p.png", (1450, 761), True, (1043, 509), ItemRarity.Rare),
        ((1920, 1080), f"{BASE_PATH}/find_descr_common_1080p.png", (75, 320), True, (127, 157), ItemRarity.Common),
        ((1920, 1080), f"{BASE_PATH}/find_descr_legendary_1080p.png", (1515, 761), True, (1088, 78), ItemRarity.Legendary),
        ((2560, 1440), f"{BASE_PATH}/find_descr_legendary_1440p.png", (1723, 1012), True, (1156, 296), ItemRarity.Legendary),
        ((3840, 2160), f"{BASE_PATH}/find_descr_magic_2160p.png", (3258, 1523), True, (2396, 743), ItemRarity.Magic),
    ],
)
def test_find_descr(img_res, input_img, anchor, expected_success, expected_top_left, expected_rarity):
    Cam().update_window_pos(0, 0, *img_res)
    img = cv2.imread(input_img)
    start = time.time()
    success, item_rarity, cropped_img, roi = find_descr(img, anchor)
    top_left_corner = None if not success else roi[:2]
    print("Runtime (find_descr()): ", time.time() - start)
    if success and False:
        cv2.imwrite(f"item_descr.png", cropped_img)
    assert success == expected_success
    tolerance = 0.01 * img_res[0]
    assert abs(top_left_corner[0] - expected_top_left[0]) <= tolerance
    assert abs(top_left_corner[1] - expected_top_left[1]) <= tolerance
    assert item_rarity == expected_rarity
