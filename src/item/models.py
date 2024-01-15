from dataclasses import dataclass, field
from item.data.aspect import Aspect
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.data.affix import Affix
from logger import Logger


@dataclass
class Item:
    rarity: ItemRarity
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
