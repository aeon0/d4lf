import cv2
import pytest

from src.cam import Cam
from src.config import BASE_DIR
from src.item.data.affix import Affix, AffixType
from src.item.data.aspect import Aspect
from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.item.descr.read_descr import read_descr
from src.item.models import Item

BASE_PATH = BASE_DIR / "tests/assets/item/season5"

items = [
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_1_2160p_medium.png",
        item1 := Item(
            affixes=[
                Affix(name="intelligence", value=101, type=AffixType.rerolled),
                Affix(name="maximum_life", value=1155),
                Affix(name="maximum_resource", value=10),
                Affix(name="lucky_hit_up_to_a_chance_to_stun_for_seconds", value=17.2, type=AffixType.tempered),
                Affix(name="to_warmth", value=1, type=AffixType.tempered),
            ],
            inherent=[],
            item_type=ItemType.Helm,
            power=914,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_1_2160p_small.png", item1),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_2_2160p_medium.png",
        item2 := Item(
            affixes=[
                Affix(name="intelligence", value=87),
                Affix(name="maximum_life", value=1441, type=AffixType.greater),
                Affix(name="mana_per_second", value=6, type=AffixType.rerolled),
                Affix(name="lucky_hit_up_to_a_chance_to_stun_for_seconds", value=15.5, type=AffixType.tempered),
                Affix(name="to_warmth", value=2, type=AffixType.tempered),
            ],
            inherent=[],
            item_type=ItemType.ChestArmor,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_2_2160p_small.png", item2),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_3_2160p_medium.png",
        item3 := Item(
            affixes=[
                Affix(name="intelligence", value=90),
                Affix(name="attack_speed", value=9.8, type=AffixType.rerolled),
                Affix(name="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=12.1),
                Affix(name="lucky_hit_up_to_a_chance_to_stun_for_seconds", value=20.1, type=AffixType.tempered),
                Affix(name="shock_critical_strike_damage", value=97.8, type=AffixType.tempered),
            ],
            inherent=[],
            item_type=ItemType.Gloves,
            power=854,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_3_2160p_small.png", item3),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_4_2160p_medium.png",
        item4 := Item(
            affixes=[
                Affix(name="chance_for_chain_lightning_projectiles_to_cast_twice", value=20.9),
                Affix(name="damage_reduction", value=16.9),
                Affix(name="resource_generation_and_maximum", value=40.9),
                Affix(name="to_chain_lightning", value=4),
            ],
            aspect=Aspect(name="axial_conduit", value=0),
            inherent=[],
            item_type=ItemType.Legs,
            power=914,
            rarity=ItemRarity.Unique,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_4_2160p_small.png", item4),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_5_2160p_medium.png",
        item5 := Item(
            affixes=[
                Affix(name="maximum_life", value=768),
                Affix(name="mana_per_second", value=6, type=AffixType.rerolled),
                Affix(name="armor", value=1679),
                Affix(name="lucky_hit_up_to_a_chance_to_freeze_for_seconds", value=18.4, type=AffixType.tempered),
                Affix(name="evade_cooldown_reduction", value=18.4, type=AffixType.tempered),
            ],
            inherent=[Affix(name="maximum_evade_charges", value=3, type=AffixType.inherent)],
            item_type=ItemType.Boots,
            power=862,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_5_2160p_small.png", item5),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_6_2160p_medium.png",
        item6 := Item(
            affixes=[
                Affix(name="intelligence", value=94),
                Affix(name="maximum_life", value=1441, type=AffixType.greater),
                Affix(name="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=13.3, type=AffixType.rerolled),
                Affix(name="vulnerable_damage", value=52.9, type=AffixType.tempered),
                Affix(name="chance_for_chain_lightning_projectiles_to_cast_twice", value=19.6, type=AffixType.tempered),
            ],
            inherent=[Affix(name="critical_strike_damage", value=17.5, type=AffixType.inherent)],
            item_type=ItemType.Sword,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_6_2160p_small.png", item6),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_7_2160p_medium.png",
        item7 := Item(
            affixes=[
                Affix(name="intelligence", value=149, type=AffixType.greater),
                Affix(name="cooldown_reduction", value=10.5),
                Affix(name="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=9.2, type=AffixType.rerolled),
                Affix(name="vulnerable_damage", value=54.6, type=AffixType.tempered),
                Affix(name="chance_for_chain_lightning_projectiles_to_cast_twice", value=16.7, type=AffixType.tempered),
            ],
            inherent=[Affix(name="lucky_hit_chance", value=10, type=AffixType.inherent)],
            item_type=ItemType.Focus,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_7_2160p_small.png", item7),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_8_2160p_medium.png",
        item8 := Item(
            affixes=[
                Affix(name="intelligence", value=92),
                Affix(name="attack_speed", value=17.1, type=AffixType.greater),
                Affix(name="critical_strike_chance", value=6.9, type=AffixType.rerolled),
                Affix(name="vulnerable_damage", value=56.3, type=AffixType.tempered),
                Affix(name="unstable_currents_cooldown_reduction", value=14.4, type=AffixType.tempered),
            ],
            inherent=[
                Affix(name="resistance_to_all_elements", value=10, type=AffixType.inherent),
                Affix(name="shadow_resistance", value=10, type=AffixType.inherent),
            ],
            item_type=ItemType.Ring,
            power=925,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_8_2160p_small.png", item8),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_9_2160p_medium.png",
        item9 := Item(
            affixes=[
                Affix(name="intelligence", value=6.3),
                Affix(name="maximum_life", value=1441, type=AffixType.greater),
                Affix(name="cooldown_reduction", value=10.5, type=AffixType.rerolled),
                Affix(name="unstable_currents_cooldown_reduction", value=13.2, type=AffixType.tempered),
                Affix(name="overpower_damage", value=86.2, type=AffixType.tempered),
            ],
            inherent=[Affix(name="resistance_to_all_elements", value=23.8, type=AffixType.inherent)],
            item_type=ItemType.Amulet,
            power=872,
            rarity=ItemRarity.Legendary,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_9_2160p_small.png", item9),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_10_2160p_medium.png",
        item10 := Item(
            affixes=[
                Affix(name="lucky_hit_chance", value=14.4, type=AffixType.greater),
                Affix(name="nonphysical_damage", value=76.7),
                Affix(name="cooldown_reduction", value=13.5),
                Affix(name="to_potent_warding", value=4),
            ],
            aspect=Aspect(name="tal_rashas_iridescent_loop", value=17.5),
            inherent=[
                Affix(name="resistance_to_all_elements", value=10, type=AffixType.inherent),
                Affix(name="resistance_to_all_elements", value=4, type=AffixType.inherent),
            ],
            item_type=ItemType.Ring,
            power=925,
            rarity=ItemRarity.Unique,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_10_2160p_medium.png", item10),
    (
        (3840, 2160),
        f"{BASE_PATH}/read_descr_11_2160p_medium.png",
        item11 := Item(
            affixes=[
                Affix(name="movement_speed", value=19),
                Affix(name="maximum_resistance_to_all_elements", value=14.3, type=AffixType.greater),
                Affix(name="resistance_to_all_elements", value=69),
                Affix(name="damage_reduction", value=23),
            ],
            aspect=Aspect(name="tyraels_might", value=4996),
            inherent=[Affix(name="ignore_durability_loss", value=None, type=AffixType.inherent)],
            item_type=ItemType.ChestArmor,
            power=925,
            rarity=ItemRarity.Mythic,
        ),
    ),
    ((3840, 2160), f"{BASE_PATH}/read_descr_11_2160p_small.png", item11),
]


def _run_test_helper(img_res: tuple[int, int], input_img: str, expected_item: Item):
    Cam().update_window_pos(0, 0, *img_res)
    img = cv2.imread(input_img)
    item = read_descr(expected_item.rarity, img)
    assert item == expected_item


@pytest.mark.parametrize(("img_res", "input_img", "expected_item"), items)
def test_item(img_res: tuple[int, int], input_img: str, expected_item: Item):
    _run_test_helper(img_res=img_res, input_img=input_img, expected_item=expected_item)
