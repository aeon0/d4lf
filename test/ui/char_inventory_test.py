import time
import pytest
import cv2
from ui.char_inventory import CharInventory
from cam import Cam
from config import Config
from template_finder import stored_templates


BASE_PATH = "test/assets/item"


@pytest.mark.parametrize(
    "img_res, input_img",
    [
        ((2560, 1440), f"{BASE_PATH}/find_descr_legendary_2560x1440_2_inv.png"),
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
