import datetime
import functools
import time
from collections.abc import Callable
from typing import Literal, TypeVar

import requests
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


def format_number_as_short_string(n: int) -> str:
    result = n / 1_000_000
    return f"{int(result)}M" if result.is_integer() else f"{result:.2f}M"


def get_with_retry(url: str) -> requests.Response:
    for _ in range(5):
        r = requests.get(url)
        if r.status_code == 200:
            return r
        Logger.debug(f"Request {url} failed with status code {r.status_code}, retrying...")
    else:
        Logger.error(msg := f"Failed to get a successful response after 5 attempts: {url=}")
        raise ConnectionError(msg)


def handle_popups(driver: ChromiumDriver, method: Callable[[D], Literal[False] | T], timeout=10):
    Logger.info("Handling cookie / adblock popups")
    wait = WebDriverWait(driver, timeout)
    for _ in range(3):
        try:
            elem = wait.until(method)
        except TimeoutException:
            break
        elem.click()
        time.sleep(1)


def match_to_enum(enum_class, target_string: str, check_keys: bool = False):
    target_string = target_string.casefold().replace(" ", "").replace("-", "")
    for enum_member in enum_class:
        if enum_member.value.casefold().replace(" ", "").replace("-", "") == target_string:
            return enum_member
        if check_keys and enum_member.name.casefold().replace(" ", "").replace("-", "") == target_string:
            return enum_member
    return None


def retry_importer(func=None, inject_webdriver: bool = False):
    def decorator_retry_importer(wrap_function):
        @functools.wraps(wrap_function)
        def wrapper(*args, **kwargs):
            if inject_webdriver and "driver" not in kwargs and not args:
                kwargs["driver"] = setup_webdriver()
            for _ in range(5):
                try:
                    res = wrap_function(*args, **kwargs)
                    if inject_webdriver:
                        kwargs["driver"].quit()
                    return res
                except Exception:
                    Logger.exception("An error occurred while importing. Retrying...")
            return None

        return wrapper

    return decorator_retry_importer if func is None else decorator_retry_importer(func)


def save_as_profile(file_name: str, profile: ProfileModel, url: str):
    file_name = file_name.replace("/", "_").replace(" ", "_").replace("'", "").replace("-", "_")
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
