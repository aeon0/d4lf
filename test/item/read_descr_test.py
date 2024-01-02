import time
import pytest
import cv2
from item.descr.read_descr import read_descr
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
                [
                    Affix("resistance_to_all_elements", 19.0),
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
                [
                    Affix("injured_potion_resource", 20),
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
            f"{BASE_PATH}/read_descr_elixir_1080p.png",
            Item(ItemRarity.Magic, ItemType.Elixir),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_sigil_1080p.png",
            Item(
                ItemRarity.Common,
                ItemType.Sigil,
                100,
                None,
                [
                    Affix("lightning_damage", 15),
                    Affix("death_pulse"),
                    Affix("monster_lightning_damage", 20),
                    Affix("monster_life", 30),
                    Affix("potion_breakers", 0.75),
                ],
                [
                    Affix("tormented_ruins"),
                    Affix("revives_allowed", 4),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_sigil_1080p_2.png",
            Item(
                ItemRarity.Common,
                ItemType.Sigil,
                100,
                None,
                [
                    Affix("lightning_damage", 15),
                    Affix("drifting_shade"),
                    Affix("monster_lightning_damage", 20),
                    Affix("monster_critical_resist", 3),
                    Affix("unstoppable_monsters", 30),
                ],
                [
                    Affix("crusaders_cathedral"),
                    Affix("revives_allowed", 4),
                ],
            ),
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
                [
                    Affix("resistance_to_all_elements", 8.0),
                    Affix("shadow_resistance", 8.0),
                ],
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_rare_1440p.png",
            Item(
                ItemRarity.Rare,
                ItemType.Amulet,
                823,
                None,
                [
                    Affix("strength", 7.3),
                    Affix("damage_reduction_while_fortified", 8.5),
                    Affix("slow_duration_reduction", 18.5),
                    Affix("ranks_of_the_crushing_earth_passive", 1),
                ],
                [
                    Affix("resistance_to_all_elements", 14.7),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_unique_1080p.png",
            Item(
                ItemRarity.Unique,
                ItemType.Amulet,
                896,
                Aspect("esadoras_overflowing_cameo", 4781),
                [
                    Affix("movement_speed", 10.5),
                    Affix("crackling_energy_damage", 24),
                    Affix("cooldown_reduction", 5.2),
                    Affix("ranks_of_the_shocking_impact_passive", 2),
                ],
                [
                    Affix("resistance_to_all_elements", 19),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_unique_1080p_2.png",
            Item(
                ItemRarity.Unique,
                ItemType.Helm,
                942,
                Aspect("deathless_visage", 2254),
                [
                    Affix("critical_strike_damage_with_bone_skills", 26.2),
                    Affix("physical_damage", 22.5),
                    Affix("maximum_essence", 18),
                    Affix("damage_reduction", 9.4),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p_2.png",
            Item(
                ItemRarity.Legendary,
                ItemType.Boots,
                925,
                Aspect("ghostwalker_aspect", 13),
                [
                    Affix("all_stats", 18),
                    Affix("intelligence", 42),
                    Affix("movement_speed", 17.5),
                    Affix("fortify_generation", 21.5),
                ],
                [Affix("evade_grants_movement_speed", 50)],
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_rare_1440p_2.png",
            Item(
                ItemRarity.Rare,
                ItemType.Gloves,
                908,
                None,
                [
                    Affix("attack_speed", 4.8),
                    Affix("lucky_hit_up_to_a_chance_to_restore_primary_resource", 14),
                    Affix("ranks_of_hammer_of_the_ancients", 3),
                    Affix("ranks_of_upheaval", 2),
                ],
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p_3.png",
            Item(
                ItemRarity.Rare,
                ItemType.Mace2H,
                513,
                None,
                [
                    Affix("basic_skill_damage", 36),
                    Affix("ultimate_skill_damage", 20),
                    Affix("damage_to_slowed_enemies", 19),
                ],
                [
                    Affix("overpower_damage", 62),
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
