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
sigil = {
    "test": {
        "blacklist": ["reduce_cooldowns_on_kill", "vault_of_copper"],
        "whitelist": ["jalals_vigil"],
        "maxTier": 80,
        "minTier": 40,
    }
}

unique = {
    "test": [
        {"itemType": ["scythe", "sword"], "minPower": 900},
        {"itemType": "scythe", "minPower": 900},
        {
            "aspect": ["lidless_wall", 20],
            "minPower": 900,
            "affixPool": [
                ["attack_speed", 8.4],
                ["lucky_hit_up_to_a_chance_to_restore_primary_resource", 12],
                ["maximum_life", 700],
                ["maximum_essence", 9],
            ],
        },
        {
            "aspect": ["soulbrand", 20],
            "minPower": 900,
            "affixPool": [["attack_speed", 8.4]],
        },
        {
            "aspect": ["soulbrand", 15, "smaller"],
        },
    ]
}
