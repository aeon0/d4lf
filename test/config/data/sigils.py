all_bad_cases = [
    # 1 item
    {"Sigils": {"blacklist": "monster_cold_resist"}},
    {"Sigils": {"blacklist": "monster_cold_resist"}},
    {"Sigils": {"blacklist": ["monster123_cold_resist"]}},
    {"Sigils": {"blacklist": ["monster_cold_resist", "test123"]}},
    {"Sigils": {"blacklist": ["monster_cold_resist"], "whitelist": ["monster_cold_resist"]}},
    {"Sigils": {"maxTier": 101}},
    {"Sigils": {"minTier": -1}},
    {"Sigils": {"whitelist": ["monster123_cold_resist"]}},
    {"Sigils": {"whitelist": ["monster_cold_resist", "test123"]}},
]

all_good_cases = [
    # 1 item
    {"Sigils": {"blacklist": ["monster_cold_resist"]}},
    {"Sigils": {"maxTier": 90}},
    {"Sigils": {"minTier": 10}},
    {"Sigils": {"whitelist": ["monster_cold_resist"]}},
    # 2 items
    {"Sigils": {"blacklist": ["monster_cold_resist"], "maxTier": 90}},
    {"Sigils": {"blacklist": ["monster_cold_resist"], "minTier": 10}},
    {"Sigils": {"blacklist": ["monster_cold_resist"], "whitelist": ["monster_fire_resist"]}},
    {"Sigils": {"maxTier": 90, "minTier": 10}},
    {"Sigils": {"maxTier": 90, "whitelist": ["monster_cold_resist"]}},
    {"Sigils": {"minTier": 10, "whitelist": ["monster_cold_resist"]}},
    # 3 items
    {"Sigils": {"blacklist": ["monster_cold_resist"], "maxTier": 90, "minTier": 10}},
    {"Sigils": {"blacklist": ["monster_cold_resist"], "maxTier": 90, "whitelist": ["monster_fire_resist"]}},
    {"Sigils": {"blacklist": ["monster_cold_resist"], "minTier": 10, "whitelist": ["monster_fire_resist"]}},
    {"Sigils": {"maxTier": 90, "minTier": 10, "whitelist": ["monster_cold_resist"]}},
]
