import cv2
import pytest

from src.cam import Cam
from src.config import BASE_DIR
from src.item.data.rarity import ItemRarity
from src.item.find_descr import find_descr

BASE_PATH = BASE_DIR / "tests/assets/item/season5"


@pytest.mark.parametrize(
    ("img_res", "input_img", "anchor", "expected_success", "expected_top_left", "expected_rarity"),
    [
        ((3840, 2160), f"{BASE_PATH}/find_descr_mythic_2160p.png", (3017, 1560), True, (2164, 109), ItemRarity.Mythic),
    ],
)
def test_find_descr(img_res, input_img, anchor, expected_success, expected_top_left, expected_rarity):
    Cam().update_window_pos(0, 0, *img_res)
    img = cv2.imread(input_img)
    success, item_rarity, cropped_img, roi = find_descr(img, anchor)
    top_left_corner = None if not success else roi[:2]
    if False:
        cv2.imwrite("item_descr.png", cropped_img)
    assert success == expected_success
    tolerance = 0.01 * img_res[0]
    assert abs(top_left_corner[0] - expected_top_left[0]) <= tolerance
    assert abs(top_left_corner[1] - expected_top_left[1]) <= tolerance
    assert item_rarity == expected_rarity
