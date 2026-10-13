import logging
import queue
import typing
from typing import cast
from unittest.mock import Mock

if typing.TYPE_CHECKING:
    import pytest
    from pytest_mock import MockerFixture

    from src.loot.highlighting import HighlightTask, _VisionModeWithHighlighting

from src.item import FilterResult, Item, MatchedFilter
from src.loot.highlighting_render import HighlightingRenderer
from src.perception import LocatedMarker, LocatorResult


class _RendererHarness(HighlightingRenderer):
    root: Mock
    canvas: Mock
    thick: int
    screen_off_x: int
    screen_off_y: int
    queue: queue.Queue[HighlightTask]
    current_item: Item | None
    is_cleared: bool


def test_highlighting_renderer_places_reliable_affix_markers(monkeypatch, mocker: MockerFixture) -> None:
    renderer = _RendererHarness()
    renderer.root = mocker.Mock()
    renderer.canvas = mocker.Mock()
    renderer.thick = 4
    renderer.screen_off_x = 0
    renderer.screen_off_y = 0
    monkeypatch.setattr(renderer, "create_signal_rect", mocker.Mock())
    monkeypatch.setattr(renderer, "draw_text", mocker.Mock(side_effect=lambda *_args: 1))
    draw_rect = Mock()
    monkeypatch.setattr(renderer, "draw_rect", draw_rect)
    cast("_VisionModeWithHighlighting", renderer).draw_match_outline(
        (10, 20, 100, 200),
        FilterResult(keep=True, matched=[MatchedFilter("Build")]),
        LocatorResult([LocatedMarker("affix", 0, (30, 40), 0.99)], reliable=True),
    )
    draw_rect.assert_called_once_with(renderer.canvas, 12, (30, 40), 10, "#23fc5d")


def test_draw_from_queue_reschedules_and_logs_when_drawing_fails(
    monkeypatch, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    item = Item(name="helm")
    renderer = _RendererHarness()
    renderer.canvas = mocker.Mock()
    renderer.queue = queue.Queue()
    renderer.current_item = item
    renderer.is_cleared = True
    renderer.queue.put(("match", item, (0, 0, 10, 10), FilterResult(keep=True, matched=[]), None))
    monkeypatch.setattr(renderer, "draw_match_outline", mocker.Mock(side_effect=RuntimeError("boom")))

    with caplog.at_level(logging.ERROR, logger="src.loot.highlighting_render"):
        cast("_VisionModeWithHighlighting", renderer).draw_from_queue()

    renderer.canvas.after.assert_called_once_with(10, renderer.draw_from_queue)
    assert "Error while drawing highlighting overlay" in caplog.text
    assert "boom" in caplog.text


def test_draw_from_queue_reschedules_when_queue_is_empty(mocker: MockerFixture) -> None:
    renderer = _RendererHarness()
    renderer.canvas = mocker.Mock()
    renderer.queue = queue.Queue()

    cast("_VisionModeWithHighlighting", renderer).draw_from_queue()

    renderer.canvas.after.assert_called_once_with(10, renderer.draw_from_queue)
