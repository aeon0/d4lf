import configparser
import string
import threading
import numpy as np
import os
from logger import Logger

config_lock = threading.Lock()


def _default_iff(value, iff, default=None):
    return default if value == iff else value


class Config:
    data_loaded = False
    # parse files and store their values
    configs = {}

    # config data
    char = {}
    advanced_options = {}
    ui_pos = {}
    ui_offsets = {}
    ui_roi = {}
    colors = {}

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            with config_lock:
                if not cls._instance.data_loaded:
                    cls._instance.data_loaded = True
                    cls._instance.load_data()
        return cls._instance

    def _select_optional(self, section: string, key: string, default=None, condition=None):
        try:
            return self._select_val(section=section, key=key)
        except:
            return default

    def _select_val(self, section: str, key: str = None):
        try:
            if section in self.configs["custom"]["parser"] and key in self.configs["custom"]["parser"][section]:
                return_value = self.configs["custom"]["parser"][section][key]
            elif section in self.configs["params"]["parser"]:
                return_value = self.configs["params"]["parser"][section][key]
            else:
                return_value = self.configs["game"]["parser"][section][key]
            return return_value
        except KeyError:
            Logger.error(f"Key '{key}' not found in section '{section}'")
            os._exit(1)

    def load_data(self):
        Logger.debug("Loading config")
        self.configs = {
            "params": {"parser": configparser.ConfigParser(), "vars": {}},
            "game": {"parser": configparser.ConfigParser(), "vars": {}},
            "custom": {"parser": configparser.ConfigParser(), "vars": {}},
        }
        self.configs["params"]["parser"].read("config/params.ini")
        self.configs["game"]["parser"].read("config/game.ini")

        if os.environ.get("RUN_ENV") != "test" and os.path.exists("config/custom.ini"):
            try:
                self.configs["custom"]["parser"].read("config/custom.ini")
            except configparser.MissingSectionHeaderError:
                Logger.error("custom.ini missing section header, defaulting to params.ini")

        for key in self.configs["params"]["parser"]["char"]:
            self.char[key] = self._select_val("char", key)

        for key in self.configs["params"]["parser"]["advanced_options"]:
            self.advanced_options[key] = self._select_val("advanced_options", key)

        for key in self.configs["game"]["parser"]["colors"]:
            self.colors[key] = np.split(np.array([int(x) for x in self._select_val("colors", key).split(",")]), 2)

        for key in self.configs["game"]["parser"]["ui_pos"]:
            self.ui_pos[key] = tuple(int(val) for val in self._select_val("ui_pos", key).split(","))

        for key in self.configs["game"]["parser"]["ui_offsets"]:
            self.ui_offsets[key] = np.array([int(x) for x in self._select_val("ui_offsets", key).split(",")])

        for key in self.configs["game"]["parser"]["ui_roi"]:
            self.ui_roi[key] = np.array([int(x) for x in self._select_val("ui_roi", key).split(",")])

        for key in self.configs["game"]["parser"]["colors"]:
            self.colors[key] = np.split(np.array([int(x) for x in self._select_val("colors", key).split(",")]), 2)


if __name__ == "__main__":
    config = Config()
