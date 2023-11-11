import tkinter as tk
import threading
from utils.window import move_window_to_foreground
from loot_filter import run_loot_filter
from version import __version__
from utils.process_handler import kill_thread
from logger import Logger
import logging
from scripts.rogue_tb import run_rogue_tb
from vision_mode import vision_mode
from config import Config
from cam import Cam


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
        self.loot_filter_thread = None
        self.script_threads = []
        self.is_minimized = True
        self.root = tk.Tk()
        self.root.title("LootFilter Overlay")
        self.root.attributes("-alpha", 0.94)
        self.hide_id = self.root.after(8000, lambda: self.root.attributes("-alpha", Config().general["hidden_transparency"]))
        self.root.overrideredirect(True)
        # self.root.wm_attributes("-transparentcolor", "white")
        self.root.wm_attributes("-topmost", True)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.initial_height = int(self.root.winfo_screenheight() * 0.03)
        self.initial_width = int(self.screen_width * 0.07)
        self.maximized_height = int(self.initial_height * 3.4)
        self.maximized_width = int(self.initial_width * 5)

        self.screen_off_x = Cam().window_roi["left"]
        self.screen_off_y = Cam().window_roi["top"]
        self.canvas = tk.Canvas(self.root, bg="black", height=self.initial_height, width=self.initial_width, highlightthickness=0)
        self.root.geometry(
            f"{self.initial_width}x{self.initial_height}+{self.screen_width//2 - self.initial_width//2 + self.screen_off_x}+{self.screen_height - self.initial_height + self.screen_off_y}"
        )
        self.canvas.pack()
        self.root.bind("<Enter>", self.show_canvas)
        self.root.bind("<Leave>", self.hide_canvas)

        self.toggle_button = tk.Button(
            self.root,
            text="max",
            bg="#222222",
            fg="#555555",
            borderwidth=0,
            command=self.toggle_size,
        )
        self.canvas.create_window(int(self.initial_width * 0.19), self.initial_height // 2, window=self.toggle_button)

        self.filter_button = tk.Button(
            self.root,
            text="filter",
            bg="#222222",
            fg="#555555",
            borderwidth=0,
            command=self.filter_items,
        )
        self.canvas.create_window(int(self.initial_width * 0.45), self.initial_height // 2, window=self.filter_button)
        if Config().general["vision_mode"]:
            self.filter_items()

        self.start_scripts_button = tk.Button(
            self.root,
            text="scripts",
            bg="#222222",
            fg="#555555",
            borderwidth=0,
            command=self.run_scripts,
        )
        self.canvas.create_window(int(self.initial_width * 0.75), self.initial_height // 2, window=self.start_scripts_button)

        font_size = 8
        window_height = Config().ui_pos["window_dimensions"][1]
        if window_height == 1440:
            font_size = 9
        elif window_height == 2160:
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
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1 - (self.initial_height / self.maximized_height),
            y=self.initial_height,
        )

        # Setup the listbox logger handler
        listbox_handler = ListboxHandler(self.terminal_listbox)
        listbox_handler.setLevel(Logger._logger_level)
        Logger.logger.addHandler(listbox_handler)

    def show_canvas(self, event):
        # Cancel the pending hide if it exists
        if self.hide_id:
            self.root.after_cancel(self.hide_id)
            self.hide_id = None
        # Make the window visible
        self.root.attributes("-alpha", 0.94)

    def hide_canvas(self, event):
        # Reset the hide timer
        if self.is_minimized:
            if self.hide_id is not None:
                self.root.after_cancel(self.hide_id)
            self.hide_id = self.root.after(3000, lambda: self.root.attributes("-alpha", Config().general["hidden_transparency"]))

    def toggle_size(self):
        if lock.acquire(blocking=False):
            try:
                if not self.is_minimized:
                    self.canvas.config(height=self.initial_height, width=self.initial_width)
                    self.root.geometry(
                        f"{self.initial_width}x{self.initial_height}+{self.screen_width//2 - self.initial_width//2 + self.screen_off_x}+{self.screen_height - self.initial_height + self.screen_off_y}"
                    )
                else:
                    self.canvas.config(height=self.maximized_height, width=self.maximized_width)
                    self.root.geometry(
                        f"{self.maximized_width}x{self.maximized_height}+{self.screen_width//2 - self.maximized_width//2 + self.screen_off_x}+{self.screen_height - self.maximized_height + self.screen_off_y}"
                    )
                self.is_minimized = not self.is_minimized
                if self.is_minimized:
                    self.hide_canvas(None)
                    self.toggle_button.config(text="max")
                else:
                    self.show_canvas(None)
                    self.toggle_button.config(text="min")
                move_window_to_foreground()
            finally:
                lock.release()
        else:
            return

    def filter_items(self):
        if lock.acquire(blocking=False):
            try:
                if self.loot_filter_thread is not None:
                    Logger.info("Stoping Filter process")
                    kill_thread(self.loot_filter_thread)
                    self.loot_filter_thread = None
                    self.filter_button.config(text="filter")
                else:
                    if self.is_minimized and not Config().general["vision_mode"]:
                        self.toggle_size()
                    self.loot_filter_thread = threading.Thread(target=self._wrapper_run_loot_filter, daemon=True)
                    self.loot_filter_thread.start()
                    self.filter_button.config(text="stop")
            finally:
                lock.release()
        else:
            return

    def _wrapper_run_loot_filter(self):
        try:
            if Config().general["vision_mode"]:
                vision_mode()
            else:
                run_loot_filter()
        finally:
            if not self.is_minimized and not Config().general["vision_mode"]:
                self.toggle_size()
            self.loot_filter_thread = None

    def run_scripts(self):
        if lock.acquire(blocking=False):
            try:
                if len(self.script_threads) > 0:
                    Logger.info("Stoping Scripts")
                    self.start_scripts_button.config(text="scripts")
                    for script_thread in self.script_threads:
                        kill_thread(script_thread)
                    self.script_threads = []
                else:
                    if len(Config().general["run_scripts"]) == 0:
                        Logger.info("No scripts configured")
                        return
                    for name in Config().general["run_scripts"]:
                        if name == "rogue_tb":
                            rogue_tb_thread = threading.Thread(target=run_rogue_tb, daemon=True)
                            rogue_tb_thread.start()
                            self.script_threads.append(rogue_tb_thread)
                        self.start_scripts_button.config(text="stop")
            finally:
                lock.release()
        else:
            return

    def run(self):
        self.root.mainloop()
