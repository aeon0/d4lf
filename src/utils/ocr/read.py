import concurrent.futures

import time
import cv2
import numpy as np
from tesserocr import OEM, PyTessBaseAPI

from utils.image_operations import crop, upscale
from utils.roi_operations import bounding_box
from utils.ocr.models import OcrResult, TextBox
from utils.ocr.text_correction import OcrCorrector

TESSDATA_PATH = "assets/tessdata"

API = PyTessBaseAPI(psm=3, oem=OEM.LSTM_ONLY, path=TESSDATA_PATH, lang="eng")


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


def _get_text_from_img(img: np.ndarray, api: PyTessBaseAPI, psm: int, correct_text: bool = True) -> OcrResult:
    """
    Extract text from the given image using Tesseract.
    :param img: The input image.
    :param api: The Tesseract API instance.
    :param psm: The PSM mode to use.
    :return: The OCR result.
    """
    api.SetImageBytes(*_img_to_bytes(img))
    original_text = api.GetUTF8Text().strip()
    text = _strip_new_lines(original_text, psm)
    res = OcrResult(
        original_text=original_text,
        text=text,
        word_confidences=api.AllWordConfidences(),
        mean_confidence=api.MeanTextConf(),
    )
    if correct_text:
        res = OcrCorrector(res, should_check_word_list=False).process_result()
    return res


def _process_rectangle(rectangle, img: np.ndarray, api: PyTessBaseAPI, upscale_if_none: bool, correct_text: bool = True) -> OcrResult:
    """
    Process a given rectangle region of the image and extract text.
    :param rectangle: The rectangle region to process.
    :param img: The input image.
    :param api: The Tesseract API instance.
    :param upscale_if_none: Whether to upscale the image if no text is found.
    :return: The OCR result.
    """
    img_cropped = crop(img, rectangle)
    result = _get_text_from_img(img_cropped, api, 7, correct_text=correct_text)
    if not result.original_text and upscale_if_none:
        img_upscaled = upscale(img_cropped, scale=2)
        result = _get_text_from_img(img_upscaled, api, 7, correct_text=correct_text)
    result.rectangle = rectangle
    return result


def image_to_text(img: np.ndarray) -> OcrResult:
    """
    Extract text from the entire image.
    :param img: The input image.
    :param langmodel: The language model to use.
    :param psm: The PSM mode to use.
    :param scale: The scaling factor for the image.
    :return: The OCR result.
    """
    img = upscale(img, scale=1)
    res = _get_text_from_img(img, API, 3)
    return res


def segmented_image_to_text(
    img: np.ndarray,
    rectangles: set[tuple[int, int, int, int]],
    langmodel: str = "eng",
    upscale_if_none: bool = True,
    run_threaded: bool = True,  # generally performs better
    correct_text: bool = True,
) -> list[OcrResult]:
    """
    Extract text from segmented regions of the image.
    :param img: The input image.
    :param rectangles: The set of rectangle regions to extract from.
    :param langmodel: The language model to use.
    :param upscale_if_none: Whether to upscale the image if no text is found.
    :param run_threaded: Whether to run the extraction in parallel threads.
    :return: A list of OCR results.
    """

    def process_rectangle(rect):
        with PyTessBaseAPI(psm=7, oem=OEM.LSTM_ONLY, path=TESSDATA_PATH, lang=langmodel) as api:
            return _process_rectangle(rect, img, api, upscale_if_none)

    if run_threaded:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = [executor.submit(process_rectangle, rect) for rect in rectangles]
            return [task.result() for task in concurrent.futures.as_completed(tasks)]
    else:
        with PyTessBaseAPI(psm=7, oem=OEM.LSTM_ONLY, path=TESSDATA_PATH, lang=langmodel) as api:
            return [_process_rectangle(rect, img, api, upscale_if_none) for rect in rectangles]


def find_and_read_boxes(img: np.ndarray, langmodel: str = "eng", scale: float = 1) -> list[TextBox]:
    """
    Find text boxes in the image and extract text from them.
    :param img: The input image.
    :param langmodel: The language model to use.
    :param scale: The scaling factor for the image.
    :return: A list of text boxes with their OCR results.
    """
    img = upscale(img, scale=scale)
    boxes = []
    with PyTessBaseAPI(path=TESSDATA_PATH, lang=langmodel) as api:
        api.SetImageBytes(*_img_to_bytes(img))
        for _, box, _, _ in api.GetTextlines():
            rectangle = (box["x"], box["y"], box["w"], box["h"])
            ocr_result = _process_rectangle(rectangle, img, api, upscale_if_none=False)
            boxes.append(TextBox(img=crop(img, rectangle), rectangle=rectangle, ocr_result=ocr_result))
    return boxes


def merge_ocr_results(*results: OcrResult, newline: bool = False) -> OcrResult:
    """
    Merge multiple OCR results into a single OCR result.
    :param results: One or more OcrResult objects to be merged.
    :param newline: If True, results are merged with newline separators.
                    If any OcrResult.text ends with a hyphen, it will be joined with the next result's text
                    without any newline character or space.
                    If False, results are merged with space separators.
    :return: A single merged OcrResult object.
    """
    if not results:
        return OcrResult()  # Return an empty OcrResult if there are no results provided
    if len(results) == 1:
        return results[0]

    # Initial values
    merged_text = results[0].text or ""
    merged_original_text = results[0].original_text or ""
    merged_word_confidences = results[0].word_confidences or []
    rectangles = [results[0].rectangle] if results[0].rectangle else []

    for res in results[1:]:
        # Check if the merged text ends with a hyphen
        if merged_text.endswith("-"):
            merged_text = merged_text[:-1] + (res.text or "")
            merged_original_text = merged_original_text[:-1] + (res.original_text or "")
        else:
            separator_text = "\n" if newline and res.text else " " if res.text else ""
            separator_original_text = "\n" if newline and res.original_text else " " if res.original_text else ""
            merged_text += separator_text + (res.text or "")
            merged_original_text += separator_original_text + (res.original_text or "")

        merged_word_confidences.extend(res.word_confidences or [])
        if res.rectangle:
            rectangles.append(res.rectangle)

    return OcrResult(
        text=merged_text if merged_text else None,
        original_text=merged_original_text if merged_original_text else None,
        rectangle=bounding_box(*rectangles) if rectangles else None,
        word_confidences=merged_word_confidences if merged_word_confidences else None,
        mean_confidence=sum(merged_word_confidences) / len(merged_word_confidences) if merged_word_confidences else None,
    )
