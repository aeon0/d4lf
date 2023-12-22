from dataclasses import asdict, dataclass, field
from item.data.aspect import Aspect
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.data.affix import Affix


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
            return False
        if self.aspect is not None and other.aspect is None:
            return False
        if self.aspect is not None and other.aspect is not None:
            if self.aspect.type != other.aspect.type or self.aspect.value != other.aspect.value:
                return False

        return (
            self.rarity == other.rarity
            and self.power == other.power
            and self.type == other.type
            and len(self.affixes) == len(other.affixes)
            and all(s.type == o.type and s.value == o.value for s, o in zip(self.affixes, other.affixes))
        )
