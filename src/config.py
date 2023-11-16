import configparser
import string
import threading
import numpy as np
import os
import ast
from logger import Logger
from cam import Cam
from pathlib import Path

config_lock = threading.Lock()


class Config:
    data_loaded = False
    # parse files and store their values
    configs = {}

    # config data
    general = {}
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
        self.configs["game"]["parser"].read(f"config/game_{Cam().res_key}.ini")

        user_dir = os.path.expanduser("~")
        custom_params_path = Path(f"{user_dir}/.d4lf/params.ini")
        if os.environ.get("RUN_ENV") != "test" and os.path.exists(custom_params_path):
            try:
                self.configs["custom"]["parser"].read(custom_params_path)
            except configparser.MissingSectionHeaderError:
                Logger.error("custom.ini missing section header, defaulting to params.ini")

        profiles_str = str(self._select_val("general", "profiles"))
        self.general = {
            "check_chest_tabs": int(self._select_val("general", "check_chest_tabs")),
            "run_vision_mode_on_startup": ast.literal_eval(self._select_val("general", "run_vision_mode_on_startup").title()),
            "hidden_transparency": max(0.01, float(self._select_val("general", "hidden_transparency"))),
            "local_prefs_path": self._select_val("general", "local_prefs_path"),
            "profiles": profiles_str.split(",") if profiles_str else [],
        }

        for key in self.configs["params"]["parser"]["char"]:
            self.char[key] = self._select_val("char", key)

        for key in self.configs["params"]["parser"]["advanced_options"]:
            if key == "scripts":
                as_string = str(self._select_val("advanced_options", key))
                self.advanced_options[key] = as_string.split(",") if as_string else []
            else:
                self.advanced_options[key] = self._select_val("advanced_options", key)

        for key in self.configs["game"]["parser"]["colors"]:
            self.colors[key] = np.split(np.array([int(x) for x in self._select_val("colors", key).split(",")]), 2)

        for key in self.configs["game"]["parser"]["ui_pos"]:
            self.ui_pos[key] = tuple(int(val) for val in self._select_val("ui_pos", key).split(","))

        for key in self.configs["game"]["parser"]["ui_offsets"]:
            self.ui_offsets[key] = int(self._select_val("ui_offsets", key))

        for key in self.configs["game"]["parser"]["ui_roi"]:
            self.ui_roi[key] = np.array([int(x) for x in self._select_val("ui_roi", key).split(",")])


if __name__ == "__main__":
    Cam().res_key = "1920x1080"
    config = Config()
