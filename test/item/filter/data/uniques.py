from item.data.affix import Affix
from item.data.aspect import Aspect
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item


class TestUnique(Item):
    def __init__(self, rarity=ItemRarity.Unique, item_type=ItemType.Shield, power=910, **kwargs):
        super().__init__(rarity=rarity, item_type=item_type, power=power, **kwargs)


uniques = [
    (
        "item power too low",
        [],
        TestUnique(power=800),
    ),
    (
        "wrong type",
        [],
        TestUnique(item_type=ItemType.Helm, aspect=Aspect(type="deathless_visage", value=1862)),
    ),
    (
        "wrong aspect",
        [],
        TestUnique(aspect=Aspect(type="bloodless_scream", value=40.0)),
    ),
    (
        "aspect power too low",
        [],
        TestUnique(aspect=Aspect(type="lidless_wall", value=15)),
    ),
    (
        "aspect power too high",
        [],
        TestUnique(aspect=Aspect(type="soulbrand", value=22)),
    ),
    (
        "affix power too low",
        [],
        TestUnique(
            aspect=Aspect(type="lidless_wall", value=22),
            affixes=[
                Affix(type="attack_speed", value=9.6),
                Affix(type="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=13.5),
                Affix(type="maximum_life", value=638),
                Affix(type="maximum_essence", value=8),
            ],
        ),
    ),
    (
        "only filter one affix",
        ["test.soulbrand"],
        TestUnique(
            aspect=Aspect(type="soulbrand", value=22),
            affixes=[
                Affix(type="attack_speed", value=9.6),
                Affix(type="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=13.5),
                Affix(type="maximum_life", value=638),
                Affix(type="maximum_essence", value=8),
            ],
        ),
    ),
    (
        "ok_1",
        ["test.lidless_wall"],
        TestUnique(
            aspect=Aspect(type="lidless_wall", value=22),
            affixes=[
                Affix(type="attack_speed", value=9.6),
                Affix(type="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=13.5),
                Affix(type="maximum_life", value=1111),
                Affix(type="maximum_essence", value=13),
            ],
        ),
    ),
    (
        "ok_2",
        ["test.black_river", "test.black_river"],
        TestUnique(
            item_type=ItemType.Scythe,
            aspect=Aspect(type="black_river", value=128),
        ),
    ),
    (
        "ok_3",
        ["test.soulbrand"],
        TestUnique(aspect=Aspect(type="soulbrand", value=11)),
    ),
]
