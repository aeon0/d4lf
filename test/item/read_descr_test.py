import time
import pytest
import cv2
from item.read_descr import read_descr
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.models import Item
from cam import Cam
from config import Config
from template_finder import stored_templates

# def read_descr(rarity: ItemRarity, img_item_descr: np.ndarray) -> Item:
BASE_PATH = "test/assets/item"


@pytest.mark.parametrize(
    "img_res, input_img, expected_item",
    [
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p.png",
            Item(
                ItemRarity.Rare,
                ItemType.Gloves,
                859,
                None,
                [
                    Affix("attack_speed", 8.4),
                    Affix("lucky_hit_chance", 9.4),
                    Affix("lucky_hit_up_to_a_chance_to_slow", 14.5),
                    Affix("ranks_of_flurry", 3),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p.png",
            Item(
                ItemRarity.Legendary,
                ItemType.Amulet,
                894,
                Aspect("frostbitten_aspect", 22),
                [
                    Affix("strength", 5.5),
                    Affix("imbuement_skill_damage", 28),
                    Affix("damage_with_ranged_weapons", 17),
                    Affix("damage_with_dualwielded_weapons", 16),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p_2.png",
            Item(
                ItemRarity.Rare,
                ItemType.Pants,
                844,
                None,
                [
                    Affix("potion_capacity", 3),
                    Affix("thorns", 873),
                    Affix("damage_reduction_from_close_enemies", 11),
                    Affix("imbuement_skill_cooldown_reduction", 5.8),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_material_1080p.png",
            Item(ItemRarity.Common, ItemType.Material),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_aspect_1080p.png",
            Item(ItemRarity.Legendary, ItemType.Material),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_sigil_1080p.png",
            Item(ItemRarity.Common, ItemType.Material),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_elixir_1080p.png",
            Item(ItemRarity.Magic, ItemType.Elixir),
        ),
        (
            (3840, 2160),
            f"{BASE_PATH}/read_descr_rare_2160p.png",
            Item(
                ItemRarity.Rare,
                ItemType.Ring,
                905,
                None,
                [
                    Affix("critical_strike_damage_with_bone_skills", 14),
                    Affix("blood_orb_healing", 15),
                    Affix("lucky_hit_chance", 4.8),
                    Affix("resource_generation", 9.5),
                ],
            ),
        ),
    ],
)
def test_read_descr(img_res: tuple[int, int], input_img: str, expected_item: Item):
    Cam().update_window_pos(0, 0, img_res[0], img_res[1])
    Config().load_data()
    stored_templates.cache_clear()
    img = cv2.imread(input_img)
    start = time.time()
    item = read_descr(expected_item.rarity, img)
    print("Runtime (read_descr()): ", time.time() - start)
    assert item == expected_item
