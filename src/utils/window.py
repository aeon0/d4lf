import threading
import ctypes
from dataclasses import dataclass
import time
import psutil
from win32gui import GetWindowText, EnumWindows, GetWindowRect
from win32process import GetWindowThreadProcessId
from logger import Logger
from utils.misc import wait
from cam import Cam
import os
import cv2
import numpy as np


detecting_window_flag = True
detect_window_thread = None

# Set the process DPI aware
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"Exception: {e}")
    print("This program requires Windows 8.1 or higher.")
    print("The program will try to continue to run, but results may be inaccurate.")
    ctypes.windll.user32.SetProcessDPIAware()


@dataclass
class WindowSpec:
    window_name: str
    process_name: str

    def match(self, hwnd: int) -> bool:
        return _get_window_name_from_id(hwnd) == self.window_name and _get_process_from_window_name(hwnd) == self.process_name


D4_WINDOW = WindowSpec("Diablo IV", "Diablo IV.exe")


def _list_active_window_ids() -> list[int]:
    window_list = []
    EnumWindows(lambda w, l: l.append(w), window_list)
    return window_list


def get_window_spec_id(window_spec: WindowSpec = D4_WINDOW) -> int | None:
    for hwnd in _list_active_window_ids():
        if window_spec.match(hwnd):
            return hwnd
    return None


def _get_window_name_from_id(hwnd: int) -> str:
    return GetWindowText(hwnd)


def _get_process_from_window_name(hwnd: int) -> str:
    return psutil.Process(GetWindowThreadProcessId(hwnd)[1]).name()


def start_detecting_window(window_spec: WindowSpec = D4_WINDOW):
    global detecting_window_flag, detect_window_thread
    if detect_window_thread is None:
        Logger.info(f"Using WinAPI to search for window: {window_spec.process_name}")
        detecting_window_flag = True
        detect_window_thread = threading.Thread(target=detect_window)
        detect_window_thread.start()


def detect_window(window_spec: WindowSpec = D4_WINDOW):
    global detecting_window_flag
    while detecting_window_flag:
        find_and_set_window_position(window_spec)
    Logger.debug("Detect window thread stopped")


def find_and_set_window_position(window_spec: WindowSpec = D4_WINDOW):
    hwnd = get_window_spec_id(window_spec)
    if hwnd is not None:
        position = GetWindowRect(hwnd)
        Cam().update_window_pos(*position)
    wait(0.5)


def stop_detecting_window():
    global detecting_window_flag, detect_window_thread
    detecting_window_flag = False
    if detect_window_thread:
        detect_window_thread.join()
    detect_window_thread = None


def move_window_to_foreground(window_spec: WindowSpec = D4_WINDOW):
    hwnd = get_window_spec_id(window_spec)
    if hwnd is not None:
        ctypes.windll.user32.SetForegroundWindow(hwnd)


def is_window_foreground(window_spec: WindowSpec = D4_WINDOW) -> bool:
    hwnd = get_window_spec_id(window_spec)
    if hwnd is not None:
        active_window_handle = ctypes.windll.user32.GetForegroundWindow()
        return active_window_handle == hwnd
    return False


def screenshot(name: str = None, path: str = "log/screenshots", img: np.ndarray = None, overwrite: bool = True, timestamp: bool = True):
    name = name if name is not None else "screenshot"
    img = img if img is not None else Cam().grab()

    os.makedirs(path, exist_ok=True)
    file_path = f"{path}/{name}{'_' + time.strftime('%Y%m%d_%H%M%S') if timestamp else ''}.png"

    if os.path.exists(file_path):
        if overwrite:
            Logger.warning(f"{name} already exists, overwriting.")
            cv2.imwrite(file_path, img)
        else:
            Logger.warning(f"{name} already exists, not overwriting because overwrite is set to False.")
    else:
        cv2.imwrite(file_path, img)
        Logger.debug(f"Saved screenshot: {file_path}")


if __name__ == "__main__":
    find_and_set_window_position(WindowSpec("Diablo IV", "Diablo IV.exe"))
