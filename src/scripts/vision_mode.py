import numpy as np
import traceback
from cam import Cam
from ui.char_inventory import CharInventory
from ui.chest import Chest
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger
from item.find_descr import find_descr
from item.descr.read_descr import read_descr
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.filter import Filter
import tkinter as tk
from config import Config

from utils.ocr.read import image_to_text
from utils.image_operations import crop


def draw_rect(canvas: tk.Canvas, bullet_width, obj, off, color):
    offset_loc = np.array(obj.loc) + off
    x1 = int(offset_loc[0] - bullet_width / 2)
    y1 = int(offset_loc[1] - bullet_width / 2)
    x2 = int(offset_loc[0] + bullet_width / 2)
    y2 = int(offset_loc[1] + bullet_width / 2)
    canvas.create_rectangle(x1, y1, x2, y2, fill=color)


def draw_text(canvas, text, color, h, off, center):
    if text is None or text == "":
        return
    font_size = 13
    window_height = Config().ui_pos["window_dimensions"][1]
    if window_height == 1440:
        font_size = 15
    elif window_height == 2160:
        font_size = 17
    if len(text) > 27:
        text = text[:24] + "..."

    # Create a white rectangle as the background
    text_width = 1.02 * len(text) * font_size  # You might need to adjust this based on your text and font
    text_height = 2.0 * font_size  # You might need to adjust this based on your font size
    dark_gray_color = "#111111"  # Dark gray with transparency (adjust the alpha value as needed)
    canvas.create_rectangle(
        center - text_width // 2,
        h - off - text_height // 2,
        center + text_width // 2,
        h - off + text_height // 2,
        fill=dark_gray_color,
        outline="",
    )
    canvas.create_text(center, h - off, text=text, font=("Courier New", font_size), fill=color)


def reset_canvas(root, canvas):
    canvas.delete("all")
    canvas.config(height=0, width=0)
    root.geometry(f"0x0+0+0")
    root.update_idletasks()
    root.update()


def is_vendor_open(img: np.ndarray):
    cropped = crop(img, Config().ui_roi["vendor_text"])
    res = image_to_text(cropped)
    return res.text.strip().lower() == "vendor"


def vision_mode():
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", "black")
    root.attributes("-alpha", 1.0)
    root.geometry(f"0x0+0+0")

    thick = int(Cam().window_roi["height"] * 0.0047)
    canvas = tk.Canvas(root, bg="black", highlightthickness=thick, highlightbackground="red")
    canvas.pack(fill=tk.BOTH, expand=True)

    Logger.info("Starting Vision Filter")
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

    screen_off_x = Cam().window_roi["left"]
    screen_off_y = Cam().window_roi["top"]

    last_top_left_corner = None
    last_center = None
    while True:
        img = Cam().grab()
        # if chest.is_open(img) or inv.is_open(img):
        mouse_pos = Cam().monitor_to_window(mouse.get_position())
        # get closest pos to a item center
        delta = possible_centers - mouse_pos
        distances = np.linalg.norm(delta, axis=1)
        closest_index = np.argmin(distances)
        item_center = possible_centers[closest_index]
        found, rarity, cropped_descr, item_roi = find_descr(img, item_center)
        if not found and is_vendor_open(img):
            vendor_item_center = [Config().ui_offsets["vendor_center_item_x"], 0]
            found, rarity, cropped_descr, item_roi = find_descr(img, vendor_item_center)

        top_left_corner = None if not found else item_roi[:2]
        if found:
            if (
                last_top_left_corner is None
                or last_top_left_corner[0] != top_left_corner[0]
                or last_top_left_corner[1] != top_left_corner[1]
                or (last_center is not None and last_center[1] != item_center[1])
            ):
                reset_canvas(root, canvas)

                # Make the canvas gray for "found the item"
                x, y, w, h = item_roi
                off = int(w * 0.086)
                x -= off
                y -= off
                w += off * 2
                h += off
                canvas.config(height=h, width=w)
                canvas.config(highlightbackground="#888888")
                root.geometry(f"{w}x{h}+{x+screen_off_x}+{y+screen_off_y}")
                root.update_idletasks()
                root.update()

                # Check if the item is a match based on our filters
                match = True
                item_descr = None
                last_top_left_corner = top_left_corner
                last_center = item_center
                item_descr = read_descr(rarity, cropped_descr, True)
                if item_descr is None:
                    last_center = None
                    last_top_left_corner = None
                    continue

                if rarity == ItemRarity.Common and item_descr.type == ItemType.Material:
                    Logger.info(f"Matched: Material")
                    continue
                elif rarity == ItemRarity.Legendary and item_descr.type == ItemType.Material:
                    Logger.info(f"Matched: Extracted Aspect")
                    continue
                elif rarity == ItemRarity.Magic and item_descr.type == ItemType.Elixir:
                    Logger.info(f"Matched: Elixir")
                    continue
                elif rarity in [ItemRarity.Magic, ItemRarity.Common] and item_descr.type != ItemType.Sigil:
                    match = False

                matched_str = ""
                if item_descr is not None:
                    keep, did_match_affixes, matched_affixes, info_str = Filter().should_keep(item_descr)
                    if not keep:
                        match = False

                # Adapt colors based on config

                if match:
                    canvas.config(highlightbackground="#23fc5d")
                    draw_text(canvas, info_str, "#23fc5d", h, off, w // 2)
                    # Show matched bullets
                    if item_descr is not None:
                        bullet_width = thick * 3
                        for affix in item_descr.affixes:
                            if affix.loc is not None and any(a == affix.type for a in matched_affixes):
                                draw_rect(canvas, bullet_width, affix, off, "#23fc5d")

                        if item_descr.aspect is not None and not did_match_affixes:
                            draw_rect(canvas, bullet_width, item_descr.aspect, off, "#23fc5d")
                elif not match:
                    canvas.config(highlightbackground="#fc2323")
                    draw_text(canvas, info_str, "#fc2323", h, off, w // 2)

                root.update_idletasks()
                root.update()
        else:
            reset_canvas(root, canvas)
            last_center = None
            last_top_left_corner = None
            wait(0.15)


if __name__ == "__main__":
    try:
        from utils.window import start_detecting_window

        start_detecting_window()
        while not Cam().is_offset_set():
            wait(0.2)
        Filter().load_files()
        vision_mode()
    except:
        traceback.print_exc()
        print("Press Enter to exit ...")
        input()
