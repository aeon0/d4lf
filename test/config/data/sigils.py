all_bad_cases = [
    # 1 item
    {"Sigil": {"blacklist": "monster_cold_resist"}},
    {"Sigil": {"blacklist": "monster_cold_resist"}},
    {"Sigil": {"blacklist": ["monster123_cold_resist"]}},
    {"Sigil": {"blacklist": ["monster_cold_resist", "test123"]}},
    {"Sigil": {"blacklist": ["monster_cold_resist"], "whitelist": ["monster_cold_resist"]}},
    {"Sigil": {"maxTier": 101}},
    {"Sigil": {"minTier": -1}},
    {"Sigil": {"whitelist": ["monster123_cold_resist"]}},
    {"Sigil": {"whitelist": ["monster_cold_resist", "test123"]}},
]

all_good_cases = [
    # 1 item
    {"Sigil": {"blacklist": ["monster_cold_resist"]}},
    {"Sigil": {"maxTier": 90}},
    {"Sigil": {"minTier": 10}},
    {"Sigil": {"whitelist": ["monster_cold_resist"]}},
    # 2 items
    {"Sigil": {"blacklist": ["monster_cold_resist"], "maxTier": 90}},
    {"Sigil": {"blacklist": ["monster_cold_resist"], "minTier": 10}},
    {"Sigil": {"blacklist": ["monster_cold_resist"], "whitelist": ["monster_fire_resist"]}},
    {"Sigil": {"maxTier": 90, "minTier": 10}},
    {"Sigil": {"maxTier": 90, "whitelist": ["monster_cold_resist"]}},
    {"Sigil": {"minTier": 10, "whitelist": ["monster_cold_resist"]}},
    # 3 items
    {"Sigil": {"blacklist": ["monster_cold_resist"], "maxTier": 90, "minTier": 10}},
    {"Sigil": {"blacklist": ["monster_cold_resist"], "maxTier": 90, "whitelist": ["monster_fire_resist"]}},
    {"Sigil": {"blacklist": ["monster_cold_resist"], "minTier": 10, "whitelist": ["monster_fire_resist"]}},
    {"Sigil": {"maxTier": 90, "minTier": 10, "whitelist": ["monster_cold_resist"]}},
]
