import typing

import pytest
from natsort import natsorted

from src.item import Affix, FilterResult, Item
from src.profiles import AffixFilterCountModel, AffixFilterModel
from src.settings import AspectFilterType, get_settings

from .conftest import _create_mocked_filter, aspects, charms, filters, seals

if typing.TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.parametrize(
    ("_name", "result", "item"), natsorted(aspects), ids=[name for name, _, _ in natsorted(aspects)]
)
def test_aspects(_name: str, result: list[str], item: Item, mocker: MockerFixture) -> None:
    test_filter = _create_mocked_filter(mocker)
    mocker.patch.object(get_settings().general, "keep_aspects", AspectFilterType.upgrade)
    mocker.patch.object(test_filter, "_check_affixes", return_value=FilterResult(keep=False, matched=[]))
    test_filter.aspect_upgrade_filters = {filters.aspects_filters.name: filters.aspects_filters.aspect_upgrades}
    assert natsorted([match.profile for match in test_filter.should_keep(item).matched]) == natsorted(result)


@pytest.mark.parametrize(("_name", "result", "item"), natsorted(seals), ids=[name for name, _, _ in natsorted(seals)])
def test_seals(_name: str, result: list[str], item: Item, mocker: MockerFixture) -> None:
    test_filter = _create_mocked_filter(mocker)
    test_filter.seal_filters = {filters.seal_charm.name: filters.seal_charm.seals}
    matches = test_filter.should_keep(item).matched
    assert natsorted([match.profile for match in matches]) == natsorted(result)
    for match in matches:
        if match.profile.startswith("seal_charm.Seals."):
            assert match.matched_affixes


@pytest.mark.parametrize(("_name", "result", "item"), natsorted(charms), ids=[name for name, _, _ in natsorted(charms)])
def test_charms(_name: str, result: list[str], item: Item, mocker: MockerFixture) -> None:
    test_filter = _create_mocked_filter(mocker)
    test_filter.charm_filters = {filters.seal_charm.name: filters.seal_charm.charms}
    matches = test_filter.should_keep(item).matched
    assert natsorted([match.profile for match in matches]) == natsorted(result)
    for match in matches:
        if match.profile in {"seal_charm.Charms.basic_magic", "seal_charm.Charms.speed"}:
            assert match.matched_affixes
        if match.profile == "seal_charm.Charms.wanted_set":
            assert match.set_match
        if match.profile == "seal_charm.Charms.wanted_unique_aspect":
            assert match.aspect_match


@pytest.mark.parametrize(
    ("expected_names", "max_count", "item_names", "missing"),
    [
        (["dexterity", "armor", "maximum_life"], 3, ["dexterity", "armor"], ["maximum_life"]),
        (["dexterity", "armor", "maximum_life"], 2, ["dexterity", "armor", "maximum_life"], []),
        (["armor", "armor"], 2, ["armor", "dexterity"], ["armor"]),
    ],
    ids=["absent_affix", "present_affix_beyond_max_count", "duplicate_requirement"],
)
def test_missing_affix_names(
    expected_names: list[str], max_count: int, item_names: list[str], missing: list[str], mocker: MockerFixture
) -> None:
    pool = [
        AffixFilterCountModel(
            count=[AffixFilterModel(name=name) for name in expected_names], min_count=1, max_count=max_count
        )
    ]
    item_affixes = [Affix(name=name) for name in item_names]

    assert _create_mocked_filter(mocker)._missing_affix_names(pool, item_affixes) == missing
