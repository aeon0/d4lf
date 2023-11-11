from item.filter import Filter
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.models import Item


def test_should_keep():
    item = Item(
        ItemRarity.Legendary,
        ItemType.Gloves,
        859,
        Aspect("aspect_of_disobedience", 1.1),
        [
            # Affix("attack_speed", 8.4),
            # Affix("lucky_hit_chance", 9.4),
            # Affix("lucky_hit_up_to_a_chance_to_slow", 14.5),
            # Affix("ranks_of_flurry", 3),
        ],
    )
    filter = Filter()
    keep, _ = filter.should_keep(item)
    print(keep)
