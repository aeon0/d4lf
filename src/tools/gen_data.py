# generate data from d4data repo
from pathlib import Path
import json
import re
import os


def remove_content_in_braces(input_string):
    pattern = r"\{.*?\}"
    result = re.sub(pattern, "", input_string)
    pattern = r"\[.*?\]"
    result = re.sub(pattern, "", result)
    result = re.sub(r"#%.*?#%", "", result)
    result = re.sub(r"\|.*?:", "|:", result)
    result = result.replace("|", "")
    result = result.replace(";", "")
    result = re.sub(r"(\d)[, ]+(\d)", r"\1\2", result)  # Remove , between numbers (large number seperator)
    result = re.sub(r"(\+)?\d+(\.\d+)?%?", "", result)  # Remove numbers and trailing % or preceding +
    result = re.sub(r"[\[\]+\-:%\'\#]", "", result)  # Remove [ and ] and leftover +, -, %, :, ', #
    result = " ".join(result.split())  # Remove extra spaces
    result.strip()
    return result


def check_ms(input_string):
    start_index = input_string.find("[ms]")
    end_index = input_string.find("[fs]")

    # Check if both "[ms]" and "[fs]" are present
    if start_index != -1 and end_index != -1:
        # Extract the part between "[ms]" and "[fs]"
        input_string = input_string[start_index + 4 : end_index]

    prefixes = ["[ms]", "[ns]", "[fs]", "[p]"]
    for prefix in prefixes:
        if input_string.startswith(prefix):
            input_string = input_string[len(prefix) :]
            break

    input_string = input_string.replace("{d}", "")

    return input_string


def main(d4data_dir: Path, companion_app_dir: Path):
    lang_arr = ["enUS", "deDE", "frFR", "esES", "esMX", "itIT", "jaJP", "koKR", "plPL", "ptBR", "ruRU", "trTR", "zhCN", "zhTW"]

    for l in lang_arr:
        f = f"assets/lang/{l}/affixes.json"
        if os.path.exists(f):
            os.remove(f)
        f = f"assets/lang/{l}/aspects.json"
        if os.path.exists(f):
            os.remove(f)
        f = f"assets/lang/{l}/uniques.json"
        if os.path.exists(f):
            os.remove(f)
        f = f"assets/lang/{l}/sigils.json"
        if os.path.exists(f):
            os.remove(f)
        os.makedirs(f"assets/lang/{l}", exist_ok=True)

    for language in lang_arr:
        # Create Aspects
        print(f"Gen Aspects for {language}")
        aspects_dict = {}
        pattern = f"json/{language}_Text/meta/StringList/Affix_legendary*.stl.json"
        json_files = list(d4data_dir.glob(pattern))
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                snoId = data["__snoID__"]
                name_idx, desc_idx = (0, 1) if data["arStrings"][0]["szLabel"] == "Name" else (1, 0)
                aspect_name = data["arStrings"][name_idx]["szText"]
                aspect_name_clean = aspect_name.strip().replace(" ", "_").lower().replace("’", "").replace("'", "").replace("-", "")
                aspect_name_clean = check_ms(aspect_name_clean)
                aspect_desc = data["arStrings"][desc_idx]["szText"]
                aspect_descr_clean = remove_content_in_braces(aspect_desc.lower().replace("’", ""))
                aspects_dict[aspect_name_clean] = {"desc": aspect_descr_clean, "snoId": snoId}

        with open(f"assets/lang/{language}/aspects.json", "w", encoding="utf-8") as json_file:
            json.dump(aspects_dict, json_file, indent=4, ensure_ascii=False)
            json_file.write("\n")

        # Create Uniques
        print(f"Gen Uniques for {language}")
        unique_dict = {}
        pattern = f"json/{language}_Text/meta/StringList/Item_*_Unique_*.stl.json"
        json_files = list(d4data_dir.glob(pattern))
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                snoId = data["__snoID__"]
                name_idx, _ = (0, 1) if data["arStrings"][0]["szLabel"] == "Name" else (1, 0)
                name = data["arStrings"][name_idx]["szText"]
                name_clean = name.strip().replace(" ", "_").lower().replace("’", "").replace("'", "").replace(",", "")
                name_clean = check_ms(name_clean)
                # Open affix file for affix
                splits = json_file.name.split("_")
                affix_file_name = "Affix_" + "_".join(splits[1:])
                affix_file_path = json_file.parent / affix_file_name
                if not affix_file_path.exists():
                    continue
                with open(affix_file_path, "r", encoding="utf-8") as affix_file:
                    data = json.load(affix_file)
                    desc = data["arStrings"][0]["szText"]
                    desc_clean = remove_content_in_braces(desc.lower().replace("’", ""))
                    unique_dict[name_clean] = {"desc": desc_clean, "snoId": snoId}

        with open(f"assets/lang/{language}/uniques.json", "w", encoding="utf-8") as json_file:
            json.dump(unique_dict, json_file, indent=4, ensure_ascii=False)
            json_file.write("\n")

        # Create Dungeons
        print(f"Gen Sigils for {language}")
        sigil_dict = {
            "dungeons": {},
            "minor": {},
            "major": {},
            "positive": {},
        }
        pattern = f"json/{language}_Text/meta/StringList/world_DGN_*.stl.json"
        json_files = list(d4data_dir.glob(pattern))
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                name_idx, _ = (0, 1) if data["arStrings"][0]["szLabel"] == "Name" else (1, 0)
                dungeon_name: str = data["arStrings"][name_idx]["szText"].lower().strip().replace("’", "").replace("'", "")
                sigil_dict["dungeons"][dungeon_name.replace(" ", "_")] = dungeon_name

        pattern = f"json/{language}_Text/meta/StringList/DungeonAffix_*.stl.json"
        json_files = list(d4data_dir.glob(pattern))
        for json_file in json_files:
            affix_type = json_file.stem.split("_")[1].lower().strip()
            if affix_type in sigil_dict:
                with open(json_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    name = ""
                    desc = ""
                    for sigil_affix in data["arStrings"]:
                        if sigil_affix["szLabel"] == "AffixName":
                            name = sigil_affix["szText"].lower().strip().replace("’", "").replace("'", "")
                            name = name.replace("(", "").replace(")", "").replace("{c_bonus}", "").replace("{/c}", "")
                        else:
                            desc = sigil_affix["szText"].lower().strip().replace("’", "").replace("'", "")
                        sigil_dict[affix_type][name.replace(" ", "_")] = f"{name} {remove_content_in_braces(desc)}"

        with open(f"assets/lang/{language}/sigils.json", "w", encoding="utf-8") as json_file:
            json.dump(sigil_dict, json_file, indent=4, ensure_ascii=False)
            json_file.write("\n")

        # Create Affixes
        # Its quite the hustle to reconstruct the displayed affixes. So using the companion app parsed json. Generated from here:
        # https://github.com/josdemmers/D4DataParser/blob/main/D4DataParser/Parsers/AffixParser.cs
        print(f"Gen Affixes for {language}")
        affix_dict = {}
        json_file = companion_app_dir / f"D4Companion/Data/Affixes.{language}.json"
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            for affix in data:
                desc: str = affix["Description"]
                desc = remove_content_in_braces(desc.lower().strip().replace("'", "").replace("’", ""))
                name = desc.replace(",", "").replace(" ", "_")
                if len(desc) > 2:
                    affix_dict[name] = desc
        with open(f"assets/lang/{language}/affixes.json", "w", encoding="utf-8") as json_file:
            json.dump(affix_dict, json_file, indent=4, ensure_ascii=False)
            json_file.write("\n")

        print("=============================")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Path Argument Parser")
    parser.add_argument("d4data_dir", type=str, help="Provide a path to d4data repo")
    parser.add_argument("companion_app_dir", type=str, help="Provide a path to d4data repo")
    args = parser.parse_args()

    input_path = Path(args.d4data_dir)
    input_path2 = Path(args.companion_app_dir)

    if input_path.exists() and input_path.is_dir() and input_path2.exists() and input_path2.is_dir():
        main(input_path, input_path2)
    else:
        print(f"The provided path '{input_path}' or '{input_path2}' does not exist or is not a directory.")
