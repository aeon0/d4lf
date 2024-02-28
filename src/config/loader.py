"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

import configparser
import os
from pathlib import Path

from config.helper import singleton
from config.models import Char, General, AdvancedOptions
from logger import Logger

CONFIG_IN_USER_DIR = ".d4lf"
PARAMS_INI = "params.ini"
USER_DIR = os.path.expanduser("~")


@singleton
class IniConfigLoader:
    def __init__(self):
        self._config_path = Path(__file__) / "../../../config"
        self._parsers = {}
        self._advanced_options = None
        self._char = None
        self._general = None
        self._loaded = False

    def _select_val(self, section: str, key: str = None):
        try:
            if section in self._parsers["custom"] and key in self._parsers["custom"][section]:
                return_value = self._parsers["custom"][section][key]
            else:
                return_value = self._parsers["params"][section][key]
            return return_value
        except KeyError:
            Logger.error(f"Key '{key}' not found in section '{section}'")
            os._exit(1)

    def _load_params(self):
        self._parsers["params"] = configparser.ConfigParser()
        self._parsers["custom"] = configparser.ConfigParser()
        self._parsers["params"].read(self._config_path / PARAMS_INI)
        if (p := (Path(USER_DIR) / CONFIG_IN_USER_DIR / PARAMS_INI)).exists():
            self._parsers["custom"].read(p)

        self._advanced_options = AdvancedOptions(
            run_scripts=self._select_val("advanced_options", "run_scripts"),
            run_filter=self._select_val("advanced_options", "run_filter"),
            exit_key=self._select_val("advanced_options", "exit_key"),
            log_lvl=self._select_val("advanced_options", "log_lvl"),
            scripts=self._select_val("advanced_options", "scripts").split(","),
            process_name=self._select_val("advanced_options", "process_name"),
        )
        self._char = Char(inventory=self._select_val("char", "inventory"))
        self._general = General(
            profiles=self._select_val("general", "profiles").split(","),
            run_vision_mode_on_startup=self._select_val("general", "run_vision_mode_on_startup"),
            check_chest_tabs=self._select_val("general", "check_chest_tabs"),
            hidden_transparency=self._select_val("general", "hidden_transparency"),
            local_prefs_path=self._select_val("general", "local_prefs_path"),
        )

    @property
    def advanced_options(self) -> AdvancedOptions:
        if not self._loaded:
            self.load()
        return self._advanced_options

    @property
    def char(self) -> Char:
        if not self._loaded:
            self.load()
        return self._char

    @property
    def general(self) -> General:
        if not self._loaded:
            self.load()
        return self._general

    def load(self):
        self._loaded = True
        self._load_params()


if __name__ == "__main__":
    a = IniConfigLoader()
    a.load()
    print(a)
