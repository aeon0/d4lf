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
        ((3840, 2160), f"{BASE_PATH}/2160p_small_find_descr_mythic_1.png", (3017, 1560), True, (2230, 200), ItemRarity.Mythic),
        ((3840, 2160), f"{BASE_PATH}/2160p_small_find_descr_2.png", (2700, 1521), True, (1872, 689), ItemRarity.Legendary),
        ((1920, 1080), f"{BASE_PATH}/1080p_small_find_descr_1.png", (1739, 844), True, (1321, 225), ItemRarity.Legendary),
    ],
)
def test_find_descr(img_res, input_img, anchor, expected_success, expected_top_left, expected_rarity):
    Cam().update_window_pos(0, 0, *img_res)
    img = cv2.imread(input_img)
    success, item_rarity, cropped_img, roi = find_descr(img, anchor)
    top_left_corner = None if not success else roi[:2]
    assert success == expected_success
    tolerance = 0.01 * img_res[0]
    assert abs(top_left_corner[0] - expected_top_left[0]) <= tolerance
    assert abs(top_left_corner[1] - expected_top_left[1]) <= tolerance
    assert item_rarity == expected_rarity
