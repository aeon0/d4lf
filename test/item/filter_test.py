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
        ItemRarity.Legendary,
        ItemType.Boots,
        925,
        Aspect("ghostwalker_aspect", 13),
        [
            Affix("all_stats", 18),
            Affix("intelligence", 42),
            Affix("movement_speed", 17.5),
            Affix("fortify_generation", 421.5),  # this is currently predicting wrongly!
        ],
    )
    filter = Filter()
    keep, x, matched_affixes, filter_name = filter.should_keep(item)
    print(keep)
