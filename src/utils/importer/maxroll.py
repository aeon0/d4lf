import datetime
import os
import pathlib
import re
import time

from logger import Logger
from pydantic_yaml import to_yaml_str
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils.importer.common import retry_importer, setup_webdriver

from config.loader import IniConfigLoader
from config.models import AffixFilterCountModel, AffixFilterModel, ItemFilterModel, ProfileModel

MAXROLL_PLANNER_URL = "maxroll.gg/d4/planner"
MAXROLL_BUILD_GUIDE_URL = "maxroll.gg/d4/build-guides/"

ACTIVE_ITEM_CLASS = "d4t-active"
ADBLOCK_BUTTON_XPATH = "//*[contains(text(), 'No Thanks')]"
BUILD_PLANNER_CLASS = "d4t-PlannerLink"
BUILD_PLANNER_OVERVIEW_CLASS = "d4t-Paperdoll"
COOKIE_ACCEPT_XPATH = "//*[@class='ncmp__btn']"
DIABLO_CLASS_NAME_CLASS = "d4t-ClassSelect"
ITEM_AFFIXES_XPATH = "//*[contains(@class, 'd4t-affix-category')]//h3[text()='Modifiers']/../*[@class='d4t-item-mods']"
ITEM_INHERENT_XPATH = "//*[contains(@class, 'd4t-affix-category')]//h3[text()='Implicit Modifiers']/../*[@class='d4t-item-mods']"
ITEM_LIBRARY_CLASS = "d4t-ItemLibrary"
ITEM_NAME_CLASS = "d4t-header-title"
ITEM_RARITY_CLASS = "d4t-item-options"
ITEM_SLOT_CLASS = "d4t-slot"
ITEM_TEMPERING_XPATH = "//*[contains(@class, 'd4t-affix-category')]//h3[text()='Tempering']/../*[@class='d4t-item-mods']"
ITEM_TYPE_CLASS = "d4t-category-header"
PARENT_XPATH = "./../.."
PLANNER_LABEL_CLASS = "d4t-label"
PLANNER_LABEL_NAME = "d4t-name"
TITLE_CLASS = "d4t-title"


@retry_importer
def import_build(driver: ChromiumDriver = None, url: str = None):
    if not url:
        Logger.info("Paste maxroll.gg build guide or planner build here ie https://maxroll.gg/d4/build-guides/minion-necromancer-guide")
        url = input()
        url = url.replace(" ", "")
    if MAXROLL_PLANNER_URL not in url and MAXROLL_BUILD_GUIDE_URL not in url:
        Logger.error("Invalid url, please use a d4 planner build on MaxRoll.gg")
        return
    wait = WebDriverWait(driver, 10)
    Logger.info(f"Loading {url}")
    driver.get(url)
    _handle_popups(driver)
    filter_name = ""
    if MAXROLL_BUILD_GUIDE_URL in url:
        filter_name = driver.title.replace(" - D4 Maxroll.gg", "").replace("/", "_").replace(" ", "_")
        original_window = driver.current_window_handle
        driver.find_element(By.CLASS_NAME, BUILD_PLANNER_CLASS).click()
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                time.sleep(1)
                break
    planner = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, BUILD_PLANNER_OVERVIEW_CLASS)))
    item_slots = planner.find_elements(By.CLASS_NAME, ITEM_SLOT_CLASS)

    filter_class = driver.find_element(By.CLASS_NAME, DIABLO_CLASS_NAME_CLASS).text.replace(" ", "_")
    filter_label = driver.find_element(By.CLASS_NAME, PLANNER_LABEL_CLASS).text.replace("/", "_").replace(" ", "_")

    # if we didn't get a filter name from the build guide
    if not filter_name:
        # use the name of the planner
        try:
            filter_name = driver.find_element(By.CLASS_NAME, PLANNER_LABEL_NAME).text.replace("/", "_").replace(" ", "_")
        except NoSuchElementException:
            # fall back to the class name
            filter_name = filter_class

    Logger.info(f"Importing {filter_name} {filter_label}")

    item_dict = {}
    for item in item_slots:
        item.click()
        # we click the d4 planner title on the page after we select an item so that the popup closes
        driver.find_element(By.CLASS_NAME, TITLE_CLASS).click()

        # skip uniques for now, need to figure out a better way to grab these
        try:
            item_options = driver.find_element(By.CLASS_NAME, ITEM_RARITY_CLASS)
        except NoSuchElementException:
            continue
        if item_options.text.startswith("Unique"):
            Logger.warning(f"Skipping {driver.find_element(By.CLASS_NAME, ITEM_NAME_CLASS).text} unique importing currently unsupported")
            continue

        item_type = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, ITEM_TYPE_CLASS))).text
        if item_type in item_dict:
            # 2nd ring
            item_type += "2"

        if item_type == "Weapon" or item_type == "Equipment":
            # if this is just "Weapon" then the planner uses different builds at different stages of the build, so we find the active weapon for this current version of the build, and grab the name of the weapon type
            item_type = (
                driver.find_element(By.CLASS_NAME, ITEM_LIBRARY_CLASS)
                .find_element(By.CLASS_NAME, ACTIVE_ITEM_CLASS)
                .find_element(By.XPATH, PARENT_XPATH)
                .find_element(By.CLASS_NAME, ITEM_TYPE_CLASS)
                .text
            )

        item_affixes = driver.find_elements(By.XPATH, ITEM_AFFIXES_XPATH)
        # normally means we've clicked the 2nd weapon slot when we've got a two-handed sword
        if not item_affixes:
            continue
        item_inherents = driver.find_elements(By.XPATH, ITEM_INHERENT_XPATH)
        item_tempering = driver.find_elements(By.XPATH, ITEM_TEMPERING_XPATH)

        item_details = {
            "affixes": _translate_modifiers(item_affixes),
            "inherents": _translate_modifiers(item_inherents),
            "tempering": _translate_modifiers(item_tempering),
        }

        item_dict[item_type] = item_details

    driver.quit()
    filter_obj = _convert_to_filter(filter_class, item_dict)
    save_path = IniConfigLoader().user_dir / f"profiles/{filter_name}_{filter_label}.yaml"
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(f"# {url}\n")
        file.write(f"# {datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")}\n")
        file.write(
            to_yaml_str(
                filter_obj,
                default_flow_style=None,
                exclude_unset=not IniConfigLoader().general.full_dump,
                exclude=["name", "Sigils", "Uniques"],
            )
        )
    Logger.info(f"Created profile {save_path}")


def _convert_to_filter(filter_class: str, items) -> ProfileModel:
    items_filters = []
    for item_type, data in items.items():
        name = f"{filter_class}{item_type}".replace(" ", "")
        item_filter = ItemFilterModel(itemType=[item_type.replace("2", "").lower()])
        item_filter.affixPool = [
            AffixFilterCountModel(count=[AffixFilterModel(name=i) for i in data["affixes"]], minCount=2, minGreaterAffixCount=0)
        ]
        if data["inherents"]:
            item_filter.inherentPool = [AffixFilterCountModel(count=[AffixFilterModel(name=i) for i in data["inherents"]])]
        items_filters.append({name: item_filter})
    return ProfileModel(name="imported profile", Affixes=items_filters)


def _handle_popups(driver):
    wait = WebDriverWait(driver, 5)
    clicked = 0
    while clicked < 2:
        try:
            elem = wait.until(
                EC.any_of(
                    EC.element_to_be_clickable((By.XPATH, ADBLOCK_BUTTON_XPATH)),
                    EC.element_to_be_clickable((By.XPATH, COOKIE_ACCEPT_XPATH)),
                )
            )
        except TimeoutException:
            break
        elem.click()
        clicked += 1
        time.sleep(1)


def _remove_extra_underscores(string: str) -> str:
    return re.sub(r"(_)\1+", r"\1", string)


def _translate_modifiers(mods: list[WebElement]) -> list[str]:
    translated_mods = []
    if not mods:
        return []
    properties = mods[0].find_elements(By.CLASS_NAME, "d4t-property")
    for mod in properties:
        translated_mods += [
            _remove_extra_underscores(re.sub(r"[0-9]|,|\.|\+|\[|\]|-|%|:|'", "", mod.text).lower().strip().replace(" ", "_"))
        ]

    return translated_mods


if __name__ == "__main__":
    os.curdir = pathlib.Path(__file__).parent.parent.parent
    driver = setup_webdriver()
    import_build(url="https://maxroll.gg/d4/planner/xu2az0w2")
