from enum import Enum

import keyboard
import numpy as np
from logger import Logger
from template_finder import SearchArgs, SearchResult, TemplateMatch
from utils.misc import run_until_condition, wait
from utils.mouse_selector import select_search_result


class ToggleMethod(Enum):
    BUTTON = 1
    HOTKEY = 2


class Menu:
    def __init__(self):
        self.menu_name: str = ""
        self.parent_menu: Menu | None = None
        self.is_open_search_args: SearchArgs | None = None
        self.open_button_search_args: SearchArgs | None = None
        self.close_button_search_args = self.open_button_search_args
        self.open_hotkey: str = ""
        self.close_hotkey: str = "esc"
        self.open_method: ToggleMethod = ToggleMethod.BUTTON
        self.close_method: ToggleMethod = ToggleMethod.HOTKEY
        self.delay = 0

    @staticmethod
    def select_button(search: SearchArgs | TemplateMatch) -> bool:
        """
        Selects a button based on a given search object.
        :param search: A SearchArgs or TemplateMatch object to identify the button
        :return: True if the button is successfully selected, False otherwise.
        """
        if isinstance(search, SearchArgs):
            result = search.detect()
            if not result.success:
                Logger.error(f"Could not find {search.ref} button")
                return False
            match = result.matches[0]
        elif isinstance(search, TemplateMatch):
            match = search
        else:
            Logger.error(f"Invalid type {type(search)} for search")
            return False
        select_search_result(match)
        return True

    def open(self) -> bool:
        """
        Opens the menu by clicking the open button.
        :return: True if the menu is successfully opened, False otherwise.
        """
        # Open parent menu if there is one to be opened
        if self.parent_menu and not self.is_open() and not self.parent_menu.open():
            Logger.error(f"Could not open parent menu {self.parent_menu.menu_name}")
            return False
        if not (is_open := self.is_open()):
            debug_string = f"Opening {self.menu_name} with"
            if self.open_method == ToggleMethod.BUTTON:
                debug_string += f" button {self.open_button_search_args.ref}"
                self.select_button(self.open_button_search_args)
            elif self.open_method == ToggleMethod.HOTKEY:
                debug_string += f" hotkey {self.open_hotkey}"
                keyboard.send(self.open_hotkey)
            Logger.debug(debug_string)
        else:
            Logger.debug(f"{self.menu_name} already open")
        return is_open or self.wait_until_open()

    def close(self) -> bool:
        """
        Closes the menu by pressing the escape key.
        :return: True if the menu is successfully closed, False otherwise.
        """
        if self.is_open():
            debug_string = f"Closing {self.menu_name} with"
            if self.close_method == ToggleMethod.BUTTON:
                debug_string += f" button {self.close_button_search_args.ref}"
                self.select_button(self.close_button_search_args)
            elif self.close_method == ToggleMethod.HOTKEY:
                debug_string += f" hotkey {self.close_hotkey}"
                keyboard.send(self.close_hotkey)
            Logger.debug(debug_string)
            return self.wait_until_closed(timeout=3)
        return True

    def _check_match(self, res: SearchResult) -> bool:
        """
        Checks if the given TemplateMatch is a match for the menu.
        :param res: The TemplateMatch to check.
        """
        if self.is_open_search_args.mode == "best":
            return res.matches[0].name.lower() == self.is_open_search_args.ref[0].lower()
        return True

    def is_open(self, img: np.ndarray = None) -> bool:
        """
        Checks if the menu is open.
        :return: True if the menu is open, False otherwise.
        """
        res = self.is_open_search_args.detect(img)
        if res.success:
            return self._check_match(res)
        return False

    def wait_until_open(self, timeout: float = 10) -> bool:
        """
        Waits until the menu is open.
        :param timeout: The number of seconds to wait before timing out.
        :return: True if the menu is open, False otherwise.
        """
        _, success = run_until_condition(self.is_open, lambda res: res, timeout)
        if not success:
            Logger.warning(f"Could not find {self.menu_name} after {timeout} seconds")
        wait(self.delay)
        return success

    def wait_until_closed(self, timeout: float = 10, mode: str = "all") -> bool:
        """
        Waits until the menu is closed.
        :param timeout: The number of seconds to wait before timing out.
        :param mode: The mode to use when searching for the menu. See template_finder.py for more info.
        :return: True if the menu is closed, False otherwise.
        """
        args: SearchArgs = self.is_open_search_args
        args.mode = mode
        _, success = run_until_condition(lambda: args.is_visible(), lambda res: not res, timeout)
        if not success:
            Logger.warning(f"{self.menu_name} still visible after {timeout} seconds")
        return success
