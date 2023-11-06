import pytest
import cv2
from ui.chest import Chest
from cam import Cam
from config import Config
from template_finder import stored_templates


BASE_PATH = "test/assets/ui"


@pytest.mark.parametrize(
    "img_res, input_img",
    [
        ((3440, 1440), f"{BASE_PATH}/chest_open_1440p_wide.png"),
    ],
)
def test_chest(img_res, input_img):
    Cam().update_window_pos(0, 0, img_res[0], img_res[1])
    Config().load_data()
    stored_templates.cache_clear()
    img = cv2.imread(input_img)
    inv = Chest()
    flag = inv.is_open(img)
    assert flag
