from dataclasses import dataclass, field
import numpy as np


@dataclass
class OcrResult:
    text: str = None
    original_text: str = None
    rectangle: tuple[int, int, int, int] = field(default=None)
    word_confidences: list = field(default_factory=list)
    mean_confidence: float = None


@dataclass
class TextBox:
    img: np.ndarray = None
    rectangle: tuple = field(default=None)
    ocr_result: OcrResult = None


@dataclass
class BestMatchResult:
    match: str
    score: float
    score_normalized: float
