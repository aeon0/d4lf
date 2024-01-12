import json
import os
import threading
from logger import Logger
from config import Config

dataloader_lock = threading.Lock()


class Dataloader:
    error_map = dict()
    affix_dict = dict()
    affix_sigil_dict = dict()
    aspect_dict = dict()
    aspect_snoids = dict()
    aspect_unique_dict = dict()
    aspect_unique_snoids = dict()

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
        if "language" not in Config().general:
            Logger.error("Could not load assets. Config not initalized!")
            os._exit(-1)

        with open(f"assets/lang/{Config().general['language']}/affixes.json", "r", encoding="utf-8") as f:
            self.affix_dict: dict = json.load(f)

        with open(f"assets/lang/{Config().general['language']}/sigils.json", "r", encoding="utf-8") as f:
            affix_sigil_dict_all = json.load(f)
            self.affix_sigil_dict = {
                **affix_sigil_dict_all["dungeons"],
                **affix_sigil_dict_all["minor"],
                **affix_sigil_dict_all["major"],
                **affix_sigil_dict_all["positive"],
            }

        with open(f"assets/lang/{Config().general['language']}/corrections.json", "r", encoding="utf-8") as f:
            self.error_map: dict = json.load(f)

        with open(f"assets/lang/{Config().general['language']}/aspects.json", "r") as f:
            data = json.load(f)
            for key, d in data.items():
                self.aspect_dict[key] = d["desc"]
                self.aspect_snoids[key] = d["snoId"]

        with open(f"assets/lang/{Config().general['language']}/uniques.json", "r") as f:
            data = json.load(f)
            for key, d in data.items():
                self.aspect_unique_dict[key] = d["desc"]
                self.aspect_unique_snoids[key] = d["snoId"]

        with open(f"assets/lang/{Config().general['language']}/affixes.json", "r", encoding="utf-8") as f:
            self.affix_dict: dict = json.load(f)

        with open(f"assets/lang/{Config().general['language']}/sigils.json", "r", encoding="utf-8") as f:
            affix_sigil_dict_all = json.load(f)
            self.affix_sigil_dict = {
                **affix_sigil_dict_all["dungeons"],
                **affix_sigil_dict_all["minor"],
                **affix_sigil_dict_all["major"],
                **affix_sigil_dict_all["positive"],
            }
