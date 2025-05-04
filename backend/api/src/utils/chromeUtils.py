from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

def get_chrome_driver():
    """Set up and return a Chrome WebDriver instance."""
    # Set a custom cache directory
    cache_dir = "/tmp/selenium_cache"
    os.makedirs(cache_dir, exist_ok=True)

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={cache_dir}")

    # Initialize the Chrome driver
    service = Service()  # Add path to chromedriver if needed
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver