import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def no_real_chrome():
    """
    Safety net: patch Selenium's Chrome and ChromeService at the source so a
    real Chromium process can NEVER be launched during any test, even if a test
    forgets to patch get_chrome_driver().

    Individual tests that apply their own @patch decorators will override this
    safely — the inner patch always takes precedence over the outer one.
    """
    with patch("selenium.webdriver.Chrome", return_value=MagicMock()), \
         patch("selenium.webdriver.ChromeService", return_value=MagicMock()):
        yield
