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
        ((2560, 1440), f"{BASE_PATH}/char_open_1440p.png"),
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
