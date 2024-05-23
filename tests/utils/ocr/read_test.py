import cv2
from utils.ocr.read import image_to_text


def test_tesserocr():
    """
    Test tesserocr
    - Reads a plain image and asserts result is as expected
    """
    img = cv2.imread("tests/assets/ocr/header_champions_demise.png")
    assert image_to_text(img).text == "Champion's Demise"
