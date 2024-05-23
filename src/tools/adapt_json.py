import json
import re

# Step 1: Read the JSON file
with open("assets/aspects_unique.json", encoding="utf-8") as file:
    data = json.load(file)


def _remove_text_after_first_keyword(text, keywords):
    for keyword in keywords:
        match = re.search(re.escape(keyword), text)
        if match:
            return text[: match.start()]
    return text


def _clean_str(s):
    cleaned_str = re.sub(r"(\+)?\d+(\.\d+)?%?", "", s)  # Remove numbers and trailing % or preceding +
    cleaned_str = re.sub(r"[\[\]+\-:%\']", "", cleaned_str)  # Remove [ and ] and leftover +, -, %, :, '
    cleaned_str = re.sub(
        r"\((rogue|barbarian|druid|sorcerer|necromancer) only\)", "", cleaned_str
    )  # this is not included in our affix table
    cleaned_str = _remove_text_after_first_keyword(cleaned_str, ["requires level", "requires lev", "account", "sell value"])
    cleaned_str = re.sub(
        r"(scroll up|account bound|requires level|only\)|sell value|durability|barbarian|rogue|sorceress|druid|necromancer|not useable|by your class|by your clas)",
        "",
        cleaned_str,
    )  # Remove new terms
    return " ".join(cleaned_str.split())  # Remove extra spaces


# Step 2: Process the data (example: modifying keys and values)
# Modify this part according to your specific needs
modified_data = {}
for key, value in data.items():
    new_key = key.strip().lower().replace(" ", "_").replace("'", "")
    new_val = _clean_str(value.lower())
    modified_data[new_key] = new_val

# Step 3: Write to a new JSON file
with open("new_data.json", "w", encoding="utf-8") as file:
    json.dump(modified_data, file, indent=4)
