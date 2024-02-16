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
    type: ItemType | None = None
    power: int | None = None
    aspect: Aspect | None = None
    affixes: list[Affix] = field(default_factory=list)
    inherent: list[Affix] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False

        if self.aspect is None and other.aspect is not None:
            Logger.debug("Aspect do not Match")
            return False
        if self.aspect is not None and other.aspect is None:
            Logger.debug("Aspect do not Match")
            return False
        if self.aspect is not None and other.aspect is not None:
            if self.aspect.type != other.aspect.type or self.aspect.value != other.aspect.value:
                Logger.debug("Aspect do not Match")
                return False

        same = True
        if self.rarity != other.rarity:
            same = False
            Logger.debug("Rarity not the same")
        if self.power != other.power:
            same = False
            Logger.debug("Power not the same")
        if self.type != other.type:
            same = False
            Logger.debug("Type not the same")
        if not (
            len(self.affixes) == len(other.affixes)
            and all(s.type == o.type and s.value == o.value for s, o in zip(self.affixes, other.affixes))
        ):
            same = False
            Logger.debug("Affixes do not match")
        if not (
            len(self.inherent) == len(other.inherent)
            and all(s.type == o.type and s.value == o.value for s, o in zip(self.inherent, other.inherent))
        ):
            same = False
            Logger.debug("Inherent Affixes do not match")
        return same


class ItemJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            return {
                "rarity": o.rarity.value if o.rarity else None,
                "type": o.type.value if o.type else None,
                "power": o.power if o.power else None,
                "aspect": o.aspect.__dict__ if o.aspect else None,
                "affixes": [affix.__dict__ for affix in o.affixes],
                "inherent": [affix.__dict__ for affix in o.inherent],
            }
        return super().default(o)
