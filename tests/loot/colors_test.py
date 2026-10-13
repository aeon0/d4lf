import typing

import pytest

from src import loot
from src.loot.colors import visible_missing_affixes
from src.settings import get_settings

if typing.TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_default_filter_colors_have_all_rendering_roles(monkeypatch) -> None:
    monkeypatch.setattr("src.loot.colors.get_settings", lambda: (_ for _ in ()).throw(RuntimeError()))
    colors = loot.get_filter_colors()
    assert colors.matched
    assert colors.no_match
    assert colors.processing


@pytest.mark.parametrize(
    ("limit", "expected"), [(0, []), (2, ["maximum_life", "armor"]), (5, ["maximum_life", "armor", "dexterity"])]
)
def test_visible_missing_affixes_keeps_profile_order_up_to_the_limit(
    limit: int, expected: list[str], mocker: MockerFixture
) -> None:
    mocker.patch.object(get_settings().advanced_options, "max_missing_affixes_shown", limit)

    assert visible_missing_affixes(["maximum_life", "armor", "dexterity"]) == expected
