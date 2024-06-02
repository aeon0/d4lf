import pytest
from pytest_mock import MockerFixture

from src.dataloader import Dataloader
from src.gui.importer.mobalytics import import_mobalytics

URLS = [
    "https://mobalytics.gg/diablo-4/builds/barbarian/barbarian-leveling-guide",
    "https://mobalytics.gg/diablo-4/builds/barbarian/bash?coreTab=assigned-skills&equipmentTab=aspects-and-uniques&variantTab=1",
    "https://mobalytics.gg/diablo-4/builds/barbarian/bash?coreTab=assigned-skills&equipmentTab=aspects-and-uniques&variantTab=2",
    "https://mobalytics.gg/diablo-4/builds/barbarian/ron-array-bash-fury-barb?coreTab=assigned-skills&equipmentTab=aspects-and-uniques&variantTab=0",
    "https://mobalytics.gg/diablo-4/builds/druid/screamhearts-quickshift-tornado",
    "https://mobalytics.gg/diablo-4/builds/druid/wind-shear",
    "https://mobalytics.gg/diablo-4/builds/druid/wind-shear?coreTab=assigned-skills&equipmentTab=aspects-and-uniques&variantTab=1",
    "https://mobalytics.gg/diablo-4/builds/necromancer/p4wnyhof-golem-slammer",
    "https://mobalytics.gg/diablo-4/builds/necromancer/ramping-minions",
    "https://mobalytics.gg/diablo-4/builds/rogue/heartseeker",
    "https://mobalytics.gg/diablo-4/builds/sorcerer/firewall-scorched-earth",
    "https://mobalytics.gg/diablo-4/builds/sorcerer/kripp-s-ultimate-fire-sorc",
    "https://mobalytics.gg/diablo-4/builds/sorcerer/nicktew-s4-blizzard",
]


@pytest.mark.parametrize("url", URLS)
@pytest.mark.requests()
def test_import_mobalytics(url: str, mock_ini_loader: MockerFixture, mocker: MockerFixture):
    Dataloader()  # need to load data first or the mock will make it impossible
    mocker.patch("builtins.open", new=mocker.mock_open())
    import_mobalytics(url=url)
