from config.models import (
    AffixFilterCountModel,
    AffixFilterModel,
    AspectUniqueFilterModel,
    ComparisonType,
    ItemFilterModel,
    ProfileModel,
    SigilFilterModel,
    UniqueModel,
)
from item.data.item_type import ItemType

# noinspection PyTypeChecker
affix = ProfileModel(
    name="test",
    Affixes=[
        {
            "Helm": ItemFilterModel(
                itemType=[ItemType.Helm],
                minPower=725,
                affixPool=[
                    AffixFilterCountModel(
                        count=[
                            AffixFilterModel(name="intelligence", value=5),
                            AffixFilterModel(name="cooldown_reduction", value=5),
                            AffixFilterModel(name="maximum_life", value=640),
                            AffixFilterModel(name="total_armor", value=9),
                        ]
                    )
                ],
            )
        },
        {
            "ResBoots": ItemFilterModel(
                itemType=[ItemType.Boots],
                minPower=725,
                affixPool=[
                    AffixFilterCountModel(count=[AffixFilterModel(name="movement_speed")]),
                    AffixFilterCountModel(
                        count=[
                            AffixFilterModel(name="shadow_resistance"),
                            AffixFilterModel(name="cold_resistance"),
                            AffixFilterModel(name="lightning_resistance"),
                            AffixFilterModel(name="poison_resistance"),
                            AffixFilterModel(name="fire_resistance"),
                        ],
                        minCount=2,
                    ),
                ],
            )
        },
        {
            "ResBootsExact": ItemFilterModel(
                itemType=[ItemType.Boots],
                minPower=725,
                affixPool=[
                    AffixFilterCountModel(count=[AffixFilterModel(name="movement_speed")]),
                    AffixFilterCountModel(
                        count=[
                            AffixFilterModel(name="shadow_resistance", value=4, comparison=ComparisonType.smaller),
                            AffixFilterModel(name="cold_resistance", value=4, comparison=ComparisonType.smaller),
                            AffixFilterModel(name="lightning_resistance", value=4, comparison=ComparisonType.smaller),
                            AffixFilterModel(name="poison_resistance", value=4, comparison=ComparisonType.smaller),
                            AffixFilterModel(name="fire_resistance", value=4, comparison=ComparisonType.smaller),
                        ],
                        minCount=2,
                    ),
                ],
            )
        },
        {
            "GreatBoots": ItemFilterModel(
                itemType=[ItemType.Boots],
                minPower=725,
                affixPool=[
                    AffixFilterCountModel(
                        count=[
                            AffixFilterModel(name="movement_speed"),
                            AffixFilterModel(name="cold_resistance"),
                            AffixFilterModel(name="lightning_resistance"),
                        ],
                    ),
                ],
                inherentPool=[
                    AffixFilterCountModel(
                        count=[
                            AffixFilterModel(name="maximum_evade_charges"),
                            AffixFilterModel(name="attacks_reduce_evades_cooldown_by_seconds"),
                        ],
                        minCount=1,
                    ),
                ],
            )
        },
        {
            "Armor": ItemFilterModel(
                itemType=[ItemType.ChestArmor, ItemType.Legs],
                minPower=725,
                affixPool=[
                    AffixFilterCountModel(
                        count=[
                            AffixFilterModel(name="maximum_life", value=700),
                            AffixFilterModel(name="dexterity", value=5),
                            AffixFilterModel(name="intelligence", value=5),
                            AffixFilterModel(name="dodge_chance", value=5),
                        ],
                    ),
                ],
            )
        },
        {
            "Boots": ItemFilterModel(
                itemType=[ItemType.Boots],
                minPower=725,
                affixPool=[
                    AffixFilterCountModel(
                        count=[
                            AffixFilterModel(name="movement_speed", value=10),
                            AffixFilterModel(name="maximum_life", value=700),
                            AffixFilterModel(name="cold_resistance", value=6.5),
                            AffixFilterModel(name="fire_resistance", value=5),
                            AffixFilterModel(name="poison_resistance", value=5),
                            AffixFilterModel(name="shadow_resistance", value=5),
                        ],
                        minCount=4,
                    ),
                ],
            )
        },
        {"GreaterAffixes": ItemFilterModel(minGreaterAffixCount=1)},
    ],
)

sigil = ProfileModel(
    name="test",
    Sigils=SigilFilterModel(blacklist=["reduce_cooldowns_on_kill", "vault_of_copper"], whitelist=["jalals_vigil"], maxTier=80, minTier=40),
)

unique = ProfileModel(
    name="test",
    Uniques=[
        UniqueModel(itemType=[ItemType.Scythe, ItemType.Sword], minPower=900),
        UniqueModel(itemType=[ItemType.Scythe], minPower=900),
        UniqueModel(
            affix=[
                AffixFilterModel(name="attack_speed", value=8.4),
                AffixFilterModel(name="lucky_hit_up_to_a_chance_to_restore_primary_resource", value=12),
                AffixFilterModel(name="maximum_life", value=700),
                AffixFilterModel(name="maximum_essence", value=9),
            ],
            aspect=AspectUniqueFilterModel(name="lidless_wall", value=20),
            minPower=900,
        ),
        UniqueModel(
            affix=[AffixFilterModel(name="attack_speed", value=8.4)],
            aspect=AspectUniqueFilterModel(name="soulbrand", value=20),
            minPower=900,
        ),
        UniqueModel(aspect=AspectUniqueFilterModel(name="soulbrand", value=15, comparison=ComparisonType.smaller), minPower=900),
    ],
)
