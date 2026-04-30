import os
import pytest
from unittest.mock import MagicMock, patch

# Ensure tests never use real credentials or API keys from backend/.env.
# This override happens before pytest collects test modules, so imports
# that call os.getenv() during module import use safe dummy values.
for key, value in {
    "CODA_API_KEY": "test-coda-key",
    "CODA_DOC_ID": "test-doc-id",
    "BAL_CODA_DOC_ID": "test-bal-doc-id",
    "BKMS_ID": "test-bkms-id",
    "BKMS_EMAIL": "test@example.com",
    "BKMS_PASSWORD": "test-pass",
    "BKMS_ACCESS_TYPE": "RegionalAdmin",
    "MAIN_GROUP_TELEGRAM_TOKEN": "fake-main-token",
    "MAIN_GROUP_TELEGRAM_CHAT_ID": "fake-main-chat",
    "SAT_K1_TELEGRAM_TOKEN": "fake-sat-k1-token",
    "SAT_K1_TELEGRAM_CHAT_ID": "fake-sat-k1-chat",
    "SAT_K2_TELEGRAM_TOKEN": "fake-sat-k2-token",
    "SAT_K2_TELEGRAM_CHAT_ID": "fake-sat-k2-chat",
    "SUN_K1_TELEGRAM_TOKEN": "fake-sun-k1-token",
    "SUN_K1_TELEGRAM_CHAT_ID": "fake-sun-k1-chat",
    "SUN_K2_TELEGRAM_TOKEN": "fake-sun-k2-token",
    "SUN_K2_TELEGRAM_CHAT_ID": "fake-sun-k2-chat",
    "SATURDAY_K1_TABLE_ID": "table-test-sat-k1",
    "SATURDAY_K2_TABLE_ID": "table-test-sat-k2",
    "SUNDAY_K1_TABLE_ID": "table-test-sun-k1",
    "SUNDAY_K2_TABLE_ID": "table-test-sun-k2",
    "SATURDAY_BAL_GROUP_0_TABLE_ID": "table-test-sat-bal-0",
    "SATURDAY_BAL_GROUP_1_TABLE_ID": "table-test-sat-bal-1",
    "SATURDAY_BAL_GROUP_2A_TABLE_ID": "table-test-sat-bal-2a",
    "SATURDAY_BAL_GROUP_2B_TABLE_ID": "table-test-sat-bal-2b",
    "SATURDAY_BAL_GROUP_3_TABLE_ID": "table-test-sat-bal-3",
    "SUNDAY_BAL_GROUP_0_TABLE_ID": "table-test-sun-bal-0",
    "SUNDAY_BAL_GROUP_1_TABLE_ID": "table-test-sun-bal-1",
    "SUNDAY_BAL_GROUP_2A_TABLE_ID": "table-test-sun-bal-2a",
    "SUNDAY_BAL_GROUP_2B_TABLE_ID": "table-test-sun-bal-2b",
    "SUNDAY_BAL_GROUP_3_TABLE_ID": "table-test-sun-bal-3",
    "GOSHTHI_9_10_TABLE_ID": "table-test-goshthi-9-10",
    "GOSHTHI_11_12_TABLE_ID": "table-test-goshthi-11-12",
    "GOSHTHI_COLLEGE_1_2_TABLE_ID": "table-test-goshthi-college-1-2",
    "GOSHTHI_COLLEGE_3_4_TABLE_ID": "table-test-goshthi-college-3-4",
}.items():
    os.environ[key] = value


def _instant_wait(driver, timeout):
    """WebDriverWait replacement that executes the condition once and returns immediately."""
    class _Instant:
        def until(self, condition):
            try:
                return condition(driver)
            except Exception:
                return None
        def until_not(self, condition):
            try:
                return not condition(driver)
            except Exception:
                return None
    return _Instant()


@pytest.fixture(autouse=True)
def no_real_chrome():
    """
    Safety net: patch Selenium's Chrome and ChromeService at the source so a
    real Chromium process can NEVER be launched during any test, even if a test
    forgets to patch get_chrome_driver(). Also patches WebDriverWait to avoid
    real polling timeouts.

    Individual tests that apply their own @patch decorators will override this
    safely — the inner patch always takes precedence over the outer one.
    """
    mock_driver = MagicMock()
    mock_driver.execute_script.return_value = "complete"
    with patch("selenium.webdriver.Chrome", return_value=mock_driver), \
         patch("selenium.webdriver.ChromeService", return_value=MagicMock()), \
         patch("backend.bal_mandal.WebDriverWait", side_effect=_instant_wait):
        yield
