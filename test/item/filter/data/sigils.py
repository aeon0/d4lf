from item.data.affix import Affix
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item


class TestSigil(Item):
    def __init__(self, rarity=ItemRarity.Common, type=ItemType.Sigil, power=60, **kwargs):
        super().__init__(rarity=rarity, type=type, power=power, **kwargs)


sigils = [
    (
        "power too low",
        [],
        TestSigil(power=20),
    ),
    (
        "power too high",
        [],
        TestSigil(power=100),
    ),
    (
        "affix in blacklist",
        [],
        TestSigil(
            affixes=[
                Affix(type="death_pulse"),
                Affix(type="reduce_cooldowns_on_kill", value=0.25),
            ],
        ),
    ),
    (
        "inherent in blacklist",
        [],
        TestSigil(
            inherent=[
                Affix(type="vault_of_copper"),
            ],
        ),
    ),
    (
        "affix in whitelist",
        ["test"],
        TestSigil(
            inherent=[
                Affix(type="jalals_vigil"),
            ],
        ),
    ),
    (
        "ok_1",
        ["test"],
        TestSigil(
            affixes=[
                Affix(type="extra_shrines"),
                Affix(type="empowered_elites_shock_lance"),
                Affix(type="monster_burning_damage", value=30.0),
                Affix(type="monster_regen", value=1.5),
                Affix(type="slowing_projectiles", value=50.0),
            ],
            inherent=[
                Affix(type="vault_of_ink"),
            ],
        ),
    ),
    (
        "ok_2",
        ["test"],
        TestSigil(
            affixes=[
                Affix(type="increased_healing", value=15.0),
                Affix(type="volcanic"),
                Affix(type="monster_cold_damage", value=20.0),
                Affix(type="monster_poison_resist", value=60),
                Affix(type="armor_breakers", value=7.0),
            ],
            inherent=[
                Affix(type="vault_of_stone"),
            ],
        ),
    ),
    (
        "ok_3",
        ["test"],
        TestSigil(
            affixes=[
                Affix(type="quick_killer", value=2.0),
                Affix(type="nightmare_portal"),
                Affix(type="monster_attack_speed", value=25.0),
                Affix(type="monster_burning_resist", value=60.0),
                Affix(type="backstabbers"),
            ],
            inherent=[
                Affix(type="vault_of_cinder"),
            ],
        ),
    ),
]
