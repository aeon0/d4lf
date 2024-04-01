import json
import threading

from config.loader import IniConfigLoader
from item.data.item_type import ItemType
from logger import Logger

dataloader_lock = threading.Lock()


class Dataloader:
    error_map = dict()
    affix_dict = dict()
    affix_sigil_dict = dict()
    aspect_dict = dict()
    aspect_num_idx = dict()
    aspect_unique_dict = dict()
    aspect_unique_num_idx = dict()
    tooltips = dict()

    _instance = None
    data_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Dataloader, cls).__new__(cls)
            with dataloader_lock:
                if not cls._instance.data_loaded:
                    cls._instance.data_loaded = True
                    cls._instance.load_data()
        return cls._instance

    def load_data(self):
        with open(f"assets/lang/{IniConfigLoader().general.language}/affixes.json", "r", encoding="utf-8") as f:
            self.affix_dict: dict = json.load(f)

        with open(f"assets/lang/{IniConfigLoader().general.language}/sigils.json", "r", encoding="utf-8") as f:
            affix_sigil_dict_all = json.load(f)
            self.affix_sigil_dict = {
                **affix_sigil_dict_all["dungeons"],
                **affix_sigil_dict_all["minor"],
                **affix_sigil_dict_all["major"],
                **affix_sigil_dict_all["positive"],
            }

        with open(f"assets/lang/{IniConfigLoader().general.language}/corrections.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.error_map = data["error_map"]
            self.filter_after_keyword = data["filter_after_keyword"]
            self.filter_words = data["filter_words"]

        with open(f"assets/lang/{IniConfigLoader().general.language}/aspects.json", "r", encdoing="utf-8") as f:
            data = json.load(f)
            for key, d in data.items():
                # Note: If you adjust the :68, also adjust it in find_aspect.py
                self.aspect_dict[key] = d["desc"][:68]
                self.aspect_num_idx[key] = d["num_idx"]

        with open(f"assets/lang/{IniConfigLoader().general.language}/uniques.json", "r", encdoing="utf-8") as f:
            data = json.load(f)
            for key, d in data.items():
                # Note: If you adjust the :45, also adjust it in find_aspect.py
                self.aspect_unique_dict[key] = d["desc"][:45]
                self.aspect_unique_num_idx[key] = d["num_idx"]

        with open(f"assets/lang/{IniConfigLoader().general.language}/affixes.json", "r", encoding="utf-8") as f:
            self.affix_dict: dict = json.load(f)

        with open(f"assets/lang/{IniConfigLoader().general.language}/sigils.json", "r", encoding="utf-8") as f:
            affix_sigil_dict_all = json.load(f)
            self.affix_sigil_dict = {
                **affix_sigil_dict_all["dungeons"],
                **affix_sigil_dict_all["minor"],
                **affix_sigil_dict_all["major"],
                **affix_sigil_dict_all["positive"],
            }

        with open(f"assets/lang/{IniConfigLoader().general.language}/item_types.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for item, value in data.items():
                if item in ItemType.__members__:
                    enum_member = ItemType[item]
                    enum_member._value_ = value
                else:
                    Logger.warning(f"{item} type not in item_type.py")

        with open(f"assets/lang/{IniConfigLoader().general.language}/tooltips.json", "r", encoding="utf-8") as f:
            self.tooltips = json.load(f)
