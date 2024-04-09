from config.models import UniqueModel, AffixAspectFilterModel, ComparisonType, ProfileModel, SigilModel
from item.data.item_type import ItemType

affix = {
    "test": [
        {
            "Helm": {
                "itemType": "helm",
                "minPower": 725,
                "affixPool": [["basic_skill_attack_speed", 6], ["cooldown_reduction", 5], ["maximum_life", 640], ["total_armor", 9]],
            }
        },
        {
            "ResBoots": {
                "itemType": "boots",
                "minPower": 725,
                "affixPool": [
                    ["movement_speed"],
                    {
                        "any_of": [
                            ["shadow_resistance"],
                            ["cold_resistance"],
                            ["lightning_resistance"],
                            ["poison_resistance"],
                            ["fire_resistance"],
                        ],
                        "minCount": 2,
                    },
                ],
            }
        },
        {
            "GreatBoots": {
                "affixPool": [["movement_speed"], ["cold_resistance"], ["lightning_resistance"]],
                "inherentPool": ["maximum_evade_charges", "attacks_reduce_evades_cooldown"],
                "itemType": "boots",
                "minPower": 800,
            }
        },
        {
            "HelmNoLife": {
                "itemType": "helm",
                "minPower": 725,
                "affixPool": [
                    {"blacklist": ["maximum_life"]},
                ],
            }
        },
        {
            "Armor": {
                "itemType": ["chest armor", "pants"],
                "minPower": 725,
                "affixPool": [
                    ["damage_reduction_from_close_enemies", 10],
                    ["maximum_life", 700],
                    ["dodge_chance_against_close_enemies", 6.5],
                    ["dodge_chance", 5.0],
                ],
            }
        },
        {
            "Boots": {
                "itemType": "boots",
                "minPower": 725,
                "affixPool": [
                    ["movement_speed", 10],
                    ["maximum_life", 700],
                    ["cold_resistance", 6.5],
                    ["fire_resistance", 5.0],
                    ["poison_resistance", 5.0],
                    ["shadow_resistance", 5.0],
                ],
            }
        },
    ]
}
aspect = {
    "test": [
        ["accelerating", 25],
        ["of_might", 6.0, "smaller"],
    ]
}
sigil = ProfileModel(
    name="test",
    Sigils=SigilModel(blacklist=["reduce_cooldowns_on_kill", "vault_of_copper"], whitelist=["jalals_vigil"], maxTier=80, minTier=40),
)

unique = ProfileModel(
    name="test",
    Uniques=[
        UniqueModel(itemType=[ItemType.Scythe, ItemType.Sword], minPower=900),
        UniqueModel(itemType=[ItemType.Scythe], minPower=900),
        UniqueModel(
            affix=[
                AffixAspectFilterModel(name="attack_speed", value=8.4),
                AffixAspectFilterModel(name="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=12),
                AffixAspectFilterModel(name="maximum_life", value=700),
                AffixAspectFilterModel(name="maximum_essence", value=9),
            ],
            aspect=AffixAspectFilterModel(name="lidless_wall", value=20),
            minPower=900,
        ),
        UniqueModel(
            affix=[AffixAspectFilterModel(name="attack_speed", value=8.4)],
            aspect=AffixAspectFilterModel(name="soulbrand", value=20),
            minPower=900,
        ),
        UniqueModel(aspect=AffixAspectFilterModel(name="soulbrand", value=15, comparison=ComparisonType.smaller)),
    ],
)
