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
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p.png",
            Item(
                affixes=[
                    Affix("attack_speed", 8.4),
                    Affix("lucky_hit_chance", 9.4),
                    Affix("lucky_hit_up_to_a_chance_to_slow", 14.5),
                    Affix("ranks_of_flurry", 3),
                ],
                item_type=ItemType.Gloves,
                power=859,
                rarity=ItemRarity.Rare,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p.png",
            Item(
                affixes=[
                    Affix("strength", 5.5),
                    Affix("imbuement_skill_damage", 28),
                    Affix("damage_with_ranged_weapons", 17),
                    Affix("damage_with_dualwielded_weapons", 16),
                ],
                aspect=Aspect("frostbitten", 22),
                inherent=[Affix("resistance_to_all_elements", 19.0)],
                item_type=ItemType.Amulet,
                power=894,
                rarity=ItemRarity.Legendary,
            ),
        ),
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
                aspect=Aspect("snap_frozen", 197),
                item_type=ItemType.ChestArmor,
                power=726,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_legendary_1440p_2.png",
            Item(
                affixes=[
                    Affix("damage_over_time", 14),
                    Affix("basic_skill_damage", 39),
                    Affix("damage_to_crowd_controlled_enemies", 13),
                    Affix("damage_to_poisoned_enemies", 9),
                ],
                aspect=Aspect("of_the_stampede", 26),
                inherent=[Affix("overpower_damage", 62)],
                item_type=ItemType.Mace2H,
                power=600,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p_2.png",
            Item(
                affixes=[
                    Affix("potion_capacity", 3),
                    Affix("thorns", 873),
                    Affix("damage_reduction_from_close_enemies", 11),
                    Affix("imbuement_skill_cooldown_reduction", 5.8),
                ],
                inherent=[Affix("while_injured_your_potion_also_restores_resource", 20)],
                item_type=ItemType.Legs,
                power=844,
                rarity=ItemRarity.Rare,
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
            (3840, 2160),
            f"{BASE_PATH}/read_descr_rare_2160p.png",
            Item(
                affixes=[
                    Affix("critical_strike_damage_with_bone_skills", 14),
                    Affix("blood_orb_healing", 15),
                    Affix("lucky_hit_chance", 4.8),
                    Affix("resource_generation", 9.5),
                ],
                inherent=[Affix("resistance_to_all_elements", 8.0), Affix("shadow_resistance", 8.0)],
                item_type=ItemType.Ring,
                power=905,
                rarity=ItemRarity.Rare,
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_rare_1440p.png",
            Item(
                affixes=[
                    Affix("strength", 7.3),
                    Affix("damage_reduction_while_fortified", 8.5),
                    Affix("slow_duration_reduction", 18.5),
                    Affix("ranks_of_the_crushing_earth_passive", 1),
                ],
                inherent=[Affix("resistance_to_all_elements", 14.7)],
                item_type=ItemType.Amulet,
                power=823,
                rarity=ItemRarity.Rare,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_unique_1080p.png",
            Item(
                affixes=[
                    Affix("movement_speed", 10.5),
                    Affix("crackling_energy_damage", 24),
                    Affix("cooldown_reduction", 5.2),
                    Affix("ranks_of_the_shocking_impact_passive", 2),
                ],
                aspect=Aspect("esadoras_overflowing_cameo", 4781),
                inherent=[Affix("resistance_to_all_elements", 19)],
                item_type=ItemType.Amulet,
                power=896,
                rarity=ItemRarity.Unique,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_unique_1080p_2.png",
            Item(
                affixes=[
                    Affix("critical_strike_damage_with_bone_skills", 26.2),
                    Affix("physical_damage", 22.5),
                    Affix("maximum_essence", 18),
                    Affix("damage_reduction", 9.4),
                ],
                aspect=Aspect("deathless_visage", 2254),
                item_type=ItemType.Helm,
                power=942,
                rarity=ItemRarity.Unique,
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
                aspect=Aspect("ghostwalker", 13),
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
                aspect=Aspect("lightning_dancers", 1915),
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
                    Affix("lightning_critical_strike_damage", 19),
                    Affix("ultimate_skill_damage", 14.5),
                    Affix("damage_to_crowd_controlled_enemies", 6.5),
                    Affix("lucky_hit_up_to_a_chance_to_execute_injured_nonelites", 10),
                ],
                aspect=Aspect("accelerating", 19),
                inherent=[Affix("overpower_damage", 52.5)],
                item_type=ItemType.Mace,
                power=886,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p_5.png",
            Item(
                affixes=[
                    Affix("lightning_resistance", 31),
                    Affix("damage_reduction_while_injured", 18.5),
                    Affix("dodge_chance", 4.8),
                    Affix("control_impaired_duration_reduction", 10.5),
                ],
                aspect=Aspect("protecting", 3),
                inherent=[Affix("while_injured_your_potion_also_grants_movement_speed_for_seconds", 30)],
                item_type=ItemType.Legs,
                power=858,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_legendary_1080p_6.png",
            Item(
                affixes=[
                    Affix("overpower_damage", 51),
                    Affix("ultimate_skill_damage", 14),
                    Affix("damage_to_slowed_enemies", 21.5),
                    Affix("damage_to_enemies_affected_by_trap_skills", 9.5),
                ],
                aspect=Aspect("icy_alchemists", 2325),
                inherent=[Affix("damage_to_close_enemies", 20)],
                item_type=ItemType.Dagger,
                power=833,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_rare_1440p_2.png",
            Item(
                affixes=[
                    Affix("attack_speed", 4.8),
                    Affix("lucky_hit_up_to_a_chance_to_restore_primary_resource", 14),
                    Affix("ranks_of_hammer_of_the_ancients", 3),
                    Affix("ranks_of_upheaval", 2),
                ],
                item_type=ItemType.Gloves,
                power=908,
                rarity=ItemRarity.Rare,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p_3.png",
            Item(
                affixes=[
                    Affix("basic_skill_damage", 36),
                    Affix("ultimate_skill_damage", 20),
                    Affix("damage_to_slowed_enemies", 19),
                ],
                inherent=[Affix("overpower_damage", 62)],
                item_type=ItemType.Mace2H,
                power=513,
                rarity=ItemRarity.Rare,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p_4.png",
            Item(
                affixes=[
                    Affix("dexterity", 31),
                    Affix("total_armor", 17.5),
                    Affix("maximum_life", 840),
                    Affix("ranks_of_poison_imbuement", 3),
                ],
                item_type=ItemType.Helm,
                power=916,
                rarity=ItemRarity.Rare,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_rare_1080p_5.png",
            Item(
                affixes=[
                    Affix("critical_strike_damage", 29.0),
                    Affix("core_skill_damage", 28),
                    Affix("ultimate_skill_damage", 29),
                ],
                inherent=[Affix("overpower_damage", 75)],
                item_type=ItemType.Mace2H,
                power=628,
                rarity=ItemRarity.Rare,
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
                aspect=Aspect("rapid", 19),
                inherent=[Affix("resistance_to_all_elements", 2.9), Affix("shadow_resistance", 2.9)],
                item_type=ItemType.Ring,
                power=426,
                rarity=ItemRarity.Legendary,
            ),
        ),
        (
            (1920, 1080),
            f"{BASE_PATH}/read_descr_unique_1080p_3.png",
            Item(
                aspect=Aspect("razorplate", 11197),
                item_type=ItemType.ChestArmor,
                power=804,
                rarity=ItemRarity.Unique,
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_rare_1440p_3.png",
            Item(
                affixes=[
                    Affix("critical_strike_damage", 23),
                    Affix("critical_strike_damage_with_werewolf_skills", 28),
                    Affix("ultimate_skill_damage", 29),
                    Affix("damage_to_crowd_controlled_enemies", 14),
                ],
                inherent=[Affix("overpower_damage", 75)],
                item_type=ItemType.Mace2H,
                power=700,
                rarity=ItemRarity.Rare,
            ),
        ),
        (
            (2560, 1440),
            f"{BASE_PATH}/read_descr_rare_1440p_4.png",
            Item(
                affixes=[
                    Affix("lightning_critical_strike_damage", 10.5),
                    Affix("critical_strike_damage_with_werewolf_skills", 11),
                    Affix("overpower_damage_with_werebear_skills", 40.5),
                    Affix("ultimate_skill_damage", 13),
                ],
                inherent=[Affix("overpower_damage", 37.5)],
                item_type=ItemType.Mace,
                power=663,
                rarity=ItemRarity.Rare,
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
    ],
)
def test_read_descr(img_res: tuple[int, int], input_img: str, expected_item: Item):
    Cam().update_window_pos(0, 0, *img_res)
    img = cv2.imread(input_img)
    start = time.time()
    item = read_descr(expected_item.rarity, img)
    print("Runtime (read_descr()): ", time.time() - start)
    assert item == expected_item
