import os

import undetected_chromedriver
from retry import retry
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.exceptions import NewConnectionError, MaxRetryError
from webdriver_manager.chrome import ChromeDriverManager


def get_driver() -> WebDriver:
    driver_kind: str = os.environ["SELENIUM_DRIVER_KIND"].lower()
    if driver_kind == "remote":
        return get_remote_driver()
    elif driver_kind == "chrome":
        return get_chrome_driver()
    else:
        raise RuntimeError(
            "Getting driver for " + driver_kind + " is not implemented yet."
        )


@retry(MaxRetryError, tries=5, delay=3)
def get_remote_driver() -> WebDriver:
    remote_host: str = os.getenv('REMOTE_DRIVER_HOST', 'localhost').lower()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-smooth-scrolling")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor=f"http://{remote_host}:3000/webdriver",
        options=options,
    )

    return driver


def get_antybot_chrom_driver() -> WebDriver:
    return undetected_chromedriver.Chrome()


def get_chrome_driver() -> WebDriver:
    options = Options()
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')
    options.add_argument("--disable-smooth-scrolling")
    options.add_argument("--disable-blink-features=AutomationControlled")

    chrome_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    chrome_driver.maximize_window()
    return chrome_driver
