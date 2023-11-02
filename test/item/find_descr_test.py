import time
import pytest
import cv2
from item.find_descr import find_descr
from item.data.rarity import ItemRarity
from cam import Cam


BASE_PATH = "test/assets/item"


@pytest.mark.parametrize(
    "img_res, input_img, anchor, expected_success, expected_top_left, expected_rarity",
    [
        ((1920, 1080), f"{BASE_PATH}/find_descr_rare_1920x1080.png", (1630, 763), True, (1196, 377), ItemRarity.Rare),
        ((1920, 1080), f"{BASE_PATH}/find_descr_legendary_1920x1080.png", (1515, 761), True, (1088, 78), ItemRarity.Legendary),
    ],
)
def test_find_descr(img_res, input_img, anchor, expected_success, expected_top_left, expected_rarity):
    Cam().update_window_pos(0, 0, img_res[0], img_res[1])
    img = cv2.imread(input_img)
    start = time.time()
    success, top_left_corner, item_rarity, cropped_img = find_descr(img, anchor)
    print("Runtime (find_descr()): ", time.time() - start)
    if success and False:
        cv2.imwrite(f"item_descr.png", cropped_img)
    assert success == expected_success
    tolerance = 0.01 * img_res[0]
    assert abs(top_left_corner[0] - expected_top_left[0]) <= tolerance
    assert abs(top_left_corner[1] - expected_top_left[1]) <= tolerance
    assert item_rarity == expected_rarity
