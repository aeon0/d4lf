import ctypes
import os
import threading
import time
from dataclasses import dataclass

import cv2
import numpy as np
import psutil
from win32gui import GetWindowText, EnumWindows, GetClientRect, ClientToScreen
from win32process import GetWindowThreadProcessId

from cam import Cam
from logger import Logger
from utils.misc import wait

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
    process_name: str

    def match(self, hwnd: int, check_window_name: bool = True) -> bool:
        window_name_ok = not check_window_name or "diablo" in _get_window_name_from_id(hwnd).lower()
        return _get_process_from_window_name(hwnd) == self.process_name and window_name_ok


def _list_active_window_ids() -> list[int]:
    window_list = []
    EnumWindows(lambda w, l: l.append(w), window_list)
    return window_list


def get_window_spec_id(window_spec: WindowSpec) -> int | None:
    for hwnd in _list_active_window_ids():
        if window_spec.match(hwnd):
            return hwnd
    # If no process was found with "diablo" in the window name, search without that restriction
    for hwnd in _list_active_window_ids():
        if window_spec.match(hwnd, check_window_name=False):
            return hwnd
    return None


def _get_window_name_from_id(hwnd: int) -> str:
    return GetWindowText(hwnd)


def _get_process_from_window_name(hwnd: int) -> str:
    try:
        pid = GetWindowThreadProcessId(hwnd)[1]
        return psutil.Process(pid).name().lower()
    except Exception as e:
        return ""


def start_detecting_window(window_spec: WindowSpec):
    global detecting_window_flag, detect_window_thread
    if detect_window_thread is None:
        Logger.info(f"Using WinAPI to search for window: {window_spec.process_name}")
        detecting_window_flag = True
        detect_window_thread = threading.Thread(target=detect_window, args=(window_spec,), daemon=True)
        detect_window_thread.start()


def detect_window(window_spec: WindowSpec):
    global detecting_window_flag
    while detecting_window_flag:
        find_and_set_window_position(window_spec)
    Logger.debug("Detect window thread stopped")


def find_and_set_window_position(window_spec: WindowSpec):
    hwnd = get_window_spec_id(window_spec)
    if hwnd is not None:
        pos = GetClientRect(hwnd)
        top_left = ClientToScreen(hwnd, (pos[0], pos[1]))
        Cam().update_window_pos(top_left[0], top_left[1], pos[2], pos[3])
    wait(1)


def stop_detecting_window():
    global detecting_window_flag, detect_window_thread
    detecting_window_flag = False
    if detect_window_thread:
        detect_window_thread.join()
    detect_window_thread = None


def move_window_to_foreground(window_spec: WindowSpec):
    hwnd = get_window_spec_id(window_spec)
    if hwnd is not None:
        ctypes.windll.user32.ShowWindow(hwnd, 5)
        ctypes.windll.user32.SetForegroundWindow(hwnd)


def is_window_foreground(window_spec: WindowSpec) -> bool:
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
    find_and_set_window_position(WindowSpec("Diablo IV.exe"))
