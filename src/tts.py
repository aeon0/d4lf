import enum
import logging
import queue
import re
import threading

import win32file
import win32pipe

LAST_ITEM = []
LOGGER = logging.getLogger(__name__)
_DATA_QUEUE = queue.Queue(maxsize=100)


class ItemIdentifiers(enum.Enum):
    COMPASS = "Compass"
    NIGHTMARE_SIGIL = "Nightmare Sigil"
    TRIBUTE = "TRIBUTE OF"
    WHISPERING_KEY = "WHISPERING KEY"


def create_pipe() -> int:
    return win32pipe.CreateNamedPipe(
        r"\\.\pipe\d4lf",
        win32pipe.PIPE_ACCESS_INBOUND,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
        1,
        2048,
        10 * 2 ** (10 * 2),
        0,
        None,
    )


def read_pipe() -> None:
    while True:
        handle = create_pipe()
        LOGGER.debug("Waiting for TTS client to connect")

        win32pipe.ConnectNamedPipe(handle, None)
        LOGGER.debug("TTS client connected")

        while True:
            try:
                data = win32file.ReadFile(handle, 512)[1].decode().strip()

                if "DISCONNECTED" in data:
                    break
                for s in [s for s in data.split("\x00") if s]:
                    _DATA_QUEUE.put(s)
            except Exception as e:
                print(f"Error while reading data: {e}")

        win32file.CloseHandle(handle)
        print("TTS client disconnected")


def detector() -> None:
    local_cache = []
    while True:
        data = fix_data(_DATA_QUEUE.get())
        local_cache.append(data)
        if any(word in data.lower() for word in ["mouse button"]) and (start := find_item_start(local_cache)) is not None:
            global LAST_ITEM
            LAST_ITEM = local_cache[start:]
            LOGGER.debug(f"TTS Found: {LAST_ITEM}")
            local_cache = []


def find_item_start(data: list[str]) -> int | None:
    ignored_words = ["COMPASS AFFIXES", "DUNGEON AFFIXES"]

    for index, item in reversed(list(enumerate(data))):
        if any(ignored in item for ignored in ignored_words):
            continue

        if any(item.startswith(x) for x in [y.value for y in ItemIdentifiers]):
            return index

        cleaned_str = re.sub(r"[^A-Za-z]", "", item)
        if len(cleaned_str) >= 3 and item.isupper():
            return index

    return None


def fix_data(data: str) -> str:
    to_remove = ["&apos;", "&quot;", "[FAVORITED ITEM]. ", "ￂﾠ", "(Spiritborn Only)", "[MARKED AS JUNK]. "]

    for item in to_remove:
        data = data.replace(item, "")

    return data.strip()


def start_connection() -> None:
    LOGGER.info("Starting tts listener")
    threading.Thread(target=detector, daemon=True).start()
    threading.Thread(target=read_pipe, daemon=True).start()
