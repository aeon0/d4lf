import os
import pathlib

from logger import Logger
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from utils.importer.common import retry_importer, setup_webdriver

DIABLO_TRADE_BASE_URL = "https://diablo.trade/listings/"
DIABLO_TRADE_LISTING_XPATH = "//*[contains(@class, 'WTS')]"


@retry_importer
def import_diablo_trade(driver: ChromiumDriver = None, url: str = None):
    if not url:
        Logger.info("Paste diablo.trade filter here ie https://diablo.trade/listings/items?rarity=legendary")
        url = input()
        url = url.replace(" ", "")
    if DIABLO_TRADE_BASE_URL not in url:
        Logger.error("Invalid url, please use a diablo.trade filter")
        return
    wait = WebDriverWait(driver, 10)
    Logger.info(f"Loading {url}")
    driver.get(url)
    # TODO loop over all pages here
    listings = driver.find_elements(By.XPATH, DIABLO_TRADE_LISTING_XPATH)
    for listing in listings:
        print(listing)


if __name__ == "__main__":
    os.curdir = pathlib.Path(__file__).parent.parent.parent
    driver = setup_webdriver()
    import_diablo_trade(url="https://maxroll.gg/d4/planner/xu2az0w2")
