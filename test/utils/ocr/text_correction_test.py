import pytest
from utils.ocr.models import OcrResult
from utils.ocr.text_correction import OcrCorrector

TEST_CASES = [
    {
        "text": "'abc.",
        "confidences": [1],
        "expected_text": "abc.",
        "expected_confidences": [1],
    },
    {
        "text": "The fo x is quick.",
        "confidences": [1, 0.5, 0.5, 1, 1],
        "expected_text": "The fox is quick.",
        "expected_confidences": [1, 0.5 * 2 / 2, 1, 1],
    },
    {
        "text": "The fo x is.\nThe fo x is not.",
        "confidences": [1, 0.5, 0.5, 1, 1, 0.5, 0.5, 1, 1],
        "expected_text": "The fox is.\nThe fox is not.",
        "expected_confidences": [1, 0.5 * 2 / 2, 1, 1, 0.5 * 2 / 2, 1, 1],
    },
    {
        "text": "The catdog is quick.",
        "confidences": [1, 0.5, 1, 1],
        "expected_text": "The cat dog is quick.",
        "expected_confidences": [1, 0.5, 0.5, 1, 1],
    },
    {
        "text": "This is a fo x.",
        "confidences": [1, 1, 1, 0.9, 0.9],
        "expected_text": "This is a fox.",
        "expected_confidences": [1, 1, 1, round(0.9 * 2 / 2, 2)],
    },
    {
        "text": "This is a catdog and a fo x!",
        "confidences": [1, 1, 1, 0.9, 1, 1, 0.8, 0.9],
        "expected_text": "This is a cat dog and a fox!",
        "expected_confidences": [1, 1, 1, 0.9, 0.9, 1, 1, round((0.8 + 0.9) / 2, 2)],
    },
    {
        "text": "This is a known error.",
        "confidences": [1, 1, 1, 0.8, 1],
        "expected_text": "This is an error.",
        "expected_confidences": [1, 1, round((1 + 0.8 + 1) / 3, 2), round((1 + 0.8 + 1) / 3, 2)],
    },
    {
        "text": "fo x catdog fo x",
        "confidences": [0.9, 0.9, 0.8, 0.9, 0.9],
        "expected_text": "fox cat dog fox",
        "expected_confidences": [round(0.9 * 2 / 2, 2), 0.8, 0.8, round(0.9 * 2 / 2, 2)],
    },
    {
        "text": "The temperature is 25I degrees.",
        "confidences": [1, 1, 1, 0.8, 1],
        "expected_text": "The temperature is 251 degrees.",
        "expected_confidences": [1, 1, 1, 0.8, 1],
    },
    {
        "text": "The dragon is a known error catdog plu ral? 25I degrees.",
        "confidences": [1, 0.5, 1, 0.8, 0.8, 0.8, 0.6, 0.7, 0.7, 0.2, 1],
        "expected_text": "The dra gun is an error cat dog plural? 251 degrees.",
        "expected_confidences": [1, 0.5, 0.5, 1, round(0.8 * 3 / 3, 2), round(0.8 * 3 / 3, 2), 0.6, 0.6, round(0.7 * 2 / 2, 2), 0.2, 1],
    },
    {
        "text": "fo x catdog fo x dragon dragon 25I 25I plu ral plu ral",
        "confidences": [0.9, 0.9, 0.8, 0.9, 0.9, 0.7, 0.7, 0.5, 0.5, 0.4, 0.4, 0.2, 0.2],
        "expected_text": "fox cat dog fox dra gun dra gun 251 251 plural plural",
        "expected_confidences": [
            round(0.9 * 2 / 2, 2),
            0.8,
            0.8,
            round(0.9 * 2 / 2, 2),
            0.7,
            0.7,
            0.7,
            0.7,
            0.5,
            0.5,
            round(0.4 * 2 / 2, 2),
            round(0.2 * 2 / 2, 2),
        ],
    },
]


TEST_ERROR_MAP = {"a known error": "an error", "catdog": "cat dog", "fo x": "fox", "dragon": "dra gun", "plu ral": "plural"}

# Sample word list for testing purposes
SAMPLE_WORD_LIST = {
    "hello",
    "world",
    "good",
    "morning",
    "SHIELD",
    "SPEAR",
    "ARMOR",
    "two",
    "AXE CLASS",
    "10%",
    "QUHAB",
    ":",
    "U",
    "1",
    "5",
    "0",
    "customword1",
    "customword2",
}


@pytest.fixture
def ocr_corrector():
    ocr_result = OcrResult(text="hwllo world", original_text="hwllo world", word_confidences=[90, 80])
    return OcrCorrector(ocr_result, word_list=SAMPLE_WORD_LIST)


def test_initialization():
    ocr_result = OcrResult(text="sample text", original_text="sample text", word_confidences=[90, 80])
    corrector = OcrCorrector(ocr_result, word_list=SAMPLE_WORD_LIST)

    assert corrector._original_result.text == "sample text"


def test_find_best_match(ocr_corrector: OcrCorrector):
    # Exact match
    result = ocr_corrector._find_best_match("hello")
    assert result.match == "hello"

    # Typo
    result = ocr_corrector._find_best_match("hwllo")
    assert result.match == "hello"


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("good I morning", "good 1 morning"),
        ("good S morning", "good 5 morning"),
        ("good O morning", "good 0 morning"),
        ("good : morning", "good : morning"),
        ("good U morning", "good U morning"),
        ("good II morning", "good 11 morning"),
    ],
)
def test_fix_common_mistakes(ocr_corrector: OcrCorrector, input_text, expected_output):
    ocr_corrector._working_result.text = input_text
    ocr_corrector._fix_common_mistakes()
    assert ocr_corrector._working_result.text == expected_output


# this section is all tested in process_result() anyway
"""
@pytest.mark.parametrize("test_case", TEST_CASES)
def test_fix_known_errors(ocr_corrector: OcrCorrector, monkeypatch, test_case):
    # Override ERROR_MAP for this test
    monkeypatch.setattr("utils.ocr.text_correction.ERROR_MAP", TEST_ERROR_MAP)

    ocr_corrector._working_result.text = test_case["text"]
    ocr_corrector._working_result.word_confidences = test_case["confidences"]
    ocr_corrector._fix_known_errors()

    assert ocr_corrector._working_result.text == test_case["expected_text"]
    assert ocr_corrector._working_result.word_confidences == test_case["expected_confidences"]
"""


def test_check_word_list():
    test_cases = [
        ("Invulnerab1lity and a hodgepodga.", "Invulnerability and a hodgepodge."),
        ("This is a customwrd1.", "This is a customword1."),
        ("An applianco, a bulldozar, and a customwrd2 went to a party.", "An appliance, a bulldozer, and a customword2 went to a party."),
        ("A simple sentence with no mistakes.", "A simple sentence with no mistakes."),
        ("The Elephint jumped over the, moon!", "The Elephant jumped over the, moon!"),
    ]

    for input_text, expected_output in test_cases:
        word_confidences = [0.9] * len(input_text.split())
        ocr_result = OcrResult(text=input_text, word_confidences=word_confidences)
        ocr_corrector = OcrCorrector(ocr_result, word_list=SAMPLE_WORD_LIST, should_check_eng_dictionary=True)
        result = ocr_corrector.process_result()
        assert result.text == expected_output, f"Expected {expected_output}, got {result.text}"


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_process_result(monkeypatch, test_case):
    # Override ERROR_MAP for this test
    monkeypatch.setattr("utils.ocr.text_correction.ERROR_MAP", TEST_ERROR_MAP)

    ocr_result = OcrResult(text=test_case["text"], original_text=test_case["text"], word_confidences=test_case["confidences"])
    corrector = OcrCorrector(
        ocr_result,
        should_fix_common_mistakes=True,
        should_fix_known_errors=True,
        should_check_word_list=False,
        should_check_eng_dictionary=False,
    )

    result = corrector.process_result()

    assert result.text == test_case["expected_text"]
