import ctypes
import logging
import threading
import tkinter as tk
import typing

from src.cam import Cam
from src.config.loader import IniConfigLoader
from src.config.ui import ResManager
from src.logger import Logger
from src.loot_filter import run_loot_filter
from src.loot_mover import move_items_to_inventory, move_items_to_stash
from src.scripts.vision_mode import vision_mode
from src.utils.process_handler import kill_thread
from src.utils.window import WindowSpec, move_window_to_foreground

# Usage
lock = threading.Lock()


class ListboxHandler(logging.Handler):
    def __init__(self, listbox):
        logging.Handler.__init__(self)
        self.listbox = listbox

    def emit(self, record):
        log_entry = self.format(record)
        padded_text = " " * 1 + log_entry + " " * 1
        self.listbox.insert(tk.END, padded_text)
        self.listbox.yview(tk.END)  # Auto-scroll to the end


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
        self.initial_width = int(self.screen_width * 0.068)
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

        self.toggle_button = tk.Button(self.root, text="max", bg="#222222", fg="#555555", borderwidth=0, command=self.toggle_size)
        self.canvas.create_window(int(self.initial_width * 0.19), self.initial_height // 2, window=self.toggle_button)

        self.filter_button = tk.Button(self.root, text="filter", bg="#222222", fg="#555555", borderwidth=0, command=self.filter_items)
        self.canvas.create_window(int(self.initial_width * 0.48), self.initial_height // 2, window=self.filter_button)

        self.start_scripts_button = tk.Button(self.root, text="vision", bg="#222222", fg="#555555", borderwidth=0, command=self.run_scripts)
        self.canvas.create_window(int(self.initial_width * 0.81), self.initial_height // 2, window=self.start_scripts_button)

        font_size = 8
        window_height = ResManager().pos.window_dimensions[1]
        if window_height == 1440:
            font_size = 9
        elif window_height > 1440:
            font_size = 10
        self.terminal_listbox = tk.Listbox(
            self.canvas,
            bg="black",
            fg="white",
            highlightcolor="white",
            highlightthickness=0,
            selectbackground="#222222",
            activestyle=tk.NONE,
            borderwidth=0,
            font=("Courier New", font_size),
        )
        self.terminal_listbox.place(
            relx=0, rely=0, relwidth=1, relheight=1 - (self.initial_height / self.maximized_height), y=self.initial_height
        )

        if IniConfigLoader().general.hidden_transparency == 0:
            self.root.update()
            hwnd = self.root.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)

        # Setup the listbox logger handler
        listbox_handler = ListboxHandler(self.terminal_listbox)
        listbox_handler.setLevel(Logger._logger_level)
        Logger.logger.addHandler(listbox_handler)

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

    def toggle_size(self):
        if not self.is_minimized:
            self.canvas.config(height=self.initial_height, width=self.initial_width)
            self.root.geometry(
                f"{self.initial_width}x{self.initial_height}+{self.screen_width // 2 - self.initial_width // 2 + self.screen_off_x}+{self.screen_height - self.initial_height + self.screen_off_y}"
            )
        else:
            self.canvas.config(height=self.maximized_height, width=self.maximized_width)
            self.root.geometry(
                f"{self.maximized_width}x{self.maximized_height}+{self.screen_width // 2 - self.maximized_width // 2 + self.screen_off_x}+{self.screen_height - self.maximized_height + self.screen_off_y}"
            )
        self.is_minimized = not self.is_minimized
        if self.is_minimized:
            self.hide_canvas(None)
            self.toggle_button.config(text="max")
        else:
            self.show_canvas(None)
            self.toggle_button.config(text="min")
        win_spec = WindowSpec(IniConfigLoader().advanced_options.process_name)
        move_window_to_foreground(win_spec)

    def filter_items(self, force_refresh=False):
        self._start_or_stop_loot_interaction_thread(run_loot_filter, (force_refresh,))

    def move_items_to_inventory(self):
        self._start_or_stop_loot_interaction_thread(move_items_to_inventory)

    def move_items_to_stash(self):
        self._start_or_stop_loot_interaction_thread(move_items_to_stash)

    def _start_or_stop_loot_interaction_thread(self, loot_interaction_method: typing.Callable, method_args=()):
        if lock.acquire(blocking=False):
            try:
                if self.loot_interaction_thread is not None:
                    Logger.info("Stopping filter or move process")
                    kill_thread(self.loot_interaction_thread)
                    self.loot_interaction_thread = None
                    self.filter_button.config(fg="#555555")
                else:
                    if self.is_minimized:
                        self.toggle_size()
                    self.loot_interaction_thread = threading.Thread(
                        target=self._wrapper_run_loot_interaction_method, args=(loot_interaction_method, method_args), daemon=True
                    )
                    self.loot_interaction_thread.start()
                    self.filter_button.config(fg="#006600")
            finally:
                lock.release()
        else:
            return

    def _wrapper_run_loot_interaction_method(self, loot_interaction_method: typing.Callable, method_args=()):
        try:
            # We will stop all scripts if they are currently running and restart them afterwards if needed
            did_stop_scripts = False
            if len(self.script_threads) > 0:
                Logger.info("Stopping Scripts")
                self.start_scripts_button.config(fg="#555555")
                for script_thread in self.script_threads:
                    kill_thread(script_thread)
                self.script_threads = []
                did_stop_scripts = True

            loot_interaction_method(*method_args)

            if did_stop_scripts:
                self.run_scripts()
        finally:
            if not self.is_minimized:
                self.toggle_size()
            self.loot_interaction_thread = None
            self.filter_button.config(fg="#555555")

    def run_scripts(self):
        if lock.acquire(blocking=False):
            try:
                if len(self.script_threads) > 0:
                    Logger.info("Stopping Vision Mode")
                    self.start_scripts_button.config(fg="#555555")
                    for script_thread in self.script_threads:
                        kill_thread(script_thread)
                    self.script_threads = []
                else:
                    if not IniConfigLoader().advanced_options.scripts:
                        Logger.info("No scripts configured")
                        return
                    for name in IniConfigLoader().advanced_options.scripts:
                        if name == "vision_mode":
                            vision_mode_thread = threading.Thread(target=vision_mode, daemon=True)
                            vision_mode_thread.start()
                            self.script_threads.append(vision_mode_thread)
                    self.start_scripts_button.config(fg="#006600")
            finally:
                lock.release()
        else:
            return

    def run(self):
        self.root.mainloop()
