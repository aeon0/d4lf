import logging
import time

import keyboard
import numpy as np

from src.cam import Cam
from src.config.ui import ResManager
from src.utils.custom_mouse import mouse
from src.utils.image_operations import crop
from src.utils.ocr.read import image_to_text

LOGGER = logging.getLogger(__name__)


def is_vendor_open(img: np.ndarray):
    cropped = crop(img, ResManager().roi.vendor_text)
    res = image_to_text(cropped, do_pre_proc=False)
    return res.text.strip().lower() == "vendor"


def mark_as_junk():
    keyboard.send("space")
    time.sleep(0.13)


def mark_as_favorite():
    LOGGER.info("Mark as favorite")
    keyboard.send("space")
    time.sleep(0.17)
    keyboard.send("space")
    time.sleep(0.13)


def reset_canvas(root, canvas):
    canvas.delete("all")
    canvas.config(height=0, width=0)
    root.geometry("0x0+0+0")
    root.update_idletasks()
    root.update()


def reset_item_status(occupied, inv):
    for item_slot in occupied:
        if item_slot.is_fav:
            inv.hover_item(item_slot)
            keyboard.send("space")
        if item_slot.is_junk:
            inv.hover_item(item_slot)
            keyboard.send("space")
            time.sleep(0.13)
            keyboard.send("space")

    if occupied:
        mouse.move(*Cam().abs_window_to_monitor((0, 0)))
