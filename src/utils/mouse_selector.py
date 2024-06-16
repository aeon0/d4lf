import logging
import time

from src.template_finder import SearchResult, TemplateMatch
from src.utils.custom_mouse import mouse

LOGGER = logging.getLogger(__name__)


def select_search_result(result: SearchResult | TemplateMatch, delay_factor: tuple[float, float] = (0.9, 1.1), click: str = "left") -> None:
    move_to_search_result(result, delay_factor)
    time.sleep(0.05)
    mouse.click(click)
    time.sleep(0.05)


def move_to_search_result(result: SearchResult | TemplateMatch, delay_factor: tuple[float, float] = (0.9, 1.1)) -> None:
    if isinstance(result, SearchResult):
        # default to first match
        match = result.matches[0]
    elif isinstance(result, TemplateMatch):
        match = result
    else:
        LOGGER.error(f"move_to_search_result: Invalid type {type(result)} for result")
        return
    mouse.move(*match.center_monitor, delay_factor=delay_factor)
