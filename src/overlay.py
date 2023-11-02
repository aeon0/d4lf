import tkinter as tk
import threading
from utils.window import move_window_to_foreground
from loot_filter import run_loot_filter
from version import __version__
from utils.process_handler import kill_thread
from logger import Logger
import logging
from scripts.rogue_tb import run_rogue_tb
from config import Config


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
        self.root.attributes("-alpha", 0.89)
        self.root.overrideredirect(True)
        # self.root.wm_attributes("-transparentcolor", "white")
        self.root.wm_attributes("-topmost", True)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.initial_height = int(self.root.winfo_screenheight() * 0.03)
        self.initial_width = int(self.screen_width * 0.072)
        self.maximized_height = int(self.initial_height * 3.85)
        self.maximized_width = int(self.initial_width * 6)

        self.canvas = tk.Canvas(self.root, bg="black", height=self.initial_height, width=self.initial_width, highlightthickness=0)
        self.root.geometry(
            f"{self.initial_width}x{self.initial_height}+{self.screen_width//2 - self.initial_width//2}+{self.screen_height - self.initial_height}"
        )
        self.canvas.pack()

        self.toggle_button = tk.Button(
            self.root,
            text="toggle",
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
        self.canvas.create_window(int(self.initial_width * 0.5), self.initial_height // 2, window=self.filter_button)

        self.start_scripts_button = tk.Button(
            self.root,
            text="scripts",
            bg="#222222",
            fg="#555555",
            borderwidth=0,
            command=self.run_scripts,
        )
        self.canvas.create_window(int(self.initial_width * 0.8), self.initial_height // 2, window=self.start_scripts_button)

        self.terminal_listbox = tk.Listbox(
            self.canvas,
            bg="black",
            fg="white",
            highlightcolor="white",
            highlightthickness=0,
            selectbackground="#222222",
            activestyle=tk.NONE,
            borderwidth=0,
            font=("Courier New", 9),
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

    def toggle_size(self):
        if not self.is_minimized:
            self.canvas.config(height=self.initial_height, width=self.initial_width)
            self.root.geometry(
                f"{self.initial_width}x{self.initial_height}+{self.screen_width//2 - self.initial_width//2}+{self.screen_height - self.initial_height}"
            )
        else:
            self.canvas.config(height=self.maximized_height, width=self.maximized_width)
            self.root.geometry(
                f"{self.maximized_width}x{self.maximized_height}+{self.screen_width//2 - self.maximized_width//2}+{self.screen_height - self.maximized_height}"
            )
        self.is_minimized = not self.is_minimized
        move_window_to_foreground()

    def filter_items(self):
        if self.loot_filter_thread is not None:
            Logger.info("Stoping Filter process")
            kill_thread(self.loot_filter_thread)
            self.loot_filter_thread = None
            return
        if self.is_minimized:
            self.toggle_size()
        self.loot_filter_thread = threading.Thread(target=self._wrapper_run_loot_filter, daemon=True)
        self.loot_filter_thread.start()

    def _wrapper_run_loot_filter(self):
        try:
            run_loot_filter()
        finally:
            self.loot_filter_thread = None

    def run_scripts(self):
        if len(self.script_threads) > 0:
            Logger.info("Stoping Scripts")
            for script_thread in self.script_threads:
                kill_thread(script_thread)
            self.script_threads = []
            return
        if self.is_minimized:
            self.toggle_size()
        if len(Config().general["run_scripts"]) == 0:
            Logger.info("No scripts configured")
            return
        for name in Config().general["run_scripts"]:
            if name == "rogue_tb":
                rogue_tb_thread = threading.Thread(target=run_rogue_tb, daemon=True)
                rogue_tb_thread.start()
                self.script_threads.append(rogue_tb_thread)

    def run(self):
        self.root.mainloop()
