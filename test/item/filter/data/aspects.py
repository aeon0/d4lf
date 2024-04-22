from item.data.aspect import Aspect
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item


class TestLegendary(Item):
    def __init__(self, rarity=ItemRarity.Legendary, item_type=ItemType.Shield, power=910, **kwargs):
        super().__init__(rarity=rarity, item_type=item_type, power=power, **kwargs)


aspects = [
    ("wrong type", [], TestLegendary(aspect=Aspect(type="of_anemia", value=30))),
    ("wrong value", [], TestLegendary(aspect=Aspect(type="accelerating", value=21))),
    ("wrong value condition", [], TestLegendary(aspect=Aspect(type="of_might", value=6.1))),
    ("ok_1", ["test"], TestLegendary(aspect=Aspect(type="accelerating", value=26))),
    ("ok_2", ["test"], TestLegendary(aspect=Aspect(type="of_might", value=5.9))),
]
