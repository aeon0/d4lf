import queue
import threading

import rapidfuzz
import win32file
import win32pipe

from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.item.models import Item

pipe_name = r"\\.\pipe\d4lf"
data_queue = queue.Queue(maxsize=100)
last_item_section = queue.Queue(maxsize=1)


def create_pipe():
    return win32pipe.CreateNamedPipe(
        pipe_name, win32pipe.PIPE_ACCESS_INBOUND, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT, 1, 2048, 10 * 2 ** (10 * 2), 0, None
    )


def read_pipe():
    while True:
        handle = create_pipe()
        print(f"Named pipe '{pipe_name}' created. Waiting for client to connect...")

        p = win32pipe.ConnectNamedPipe(handle, None)
        print("Client connected. Waiting for data...")

        while True:
            try:
                data = win32file.ReadFile(handle, 512)[1].decode().strip()

                if "DISCONNECTED" in data:
                    break
                for s in [s for s in data.split("\x00") if s]:
                    print(s)
                    data_queue.put(s)
            except Exception as e:
                print(f"Error while reading data: {e}")
                break

        win32file.CloseHandle(handle)
        print("Client disconnected. Waiting for a new client...")


def detector():
    local_cache = []
    while True:
        data = data_queue.get()
        data = (
            data.replace("&apos;", "").replace("&quot;", "").replace("[FAVORITED ITEM]. ", "").replace("ￂﾠ", "")
        )  # TODO only im namen. apos  und quot auch überall
        local_cache.append(data)
        if "markasjunk" in data.lower() or "markasfavorite" in data.lower() or "unmarkitem" in data.lower():
            start = find_item_start(local_cache)
            last_item_section.put(local_cache[start:])
            local_cache = []


def has_more_than_consecutive_capitals(s, n=5):
    capital_count = 0
    for char in s:
        if char.isupper():
            capital_count += 1
            if capital_count > n:
                return True
        else:
            capital_count = 0
    return False


def find_item_start(strings):
    item_starts = ["Compass", "Nightmare Sigil", "Tribute of"]
    for index in range(len(strings) - 1, -1, -1):
        if any(word in strings[index] for word in item_starts):
            return index
    for index in range(len(strings) - 1, -1, -1):
        if has_more_than_consecutive_capitals(strings[index]):
            return index
    return -1


def create_item_from_tts(tts_item):
    if tts_item[0] == "Compass":
        return Item(rarity=ItemRarity.Common, item_type=ItemType.Compass)
    if tts_item[0] == "Nightmare Sigil":
        return Item(rarity=ItemRarity.Common, item_type=ItemType.Sigil)

    if any(word in tts_item[0] for word in ["Tribute of"]):
        search_string = tts_item[0].lower()
    else:
        search_string = tts_item[1].lower().replace("ancestral", "").strip()
    item = Item()
    res = rapidfuzz.process.extractOne(search_string, [rar.value for rar in ItemRarity], scorer=rapidfuzz.distance.Levenshtein.distance)
    try:
        item.rarity = ItemRarity(res[0]) if res else None
    except ValueError:
        item.rarity = None
    res = rapidfuzz.process.extractOne(search_string, [it.value for it in ItemType], scorer=rapidfuzz.distance.Levenshtein.distance)
    try:
        item.item_type = ItemType(res[0]) if res else None
    except ValueError:
        item.item_type = None
    return item


def start():
    threading.Thread(target=detector, daemon=True).start()
    threading.Thread(target=read_pipe, daemon=True).start()
