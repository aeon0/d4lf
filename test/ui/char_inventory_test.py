import time
import pytest
import cv2
from ui.char_inventory import CharInventory
from cam import Cam
from config import Config
from template_finder import stored_templates


BASE_PATH = "test/assets/ui"


@pytest.mark.parametrize(
    "img_res, input_img",
    [
        ((1920, 1080), f"{BASE_PATH}/char_open_1080p.png"),
        ((2560, 1440), f"{BASE_PATH}/char_open_1440p.png"),
        ((3440, 1440), f"{BASE_PATH}/char_open_1440p_wide.png"),
        ((3840, 2160), f"{BASE_PATH}/char_open_2160p.png"),
    ],
)
def test_char_inventory(img_res, input_img):
    Cam().update_window_pos(0, 0, img_res[0], img_res[1])
    Config().load_data()
    stored_templates.cache_clear()
    img = cv2.imread(input_img)
    inv = CharInventory()
    flag = inv.is_open(img)
    assert flag


@pytest.mark.parametrize(
    "img_res, input_img",
    [
        ((1920, 1080), f"{BASE_PATH}/char_inventory_fav_junk_1080p.png"),
    ],
)
def test_get_item_slots(img_res, input_img):
    Cam().update_window_pos(0, 0, img_res[0], img_res[1])
    Config().load_data()
    stored_templates.cache_clear()
    img = cv2.imread(input_img)
    inv = CharInventory()
    occupied, open = inv.get_item_slots(img)
    for slot in occupied:
        if slot.is_fav:
            cv2.circle(img, slot.center, 5, (0, 255, 0), 4)
        elif slot.is_junk:
            cv2.circle(img, slot.center, 5, (0, 0, 255), 4)
        else:
            cv2.circle(img, slot.center, 5, (255, 0, 0), 4)
    for slot in open:
        cv2.circle(img, slot.center, 5, (255, 255, 0), 4)
    if False:
        cv2.imshow("char_inv", img)
        cv2.waitKey(0)
