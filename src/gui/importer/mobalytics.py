import json
import os
import pathlib
import re

import lxml.html

from src.config.models import AffixFilterCountModel, AffixFilterModel, ItemFilterModel, ProfileModel
from src.dataloader import Dataloader
from src.gui.importer.common import get_with_retry, match_to_enum, retry_importer, save_as_profile
from src.item.data.affix import Affix
from src.item.data.item_type import ItemType
from src.item.descr.text import clean_str, closest_match
from src.logger import Logger

BUILD_GUIDE_BASE_URL = "https://mobalytics.gg/diablo-4/"
STATS_BASE_URL = "?coreTab=assigned-skills&equipmentTab=gear-stats&variantTab="
STATS_GRID_XPATH = "//*[@class='m-4tf4x5']"
STATS_GRID_OCCUPIED_XPATH = ".//*[@class='m-0']"
IMAGE_XPATH = ".//img"
CLASS_XPATH = "(//*[@class='m-47xh8o'])[4]"
ITEM_NAME_XPATH = "//*[@class='m-ndz0o2']"

class MobalyticsException(Exception):
    pass

@retry_importer
def import_mobalytics(url: str):
    url = url.strip().replace("\n", "")
    if BUILD_GUIDE_BASE_URL not in url:
        Logger.error("Invalid url, please use a mobalytics build guide")
        return
    if STATS_BASE_URL not in url:
        url += STATS_BASE_URL + "0"
    Logger.info(f"Loading {url}")
    try:
        r = get_with_retry(url=url)
    except ConnectionError:
        Logger.error(msg:="Couldn't get build")
        raise MobalyticsException(msg)
    data = lxml.html.fromstring(r.text)
    if not (class_name := data.xpath(CLASS_XPATH)[0].text.lower()):
        Logger.error(msg:="Couldn't get class")
        raise MobalyticsException(msg)
    if not (stats_grid := data.xpath(STATS_GRID_XPATH)):
        Logger.error(msg:="No stats grid found")
        raise MobalyticsException(msg)
    items = stats_grid[0].xpath(STATS_GRID_OCCUPIED_XPATH)
    if not items:
        Logger.error(msg := "No items found")
        raise MobalyticsException(msg)
    for item in items:
        item_filter = ItemFilterModel()
        # check if unique by using //*[@class='m-ndz0o2'] and then checking if not aspect in name
        slot = item.xpath(IMAGE_XPATH)
        if not slot:
            Logger.error("No item_type found")
            continue
        item_filter.itemType = match_to_enum(enum_class=ItemType, target_string=slot[0].attrib["alt"].lower())
        stats = item.xpath(ITEM_STATS_XPATH)
        if not stats:
            Logger.error(f"No stats found for {slot=}")
            continue
        affixes = []
        inherents = []
        for stat in stats:
            if stat.xpath(TEMPERING_ICON_XPATH):
                continue
            if "filled" not in stat.xpath("../..")[0].attrib["class"]:
                continue
            affix_name = stat.xpath("./span")[0].text
            if "Weapon" in slot and (x := _fix_weapon_type(affix_name)) is not None:
                item_type = x
                continue
            if "Offhand" in slot and (x := _fix_offhand_type(input_str=affix_name, class_str=class_name)) is not None:
                item_type = x
                continue
            affix_obj = Affix(name=closest_match(clean_str(_corrections(input_str=affix_name)).strip().lower(), Dataloader().affix_dict))
            if affix_obj.name is None:
                Logger.error(f"Couldn't match {affix_name=}")
                continue
            if (("Ring" in slot or "Amulet" in slot) and "%" in affix_name) or "Boots" in slot and "Max Evade Charges" in affix_name:
                inherents.append(affix_obj)
            else:
                affixes.append(affix_obj)
        item_type = (
            match_to_enum(enum_class=ItemType, target_string=re.sub(r"\d+", "", slot.replace(" ", ""))) if item_type is None else item_type
        )
        if item_type is None:
            Logger.warning(f"Couldn't match item_type: {slot}. Please edit manually")
        item_filter.itemType = [item_type] if item_type is not None else []
        item_filter.affixPool = [
            AffixFilterCountModel(
                count=[AffixFilterModel(name=x.name) for x in affixes],
                minCount=2,
                minGreaterAffixCount=0,
            )
        ]
        if inherents:
            item_filter.inherentPool = [AffixFilterCountModel(count=[AffixFilterModel(name=x.name) for x in inherents])]
        filter_name_template = item_filter.itemType[0].name if item_filter.itemType else slot.replace(" ", "")
        filter_name = filter_name_template
        i = 2
        while any(filter_name == next(iter(x)) for x in finished_filters):
            filter_name = f"{filter_name_template}{i}"
            i += 1
        finished_filters.append({filter_name: item_filter})
    profile = ProfileModel(name="imported profile", Affixes=sorted(finished_filters, key=lambda x: next(iter(x))))
    save_as_profile(
        file_name=f"d4build_{class_name}_{datetime.datetime.now(tz=datetime.UTC).strftime("%Y_%m_%d_%H_%M_%S")}", profile=profile, url=url
    )
    Logger.info("Finished")


def _corrections(input_str: str) -> str:
    match input_str.lower():
        case "max life":
            return "maximum life"
    return input_str


def _fix_offhand_type(input_str: str, class_str: str) -> ItemType | None:
    input_str = input_str.lower()
    class_str = class_str.lower()
    if "offhand" not in input_str:
        return None
    if "sorc" in class_str:
        return ItemType.Focus
    if "druid" in class_str:
        return ItemType.OffHandTotem
    if "necro" in class_str:
        if "cooldown reduction" in input_str:
            return ItemType.Focus
        return ItemType.Shield
    return None


def _fix_weapon_type(input_str: str) -> ItemType | None:
    input_str = input_str.lower()
    if "1h mace" in input_str:
        return ItemType.Mace
    if "2h mace" in input_str:
        return ItemType.Mace2H
    if "1h sword" in input_str:
        return ItemType.Sword
    if "2h sword" in input_str:
        return ItemType.Sword2H
    if "1h axe" in input_str:
        return ItemType.Axe
    if "2h axe" in input_str:
        return ItemType.Axe2H
    if "scythe" in input_str:
        return ItemType.Scythe
    if "2h scythe" in input_str:
        return ItemType.Scythe2H
    if "crossbow" in input_str:
        return ItemType.Crossbow2H
    if "wand" in input_str:
        return ItemType.Wand
    return None


def _get_non_unique_slots(data: lxml.html.HtmlElement) -> list[str]:
    result = []
    paperdoll = data.xpath(PAPERDOLL_XPATH)
    if not paperdoll:
        Logger.error(msg := "No paperdoll found")
        raise D4BuildsException(msg)
    items = paperdoll[0].xpath(PAPERDOLL_ITEM_XPATH)
    if not items:
        Logger.error(msg := "No items found")
        raise D4BuildsException(msg)
    for item in items:
        if not item.xpath(UNIQUE_ICON_XPATH):
            slot = item.xpath(PAPERDOLL_ITEM_SLOT_XPATH)
            result.append(slot[0].text)
    return result


if __name__ == "__main__":
    Logger.init("debug")
    os.chdir(pathlib.Path(__file__).parent.parent.parent.parent)
    URLS = [
        "https://mobalytics.gg/diablo-4/builds/sorcerer/firewall-scorched-earth",
    ]
    for x in URLS:
        import_mobalytics(url=x)
