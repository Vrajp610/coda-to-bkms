from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_chrome_driver():
    """Set up and return a Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--kiosk")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("detach", True)
    options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'profile.password_manager_leak_detection': False
    })
    service = webdriver.ChromeService()
    return webdriver.Chrome(service=service, options=options)