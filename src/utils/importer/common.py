import datetime
import time
from collections.abc import Callable
from typing import Literal, TypeVar

from logger import Logger
from pydantic_yaml import to_yaml_str
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from config.loader import IniConfigLoader
from config.models import BrowserType, ProfileModel

D = TypeVar("D", bound=WebDriver | WebElement)
T = TypeVar("T")


def extract_digits(text: str) -> int:
    return int("".join([char for char in text if char.isdigit()]))


def find_enum_key(enum_class, target_string: str):
    for enum_member in enum_class:
        if enum_member.value.casefold() in target_string.casefold():
            return enum_member
    return None


def format_number_as_short_string(n: int) -> str:
    result = n / 1_000_000
    return f"{int(result)}M" if result.is_integer() else f"{result:.2f}M"


def handle_popups(driver: ChromiumDriver, method: Callable[[D], Literal[False] | T]):
    wait = WebDriverWait(driver, 5)
    for _ in range(10):
        try:
            elem = wait.until(method)
        except TimeoutException:
            break
        elem.click()
        time.sleep(1)


def retry_importer(func):
    def wrapper(*args, **kwargs):
        if "driver" not in kwargs and not args:
            kwargs["driver"] = setup_webdriver()
        for _ in range(5):
            try:
                func(*args, **kwargs)
                break
            except Exception:
                Logger.exception("An error occurred while importing. Retrying...")

    return wrapper


def save_as_profile(file_name: str, profile: ProfileModel, url: str):
    save_path = IniConfigLoader().user_dir / f"profiles/{file_name}.yaml"
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(f"# {url}\n")
        file.write(f"# {datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")}\n")
        file.write(
            to_yaml_str(
                profile,
                default_flow_style=None,
                exclude_unset=not IniConfigLoader().general.full_dump,
                exclude=["name", "Sigils", "Uniques"],
            )
        )
    Logger.info(f"Created profile {save_path}")


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
