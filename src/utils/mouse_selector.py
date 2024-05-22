from logger import Logger
from template_finder import SearchResult, TemplateMatch
from utils.custom_mouse import mouse
from utils.misc import wait


def select_search_result(result: SearchResult | TemplateMatch, delay_factor: tuple[float, float] = (0.9, 1.1), click: str = "left") -> None:
    move_to_search_result(result, delay_factor)
    wait(0.05, 0.09)
    mouse.click(click)
    wait(0.05, 0.09)


def move_to_search_result(result: SearchResult | TemplateMatch, delay_factor: tuple[float, float] = (0.9, 1.1)) -> None:
    if isinstance(result, SearchResult):
        # default to first match
        match = result.matches[0]
    elif isinstance(result, TemplateMatch):
        match = result
    else:
        Logger.error(f"move_to_search_result: Invalid type {type(result)} for result")
        return
    mouse.move(*match.center_monitor, delay_factor=delay_factor)
