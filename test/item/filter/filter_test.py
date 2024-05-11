import pytest
from natsort import natsorted
from pytest_mock import MockerFixture

import test.item.filter.data.filters as filters
from config.models import AspectFilterType
from item.filter import Filter, FilterResult
from item.models import Item
from test.custom_fixtures import mock_ini_loader
from test.item.filter.data.affixes import affixes
from test.item.filter.data.aspects import aspects
from test.item.filter.data.sigils import sigils
from test.item.filter.data.uniques import uniques


def _create_mocked_filter(mocker: MockerFixture) -> Filter:
    filter_obj = Filter()
    filter_obj.files_loaded = True
    mocker.patch.object(filter_obj, "_did_files_change", return_value=False)
    return filter_obj


@pytest.mark.parametrize("name, result, item", natsorted(affixes), ids=[name for name, _, _ in natsorted(affixes)])
def test_affixes(name: str, result: list[str], item: Item, mocker: MockerFixture):
    test_filter = _create_mocked_filter(mocker)
    mocker.patch("item.filter.Filter._check_aspect", return_value=FilterResult(keep=False, matched=[]))
    test_filter.affix_filters = {filters.affix.name: filters.affix.Affixes}
    assert natsorted([match.profile for match in test_filter.should_keep(item).matched]) == natsorted(result)


@pytest.mark.parametrize("name, result, item", natsorted(aspects), ids=[name for name, _, _ in natsorted(aspects)])
def test_aspects_all(name: str, result: list[str], item: Item, mocker: MockerFixture, mock_ini_loader: MockerFixture):
    test_filter = _create_mocked_filter(mocker)
    mock_ini_loader._general.keep_aspects = AspectFilterType.all
    filter_res = test_filter.should_keep(item).matched
    assert len(filter_res) == 1 if AspectFilterType.all in result else len(filter_res) == 0


@pytest.mark.parametrize("name, result, item", natsorted(aspects), ids=[name for name, _, _ in natsorted(aspects)])
def test_aspects_none(name: str, result: list[str], item: Item, mocker: MockerFixture, mock_ini_loader: MockerFixture):
    test_filter = _create_mocked_filter(mocker)
    mock_ini_loader._general.keep_aspects = AspectFilterType.none
    filter_res = test_filter.should_keep(item).matched
    assert len(filter_res) == 0


@pytest.mark.parametrize("name, result, item", natsorted(aspects), ids=[name for name, _, _ in natsorted(aspects)])
def test_aspects_upgrade(name: str, result: list[str], item: Item, mocker: MockerFixture, mock_ini_loader: MockerFixture):
    test_filter = _create_mocked_filter(mocker)
    mock_ini_loader._general.keep_aspects = AspectFilterType.upgrade
    filter_res = test_filter.should_keep(item).matched
    assert len(filter_res) == 1 if AspectFilterType.upgrade in result else len(filter_res) == 0


@pytest.mark.parametrize("name, result, item", natsorted(sigils), ids=[name for name, _, _ in natsorted(sigils)])
def test_sigils(name: str, result: list[str], item: Item, mocker: MockerFixture):
    test_filter = _create_mocked_filter(mocker)
    test_filter.sigil_filters = {filters.sigil.name: filters.sigil.Sigils}
    assert natsorted([match.profile.split(".")[0] for match in test_filter.should_keep(item).matched]) == natsorted(result)


@pytest.mark.parametrize("name, result, item", natsorted(uniques), ids=[name for name, _, _ in natsorted(uniques)])
def test_uniques(name: str, result: list[str], item: Item, mocker: MockerFixture):
    test_filter = _create_mocked_filter(mocker)
    test_filter.unique_filters = {filters.unique.name: filters.unique.Uniques}
    assert natsorted([match.profile for match in test_filter.should_keep(item).matched]) == natsorted(result)
