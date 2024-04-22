import time

import cv2
import numpy as np
from tesserocr import OEM, PyTessBaseAPI, RIL

from config.data import COLORS
from config.loader import IniConfigLoader
from logger import Logger
from utils.image_operations import color_filter
from utils.ocr.models import OcrResult

TESSDATA_PATH = "assets/tessdata"

#   0    Orientation and script detection (OSD) only.
#   1    Automatic page segmentation with OSD.
#   2    Automatic page segmentation, but no OSD, or OCR.
#   3    Fully automatic page segmentation, but no OSD. (Default)
#   4    Assume a single column of text of variable sizes.
#   5    Assume a single uniform block of vertically aligned text.
#   6    Assume a single uniform block of text.
#   7    Treat the image as a single text line.
#   8    Treat the image as a single word.
#   9    Treat the image as a single word in a circle.
#  10    Treat the image as a single character.
#  11    Sparse text. Find as much text as possible in no particular order.
#  12    Sparse text with OSD.
#  13    Raw line. Treat the image as a single text line,
#           bypassing hacks that are Tesseract-specif

API = None


# supposed to give fruther runtime improvements, but reading performance really goes down...
# API.SetVariable("tessedit_do_invert", "0")


def load_api():
    global API
    API = PyTessBaseAPI(psm=3, oem=OEM.LSTM_ONLY, path=TESSDATA_PATH, lang=IniConfigLoader().general.language)


def _img_to_bytes(image: np.ndarray, colorspace: str = "BGR"):
    """
    Convert the given image to bytes suitable for Tesseract.
    :param image: The input image.
    :param colorspace: The color space of the image.
    :return: A tuple containing the image bytes, width, height, bytes per pixel, and bytes per line.
    """
    bytes_per_pixel = image.shape[2] if len(image.shape) == 3 else 1
    height, width = image.shape[:2]
    bytes_per_line = bytes_per_pixel * width
    if bytes_per_pixel > 1 and colorspace != "RGB":
        image = cv2.cvtColor(image, getattr(cv2, f"COLOR_{colorspace}2RGB"))
    elif image.dtype == bool:
        image = np.packbits(image, axis=1)
        bytes_per_line = image.shape[1]
        width = bytes_per_line * 8
        bytes_per_pixel = 0
    return image.tobytes(), width, height, bytes_per_pixel, bytes_per_line


def image_to_text(img: np.ndarray, line_boxes: bool = False, do_pre_proc: bool = True) -> OcrResult | tuple[OcrResult, list[int]]:
    """
    Extract text from the entire image.
    :param img: The input image.
    :param langmodel: The language model to use.
    :param psm: The PSM mode to use.
    :param scale: The scaling factor for the image.
    :return: The OCR result.
    """
    if API is None:
        load_api()

    if img is None or len(img) == 0:
        Logger.warning("img provided to image_to_text() is empty!")
        return OcrResult("", "", word_confidences=0, mean_confidence=0), [] if line_boxes else ""

    if do_pre_proc:
        pre_proced_img = pre_proc_img(img)
        API.SetImageBytes(*_img_to_bytes(pre_proced_img))
    else:
        API.SetImageBytes(*_img_to_bytes(img))
    start = time.time()
    text = API.GetUTF8Text().strip()
    # print(f"Get Text: {time.time() - start}")
    res = OcrResult(
        original_text=text,
        text=text,
        word_confidences=API.AllWordConfidences(),
        mean_confidence=API.MeanTextConf(),
    )
    if line_boxes:
        start = time.time()
        line_boxes_res = API.GetComponentImages(RIL.TEXTLINE, True)
        # print(f"Get Lines: {time.time() - start}")
        return res, line_boxes_res
    return res


def pre_proc_img(input_img: np.ndarray) -> np.ndarray:
    img = input_img.copy()
    masked_red, _ = color_filter(img, COLORS.unusable_red, False)
    contours, _ = cv2.findContours(masked_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gamma = 1.8
    gamma_corrected = np.power(gray / 255.0, gamma) * 255.0
    gamma_corrected = gamma_corrected.astype(np.uint8)

    # Apply Gaussian blur to reduce noise and smoothen the image
    blurred = gamma_corrected  # cv2.GaussianBlur(gamma_corrected, (3, 3), 0)

    # Perform morphological operations to further enhance text regions
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(blurred, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)

    return eroded
