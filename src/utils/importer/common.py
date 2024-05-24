from logger import Logger
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver

from config.loader import IniConfigLoader
from config.models import BrowserType


def retry_importer(func):
    def wrapper(*args, **kwargs):
        if "driver" not in kwargs and not args:
            kwargs["driver"] = setup_webdriver()
        for _ in range(5):
            try:
                func(*args, **kwargs)
                break
            except Exception as e:
                Logger.error(f"An error occurred importing the build {e}. retrying")

    return wrapper


def setup_webdriver() -> ChromiumDriver:
    match IniConfigLoader().general.browser:
        case BrowserType.edge:
            options = webdriver.EdgeOptions()
            options.add_argument("--headless=new")
            driver = webdriver.Edge(options=options)
        case BrowserType.chrome:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options)
        case BrowserType.firefox:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
    return driver  # noqa # It must be one of the 3 browsers due to ini validation
