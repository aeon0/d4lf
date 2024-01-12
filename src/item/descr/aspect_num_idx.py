# Some aspects/uniques have their variable number as second (number_idx_1) or third (number_idx_2)
ASPECT_NUMBER_AT_IDX1 = [
    # Legendary
    # ================================
    1302633,  # frostbitten
    1620632,  # of_artful_initiative
    1302490,  # of_noxious_ice
    1213532,  # elementalists
    1211282,  # snowveiled
    1106483,  # of_might
    1226354,  # assimilation
    1225582,  # exploiters
    1438478,  # of_audacity
    1225424,  # ghostwalker
    1602955,  # of_slaughter
    1200857,  # of_tempering_blows
    1427872,  # of_ancestral_charge
    1106004,  # of_encroaching_wrath
    1106002,  # brawlers
    1199627,  # devilish
    1199203,  # earthstrikers
    1106039,  # steadfast_berserkers
    1106011,  # windlasher
    1199207,  # bear_clan_berserkers
    1106061,  # of_mending_stone
    1338010,  # of_metamorphic_stone
    1222401,  # of_the_stampede
    1106166,  # of_the_trampled_earth
    1105811,  # lightning_dancers
    1619484,  # raw_might
    1221533,  # of_decay
    1220407,  # osseous_gale
    1106650,  # rotting
    1220423,  # of_exposed_flesh
    1106690,  # coldbringers
    1184417,  # of_uncanny_treachery
    1301760,  # of_lethal_dusk
    1106674,  # enshrouding
    1106339,  # of_arrow_storms
    1106355,  # of_bursting_venoms
    1439745,  # of_pestilent_points
    1301737,  # of_synergy
    1106291,  # icy_alchemists
    1106283,  # toxic_alchemists
    1106115,  # trickshot
    1106418,  # snowguards
    1106733,  # of_frozen_orbit
    1106123,  # serpentine
    # Uniques
    # ================================
    1561309,  # banished_lords_talisman
    941951,  # ancients_oath
    1304468,  # battle_trance
    942555,  # gohrs_devastating_grips
    1306218,  # waxing_gibbous
    1306235,  # black_river
    1220207,  # bloodless_scream
    1222626,  # ring_of_mendeln
    1211653,  # blue_rose
    1225299,  # esadoras_overflowing_cameo
    942111,  # staff_of_endless_rage
    942559,  # fists_of_fate
    1215133,  # mothers_embrace
    1306325,  # temerity
    941704,  # the_butchers_cleaver
    1559923,  # xfals_corroded_signet
    1706657,  # writhing_band_of_trickery
    1706650,  # airidahs_inexorable_will
]

ASPECT_NUMBER_AT_IDX2 = [
    # Legendary
    # ================================
    1106134,  # of_retribution
    1221425,  # of_serration
    1221706,  # of_untimely_death
    # Unique
    # ================================
    1439438,  # azurewrath
    1560873,  # soulbrand
    1706603,  # ring_of_red_furor
]

if __name__ == "__main__":
    import json

    with open("assets/lang/enUS/uniques_enUS.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        key_used = []
        key_not_found = []
        for key in ASPECT_NUMBER_AT_IDX2:
            if key in data and key not in key_used:
                print(f"{data[key]['snoId']}, # {key}")
                key_used.append(key)
            if key not in data:
                key_not_found.append(key)
        for key in key_not_found:
            print(f"WARNING: Not found: {key}")
