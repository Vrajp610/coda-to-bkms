from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import os
from pyppeteer import launch
import asyncio

# def get_chrome_driver():
#     """Set up and return a Chrome WebDriver instance."""
#     # Automatically download and install the correct version of ChromeDriver
#     chromedriver_autoinstaller.install()

#     # Set a custom cache directory
#     cache_dir = "/tmp/selenium_cache"
#     os.makedirs(cache_dir, exist_ok=True)

#     # Configure Chrome options
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument(f"--user-data-dir={cache_dir}")

#     # Initialize the Chrome driver
#     service = Service()  # No need to specify path; chromedriver-autoinstaller handles it
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver

async def get_chrome_browser():
    """Set up and return a Pyppeteer browser instance."""
    browser = await launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--single-process",
            "--disable-extensions",
        ],
    )
    return browser

async def get_page():
    """Return a new page from the Pyppeteer browser."""
    browser = await get_chrome_browser()
    page = await browser.newPage()
    return page, browser