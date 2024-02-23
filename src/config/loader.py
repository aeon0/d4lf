"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

import configparser
import os
from pathlib import Path

from config.helper import singleton
from config.models import Char, General, AdvancedOptions

CONFIG_IN_USER_DIR = ".d4lf"
PARAMS_INI = "params.ini"
USER_DIR = os.path.expanduser("~")


@singleton
class IniConfigLoader:

    def __init__(self):
        self._config_path = Path(__file__) / "../../../config"
        self._advanced_options = None
        self._char = None
        self._general = None
        self.__loaded = False

    def __load_params(self):
        parser = configparser.ConfigParser()
        if (p := (Path(USER_DIR) / CONFIG_IN_USER_DIR / PARAMS_INI)).exists():
            parser.read(p)
        else:
            parser.read(self._config_path / PARAMS_INI)
        self._advanced_options = AdvancedOptions(
            run_scripts=parser["advanced_options"]["run_scripts"],
            run_filter=parser["advanced_options"]["run_filter"],
            exit_key=parser["advanced_options"]["exit_key"],
            log_lvl=parser["advanced_options"]["log_lvl"],
            scripts=parser["advanced_options"]["scripts"].split(","),
            process_name=parser["advanced_options"]["process_name"],
        )
        self._char = Char(inventory=parser["char"]["inventory"])
        self._general = General(
            profiles=parser["general"]["profiles"].split(","),
            run_vision_mode_on_startup=parser["general"]["run_vision_mode_on_startup"],
            check_chest_tabs=parser["general"]["check_chest_tabs"],
            hidden_transparency=parser["general"]["hidden_transparency"],
            local_prefs_path=parser["general"]["local_prefs_path"],
        )

    @property
    def advanced_options(self) -> AdvancedOptions:
        if not self.__loaded:
            self.load()
        return self._advanced_options

    @property
    def char(self) -> Char:
        if not self.__loaded:
            self.load()
        return self._char

    @property
    def general(self) -> General:
        if not self.__loaded:
            self.load()
        return self._general

    def load(self):
        self.__load_params()
        self.__loaded = True


if __name__ == "__main__":
    a = IniConfigLoader()
    a.load()
    print(a)
