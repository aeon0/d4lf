import time

import cv2
import pytest

from cam import Cam
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.descr.read_descr import read_descr
from item.models import Item

# def read_descr(rarity: ItemRarity, img_item_descr: np.ndarray) -> Item:
BASE_PATH = "test/assets/item"


@pytest.mark.parametrize(
    "img_res, input_img, expected_item",
    [
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_legendary_1440p.png",
            Item(
                affixes=[
                    Affix("physical_damage", 7.5),
                    Affix("damage_with_ranged_weapons", 7.5),
                    Affix("maximum_life", 273),
                    Affix("damage_reduction_from_close_enemies", 6.5),
                ],
                item_type=ItemType.ChestArmor,
                power=726,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_material_1080p.png",
            Item(item_type=ItemType.Material, rarity=ItemRarity.Common),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_aspect_1080p.png",
            Item(item_type=ItemType.Material, rarity=ItemRarity.Legendary),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_elixir_1080p.png",
            Item(item_type=ItemType.Elixir, rarity=ItemRarity.Magic),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_sigil_1080p.png",
            Item(
                affixes=[
                    Affix("lightning_damage", 15),
                    Affix("blood_blister"),
                    Affix("monster_poison_damage", 30),
                    Affix("monster_critical_resist", 3),
                    Affix("potion_breakers", 0.75),
                ],
                inherent=[Affix("wretched_delve")],
                item_type=ItemType.Sigil,
                power=89,
                rarity=ItemRarity.Common,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p.png",
            Item(
                affixes=[
                    Affix("intelligence", 88),
                    Affix("maximum_life", 828),
                    Affix("damage", 25),
                ],
                inherent=[Affix("lucky_hit_chance", 10.0)],
                item_type=ItemType.Wand,
                power=925,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p_2.png",
            Item(
                affixes=[
                    Affix("all_stats", 18),
                    Affix("intelligence", 42),
                    Affix("movement_speed", 17.5),
                    Affix("fortify_generation", 21.5),
                ],
                inherent=[Affix("evade_grants_movement_speed_for_second", 50.0)],
                item_type=ItemType.Boots,
                power=925,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p_3.png",
            Item(
                affixes=[
                    Affix("willpower", 82),
                    Affix("critical_strike_damage", 25),
                    Affix("overpower_damage", 87),
                    Affix("damage_to_close_enemies", 26),
                ],
                inherent=[Affix("overpower_damage", 75)],
                item_type=ItemType.Mace2H,
                power=704,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p_4.png",
            Item(
                affixes=[
                    Affix("intelligence", 83),
                    Affix("maximum_life", 728),
                    Affix("damage", 20),
                ],
                inherent=[Affix("lucky_hit_chance", 10.0)],
                item_type=ItemType.Wand,
                power=910,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p_5.png",
            Item(
                affixes=[
                    Affix("maximum_life", 666),
                    Affix("damage", 45),
                    Affix("vulnerable_damage", 31),
                ],
                inherent=[Affix("lucky_hit_chance", 10.0)],
                item_type=ItemType.Wand,
                power=925,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (3840, 1600),
            f"{BASE_PATH}/read_descr_legendary_1600p.png",
            Item(
                affixes=[
                    Affix("vulnerable_damage", 8),
                    Affix("damage_to_close_enemies", 9),
                    Affix("damage_to_crowd_controlled_enemies", 4),
                    Affix("barrier_generation", 5.5),
                ],
                inherent=[Affix("resistance_to_all_elements", 2.9), Affix("shadow_resistance", 2.9)],
                item_type=ItemType.Ring,
                power=426,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (3840, 2160),
            f"{BASE_PATH}/read_descr_codex_upgrade_2160p.png",
            Item(
                codex_upgrade=True,
                item_type=ItemType.Helm,
                power=920,
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/upgrade_aspect_codex_1440p.png",
            Item(
                affixes=[
                    Affix("intelligence", 90),
                    Affix("life_per_second", 87),
                    Affix("fire_resistance", 38),
                ],
                item_type=ItemType.ChestArmor,
                power=823,
                rarity=ItemRarity.Legendary,
                codex_upgrade=True,
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/upgrade_aspect_codex_1440p_2.png",
            Item(
                affixes=[
                    Affix("strength", 86),
                    Affix("maximum_life", 394),
                    Affix("damage_over_time", 57),
                ],
                inherent=[Affix("critical_strike_damage", 17.5)],
                item_type=ItemType.Sword,
                power=804,
                rarity=ItemRarity.Legendary,
                codex_upgrade=True,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/upgrade_aspect_codex_1080p.png",
            Item(
                affixes=[
                    Affix("intelligence", 46),
                    Affix("maximum_life", 25),
                    Affix("essence_on_kill", 2),
                ],
                inherent=[Affix("critical_strike_damage", 9)],
                item_type=ItemType.Sword2H,
                power=254,
                rarity=ItemRarity.Legendary,
                codex_upgrade=True,
            ),
        ),
        (
            (3840, 2160),
            f"{BASE_PATH}/temper_manual_2160p.png",
            Item(
                item_type=ItemType.TemperManual,
                rarity=ItemRarity.Magic,
            ),
        ),
    ],
)
def test_read_descr(img_res: tuple[int, int], input_img: str, expected_item: Item):
    Cam().update_window_pos(0, 0, *img_res)
    img = cv2.imread(input_img)
    start = time.time()
    item = read_descr(expected_item.rarity, img)
    print("Runtime (read_descr()): ", time.time() - start)
    assert item == expected_item
