import ctypes
import logging
import threading
import tkinter as tk
import typing

from src.cam import Cam
from src.config.loader import IniConfigLoader
from src.config.ui import ResManager
from src.loot_filter import run_loot_filter
from src.loot_mover import move_items_to_inventory, move_items_to_stash
from src.scripts.vision_mode import vision_mode
from src.utils.process_handler import kill_thread
from src.utils.window import WindowSpec, move_window_to_foreground

LOGGER = logging.getLogger(__name__)

LOCK = threading.Lock()


class TextLogHandler(logging.Handler):
    def __init__(self, text):
        logging.Handler.__init__(self)
        self.text = text
        self.text.tag_configure("wrapindent", lmargin2=60)

    def emit(self, record):
        log_entry = self.format(record)
        padded_text = " " * 1 + log_entry + " \n" * 1
        self.text.insert(tk.END, padded_text, "wrapindent")
        self.text.yview(tk.END)  # Auto-scroll to the end


class CustomButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        font_size = Overlay.get_scaled_font_size(self)
        super().__init__(master, **kwargs)
        self.config(
            background="#1a1a1a",  # Dark background
            foreground="#ffffff",  # White text
            activebackground="#333333",  # Slightly lighter background on press
            activeforeground="#ffffff",  # White text on press
            borderwidth=3,
            relief="flat",
            overrelief="sunken",
            font=("Courier New", font_size),  # Default font
            padx=5,
            pady=0,
        )


class Overlay:
    def __init__(self, master=None):
        self.root = tk.Tk(master)
        self.root.configure(background="#000000", borderwidth="0")
        self.root.title("LootFilter Overlay")
        self.root.attributes("-alpha", 0.94)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        font_size = self.get_scaled_font_size()
        self.mainframe = tk.Frame(self.root, name="mainframe", background="#000000")
        self.mainframe.pack(
            anchor="center",
            expand=True,
            fill="both",
            side="bottom",
            padx=0,
            pady=0,
        )
        self.mainframe.configure(borderwidth=0)

        # Listbox for logging
        self.terminal_text = tk.Text(
            self.mainframe,
            # activestyle="none",
            background="#050505",
            font=("Courier New", font_size),
            foreground="#ffffff",
            highlightcolor="white",
            highlightthickness=0,
            selectbackground="#222222",
        )
        self.terminal_text.grid(column=0, columnspan=3, row=0, sticky="nsew")
        self.terminal_text.grid_remove()

        # Separate frames for each button group
        self.button_frames = []
        for _ in range(4):
            frame = tk.Frame(self.mainframe, background="#000000", borderwidth=0)
            frame.grid(row=1, column=_, sticky="ew")
            self.button_frames.append(frame)

        # MinMax button
        self.toggle_button = CustomButton(
            self.button_frames[0],
            name="toggle_button",
            text="Console",
            command=self.toggle_size,
        )
        self.toggle_button.pack(side="bottom", fill="x", expand=True)

        # Vision Button
        self.start_scripts_button = CustomButton(
            self.button_frames[1],
            name="start_scripts_button",
            text=f"Vision [{IniConfigLoader().advanced_options.run_scripts.upper()}]",
            command=self.run_scripts,
        )
        self.start_scripts_button.pack(side="bottom", fill="x", expand=True)

        # Filter buttons
        self.filter_frame = tk.Frame(self.button_frames[2], background="#000000", borderwidth=0)
        self.filter_frame.pack(anchor="center", expand=True, fill="both")
        self.filter_button = CustomButton(
            self.filter_frame,
            name="filter_button",
            text=f"Filter [{IniConfigLoader().advanced_options.run_filter.upper()}]",
            command=self.handle_filter,
        )
        self.filter_button.pack(side="top", fill="x", expand=True)

        self.auto_filter_button = CustomButton(
            self.filter_frame,
            name="auto_filter_button",
            text="Auto Filter",  # [{IniConfigLoader().advanced_options.run_filter.upper()}]",
            command=self.filter_items,
        )
        self.auto_filter_button.config(background="#303030")
        self.auto_filter_button.pack(side="right", fill="x", expand=True)
        self.auto_filter_button.pack_forget()  # Hide initially
        self.auto_filter_button.bind("<Leave>", self.hide_filter_buttons)

        self.reset_status_button = CustomButton(
            self.filter_frame,
            name="reset_status_button",
            text="Reset Status",  # [{IniConfigLoader().advanced_options.run_filter_force_refresh.upper()}]",
            command=lambda: self.filter_items(True),
        )
        self.reset_status_button.config(background="#303030")
        self.reset_status_button.pack(side="left", fill="x", expand=True)
        self.reset_status_button.pack_forget()  # Hide initially
        self.reset_status_button.bind("<Leave>", self.hide_filter_buttons)

        # Stock buttons
        self.stock_frame = tk.Frame(self.button_frames[3], background="#000000", borderwidth=0)
        self.stock_frame.pack(expand=True, fill="both")

        self.stock_move_button = CustomButton(
            self.stock_frame,
            name="stock_move_button",
            text="Move items",
            command=self.handle_stock_move,
        )
        self.stock_move_button.pack(side="bottom", fill="x", expand=True)

        self.stock_to_stash_button = CustomButton(
            self.stock_frame,
            name="stock_to_stash_button",
            text="to stash",
            command=self.move_items_to_stash,
        )
        self.stock_to_stash_button.config(background="#303030")
        self.stock_to_stash_button.pack(side="bottom", fill="x", expand=True)
        self.stock_to_stash_button.pack_forget()  # Hide initially
        self.stock_to_stash_button.bind("<Leave>", self.hide_stock_buttons)

        self.stock_to_inv_button = CustomButton(
            self.stock_frame,
            name="stock_to_inv_button",
            text="to Inventory",
            command=self.move_items_to_inventory,
        )
        self.stock_to_inv_button.config(background="#303030")
        self.stock_to_inv_button.pack(side="bottom", fill="x", expand=True)
        self.stock_to_inv_button.pack_forget()  # Hide initially
        self.stock_to_inv_button.bind("<Leave>", self.hide_stock_buttons)

        # Configure grid weights for resizing
        self.mainframe.grid_rowconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(1, weight=1)
        self.mainframe.grid_columnconfigure(2, weight=1)
        self.mainframe.grid_columnconfigure(3, weight=1)

        # Initialize variables
        self.loot_interaction_thread = None
        self.script_threads = []
        self.is_minimized = True

       # Setup the listbox logger handler
        textlog_handler = TextLogHandler(self.terminal_text)
        textlog_handler.setLevel(LOGGER.level)
        LOGGER.root.addHandler(textlog_handler)

        # Additional setup for transparency and positioning
        self.screen_width = Cam().window_roi["width"]
        self.screen_height = Cam().window_roi["height"]
        self.initial_height = int(Cam().window_roi["height"] * 0.03)
        self.initial_width = int(self.screen_width * 0.27)
        self.maximized_height = int(self.screen_height * 0.2)
        self.maximized_width = int(self.screen_width * 0.31)

        self.screen_off_x = Cam().window_roi["left"]
        self.screen_off_y = Cam().window_roi["top"]
        self.root.geometry(
            f"{self.initial_width}x{self.initial_height}+{self.screen_width // 2 - self.initial_width // 2 + self.screen_off_x}+{self.screen_height - self.initial_height + self.screen_off_y}"
        )

        if IniConfigLoader().general.hidden_transparency == 0:
            self.root.update()
            hwnd = self.root.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)

        self.hide_id = self.root.after(
            8000,
            lambda: self.root.attributes("-alpha", IniConfigLoader().general.hidden_transparency),
        )
        self.root.bind("<Enter>", self.show_canvas)
        self.root.bind("<Leave>", self.hide_canvas)
        if IniConfigLoader().general.run_vision_mode_on_startup:
            self.run_scripts()

        # Follow the Resolution and window size
        self.current_roi = self.get_current_roi()
        self.update_layout()
        self.check_roi_and_update()

    def get_current_roi(self):
        return f"{Cam.window_roi['top']}x{Cam.window_roi['left']}x{Cam.window_roi['width']}x{Cam.window_roi['height']}"

    def update_layout(self):
        self.screen_width = Cam().window_roi["width"]
        self.screen_height = Cam().window_roi["height"]
        self.initial_height = int(self.screen_height * 0.03)
        self.initial_width = int(self.screen_width * 0.27)
        self.maximized_height = int(self.screen_height * 0.2)
        self.maximized_width = int(self.screen_width * 0.31)

        self.screen_off_x = Cam().window_roi["left"]
        self.screen_off_y = Cam().window_roi["top"]

        if self.is_minimized:
            width = self.initial_width
            height = self.initial_height
        else:
            width = self.maximized_width
            height = self.maximized_height

        self.root.geometry(
            f"{width}x{height}+{self.screen_width // 2 - width // 2 + self.screen_off_x}+{self.screen_height - height + self.screen_off_y}"
        )

    def check_roi_and_update(self):
        new_roi = self.get_current_roi()
        if self.current_roi != new_roi:
            self.current_roi = new_roi
            self.update_layout()
        self.root.after(1000, self.check_roi_and_update)

    def show_filter_buttons(self, event=None):
        self.auto_filter_button.pack(side="right", expand="true", fill="x")
        self.reset_status_button.pack(side="left", expand="true", fill="x")
        self.filter_button.pack_forget()

    def hide_filter_buttons(self, _=None):
        def _hide():
            self.auto_filter_button.pack_forget()
            self.reset_status_button.pack_forget()
            self.filter_button.pack(expand="true", fill="x")

        self.root.after(3000, _hide)

    def handle_filter(self):
        if not self.auto_filter_button.winfo_ismapped():
            self.show_filter_buttons()

    def show_stock_buttons(self, event=None):
        self.stock_to_stash_button.pack(side="left", expand="true", fill="x")
        self.stock_to_inv_button.pack(side="right", expand="true", fill="x")
        self.stock_move_button.pack_forget()

    def hide_stock_buttons(self, _=None):
        def _hide():
            self.stock_to_stash_button.pack_forget()
            self.stock_to_inv_button.pack_forget()
            self.stock_move_button.pack(expand="true", fill="x")

        self.root.after(3000, _hide)

    def handle_stock_move(self):
        if not self.stock_to_stash_button.winfo_ismapped():
            self.show_stock_buttons(event=None)

    def show_canvas(self, _):
        if self.hide_id:
            self.root.after_cancel(self.hide_id)
            self.hide_id = None
        self.root.attributes("-alpha", 0.94)

    def hide_canvas(self, _):
        if self.is_minimized:
            if self.hide_id is not None:
                self.root.after_cancel(self.hide_id)
            self.hide_id = self.root.after(3000, lambda: self.root.attributes("-alpha", IniConfigLoader().general.hidden_transparency))

    def toggle_size(self):
        if not self.is_minimized:
            self.mainframe.config(height=self.initial_height, width=self.initial_width)
            self.root.geometry(
                f"{self.initial_width}x{self.initial_height}+{self.screen_width // 2 - self.initial_width // 2 + self.screen_off_x}+{self.screen_height - self.initial_height + self.screen_off_y}"
            )
        else:
            self.mainframe.config(height=self.maximized_height, width=self.maximized_width)
            self.root.geometry(
                f"{self.maximized_width}x{self.maximized_height}+{self.screen_width // 2 - self.maximized_width // 2 + self.screen_off_x}+{self.screen_height - self.maximized_height + self.screen_off_y}"
            )
        self.is_minimized = not self.is_minimized
        if self.is_minimized:
            self.terminal_text.grid_remove()
            self.hide_canvas(None)
            self.toggle_button.config(text="Console")
        else:
            self.terminal_text.grid(column=0, columnspan=4, row=0, padx=5, pady=5, sticky="nsew")
            self.show_canvas(None)
            self.toggle_button.config(text="Hide Console")
        win_spec = WindowSpec(IniConfigLoader().advanced_options.process_name)
        move_window_to_foreground(win_spec)

    def filter_items(self, force_refresh=False):
        self._start_or_stop_loot_interaction_thread(run_loot_filter, (force_refresh,))

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
                    if self.is_minimized:
                        self.toggle_size()
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
            if not self.is_minimized:
                self.toggle_size()
            self.loot_interaction_thread = None
            self.filter_button.config(fg="#555555")

    def run_scripts(self):
        if LOCK.acquire(blocking=False):
            try:
                if len(self.script_threads) > 0:
                    LOGGER.info("Stopping Vision Mode")
                    self.start_scripts_button.config(fg="#114411")
                    for script_thread in self.script_threads:
                        kill_thread(script_thread)
                    self.script_threads = []
                else:
                    if not IniConfigLoader().advanced_options.scripts:
                        LOGGER.info("No scripts configured")
                        return
                    for name in IniConfigLoader().advanced_options.scripts:
                        if name == "vision_mode":
                            vision_mode_thread = threading.Thread(target=vision_mode, daemon=True)
                            vision_mode_thread.start()
                            self.script_threads.append(vision_mode_thread)
                    self.start_scripts_button.config(fg="#009900")
            finally:
                LOCK.release()
        else:
            return

    def get_scaled_font_size(self):
        window_height = Cam().window_roi["height"]
        font_size = 8
        if window_height == 1440:
            font_size = 9
        elif window_height > 1440:
            font_size = 10
        return font_size

    def run(self):
        self.root.mainloop()
