import numpy as np
import traceback
from cam import Cam
from ui.char_inventory import CharInventory
from ui.chest import Chest
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger
from item.find_descr import find_descr
from item.read_descr import read_descr
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.filter import Filter
import tkinter as tk


def vision_only():
    # Create the main window
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)  # Keep on top of other windows
    root.attributes("-transparentcolor", "black")
    root.attributes("-alpha", 1.0)
    root.geometry(f"0x0+0+0")

    canvas = tk.Canvas(root, bg="black", highlightthickness=5, highlightbackground="red")
    canvas.pack(fill=tk.BOTH, expand=True)

    Logger.info("Starting Vision Only Script")
    # Filter().load_files()
    inv = CharInventory()
    chest = Chest()
    img = Cam().grab()
    occ_inv, empty_inv = inv.get_item_slots(img)
    occ_chest, empty_chest = chest.get_item_slots(img)
    possible_centers = []
    possible_centers += [slot.center for slot in occ_inv]
    possible_centers += [slot.center for slot in empty_inv]
    possible_centers += [slot.center for slot in occ_chest]
    possible_centers += [slot.center for slot in empty_chest]
    possible_centers = np.array(possible_centers)

    last_top_left_corner = None
    while True:
        img = Cam().grab()
        # if chest.is_open(img) or inv.is_open(img):
        mouse_pos = Cam().monitor_to_window(mouse.get_position())
        # get closest pos to a item center
        differences = possible_centers - mouse_pos
        distances = np.linalg.norm(differences, axis=1)
        closest_index = np.argmin(distances)
        item_center = possible_centers[closest_index]
        found, rarity, cropped_descr, top_left_corner, item_roi = find_descr(img, item_center)
        if found:
            if (
                last_top_left_corner is None
                or last_top_left_corner[0] != top_left_corner[0]
                or last_top_left_corner[1] != top_left_corner[1]
            ):
                match = True
                item_descr = None
                last_top_left_corner = top_left_corner
                if rarity in [ItemRarity.Unique]:
                    Logger.info("Matched: Unique")
                else:
                    item_descr = read_descr(rarity, cropped_descr)
                    if item_descr is None:
                        Logger.warning("Failed to read properties")
                        continue

                    if rarity == ItemRarity.Common and item_descr.type == ItemType.Material:
                        Logger.info(f"Matched: Material / Sigil")
                    elif rarity == ItemRarity.Legendary and item_descr.type == ItemType.Material:
                        Logger.info(f"Matched: Extracted Aspect")
                    elif rarity == ItemRarity.Magic and item_descr.type == ItemType.Elixir:
                        Logger.info(f"Matched: Elixir")
                    elif rarity in [ItemRarity.Magic, ItemRarity.Common]:
                        Logger.info(f"Junk")
                        match = False

                if item_descr is not None:
                    res = Filter().should_keep(item_descr)
                    if not res:
                        Logger.info(f"Junk")
                        match = False

                x, y, w, h = item_roi
                off = int(w * 0.08)
                x -= off
                y -= off
                w += off * 2
                h += off * 2
                if match:
                    canvas.config(height=h, width=w)
                    canvas.config(highlightbackground="#23fc5d")
                    root.geometry(f"{w}x{h}+{x}+{y}")
                elif not match:
                    canvas.config(height=h, width=w)
                    canvas.config(highlightbackground="#fc2323")
                    root.geometry(f"{w}x{h}+{x}+{y}")
                root.update_idletasks()
                root.update()
        else:
            canvas.config(height=0, width=0)
            root.geometry(f"0x0+0+0")
            last_top_left_corner = None
            root.update_idletasks()
            root.update()
            wait(0.2)


if __name__ == "__main__":
    try:
        from utils.window import start_detecting_window

        start_detecting_window()
        while not Cam().is_offset_set():
            wait(0.2)
        vision_only()
    except:
        traceback.print_exc()
        print("Press Enter to exit ...")
        input()
