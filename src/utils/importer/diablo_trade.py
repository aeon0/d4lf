import dataclasses
import datetime
import os
import pathlib

import lxml.html
from dataloader import Dataloader
from item.data.affix import Affix
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.descr.text import clean_str, closest_match, find_number
from logger import Logger
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils.importer.common import (
    extract_digits,
    find_enum_key,
    format_number_as_short_string,
    handle_popups,
    retry_importer,
    save_as_profile,
    setup_webdriver,
)

from config.models import AffixFilterCountModel, AffixFilterModel, ItemFilterModel, ProfileModel

AFFIXES_XPATH = ".//*[contains(@class, 'group-data-[search=true]:font-bold')]"
BASE_URL = "diablo.trade/listings/"
COOKIE_ACCEPT_XPATH = "//*[@class='ncmp__btn']"
EXACT_PRICE_TEXT = "Exact Price"
ITEM_POWER_TEXT = "Item Power"
LEGENDARY_TEXT_CLASS = "text-legendary"
LISTING_XPATH = "//*[contains(@class, 'WTS')]"
NEXT_BUTTON_XPATH = "//*[@aria-label='next page']"  # last page: aria-disabled="true"
PRICE_BUTTON_TEXT_XPATH = ".//h6"
PRICE_BUTTON_VALUE_XPATH = ".//h4"
RARITY_TYPE_POWER_XPATH = ".//div[@data-rarity]//span[contains(@class, 'text-shadow')]"


@dataclasses.dataclass
class _AnnotatedFilter:
    filter: ItemFilterModel | None = None
    max_price: int | None = None
    min_price: int | None = None


@dataclasses.dataclass
class _Listing:
    affixes: list[Affix] | None = None
    inherents: list[Affix] | None = None
    item_power: int = 0
    item_rarity: ItemRarity | None = None
    item_type: ItemType | None = None
    price: int = 0


@retry_importer
def import_diablo_trade(url: str, max_listings: int, driver: ChromiumDriver = None):
    url = url.strip().replace("\n", "")
    if BASE_URL not in url:
        Logger.error("Invalid url, please use a diablo.trade filter")
        return
    Logger.info(f"Loading {url}")
    all_listings = []
    finished = False
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    handle_popups(driver=driver, method=EC.any_of(EC.element_to_be_clickable((By.XPATH, COOKIE_ACCEPT_XPATH))))
    while not finished:
        for _ in range(5):
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, LISTING_XPATH)))
                break
            except TimeoutException:
                driver.refresh()
        else:
            Logger.error("No listings found, cancelling...")
            break
        page_source: lxml.html.HtmlElement = lxml.html.fromstring(driver.page_source)
        listings = page_source.xpath(LISTING_XPATH)
        for listing in listings:
            listing_obj = _Listing()
            if (price := _get_price(listing)) is None:
                Logger.debug("Price not found")
                continue
            listing_obj.price = price
            if (res := _get_item_type_rarity_power(listing)) is None:
                Logger.debug("Item type, rarity or power not found")
                continue
            listing_obj.item_type = res[0]
            listing_obj.item_rarity = res[1]
            listing_obj.item_power = res[2]
            if (res := _get_affixes(listing)) is None:
                Logger.debug("Affixes not found")
                continue
            listing_obj.affixes = res[0]
            listing_obj.inherents = res[1]
            all_listings.append(listing_obj)
        Logger.info(f"Fetched {len(all_listings)} listings")
        if len(all_listings) >= max_listings:
            finished = True
        for _ in range(5):
            try:
                elem = driver.find_element(by=By.XPATH, value=NEXT_BUTTON_XPATH)
                break
            except NoSuchElementException:
                pass
        else:
            Logger.error("Next button not found")
            break
        if "true" in elem.get_attribute("aria-disabled"):
            finished = True
        else:
            elem.click()
    driver.quit()
    filters = _create_filters_from_items(items=all_listings)
    profile = ProfileModel(name="diablo_trade", Affixes=filters)
    save_as_profile(
        file_name=f"diablo_trade_{datetime.datetime.now(tz=datetime.UTC).strftime("%Y_%m_%d_%H_%M_%S")}", profile=profile, url=url
    )


def _create_filters_from_items(items: list[_Listing]) -> list[dict[str, ItemFilterModel]]:
    to_check = items.copy()
    result = []
    for item in items.copy():
        if item not in to_check:
            continue
        to_check.remove(item)
        annotated_filter = _AnnotatedFilter(
            max_price=item.price,
            min_price=item.price,
            filter=ItemFilterModel(
                minPower=item.item_power,
                itemType=[item.item_type],
                affixPool=[AffixFilterCountModel(count=[AffixFilterModel(name=x.name, value=x.value) for x in item.affixes])],
                # inherentPool=[AffixFilterCountModel(count=[AffixFilterModel(name=x.name, value=x.value) for x in item.inherents])],
            ),
        )
        to_delete = []
        for to_check_item in [x for x in to_check if x.item_type in annotated_filter.filter.itemType]:
            annotated_filter_affixes = [(x.name, x.value) for x in annotated_filter.filter.affixPool[0].count]
            to_check_item_affixes = [(x.name, x.value) for x in to_check_item.affixes]
            for x in annotated_filter_affixes:
                if not any(a[0] == x[0] for a in to_check_item_affixes):
                    break
            else:
                to_delete.append(to_check_item)
                annotated_filter.min_price = min(annotated_filter.min_price, to_check_item.price)
                annotated_filter.max_price = max(annotated_filter.max_price, to_check_item.price)
                for x in annotated_filter.filter.affixPool[0].count:
                    for y in [a for a in to_check_item.affixes if x.name == a.name]:
                        x.value = min(x.value, y.value)
        for to_delete_item in to_delete:
            to_check.remove(to_delete_item)
        result.append(annotated_filter)
    converted_result = []
    for annotated_filter in result:
        name = f"{annotated_filter.filter.itemType[0].value}_{format_number_as_short_string(annotated_filter.min_price)}"
        if annotated_filter.min_price != annotated_filter.max_price:
            name += f"_{format_number_as_short_string(annotated_filter.max_price)}"
        # if there is a dict with this key name already in the list, append a number to the key name using change_key_of_dict
        suffixed_name = name
        i = 2
        while any(suffixed_name in x for x in converted_result):
            suffixed_name = f"{name}_{i}"
            i += 1
        converted_result.append({suffixed_name: annotated_filter.filter})
    return sorted(converted_result, key=lambda x: next(iter(x)))


def _create_affix_from_string(affix_str: str) -> Affix | None:
    name = closest_match(clean_str(affix_str).replace("?", "").strip().lower(), Dataloader().affix_dict)
    return Affix(name=name, value=find_number(affix_str)) if name is not None else None


def _get_affixes(html_element: lxml.html.HtmlElement) -> tuple[list[Affix], list[Affix]] | None:
    lines = html_element.xpath(AFFIXES_XPATH)
    lines = [x for x in lines if LEGENDARY_TEXT_CLASS not in x.attrib["class"]]  # remove legendary affixes
    if len(lines) < 3:
        return None
    affixes = []
    inherents = []
    for line in lines[-3:]:  # last 3 lines should be affixes
        if (affix := _create_affix_from_string(line.text)) is None:
            return None
        affixes.append(affix)
    for line in lines[:-3]:  # all other lines should be inherent affixes
        if (affix := _create_affix_from_string(line.text)) is None:
            return None
        inherents.append(affix)
    return affixes, inherents


def _get_item_type_rarity_power(html_element: lxml.html.HtmlElement) -> tuple[ItemType, ItemRarity, int] | None:
    spans = html_element.xpath(RARITY_TYPE_POWER_XPATH)
    item_type, item_rarity, item_power = None, None, None
    for span in spans:
        if ITEM_POWER_TEXT in span.text:
            item_power = extract_digits(span.text)
        else:
            item_rarity = find_enum_key(ItemRarity, span.text)
            item_type = find_enum_key(ItemType, span.text)
    if not all([item_type, item_rarity, item_power]):
        return None
    if item_rarity != ItemRarity.Legendary:
        Logger.error(f"Only legendaries are supported, {item_rarity=}")
        return None
    return item_type, item_rarity, item_power


def _get_price(html_element: lxml.html.HtmlElement) -> int | None:
    price_text: lxml.html.HtmlElement = html_element.xpath(PRICE_BUTTON_TEXT_XPATH)
    if not price_text or price_text[0].text.casefold() != EXACT_PRICE_TEXT.casefold():
        return None
    price_value: lxml.html.HtmlElement = html_element.xpath(PRICE_BUTTON_VALUE_XPATH)
    if not price_value:
        return None
    return extract_digits(price_value[0].text)


if __name__ == "__main__":
    Logger.init()
    os.chdir(pathlib.Path(__file__).parent.parent.parent.parent)
    DRIVER = setup_webdriver()
    import_diablo_trade(
        url="https://diablo.trade/listings/items?exactPrice=true&itemType=equipment&price=10000000,9999999999&rarity=legendary",
        max_listings=500,
    )
