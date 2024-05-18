from item.data.affix import Affix
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item

items = [
    (
        Item(
            affixes=[
                Affix(name="potion_capacity", value=3),
                Affix(name="thorns", value=873),
                Affix(name="damage_reduction_from_close_enemies", value=11),
                Affix(name="imbuement_skill_cooldown_reduction", value=5.8),
            ],
            inherent=[Affix(name="injured_potion_resource", value=20)],
            item_type=ItemType.Legs,
            power=844,
            rarity=ItemRarity.Rare,
        ),
        False,
    ),
]
