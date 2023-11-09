from typing import Optional
import numpy as np
import cv2
from dataclasses import dataclass
from cam import Cam
from config import Config
from ui.menu import Menu
from utils.image_operations import crop, threshold
from utils.roi_operations import get_center, to_grid
from utils.custom_mouse import mouse
from utils.misc import wait
from template_finder import get_template


@dataclass
class ItemSlot:
    bounding_box: list[int] = None
    center: list[int] = None
    is_fav: bool = False
    is_junk: bool = False


class InventoryBase(Menu):
    """
    Base class for all menus with a grid inventory
    Provides methods for identifying occupied and empty slots, item operations, etc.
    """

    def __init__(self, rows: int = 3, columns: int = 11):
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.slots_roi = Config().ui_roi[f"slots_{self.rows}x{self.columns}"]
        mask_gray = cv2.cvtColor(get_template("JUNK_MASK"), cv2.COLOR_BGR2GRAY)
        _, self.junk_mask = cv2.threshold(mask_gray, 127, 255, cv2.THRESH_BINARY)

    def get_item_slots(self, img: Optional[np.ndarray] = None) -> tuple[list[ItemSlot], list[ItemSlot], list[ItemSlot], list[ItemSlot]]:
        """
        Identifies occupied and empty slots in a grid of slots within a given rectangle of interest (ROI).
        :param roi: The rectangle to consider, represented as (x_min, y_min, width, height).
        :param rows: The number of rows in the grid.
        :param columns: The number of columns in the grid.
        :param img: An optional image (as a numpy array) to use for identifying empty slots.
        :return: Four sets of coordinates.
            - Centers of the occupied slots
            - Centers of the empty slots
        """
        if img is None:
            mouse.move(*Cam().abs_window_to_monitor((0, -int(Cam().window_roi["height"] * 0.4))), randomize=5)
            wait(0.5)
            img = Cam().grab()
        grid = to_grid(self.slots_roi, self.rows, self.columns)
        occupied_slots = []
        empty_slots = []

        for _, slot_roi in enumerate(grid):
            item_slot = ItemSlot(bounding_box=slot_roi, center=get_center(slot_roi))
            slot_img = crop(img, slot_roi)

            junk_mask = self.junk_mask.copy()
            if self.junk_mask.shape[:2] != slot_img.shape[:2]:
                junk_mask = cv2.resize(junk_mask, (slot_img.shape[1], slot_img.shape[0]))
            junk_mask_inv = cv2.bitwise_not(junk_mask)

            hsv_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
            mean_value_overall = np.mean(hsv_img[:, :, 2])
            fav_flag_crop = crop(hsv_img, Config().ui_roi["rel_fav_flag"])
            mean_value_fav = cv2.mean(fav_flag_crop)[2]

            # check junk
            hsv_junk = cv2.bitwise_and(hsv_img, hsv_img, mask=junk_mask)
            mean_hsv = cv2.mean(hsv_junk, mask=junk_mask)
            _, mean_saturation, mean_value = mean_hsv[:3]
            hsv_junk_inv = cv2.bitwise_and(hsv_img, hsv_img, mask=junk_mask_inv)
            mean_hsv_inv = cv2.mean(hsv_junk_inv, mask=junk_mask_inv)
            _, _, mean_value_inv = mean_hsv_inv[:3]

            if mean_value_fav > 205:
                item_slot.is_fav = True
                occupied_slots.append(item_slot)
            elif mean_value > 110 and mean_saturation < 50 and (mean_value - mean_value_inv) > 90:
                item_slot.is_junk = True
                occupied_slots.append(item_slot)
            elif mean_value_overall > 37:
                occupied_slots.append(item_slot)
            else:
                empty_slots.append(item_slot)

        return occupied_slots, empty_slots

    def hover_item(self, item: ItemSlot):
        mouse.move(*Cam().window_to_monitor(item.center), randomize=15, delay_factor=(1.1, 1.3))
