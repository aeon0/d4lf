import logging
import queue
import threading

import win32file
import win32pipe

LAST_ITEM_SECTION = []
LOGGER = logging.getLogger(__name__)
_DATA_QUEUE = queue.Queue(maxsize=100)
_PIPE_NAME = r"\\.\pipe\d4lf"


def create_pipe() -> int:
    return win32pipe.CreateNamedPipe(
        _PIPE_NAME, win32pipe.PIPE_ACCESS_INBOUND, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT, 1, 2048, 10 * 2 ** (10 * 2), 0, None
    )


def read_pipe() -> None:
    while True:
        handle = create_pipe()
        LOGGER.debug(f"Named pipe '{_PIPE_NAME}' created. Waiting for client to connect...")

        win32pipe.ConnectNamedPipe(handle, None)
        LOGGER.debug("Client connected. Waiting for data...")

        while True:
            try:
                data = win32file.ReadFile(handle, 512)[1].decode().strip()

                if "DISCONNECTED" in data:
                    break
                for s in [s for s in data.split("\x00") if s]:
                    _DATA_QUEUE.put(s)
            except Exception as e:
                print(f"Error while reading data: {e}")
                break

        win32file.CloseHandle(handle)
        print("Client disconnected. Waiting for a new client...")


def detector() -> None:
    local_cache = []
    while True:
        data = fix_data(_DATA_QUEUE.get())
        local_cache.append(data)
        if any(word in data.lower() for word in ["markasjunk", "markasfavorite", "unmarkitem"]):
            start = find_item_start(local_cache)
            global LAST_ITEM_SECTION
            LAST_ITEM_SECTION = local_cache[start:]
            local_cache = []


def has_more_than_consecutive_capitals(s: str, n: int = 5) -> bool:
    capital_count = 0
    for char in s:
        if char.isupper():
            capital_count += 1
            if capital_count > n:
                return True
        else:
            capital_count = 0
    return False


def find_item_start(data: list[str]) -> int:
    item_starts = ["Compass", "Nightmare Sigil", "Tribute of"]
    for index in range(len(data) - 1, -1, -1):
        if any(word in data[index] for word in item_starts):
            return index
    for index in range(len(data) - 1, -1, -1):
        if has_more_than_consecutive_capitals(data[index]):
            return index
    return -1


def fix_data(data: str) -> str:
    return (
        data.replace("&apos;", "")
        .replace("&quot;", "")
        .replace("[FAVORITED ITEM]. ", "")
        .replace("ￂﾠ", "")
        .replace("(Spiritborn Only", "")
        .strip()
    )


def start_connection() -> None:
    LOGGER.info("Starting tts connection...")
    threading.Thread(target=detector, daemon=True).start()
    threading.Thread(target=read_pipe, daemon=True).start()
