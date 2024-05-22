import json

# Load JSON files into dictionaries
with open("src/tools/data/custom_affixes.json") as f:
    dict1 = json.load(f)
with open("assets/lang/enUS/affixes.json") as f:
    dict2 = json.load(f)

# Create a new dictionary for keys not in the second file
new_dict = {key: value for key, value in dict1.items() if key not in dict2}

# Write the new dictionary to a JSON file
with open("src/tools/data/new_custom_affixes.json", "w") as f:
    json.dump(new_dict, f, indent=4, ensure_ascii=False)
