from item.data.affix import Affix
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item

items = [
    (
        Item(
            affixes=[
                Affix("potion_capacity", 3),
                Affix("thorns", 873),
                Affix("damage_reduction_from_close_enemies", 11),
                Affix("imbuement_skill_cooldown_reduction", 5.8),
            ],
            inherent=[Affix("injured_potion_resource", 20)],
            item_type=ItemType.Legs,
            power=844,
            rarity=ItemRarity.Rare,
        ),
        False,
    ),
]
