"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

import configparser
import os
import pathlib
from pathlib import Path

from logger import Logger

from config.helper import singleton
from config.models import AdvancedOptionsModel, CharModel, GeneralModel

PARAMS_INI = "params.ini"


@singleton
class IniConfigLoader:
    def __init__(self):
        self._advanced_options = None
        self._char = None
        self._config_path = Path("./config")
        self._general = None
        self._loaded = False
        self._parsers = {}
        self._user_dir = pathlib.Path.home() / ".d4lf"

    def _select_val(self, section: str, key: str | None = None):
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
        self._parsers["params"].read(self._config_path / PARAMS_INI, encoding="utf-8")
        if (p := (self.user_dir / PARAMS_INI)).exists() and p.stat().st_size:
            self._parsers["custom"].read(p, encoding="utf-8")

        self._advanced_options = AdvancedOptionsModel(
            exit_key=self._select_val("advanced_options", "exit_key"),
            log_lvl=self._select_val("advanced_options", "log_lvl"),
            open_gui=self._select_val("advanced_options", "open_gui"),
            process_name=self._select_val("advanced_options", "process_name"),
            run_filter=self._select_val("advanced_options", "run_filter"),
            run_scripts=self._select_val("advanced_options", "run_scripts"),
            scripts=self._select_val("advanced_options", "scripts").split(","),
        )
        self._char = CharModel(inventory=self._select_val("char", "inventory"))
        self._general = GeneralModel(
            browser=self._select_val("general", "browser"),
            check_chest_tabs=self._select_val("general", "check_chest_tabs").split(","),
            full_dump=self._select_val("general", "full_dump"),
            handle_rares=self._select_val("general", "handle_rares"),
            hidden_transparency=self._select_val("general", "hidden_transparency"),
            keep_aspects=self._select_val("general", "keep_aspects"),
            profiles=self._select_val("general", "profiles").split(","),
            run_vision_mode_on_startup=self._select_val("general", "run_vision_mode_on_startup"),
        )

    @property
    def advanced_options(self) -> AdvancedOptionsModel:
        if not self._loaded:
            self.load()
        return self._advanced_options

    @property
    def char(self) -> CharModel:
        if not self._loaded:
            self.load()
        return self._char

    @property
    def general(self) -> GeneralModel:
        if not self._loaded:
            self.load()
        return self._general

    @property
    def user_dir(self) -> Path:
        return self._user_dir

    def load(self):
        self._loaded = True
        self._load_params()


if __name__ == "__main__":
    a = IniConfigLoader()
    a.load()
    print(a)
