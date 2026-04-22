from pathlib import Path
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService


def get_chrome_driver():
    """Set up and return a Chrome WebDriver instance.

    Uses webdriver-manager to automatically handle chromedriver,
    working consistently across all environments (local and Docker).
    """
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1600,1000")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    chrome_binary = _chrome_binary()
    if chrome_binary:
        chrome_options.binary_location = chrome_binary

    service = _auto_service()
    if service is None:
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.maximize_window()
    except Exception:
        # Some environments ignore maximize requests; the window-size arg above is the fallback.
        pass
    return driver


def _auto_service() -> ChromeService | None:
    """Return a Service using chromedriver from PATH, or let Selenium manage it."""
    if shutil.which("chromedriver"):
        return ChromeService()
    return None


def _chrome_binary() -> str | None:
    chrome_app = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if chrome_app.exists():
        return str(chrome_app)
    return None
