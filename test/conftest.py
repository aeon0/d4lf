import pytest
from pytest_mock import MockerFixture

from config.loader import IniConfigLoader


@pytest.fixture()
def mock_ini_loader(mocker: MockerFixture):
    mocker.patch.object(IniConfigLoader(), "_loaded", True)
    general_mock = mocker.patch.object(IniConfigLoader(), "_general")
    general_mock.language = "enUS"
    return IniConfigLoader()
