from item.filter import Filter
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.models import Item
from cam import Cam
from config import Config
from template_finder import stored_templates


def test_should_keep():
    Cam().update_window_pos(0, 0, 1920, 1080)
    Config().load_data()
    stored_templates.cache_clear()

    item = Item(
        ItemRarity.Common,
        ItemType.Sigil,
        100,
        None,
        [
            Affix("lightning_damage", 15),
            Affix("death_pulse"),
            Affix("monster_lightning_damage", 20),
            Affix("monster_life", 30),
            Affix("potion_breakers", 0.75),
        ],
        [Affix("tormented_ruins"), Affix("revives_allowed", 4)],
    )

    filter = Filter()
    keep, x, matched_affixes, filter_name = filter.should_keep(item)
    print(keep)
