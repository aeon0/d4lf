from logger import Logger
from pathlib import Path
import os
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from yaml import dump


def import_build():
    Logger.info(f"Paste maxroll.gg build guide or planner build here ie https://maxroll.gg/d4/build-guides/minion-necromancer-guide")
    url = input()
    if "maxroll.gg/d4/planner" not in url and "maxroll.gg/d4/build-guides/" not in url:
        Logger.info(f"Invalid url, please use a d4 planner build on MaxRoll.gg")
        return
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ncmp__btn")))
    driver.find_elements(By.CLASS_NAME, "ncmp__btn")[1].click()
    if "maxroll.gg/d4/build-guides/" in url:
        original_window = driver.current_window_handle
        driver.find_element(By.CLASS_NAME, "d4t-PlannerLink").click()
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
    planner = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "d4t-Paperdoll")))
    item_slots = planner.find_elements(By.CLASS_NAME, "d4t-slot")
    item_dict = {}
    item_dict["class"] = driver.find_element(By.CLASS_NAME, "d4t-ClassSelect").text
    filter_label = driver.find_element(By.CLASS_NAME, "d4t-label").text
    Logger.info(f"Importing {item_dict["class"]} {filter_label} build")

    for item in item_slots:
        item.click()
        driver.find_element(By.CLASS_NAME, "d4t-title").click()
        item_type = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "d4t-category-header"))).text
        if item_type == "Weapon" or item_type == "Equipment":
            # if this is just "Weapon" then the planner uses different builds at different stages of the build, so we find the active weapon for this current version of the build, and grab the name of the weapon type
            item_type = (
                driver.find_element(By.CLASS_NAME, "d4t-ItemLibrary")
                .find_element(By.CLASS_NAME, "d4t-active")
                .find_element(By.XPATH, "./../..")
                .find_element(By.CLASS_NAME, "d4t-category-header")
                .text
            )
        item_properties = driver.find_elements(By.CLASS_NAME, "d4t-item-mods")
        try:
            item_options = driver.find_element(By.CLASS_NAME, "d4t-item-options")
        except NoSuchElementException:
            continue
        # skip uniques for now, need to figure out a better way to grab these
        if item_options.text.startswith("Unique"):
            driver.find_element(By.CLASS_NAME, "d4t-header-title").text
            Logger.info(f"Skipping {driver.find_element(By.CLASS_NAME, "d4t-header-title").text} unique importing currently unsupported")
            continue
        item_details = {}
        item_details["implicits"] = ""
        if item_type != "Helm" and item_type != "Chest Armor" and item_type != "Gloves":
            item_details["implicits"] = translate_modifiers(item_properties[0]) if len(item_properties) > 0 else ""
            item_properties = item_properties[1:]
        item_details["mods"] = translate_modifiers(item_properties[0]) if len(item_properties) > 0 else ""
        if item_details["mods"] == "":
            # normally means we've clicked the 2nd weapon slot when we've got a two-handed sword
            continue
        # commenting out for now, but leaving here to sort in the future
        # item_details["tempers"] = item_properties[1] if len(item_properties) > 1 else ""
        # item_details["aspect"] = item_properties[2] if len(item_properties) > 2 else ""
        # item_details["gems"] = item_properties[3] if len(item_properties) > 3 else ""
        item_dict[item_type] = item_details

    driver.quit()
    filter = convert_to_filter(item_dict)
    with open(f"{Path(f"{os.path.expanduser("~")}/.d4lf")}/profiles/{filter_label}.yaml", "w") as file:
        file.write(dump(filter, default_flow_style=None, sort_keys=False))

    print(f"Created profile {Path(f"{os.path.expanduser("~")}/.d4lf")}\\profiles\\{filter_label}.yaml")


def translate_modifiers(mods):
    translated_mods = []
    mods = mods.find_elements(By.CLASS_NAME, "d4t-property")
    for mod in mods:
        translated_mods += [[remove_extra_underscores(re.sub(r"[0-9]|,|\.|\+|\[|\]|-|%", "", mod.text).lower().strip().replace(" ", "_"))]]

    return translated_mods


def remove_extra_underscores(str):
    i = 1
    while i < len(str):
        if str[i] == str[i - 1] and str[i] == "_":
            str = str[:i] + str[(i + 1) :]
            i -= 1
        i += 1

    return str


def convert_to_filter(items):
    filter = {}
    filter["Affixes"] = []
    for key in list(items.keys())[1:]:
        item = items[key]
        filter["Affixes"] += [
            {(f"{items['class']}{key}").replace(" ", ""): {"itemType": key.lower(), "affixPool": [{"count": item["mods"], "minCount": 2}]}}
        ]

    return filter
