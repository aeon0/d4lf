from item.data.affix import Affix
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item

items = [
    (
        Item(
            ItemRarity.Rare,
            ItemType.Legs,
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
        False,
    ),
]
