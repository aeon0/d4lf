all_bad_cases = [
    {"Uniques": [{"affix": "test"}]},  # not a list
    {"Uniques": [{"affix": [12]}]},  # list but bad type
    {"Uniques": [{"affix": [["damage_reduction_from_close_enemies", "asd"]]}]},  # list but bad type
    {"Uniques": [{"affix": [["damage_reduction_from_close_enemies", 12, "bigger"]]}]},  # list but bad type
]

all_good_cases = {
    "name": "good",
    "Uniques": [
        # 1 filter criteria
        {"affix": ["damage_reduction_from_close_enemies"]},
        {"affix": [["damage_reduction_from_close_enemies", 12, "smaller"], ["damage_reduction_from_distant_enemies", 12, "smaller"]]},
        {"affix": [["damage_reduction_from_close_enemies", 12, "smaller"]]},
        {"affix": [["damage_reduction_from_close_enemies", 12]]},
        {"aspect": "tibaults_will"},
        {"itemType": "pants"},
        {"itemType": ["chest armor", "pants"]},
        {"minPower": 900},
        # 2 filter criterias
        {"affix": ["damage_reduction_from_close_enemies"], "aspect": "tibaults_will"},
        {"affix": ["damage_reduction_from_close_enemies"], "itemType": "pants"},
        {"affix": ["damage_reduction_from_close_enemies"], "minPower": 900},
        {"aspect": "tibaults_will", "itemType": "pants"},
        {"aspect": "tibaults_will", "minPower": 900},
        {"itemType": "pants", "minPower": 900},
        # 3 filter criterias
        {"affix": ["damage_reduction_from_close_enemies"], "aspect": "tibaults_will", "itemType": "pants"},
        {"affix": ["damage_reduction_from_close_enemies"], "aspect": "tibaults_will", "minPower": 900},
        {"affix": ["damage_reduction_from_close_enemies"], "itemType": "pants", "minPower": 900},
        {"aspect": "tibaults_will", "itemType": "pants", "minPower": 900},
    ],
}
