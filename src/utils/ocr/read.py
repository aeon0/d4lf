import cv2
import numpy as np
from tesserocr import OEM, PyTessBaseAPI

from utils.ocr.models import OcrResult

TESSDATA_PATH = "assets/tessdata"

API = PyTessBaseAPI(psm=3, oem=OEM.LSTM_ONLY, path=TESSDATA_PATH, lang="eng")
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


def image_to_text(img: np.ndarray) -> OcrResult:
    """
    Extract text from the entire image.
    :param img: The input image.
    :param langmodel: The language model to use.
    :param psm: The PSM mode to use.
    :param scale: The scaling factor for the image.
    :return: The OCR result.
    """
    psm = 3
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
