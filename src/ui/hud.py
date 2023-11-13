import cv2
import numpy as np
import math
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
        _, binary_mask = cv2.threshold(cropped_img, 145, 255, cv2.THRESH_BINARY)
        mini_map_visible = cv2.countNonZero(binary_mask) > 20
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

    @staticmethod
    def get_health(img: np.ndarray = None) -> float:
        img = Cam().grab() if img is None else img
        cut_img = crop(img, Config().ui_roi["health_slice"])
        sobel_y = cv2.Sobel(cut_img, cv2.CV_64F, 0, 1, ksize=3)
        _, binary = cv2.threshold(np.abs(sobel_y), 100, 255, cv2.THRESH_BINARY)
        blue, green, red = cv2.split(binary)
        lines_red = cv2.HoughLinesP(red.astype(np.uint8), 1, math.pi / 2, 2, None, 30, 1)
        lines_green = cv2.HoughLinesP(green.astype(np.uint8), 1, math.pi / 2, 2, None, 30, 1)
        lines_blue = cv2.HoughLinesP(blue.astype(np.uint8), 1, math.pi / 2, 2, None, 30, 1)
        lines = []
        if lines_red is not None:
            lines.extend(lines_red)
        if lines_green is not None:
            lines.extend(lines_green)
        if lines_blue is not None:
            lines.extend(lines_blue)
        # for line in lines[0]:
        #     pt1 = (line[0], line[1])
        #     pt2 = (line[2], line[3])
        #     draw_img = cut_img.copy()
        #     cv2.line(draw_img, pt1, pt2, (0, 0, 255), 3)
        max_health = 1.0
        if len(lines) > 0:
            max_health = 0.0
            for line in lines[0]:
                max_health = line[1] if line[1] > max_health else max_health
        percentage = 1.0 - (max_health / cut_img.shape[0])
        return percentage
