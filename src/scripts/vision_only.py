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


def draw_rectangle(canvas, color):
    item_roi = [50, 50, 100, 100]  # Example ROI values
    x1, y1, width, height = item_roi
    x2 = x1 + width
    y2 = y1 + height
    return canvas.create_rectangle(x1, y1, x2, y2, outline=color)


def vision_only():
    ww, wh = (1920, 1080)
    # Create the main window
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)  # Keep on top of other windows
    root.attributes("-alpha", 0.7)
    root.geometry(f"{ww}x{wh}+{0}+{0}")

    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    rectangle_id = None  # To store the rectangle's canvas ID

    canvas.create_rectangle(50, 50, 150, 150, outline="red", width=2)

    Logger.info("Starting Vision Only Script")
    Filter().load_files()
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
                last_top_left_corner = top_left_corner
                item_descr = read_descr(rarity, cropped_descr)
                if item_descr is None:
                    Logger.warning("Failed to read properties")
                    continue

                # Hardcoded filters
                match = True

                if rarity == ItemRarity.Common and item_descr.type == ItemType.Material:
                    Logger.info(f"Matched: Material / Sigil")
                elif rarity == ItemRarity.Legendary and item_descr.type == ItemType.Material:
                    Logger.info(f"Matched: Extracted Aspect")
                elif rarity == ItemRarity.Magic and item_descr.type == ItemType.Elixir:
                    Logger.info(f"Matched: Elixir")
                elif rarity in [ItemRarity.Magic, ItemRarity.Common]:
                    Logger.info(f"Junk")
                    match = False
                elif rarity in [ItemRarity.Unique]:
                    Logger.info("Matched: Unique")
                elif not Filter().should_keep(item_descr):
                    Logger.info(f"Junk")
                    match = False

                item_roi
                if match and not rectangle_id:
                    rectangle_id = draw_rectangle(canvas, "green")
                elif not match and not rectangle_id:
                    rectangle_id = draw_rectangle(canvas, "red")

        else:
            if rectangle_id:  # If the rectangle is drawn
                canvas.delete(rectangle_id)  # Remove the rectangle
                rectangle_id = None  # Reset the ID
            wait(0.1)

        root.update_idletasks()
        root.update()


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
