import ctypes
import logging
import threading
import time
import tkinter as tk
import typing

import src.item.descr.read_descr_tts
import src.logger
import src.scripts.loot_filter
import src.scripts.loot_filter_tts
import src.scripts.vision_mode
import src.scripts.vision_mode_tts
import src.tts
from src.cam import Cam
from src.config.loader import IniConfigLoader
from src.config.models import ItemRefreshType, UseTTSType
from src.loot_mover import move_items_to_inventory, move_items_to_stash
from src.ui.char_inventory import CharInventory
from src.ui.chest import Chest
from src.utils.custom_mouse import mouse
from src.utils.process_handler import kill_thread
from src.utils.window import screenshot

LOGGER = logging.getLogger(__name__)

LOCK = threading.Lock()


class Overlay:
    def __init__(self):
        self.loot_interaction_thread = None
        self.script_threads = []
        self.is_minimized = True
        self.root = tk.Tk()
        self.root.title("LootFilter Overlay")
        self.root.attributes("-alpha", 0.94)
        self.hide_id = self.root.after(8000, lambda: self.root.attributes("-alpha", IniConfigLoader().general.hidden_transparency))
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        self.screen_width = Cam().window_roi["width"]
        self.screen_height = Cam().window_roi["height"]
        self.initial_height = int(Cam().window_roi["height"] * 0.03)
        self.initial_width = int(self.screen_width * 0.047)
        self.maximized_height = int(self.initial_height * 3.4)
        self.maximized_width = int(self.initial_width * 5)

        self.screen_off_x = Cam().window_roi["left"]
        self.screen_off_y = Cam().window_roi["top"]
        self.canvas = tk.Canvas(self.root, bg="black", height=self.initial_height, width=self.initial_width, highlightthickness=0)
        self.root.geometry(
            f"{self.initial_width}x{self.initial_height}+{self.screen_width // 2 - self.initial_width // 2 + self.screen_off_x}+{self.screen_height - self.initial_height + self.screen_off_y}"
        )
        self.canvas.pack()
        self.root.bind("<Enter>", self.show_canvas)
        self.root.bind("<Leave>", self.hide_canvas)

        self.start_scripts_button = tk.Button(self.root, text="vision", bg="#222222", fg="#555555", borderwidth=0, command=self.run_scripts)

        if not IniConfigLoader().advanced_options.vision_mode_only:
            self.filter_button = tk.Button(self.root, text="filter", bg="#222222", fg="#555555", borderwidth=0, command=self.filter_items)
            self.canvas.create_window(int(self.initial_width * 0.24), self.initial_height // 2, window=self.filter_button)

        self.start_scripts_button = tk.Button(self.root, text="vision", bg="#222222", fg="#555555", borderwidth=0, command=self.run_scripts)
        self.canvas.create_window(int(self.initial_width * 0.73), self.initial_height // 2, window=self.start_scripts_button)

        if IniConfigLoader().general.hidden_transparency == 0:
            self.root.update()
            hwnd = self.root.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)

        if IniConfigLoader().general.run_vision_mode_on_startup:
            self.run_scripts()

    def show_canvas(self, _):
        # Cancel the pending hide if it exists
        if self.hide_id:
            self.root.after_cancel(self.hide_id)
            self.hide_id = None
        # Make the window visible
        self.root.attributes("-alpha", 0.94)

    def hide_canvas(self, _):
        # Reset the hide timer
        if self.is_minimized:
            if self.hide_id is not None:
                self.root.after_cancel(self.hide_id)
            self.hide_id = self.root.after(3000, lambda: self.root.attributes("-alpha", IniConfigLoader().general.hidden_transparency))

    def filter_items(self, force_refresh=ItemRefreshType.no_refresh):
        if IniConfigLoader().general.use_tts in [UseTTSType.full, UseTTSType.mixed]:
            self._start_or_stop_loot_interaction_thread(run_loot_filter, (force_refresh, True))
        else:
            self._start_or_stop_loot_interaction_thread(run_loot_filter, (force_refresh, False))

    def move_items_to_inventory(self):
        self._start_or_stop_loot_interaction_thread(move_items_to_inventory)

    def move_items_to_stash(self):
        self._start_or_stop_loot_interaction_thread(move_items_to_stash)

    def _start_or_stop_loot_interaction_thread(self, loot_interaction_method: typing.Callable, method_args=()):
        if LOCK.acquire(blocking=False):
            try:
                if self.loot_interaction_thread is not None:
                    LOGGER.info("Stopping filter or move process")
                    kill_thread(self.loot_interaction_thread)
                    self.loot_interaction_thread = None
                    self.filter_button.config(fg="#555555")
                else:
                    self.loot_interaction_thread = threading.Thread(
                        target=self._wrapper_run_loot_interaction_method, args=(loot_interaction_method, method_args), daemon=True
                    )
                    self.loot_interaction_thread.start()
                    self.filter_button.config(fg="#006600")
            finally:
                LOCK.release()
        else:
            return

    def _wrapper_run_loot_interaction_method(self, loot_interaction_method: typing.Callable, method_args=()):
        try:
            # We will stop all scripts if they are currently running and restart them afterwards if needed
            did_stop_scripts = False
            if len(self.script_threads) > 0:
                LOGGER.info("Stopping Scripts")
                self.start_scripts_button.config(fg="#555555")
                for script_thread in self.script_threads:
                    kill_thread(script_thread)
                self.script_threads = []
                did_stop_scripts = True

            loot_interaction_method(*method_args)

            if did_stop_scripts:
                self.run_scripts()
        finally:
            self.loot_interaction_thread = None
            self.filter_button.config(fg="#555555")

    def run_scripts(self):
        if LOCK.acquire(blocking=False):
            try:
                if len(self.script_threads) > 0:
                    LOGGER.info("Stopping Vision Mode")
                    self.start_scripts_button.config(fg="#555555")
                    for script_thread in self.script_threads:
                        kill_thread(script_thread)
                    self.script_threads = []
                else:
                    if not IniConfigLoader().advanced_options.scripts:
                        LOGGER.info("No scripts configured")
                        return
                    for name in IniConfigLoader().advanced_options.scripts:
                        if name == "vision_mode":
                            if IniConfigLoader().general.use_tts == UseTTSType.full:
                                vision_mode_thread = threading.Thread(target=src.scripts.vision_mode_tts.VisionMode().start, daemon=True)
                            else:
                                vision_mode_thread = threading.Thread(target=src.scripts.vision_mode.vision_mode, daemon=True)
                            vision_mode_thread.start()
                            self.script_threads.append(vision_mode_thread)
                    self.start_scripts_button.config(fg="#006600")
            finally:
                LOCK.release()
        else:
            return

    def run(self):
        self.root.mainloop()


def run_loot_filter(force_refresh: ItemRefreshType = ItemRefreshType.no_refresh, tts: bool = False):
    LOGGER.info("Run Loot filter")
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    check_items = src.scripts.loot_filter_tts.check_items if tts else src.scripts.loot_filter.check_items

    inv = CharInventory()
    chest = Chest()

    if chest.is_open():
        for i in IniConfigLoader().general.check_chest_tabs:
            chest.switch_to_tab(i)
            time.sleep(0.3)
            check_items(chest, force_refresh)
        mouse.move(*Cam().abs_window_to_monitor((0, 0)))
        time.sleep(0.3)
        check_items(inv, force_refresh)
    else:
        if not inv.open():
            screenshot("inventory_not_open", img=Cam().grab())
            LOGGER.error("Inventory did not open up")
            return
        check_items(inv, force_refresh)
    mouse.move(*Cam().abs_window_to_monitor((0, 0)))
    LOGGER.info("Loot Filter done")
