import typing
from typing import cast
from unittest.mock import Mock

if typing.TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from src.loot.highlighting import _VisionModeWithHighlighting

from src.item import Affix, FilterResult, MatchedFilter
from src.loot.highlighting_render import HighlightingRenderer
from src.perception import LocatedMarker, LocatorResult


class _RendererHarness(HighlightingRenderer):
    root: Mock
    canvas: Mock
    thick: int
    screen_off_x: int
    screen_off_y: int


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


def test_highlighting_renderer_shows_missing_affixes_in_one_line_under_their_profile(
    monkeypatch, mocker: MockerFixture
) -> None:
    renderer = _RendererHarness()
    renderer.root = mocker.Mock()
    renderer.canvas = mocker.Mock()
    renderer.thick = 4
    renderer.screen_off_x = 0
    renderer.screen_off_y = 0
    monkeypatch.setattr(renderer, "create_signal_rect", mocker.Mock())
    drawn: list[tuple[str, str]] = []

    def _record_text(_canvas: Mock, text: str, color: str, text_y: int, _offset: int, _center: int) -> int:
        drawn.append((text, color))
        return text_y - 1

    monkeypatch.setattr(renderer, "draw_text", _record_text)
    cast("_VisionModeWithHighlighting", renderer).draw_match_outline(
        (10, 20, 100, 200),
        FilterResult(
            keep=True,
            matched=[
                MatchedFilter("Build.Helm", [Affix(name="armor")], missing_affixes=["maximum_life", "dexterity"]),
                MatchedFilter("Other.Helm", [Affix(name="armor")]),
            ],
        ),
        None,
    )

    top_to_bottom = list(reversed(drawn))
    assert top_to_bottom == [
        ("Build.Helm", "#23fc5d"),
        ("missing: maximum_life, dexterity", "#8b2e2e"),
        ("Other.Helm", "#23fc5d"),
    ]
