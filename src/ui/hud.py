import cv2
import numpy as np

from cam import Cam
from config import Config
from utils.image_operations import color_filter, crop
from template_finder import SearchArgs


class Hud(SearchArgs):
    def __init__(self):
        self.ref = ["HUD_DETECTION_LEFT"]
        self.threshold = 0.94
        self.roi = "hud_detection"
        self.use_grayscale = True
        self.do_multi_process = False

    def is_ingame(self, img: np.ndarray = None) -> bool:
        img = img if img is not None else Cam().grab()
        cropped_img = cv2.cvtColor(crop(img, Config().ui_roi["mini_map_visible"]), cv2.COLOR_BGR2GRAY)
        _, binary_mask = cv2.threshold(cropped_img, 155, 255, cv2.THRESH_BINARY)
        mini_map_visible = cv2.countNonZero(binary_mask) > 5
        return self.is_visible(img=img) and mini_map_visible

    @staticmethod
    def is_skill_ready(img: np.ndarray = None, roi_name: str = "skill4") -> bool:
        img = Cam().grab() if img is None else img
        # Check avg saturation
        roi = Config().ui_roi[roi_name]
        cropped = crop(img, roi)
        hsv_image = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
        _, saturation, _ = cv2.split(hsv_image)
        avg_saturation = np.mean(saturation)
        # Check if on cd
        cropped = crop(cropped, Config().ui_roi["rel_skill_cd"])
        mask, _ = color_filter(cropped, Config().colors[f"skill_cd"], False)
        # at least half of the row must be filled
        target_sum = (mask.shape[0] * mask.shape[1] * 255) * 0.8
        cd_sum = np.sum(mask)
        ready = avg_saturation > 100 and cd_sum < target_sum
        return ready

    @staticmethod
    def is_imbued(img: np.ndarray = None, roi_name: str = "core_skill") -> bool:
        colors = ["shadow_imbued", "posion_imbued", "cold_imbued"]
        for color in colors:
            img = Cam().grab() if img is None else img
            # Check avg saturation
            roi = Config().ui_roi[roi_name]
            cropped = crop(img, roi)
            mask, _ = color_filter(cropped, Config().colors[color], False)
            # at least half of the row must be filled
            target_sum = (mask.shape[0] * mask.shape[1] * 255) * 0.3
            cd_sum = np.sum(mask)
            if cd_sum > target_sum:
                return True
        return False
