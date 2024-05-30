import json
from dataclasses import dataclass, field

from src.item.data.affix import Affix
from src.item.data.aspect import Aspect
from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.logger import Logger


@dataclass
class Item:
    affixes: list[Affix] = field(default_factory=list)
    aspect: Aspect | None = None
    codex_upgrade: bool = False
    inherent: list[Affix] = field(default_factory=list)
    item_type: ItemType | None = None
    power: int | None = None
    rarity: ItemRarity | None = None

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        res = True
        if self.affixes != other.affixes:
            Logger.debug("Affixes do not match")
            res = False
        if self.aspect != other.aspect:
            Logger.debug("Aspect not the same")
            res = False
        if self.codex_upgrade != other.codex_upgrade:
            Logger.debug("Codex upgrade not the same")
            res = False
        if self.inherent != other.inherent:
            Logger.debug("Inherent affixes do not match")
            res = False
        if self.item_type != other.item_type:
            Logger.debug("Type not the same")
            res = False
        if self.power != other.power:
            Logger.debug("Power not the same")
            res = False
        if self.rarity != other.rarity:
            Logger.debug("Rarity not the same")
            res = False
        return res


class ItemJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            return {
                "affixes": [affix.__dict__ for affix in o.affixes],
                "aspect": o.aspect.__dict__ if o.aspect else None,
                "codex_upgrade": o.codex_upgrade,
                "inherent": [affix.__dict__ for affix in o.inherent],
                "item_type": o.item_type.value if o.item_type else None,
                "power": o.power if o.power else None,
                "rarity": o.rarity.value if o.rarity else None,
            }
        return super().default(o)
