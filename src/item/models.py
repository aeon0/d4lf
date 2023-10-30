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
