import os
import re
from pathlib import Path

from item.data.item_type import ItemType
from logger import Logger
from pydantic_yaml import to_yaml_str
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.loader import IniConfigLoader
from config.models import AffixFilterCountModel, AffixFilterModel, Browser, ItemFilterModel, ProfileModel

MAXROLL_PLANNER_URL = "maxroll.gg/d4/planner"
MAXROLL_BUILD_GUIDE_URL = "maxroll.gg/d4/build-guides/"

COOKIE_ACCEPT_BUTTON = "ncmp__btn"
BUILD_PLANNER_CLASS = "d4t-PlannerLink"
BUILD_PLANNER_OVERVIEW_CLASS = "d4t-Paperdoll"
DIABLO_CLASS_NAME_CLASS = "d4t-ClassSelect"
PLANNER_LABEL_CLASS = "d4t-label"
ITEM_SLOT_CLASS = "d4t-slot"
TITLE_CLASS = "d4t-title"
ITEM_TYPE_CLASS = "d4t-category-header"
ITEM_LIBRARY_CLASS = "d4t-ItemLibrary"
ACTIVE_ITEM_CLASS = "d4t-active"
PARENT_XPATH = "./../.."
ITEM_MODIFIERS_CLASS = "d4t-item-mods"
ITEM_RARITY_CLASS = "d4t-item-options"
ITEM_NAME_CLASS = "d4t-header-title"


def import_build():
    Logger.info("Paste maxroll.gg build guide or planner build here ie https://maxroll.gg/d4/build-guides/minion-necromancer-guide")
    url = input()
    if MAXROLL_PLANNER_URL not in url and MAXROLL_BUILD_GUIDE_URL not in url:
        Logger.error("Invalid url, please use a d4 planner build on MaxRoll.gg")
        return
    match IniConfigLoader().general.browser:
        case Browser.edge:
            options = webdriver.EdgeOptions()
            options.add_argument("--headless=new")
            driver = webdriver.Edge(options=options)
        case Browser.chrome:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options)
        case Browser.firefox:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless=new")
            driver = webdriver.Firefox(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, COOKIE_ACCEPT_BUTTON)))
    driver.find_elements(By.CLASS_NAME, COOKIE_ACCEPT_BUTTON)[1].click()
    if MAXROLL_BUILD_GUIDE_URL in url:
        original_window = driver.current_window_handle
        driver.find_element(By.CLASS_NAME, BUILD_PLANNER_CLASS).click()
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
    planner = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, BUILD_PLANNER_OVERVIEW_CLASS)))
    item_slots = planner.find_elements(By.CLASS_NAME, ITEM_SLOT_CLASS)
    item_dict = {}
    item_dict["class"] = driver.find_element(By.CLASS_NAME, DIABLO_CLASS_NAME_CLASS).text
    filter_label = driver.find_element(By.CLASS_NAME, PLANNER_LABEL_CLASS).text
    Logger.info(f"Importing {item_dict["class"]} {filter_label} build")

    for item in item_slots:
        item.click()
        driver.find_element(
            By.CLASS_NAME, TITLE_CLASS
        ).click()  # we click the d4 planner title on the page after we select an item so that the popup closes
        item_type = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, ITEM_TYPE_CLASS))).text
        if item_type == "Weapon" or item_type == "Equipment":
            # if this is just "Weapon" then the planner uses different builds at different stages of the build, so we find the active weapon for this current version of the build, and grab the name of the weapon type
            item_type = (
                driver.find_element(By.CLASS_NAME, ITEM_LIBRARY_CLASS)
                .find_element(By.CLASS_NAME, ACTIVE_ITEM_CLASS)
                .find_element(By.XPATH, PARENT_XPATH)
                .find_element(By.CLASS_NAME, ITEM_TYPE_CLASS)
                .text
            )
        item_properties = driver.find_elements(By.CLASS_NAME, ITEM_MODIFIERS_CLASS)
        try:
            item_options = driver.find_element(By.CLASS_NAME, ITEM_RARITY_CLASS)
        except NoSuchElementException:
            continue
        # skip uniques for now, need to figure out a better way to grab these
        if item_options.text.startswith("Unique"):
            Logger.warning(f"Skipping {driver.find_element(By.CLASS_NAME, ITEM_NAME_CLASS).text} unique importing currently unsupported")
            continue
        item_details = {}
        item_details["implicits"] = ""
        if item_type.lower() != ItemType.Helm.value and item_type.lower() != ItemType.ChestArmor.value and item_type.lower() != ItemType.Gloves.value:
            item_details["implicits"] = _translate_modifiers(item_properties[0]) if len(item_properties) > 0 else ""
            item_properties = item_properties[1:]
        item_details["mods"] = _translate_modifiers(item_properties[0]) if len(item_properties) > 0 else ""
        if item_details["mods"] == "":
            # normally means we've clicked the 2nd weapon slot when we've got a two-handed sword
            continue
        # commenting out for now, but leaving here to sort in the future
        # item_details["tempers"] = item_properties[1] if len(item_properties) > 1 else ""
        # item_details["aspect"] = item_properties[2] if len(item_properties) > 2 else ""
        # item_details["gems"] = item_properties[3] if len(item_properties) > 3 else ""
        if item_type in item_dict:
            # 2nd ring
            item_type += "2"
        item_dict[item_type] = item_details

    driver.quit()
    filter_obj = _convert_to_filter(item_dict)
    filter_label = filter_label.replace("/", "_").replace(" ", "_")
    with open(f"{Path(f"{os.path.expanduser("~")}/.d4lf")}/profiles/{item_dict["class"]} {filter_label}.yaml", "w") as file:
        file.write(
            to_yaml_str(filter_obj, default_flow_style=None)[:-10]
        )  # This exports the name at the end, which causes an error when we load it back in, so just strip this for now

    Logger.info(f"Created profile {Path(f"{os.path.expanduser("~")}/.d4lf")}\\profiles\\{item_dict["class"]} {filter_label}.yaml")


def _translate_modifiers(mods):
    translated_mods = []
    mods = mods.find_elements(By.CLASS_NAME, "d4t-property")
    for mod in mods:
        translated_mods += [_remove_extra_underscores(re.sub(r"[0-9]|,|\.|\+|\[|\]|-|%|:", "", mod.text).lower().strip().replace(" ", "_"))]

    return translated_mods


def _remove_extra_underscores(string: str) -> str:
    return re.sub(r"(_)\1+", r"\1", string)


def _convert_to_filter(items: dict[str, str]) -> ProfileModel:
    return ProfileModel(
        name="",  # This causes an error when we export it and then try and load it back in, but also errors if we don't have it here
        Affixes=[
            {
                (f"{items['class']}{key}").replace(" ", ""): ItemFilterModel(
                    # replace that ring2 back to just ring
                    itemType=[key.replace("2", "").lower()],
                    affixPool=[AffixFilterCountModel(count=[AffixFilterModel(name=i) for i in items[key]["mods"]], minCount=2)],
                )
            }
            for key in list(items.keys())[1:]
        ],
    )
