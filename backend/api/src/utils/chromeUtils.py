from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

def get_chrome_driver():
    """Set up and return a Chrome WebDriver instance."""
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("detach", True)
    service = ChromeService()
    return webdriver.Chrome(service=service, options=options)