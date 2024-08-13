import cv2
import pytest

from src.cam import Cam
from src.config import BASE_DIR
from src.item.data.affix import Affix, AffixType
from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.item.descr.read_descr import read_descr
from src.item.models import Item

BASE_PATH = BASE_DIR / "tests/assets/item"

legendary = [
    (
        (2560, 1440),
        f"{BASE_PATH}/unknown/read_descr_codex_upgrade_1440p.png",
        Item(
            affixes=[
                Affix(name="intelligence", value=90),
                Affix(name="life_per_second", value=87),
                Affix(name="fire_resistance", value=38),
            ],
            codex_upgrade=True,
            item_type=ItemType.ChestArmor,
            power=823,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (2560, 1440),
        f"{BASE_PATH}/unknown/read_descr_codex_upgrade_1440p_2.png",
        Item(
            affixes=[Affix(name="strength", value=86), Affix(name="maximum_life", value=394), Affix(name="damage_over_time", value=57)],
            codex_upgrade=True,
            inherent=[Affix(name="critical_strike_damage", value=17.5, type=AffixType.inherent)],
            item_type=ItemType.Sword,
            power=804,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (3840, 2160),
        f"{BASE_PATH}/unknown/read_descr_codex_upgrade_2160p.png",
        Item(
            affixes=[
                Affix(name="intelligence", value=76),
                Affix(name="life_per_second", value=114),
                Affix(name="cooldown_reduction", value=7),
            ],
            codex_upgrade=True,
            item_type=ItemType.Helm,
            power=920,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (1920, 1080),
        f"{BASE_PATH}/unknown/read_descr_legendary_1080p.png",
        Item(
            affixes=[Affix(name="intelligence", value=88), Affix(name="maximum_life", value=828), Affix(name="damage", value=25)],
            inherent=[Affix(name="lucky_hit_chance", value=10.0, type=AffixType.inherent)],
            item_type=ItemType.Wand,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (1920, 1080),
        f"{BASE_PATH}/unknown/read_descr_legendary_1080p_2.png",
        Item(
            affixes=[
                Affix(name="all_stats", value=18),
                Affix(name="intelligence", value=42),
                Affix(name="movement_speed", value=17.5),
                Affix(name="fortify_generation", value=21.5),
            ],
            inherent=[Affix(name="evade_grants_movement_speed_for_second", value=50.0, type=AffixType.inherent)],
            item_type=ItemType.Boots,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (1920, 1080),
        f"{BASE_PATH}/unknown/read_descr_legendary_1080p_4.png",
        Item(
            affixes=[Affix(name="intelligence", value=83), Affix(name="maximum_life", value=728), Affix(name="damage", value=20)],
            inherent=[Affix(name="lucky_hit_chance", value=10.0, type=AffixType.inherent)],
            item_type=ItemType.Wand,
            power=910,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (1920, 1080),
        f"{BASE_PATH}/unknown/read_descr_legendary_1080p_7.png",
        Item(
            affixes=[
                Affix(name="maximum_life", value=1591),
                Affix(name="energy_on_kill", value=4),
                Affix(name="critical_strike_damage", value=150, type=AffixType.greater),
            ],
            inherent=[Affix(name="vulnerable_damage", value=32, type=AffixType.inherent)],
            item_type=ItemType.Crossbow2H,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (1920, 1080),
        f"{BASE_PATH}/unknown/read_descr_legendary_1080p_8.png",
        Item(
            affixes=[
                Affix(name="maximum_life", value=1591),
                Affix(name="energy_on_kill", value=4),
                Affix(name="critical_strike_damage", value=150, type=AffixType.greater),
            ],
            inherent=[Affix(name="vulnerable_damage", value=32, type=AffixType.inherent)],
            item_type=ItemType.Crossbow2H,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (2560, 1440),
        f"{BASE_PATH}/unknown/read_descr_legendary_1440p.png",
        Item(
            affixes=[
                Affix(name="physical_damage", value=7.5),
                Affix(name="damage_with_ranged_weapons", value=7.5),
                Affix(name="maximum_life", value=273),
                Affix(name="damage_reduction_from_close_enemies", value=6.5),
            ],
            item_type=ItemType.ChestArmor,
            power=726,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (2560, 1440),
        f"{BASE_PATH}/unknown/read_descr_legendary_1440p_2.png",
        Item(
            affixes=[
                Affix(name="intelligence", value=178),
                Affix(name="life_on_hit", value=38),
                Affix(name="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=19),
            ],
            inherent=[Affix(name="life_on_kill", value=228, type=AffixType.inherent)],
            item_type=ItemType.Scythe2H,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (2560, 1440),
        f"{BASE_PATH}/unknown/read_descr_legendary_1440p_3.png",
        Item(
            affixes=[
                Affix(name="intelligence", value=60),
                Affix(name="maximum_life", value=233),
                Affix(name="resistance_to_all_elements", value=7),
            ],
            item_type=ItemType.Legs,
            power=700,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (2560, 1440),
        f"{BASE_PATH}/unknown/read_descr_legendary_1440p_4.png",
        Item(
            affixes=[Affix(name="strength", value=87), Affix(name="maximum_life", value=767), Affix(name="lucky_hit_chance", value=6.5)],
            item_type=ItemType.Gloves,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        (3840, 1600),
        f"{BASE_PATH}/unknown/read_descr_legendary_1600p.png",
        Item(
            affixes=[
                Affix(name="vulnerable_damage", value=8),
                Affix(name="damage_to_close_enemies", value=9),
                Affix(name="damage_to_crowd_controlled_enemies", value=4),
                Affix(name="barrier_generation", value=5.5),
            ],
            inherent=[
                Affix(name="resistance_to_all_elements", value=2.9, type=AffixType.inherent),
                Affix(name="shadow_resistance", value=2.9, type=AffixType.inherent),
            ],
            item_type=ItemType.Ring,
            power=426,
            rarity=ItemRarity.Legendary,
        ),
    ),
]

material = [
    ((1920, 1080), f"{BASE_PATH}/unknown/read_descr_elixir_1080p.png", Item(item_type=ItemType.Elixir, rarity=ItemRarity.Magic)),
    ((1920, 1080), f"{BASE_PATH}/unknown/read_descr_material_1080p.png", Item(item_type=ItemType.Material, rarity=ItemRarity.Common)),
    (
        (3840, 2160),
        f"{BASE_PATH}/unknown/read_descr_temper_manual_2160p.png",
        Item(item_type=ItemType.TemperManual, rarity=ItemRarity.Magic),
    ),
]

sigil = [
    (
        (2560, 1440),
        f"{BASE_PATH}/unknown/read_descr_sigil_1440p_2.png",
        Item(
            affixes=[Affix(name="extra_shrines"), Affix(name="avenger")],
            inherent=[Affix(name="serpents_lair", type=AffixType.inherent)],
            item_type=ItemType.Sigil,
            power=76,
            rarity=ItemRarity.Common,
        ),
    ),
]


def _run_test_helper(img_res: tuple[int, int], input_img: str, expected_item: Item):
    Cam().update_window_pos(0, 0, *img_res)
    img = cv2.imread(input_img)
    item = read_descr(expected_item.rarity, img)
    assert item == expected_item


@pytest.mark.parametrize(("img_res", "input_img", "expected_item"), legendary)
def test_legendary(img_res: tuple[int, int], input_img: str, expected_item: Item):
    _run_test_helper(img_res=img_res, input_img=input_img, expected_item=expected_item)


@pytest.mark.parametrize(("img_res", "input_img", "expected_item"), material)
def test_material(img_res: tuple[int, int], input_img: str, expected_item: Item):
    _run_test_helper(img_res=img_res, input_img=input_img, expected_item=expected_item)


@pytest.mark.parametrize(("img_res", "input_img", "expected_item"), sigil)
def test_sigil(img_res: tuple[int, int], input_img: str, expected_item: Item):
    _run_test_helper(img_res=img_res, input_img=input_img, expected_item=expected_item)
