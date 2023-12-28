import pytest
from item.filter import Filter
from item.data.rarity import ItemRarity
from item.data.item_type import ItemType
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.models import Item
from cam import Cam
from config import Config
from template_finder import stored_templates


@pytest.mark.parametrize(
    "item_descr",
    [
        Item(
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
        ),
        Item(
            ItemRarity.Rare,
            ItemType.Pants,
            844,
            None,
            [
                Affix("potion_capacity", 3),
                Affix("thorns", 873),
                Affix("damage_reduction_from_close_enemies", 11),
                Affix("imbuement_skill_cooldown_reduction", 5.8),
            ],
            [
                Affix("injured_potion_resource", 20),
            ],
        ),
    ],
)
def test_should_keep(item_descr: Item):
    Cam().update_window_pos(0, 0, 1920, 1080)
    Config().load_data()
    stored_templates.cache_clear()

    filter = Filter()
    res = filter.should_keep(item_descr)
    print(res.keep)
