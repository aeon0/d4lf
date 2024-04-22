import json
from dataclasses import dataclass, field

from item.data.affix import Affix
from item.data.aspect import Aspect
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from logger import Logger


@dataclass
class Item:
    rarity: ItemRarity | None = None
    item_type: ItemType | None = None
    power: int | None = None
    aspect: Aspect | None = None
    affixes: list[Affix] = field(default_factory=list)
    inherent: list[Affix] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        res = True
        if self.aspect != other.aspect:
            Logger.debug("Aspect not the same")
            res = False
        if self.rarity != other.rarity:
            Logger.debug("Rarity not the same")
            res = False
        if self.power != other.power:
            Logger.debug("Power not the same")
            res = False
        if self.item_type != other.item_type:
            Logger.debug("Type not the same")
            res = False
        if self.affixes != other.affixes:
            Logger.debug("Affixes do not match")
            res = False
        if self.inherent != other.inherent:
            Logger.debug("Inherent affixes do not match")
            res = False
        return res


class ItemJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            return {
                "rarity": o.rarity.value if o.rarity else None,
                "item_type": o.item_type.value if o.item_type else None,
                "power": o.power if o.power else None,
                "aspect": o.aspect.__dict__ if o.aspect else None,
                "affixes": [affix.__dict__ for affix in o.affixes],
                "inherent": [affix.__dict__ for affix in o.inherent],
            }
        return super().default(o)
