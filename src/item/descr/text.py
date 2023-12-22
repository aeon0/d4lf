import re
from rapidfuzz import process


def closest_match(target, candidates, min_score=86):
    keys, values = zip(*candidates.items())
    result = process.extractOne(target, values)
    if result and result[1] >= min_score:
        matched_key = keys[values.index(result[0])]
        return matched_key
    return None


def closest_to(value, choices):
    return min(choices, key=lambda x: abs(x - value))


def find_number(s: str, idx: int = 0) -> float:
    s = re.sub(r",", "", s)  # remove commas because of large numbers having a comma seperator
    matches = re.findall(r"[+-]?(\d+\.\d+|\.\d+|\d+\.?|\d+)\%?", s)
    if "up to a 5%" in s:
        number = matches[1] if len(matches) > 1 else None
    else:
        number = matches[idx] if matches and len(matches) > idx else None
    if number is not None:
        return float(number.replace("+", "").replace("%", ""))
    return None


def remove_text_after_first_keyword(text: str, keywords: str) -> str:
    for keyword in keywords:
        match = re.search(re.escape(keyword), text)
        if match:
            return text[: match.start()]
    return text


def clean_str(s: str) -> str:
    cleaned_str = re.sub(r"(\d)[, ]+(\d)", r"\1\2", s)  # Remove , between numbers (large number seperator)
    cleaned_str = re.sub(r"(\+)?\d+(\.\d+)?%?", "", cleaned_str)  # Remove numbers and trailing % or preceding +
    cleaned_str = cleaned_str.replace("[x]", "")  # Remove all [x]
    cleaned_str = cleaned_str.replace("durability:", "")
    cleaned_str = re.sub(r"[\[\]+\-:%\']", "", cleaned_str)  # Remove [ and ] and leftover +, -, %, :, '
    cleaned_str = re.sub(
        r"\((rogue|barbarian|druid|sorcerer|necromancer) only\)", "", cleaned_str
    )  # this is not included in our affix table
    cleaned_str = remove_text_after_first_keyword(cleaned_str, ["requires level", "requires lev", "account", "sell value", "pacts"])
    cleaned_str = re.sub(
        r"(scroll up|account bound|requires level|only\)|sell value|barbarian|rogue|sorceress|druid|necromancer|not useable|by your class|by your clas)",
        "",
        cleaned_str,
    )  # Remove new terms
    cleaned_str = " ".join(cleaned_str.split())  # Remove extra spaces
    return cleaned_str
