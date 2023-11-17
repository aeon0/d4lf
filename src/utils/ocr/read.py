import cv2
import numpy as np
from tesserocr import OEM, PyTessBaseAPI

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

API = PyTessBaseAPI(psm=3, oem=OEM.LSTM_ONLY, path=TESSDATA_PATH, lang="eng")
API2 = PyTessBaseAPI(psm=12, oem=OEM.LSTM_ONLY, path=TESSDATA_PATH, lang="eng")
# supposed to give fruther runtime improvements, but reading performance really goes down...
# API.SetVariable("tessedit_do_invert", "0")


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


def _strip_new_lines(original_text: str, psm: int) -> str:
    """
    Post-process the extracted text
    :param original_text: The original extracted text.
    :param psm: The PSM mode used for extraction.
    :return: The post-processed text.
    """
    new_text = original_text
    if psm in {7, 8, 13}:
        new_text.replace("\n", "")
    return new_text


def image_to_text(img: np.ndarray, spares_text: bool = False) -> OcrResult:
    """
    Extract text from the entire image.
    :param img: The input image.
    :param langmodel: The language model to use.
    :param psm: The PSM mode to use.
    :param scale: The scaling factor for the image.
    :return: The OCR result.
    """
    psm = 3
    if spares_text:
        API2.SetImageBytes(*_img_to_bytes(img))
        original_text = API2.GetUTF8Text().strip()
    else:
        API.SetImageBytes(*_img_to_bytes(img))
        original_text = API.GetUTF8Text().strip()
    text = _strip_new_lines(original_text, psm)
    res = OcrResult(
        original_text=original_text,
        text=text,
        word_confidences=API.AllWordConfidences(),
        mean_confidence=API.MeanTextConf(),
    )
    return res
