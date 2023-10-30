from typing import Optional
import numpy as np
from dataclasses import dataclass
from cam import Cam
from config import Config
from ui.menu import Menu
from utils.image_operations import crop, threshold
from utils.roi_operations import get_center, pad, to_grid
from utils.custom_mouse import mouse
from utils.misc import wait


@dataclass
class ItemSlot:
    bounding_box: list[int] = None
    center: list[int] = None


class InventoryBase(Menu):
    """
    Base class for all menus with a grid inventory
    Provides methods for identifying occupied and empty slots, item operations, etc.
    """

    def __init__(self):
        super().__init__()
        self.rows = 3
        self.columns = 11
        self.slots_roi = Config().ui_roi[f"{self.rows}x{self.columns}_slots"]

    def get_item_slots(self, img: Optional[np.ndarray] = None) -> tuple[list[ItemSlot], list[ItemSlot]]:
        """
        Identifies occupied and empty slots in a grid of slots within a given rectangle of interest (ROI).
        :param roi: The rectangle to consider, represented as (x_min, y_min, width, height).
        :param rows: The number of rows in the grid.
        :param columns: The number of columns in the grid.
        :param img: An optional image (as a numpy array) to use for identifying empty slots.
        :return: Two sets of coordinates. The first set represents the centers of the occupied slots, and the second set represents the centers of the empty slots.
        """
        if img is None:
            mouse.move(*Cam().abs_window_to_monitor((0, 0)), randomize=5)
            img = Cam().grab()
        grid = to_grid(self.slots_roi, self.rows, self.columns)
        occupied_slots = []
        empty_slots = []
        threshold_strength = 40

        for _, slot_roi in enumerate(grid):
            sub_roi = pad(rectangle=slot_roi, pixels=-4, direction="all")
            slot_img = crop(img, sub_roi)
            thresholded_slot = threshold(slot_img, threshold=threshold_strength)
            # check if there are any white pixels in thresholded_slot
            if np.any(thresholded_slot):
                occupied_slots.append(ItemSlot(bounding_box=slot_roi, center=get_center(slot_roi)))
            else:
                empty_slots.append(ItemSlot(bounding_box=slot_roi, center=get_center(slot_roi)))

        return occupied_slots, empty_slots

    def hover_item(self, item: ItemSlot):
        mouse.move(*Cam().window_to_monitor(item.center), randomize=15, delay_factor=(1.4, 1.6))
