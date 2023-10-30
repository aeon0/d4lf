import os
import re
from functools import cache

ERROR_MAP = {
    "SHIFLD": "SHIELD",
    "SPFAR": "SPEAR",
    "GLOVFS": "GLOVES",
    "GOLP": "GOLD",
    "TELEFORT": "TELEPORT",
    "TROPHV": "TROPHY",
    "CLAVMORE": "CLAYMORE",
    "MAKIMUM": "MAXIMUM",
    "DEKTERITY": "DEXTERITY",
    "DERTERITY": "DEXTERITY",
    "QUAHTITY": "QUANTITY",
    "DEFERSE": "DEFENSE",
    "ARMGR": "ARMOR",
    "ARMER": "ARMOR",
    "COMDAT": "COMBAT",
    "WEAPORS": "WEAPONS",
    "AXECLASS": "AXE CLASS",
    "IOX%": "10%",
    "IO%": "10%",
    "TWYO": "TWO",
    "ATTRIOUTES": "ATTRIBUTES",
    "MONARCHI": "MONARCH",
    "10 RUNE": "IO RUNE",
    "1O RUNE": "IO RUNE",
    "I0 RUNE": "IO RUNE",
    "1IST RUNE": "IST RUNE",
    "JAR RUNE": "JAH RUNE",
    "YO": "TO",
    "QU AB": "QUHAB",
    "QUAB": "QUHAB",
    " :": ":",
}

REGEX_CORRECTIONS = [
    (re.compile(r"(?<=[A-Z])II|II(?=[A-Z])|1?=[a-z]"), "U"),
    (re.compile(r"(?<=[A-Z])11|11(?=[A-Z])|1?=[a-z]"), "U"),
    (re.compile(r"(?<=[%I0-9\-+])I|I(?=[%I0-9\-+])"), "1"),
    (re.compile(r"(?<=[A-Z])1|1(?=[A-Z])|1?=[a-z]"), "I"),
]

SINGLE_CHARACTER_ERRORS = {
    " I ": " 1 ",
    " I\n": " 1\n",
    "\nI ": "\n1 ",
    " S ": " 5 ",
    " S\n": " 5\n",
    "\nS ": "\n5 ",
    " O ": " 0 ",
    " O\n": " 0\n",
    "\nO ": "\n0 ",
}

STARTING_CHARACTERS_TO_STRIP = {"‘", "'"}

SUFFIXES = {"s", "es", "ies", "ves", "ing", "ed", "er", "est", "ly", "y", "ful", "less", "ness", "'", "'s"}


@cache
def word_lists(directory: str = "assets/word_lists") -> dict[str, set[str]]:
    word_lists = {}

    # Iterate over every file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Ensure we are reading files and not directories
        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                # Assuming each word in the file is on a new line
                words_set = set(line.strip() for line in f)

            # Use filename without extension as the key
            key = os.path.splitext(filename)[0].lower()
            word_lists[key] = words_set

    return word_lists
