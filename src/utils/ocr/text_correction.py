import re

from nltk import download
from nltk.data import find

# Check if the "words" corpus from nltk is already downloaded. If not, download it.
try:
    find("corpora/words")
except LookupError:
    download("words")
from nltk.corpus import words
from nltk.stem import PorterStemmer
from rapidfuzz.distance import Levenshtein
from rapidfuzz.process import extractOne

from logger import Logger
from utils.ocr.constants import ERROR_MAP, REGEX_CORRECTIONS, SINGLE_CHARACTER_ERRORS, STARTING_CHARACTERS_TO_STRIP, word_lists, SUFFIXES
from utils.ocr.models import BestMatchResult, OcrResult


class OcrCorrector:
    def __init__(
        self,
        ocr_result: OcrResult,
        word_list: set[str] | list[str] = word_lists()["all"],
        normalized_lev_threshold: float = 0.6,
        should_fix_common_mistakes: bool = True,
        should_fix_known_errors: bool = True,
        should_check_word_list: bool = True,
        should_check_eng_dictionary: bool = False,
        min_word_length_to_correct: int = 3,
    ):
        """
        Initializes the OCR Corrector with the given parameters.
        :param ocr_result: The OCR result to be corrected.
        :param word_list: Custom list or set of words to check against, defaults to all D4 strings
        :param normalized_lev_threshold: Threshold for the normalized Levenshtein distance to decide a best match.
        :param should_fix_common_mistakes: Flag to decide if common OCR mistakes should be fixed.
        :param should_fix_known_errors: Flag to decide if known OCR errors should be fixed.
        :param should_check_word_list: Flag to decide if a word list should be used for corrections.
        :param should_check_eng_dictionary: Flag to decide if English dictionary should be used for corrections.
        :param min_word_length_to_correct: Minimum word length to consider for corrections.
        """
        self._original_result = ocr_result
        self._working_result = ocr_result
        self._word_list = set(word_list) if isinstance(word_list, list) else word_list
        self._normalized_lev_threshold = normalized_lev_threshold
        self._should_fix_common_mistakes = should_fix_common_mistakes
        self._should_fix_known_errors = should_fix_known_errors
        self._min_word_length_to_correct = min_word_length_to_correct
        self._combined_word_list = set()
        # set self._words to the union of the word list and the english words depending on which should be checked, if any
        if should_check_eng_dictionary:
            self._combined_word_list.update(set(words.words()))
        if should_check_word_list:
            self._combined_word_list.update(self._word_list)
        self._stemmer = PorterStemmer()

    def _find_best_match(self, word: str) -> BestMatchResult:
        """
        Find the best match for a given word from the combined word list.
        :param word: The word to find the best match for.
        :return: A result containing the best match and associated scores.
        """
        best_match, best_lev, _ = extractOne(word, self._combined_word_list, scorer=Levenshtein.distance)
        best_lev_normalized = round(1 - best_lev / max(1, len(word)), 3)
        # print(f"{word} is not in word list. Best match is {best_match} with score {round(best_lev_normalized, 2)}")
        return BestMatchResult(best_match, best_lev, best_lev_normalized)

    def _fix_common_mistakes(self) -> str:
        """
        Fixes common OCR misinterpretations using regex patterns in the working OCR result.
        """
        # Apply regex replacements
        for pattern, replacement in REGEX_CORRECTIONS:
            substituted_text, num_substitutions = pattern.subn(replacement, self._working_result.text)
            if num_substitutions > 0:
                Logger.debug(f"_fix_common_mistakes: Replacing '{pattern.pattern}' with: '{replacement}'.")
                self._working_result.text = substituted_text

        # Apply single character replacements
        for pattern, replacement in SINGLE_CHARACTER_ERRORS.items():
            if pattern in self._working_result.text:
                Logger.debug(f"_fix_common_mistakes: Replacing '{pattern}' with: '{replacement}'.")
                self._working_result.text = self._working_result.text.replace(pattern, replacement)

        # Replace consecutive I's
        while "II" in self._working_result.text:
            Logger.debug(f"_fix_common_mistakes: Replacing 'II' with: '11'.")
            self._working_result.text = self._working_result.text.replace("II", "11")

        # Delete starting characters if they're in the list of characters to strip
        if len(self._working_result.text) > 0 and self._working_result.text[0] in STARTING_CHARACTERS_TO_STRIP:
            Logger.debug(
                f"_fix_common_mistakes: Stripping starting character '{self._working_result.text[0]}' in {self._working_result.text}."
            )
            self._working_result.text = self._working_result.text[1:]

    def _fix_known_errors(self) -> str:
        """
        Fixes known OCR errors based on a predefined map in the working OCR result.
        """
        new_text = ""
        new_confidences = []
        confidences = self._working_result.word_confidences
        for line in self._working_result.text.splitlines():
            words = line.split()
            error_length = correction_length = 0
            cursor_pos = 0
            while cursor_pos < len(words):
                word = words[cursor_pos]
                found_error = False
                for error, correction in ERROR_MAP.items():
                    if error not in line:
                        continue
                    error_length = len(error.split())
                    compare_string = " ".join(words[cursor_pos : cursor_pos + error_length]) if error_length > 1 else word
                    if error in compare_string:
                        found_error = True
                        Logger.debug(f"_fix_known_errors: Replacing {error} with {correction}")
                        new_string = compare_string.replace(error, correction)
                        new_text += new_string + " "
                        correction_length = len(correction.split())
                        # "frozen chicken" -> "fried turkey"
                        if error_length == correction_length:
                            new_confidences.extend(confidences[cursor_pos : cursor_pos + error_length])
                        # "catdog" -> "cat dog"
                        elif error_length < correction_length:
                            new_confidences.extend([confidences[cursor_pos]] * len(correction.split()))
                        # "fo x" -> "fox"
                        elif error_length > correction_length:
                            avg_confidence = round(sum(confidences[cursor_pos : cursor_pos + error_length]) / error_length, 2)
                            # print(f"    Extending confidences- {[avg_confidence] * len(correction.split())}")
                            new_confidences.extend([avg_confidence] * len(correction.split()))
                        cursor_pos += error_length
                if not found_error:
                    new_text += word + " "
                    new_confidences.append(confidences[cursor_pos])
                    cursor_pos += 1
            new_text = new_text.rstrip() + "\n"
        self._working_result.word_confidences = new_confidences
        self._working_result.text = new_text.rstrip()

    def _check_word_list(self) -> str:
        """
        Check the OCR results against a list of words and fix errors in the working OCR result.
        """

        def preserve_case(original: str, corrected: str) -> str:
            """Preserve the case of the original word when correcting it."""
            if original.isupper():
                return corrected.upper()
            elif original[0].isupper():
                return corrected.capitalize()
            else:
                return corrected.lower()

        if len(self._combined_word_list) == 0:
            return

        new_lines = ""
        for line in self._working_result.text.splitlines():
            words_with_punctuation: list[str] = re.findall(r"[\+\-]?\d*\.?\d+%?|\w+[\w'-.]*|\S", line)
            new_words = []

            for word in words_with_punctuation:
                is_corrected = False

                # Extract trailing punctuation
                trailing_punct = re.findall(r'[.!?,"\'-]+$', word)
                trailing_punct = trailing_punct[0] if trailing_punct else ""
                stripped_word = word[: -len(trailing_punct)] if trailing_punct else word

                # If the word is alphanumeric and not just punctuation
                if (
                    re.match(r"\w+", stripped_word)
                    and len(stripped_word) >= self._min_word_length_to_correct
                    and any(c.isalpha() for c in word)
                ):
                    # Check the word in its original form first
                    if word.lower() in self._combined_word_list:
                        new_words.append(word)
                        continue

                    # Check for common plural suffixes and return the best match of the base word minus each suffix

                    res = self._find_best_match(stripped_word.lower())
                    best_base_word = res.match
                    best_match_score = res.score_normalized
                    best_suffix = ""
                    for suffix in SUFFIXES:
                        if not stripped_word.lower().endswith(suffix):
                            continue
                        base_word = stripped_word[: -len(suffix)]
                        if base_word.lower() in self._combined_word_list:
                            best_base_word = base_word
                            best_suffix = suffix
                            break
                        match = self._find_best_match(base_word.lower())
                        if match.score_normalized > best_match_score:
                            best_match_score = match.score_normalized
                            best_base_word = base_word
                            best_suffix = suffix
                    if stripped_word != best_base_word + best_suffix:
                        if best_match_score >= self._normalized_lev_threshold:
                            corrected_word = preserve_case(word, best_base_word) + best_suffix + trailing_punct
                            Logger.debug(f"_check_word_list: Replacing {word} with {corrected_word} (score {best_match_score:.1%})")
                            new_words.append(corrected_word)
                            is_corrected = True
                            continue
                        else:
                            Logger.debug(f"_check_word_list: No word list match for {word} (score {best_match_score:.1%})")

                if not is_corrected:
                    new_words.append(word)  # Add the word or punctuation back to the new list

            # Recombine words with a space unless the next word is punctuation
            result_text = []
            for i, word in enumerate(new_words):
                result_text.append(word)
                # Ensure the next word is a word character and not punctuation to add space
                if i < len(new_words) - 1 and re.match(r"\w+", new_words[i + 1]) and not (word == "," and new_words[i + 1].isdigit()):
                    result_text.append(" ")

            new_lines += "".join(result_text) + "\n"
            # print(repr(new_lines))
        self._working_result.text = new_lines.rstrip()

    def process_result(self) -> OcrResult:
        """
        Processes the OCR result to fix common mistakes, known errors, and check against the word list.
        :return: Corrected OCR result.
        """
        if self._should_fix_common_mistakes:
            self._fix_common_mistakes()
        if self._should_fix_known_errors:
            self._fix_known_errors()
        self._check_word_list()
        return self._working_result
