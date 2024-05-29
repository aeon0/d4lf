import ctypes
import os

from src.logger import Logger
from src.utils.window import get_window_spec_id


def kill_thread(thread):
    thread_id = thread.ident
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        Logger.error("Exception raise failure")


def safe_exit(error_code=0):
    Logger.info("Shutting down")
    os._exit(error_code)


def set_process_name(name, window_spec):
    try:
        hwnd = get_window_spec_id(window_spec)
        kernel32 = ctypes.WinDLL("kernel32")
        kernel32.SetConsoleTitleW(hwnd, name)
    except Exception as e:
        Logger.error("Failed to set process name:", str(e))
