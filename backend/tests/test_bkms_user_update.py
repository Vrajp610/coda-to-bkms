import pytest
from unittest.mock import patch, MagicMock, call
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from backend.bkms_user_update import update_users
from backend.utils.constants import (
    CANCEL_BUTTON_XPATH,
    CHECKBOX_XPATH,
    FATHER_FIRST_NAME_XPATH,
    FATHER_LAST_NAME_XPATH,
    MOTHER_FIRST_NAME_XPATH,
    MOTHER_LAST_NAME_XPATH,
)


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    import time
    monkeypatch.setattr(time, "sleep", lambda *_: None)


def make_driver(main_handle="main", extra_handles=None):
    driver = MagicMock()
    driver.current_window_handle = main_handle
    driver.window_handles = [main_handle] + (extra_handles or [])
    driver.current_url = "https://bk.na.baps.org/admin/user/userlist"
    return driver


def make_row(text):
    row = MagicMock()
    cell = MagicMock()
    cell.text = text
    row.find_element.return_value = cell
    return row


def make_error_el():
    el = MagicMock()
    el.is_displayed.return_value = True
    return el


def make_xpath_finder(row_id, active_error_texts=None):
    active = set(active_error_texts or [])
    def side_effect(by, xpath):
        if "tbody/tr" in xpath:
            return [make_row(row_id)]
        for err in active:
            if err in xpath:
                return [make_error_el()]
        return []
    return side_effect


# ──────────────────────────────────────────────
# log callback
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_log_callback_called(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    wait_mock = MagicMock()
    checkbox = MagicMock()
    checkbox.is_selected.return_value = True
    wait_mock.until.return_value = checkbox

    messages = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        driver.find_elements.side_effect = make_xpath_finder("99999")
        update_users(["99999"], log_callback=messages.append)

    assert any("99999" in m for m in messages)


@patch("backend.bkms_user_update.get_chrome_driver")
def test_log_without_callback(mock_get_driver, capsys):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    wait_mock = MagicMock()
    checkbox = MagicMock()
    checkbox.is_selected.return_value = True
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        driver.find_elements.side_effect = make_xpath_finder("99999")
        update_users(["99999"])

    captured = capsys.readouterr()
    assert "99999" in captured.out


# ──────────────────────────────────────────────
# has_error helper
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_has_error_returns_true_for_visible_element(mock_get_driver):
    """has_error returns True when a visible element with the text exists."""
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    wait_mock = MagicMock()
    checkbox = MagicMock()
    checkbox.is_selected.return_value = True
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder("12345", ["Please Select Student Type"])

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Student type missing" in m for m in logs)


# ──────────────────────────────────────────────
# No results / no matching row
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_no_results_skips_user(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = []

    wait_mock = MagicMock()
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["00000"], log_callback=logs.append)

    assert any("No results found" in m for m in logs)


@patch("backend.bkms_user_update.get_chrome_driver")
def test_no_matching_row_skips_user(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = [make_row("11111")]

    wait_mock = MagicMock()
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["99999"], log_callback=logs.append)

    assert any("No row with User ID" in m for m in logs)


# ──────────────────────────────────────────────
# Search field / button / rows errors
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_search_field_error_skips_user(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver

    wait_mock = MagicMock()
    wait_mock.until.side_effect = TimeoutException("timeout")

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Could not find search field" in m for m in logs)


@patch("backend.bkms_user_update.get_chrome_driver")
def test_search_button_error_skips_user(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver

    search_field = MagicMock()
    wait_mock = MagicMock()
    wait_mock.until.return_value = search_field

    def find_element_side(by, xpath):
        if "div[5]/div[2]/input" in str(xpath):  # SEARCH_BUTTON_XPATH
            raise NoSuchElementException("no button")
        return MagicMock()

    driver.find_element.side_effect = find_element_side

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Could not click search button" in m for m in logs)


@patch("backend.bkms_user_update.get_chrome_driver")
def test_rows_exception_skips_user(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver

    wait_mock = MagicMock()
    wait_mock.until.return_value = MagicMock()
    driver.find_elements.side_effect = Exception("DOM error")

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Could not read result rows" in m for m in logs)


# ──────────────────────────────────────────────
# Row cell exception (continue inner loop)
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_row_cell_exception_continues(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver

    bad_row = MagicMock()
    bad_row.find_element.side_effect = NoSuchElementException("no cell")
    driver.find_elements.return_value = [bad_row]

    wait_mock = MagicMock()
    wait_mock.until.return_value = MagicMock()

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("No row with User ID" in m for m in logs)


# ──────────────────────────────────────────────
# Action button not found
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_no_action_button_skips_user(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = [make_row("12345")]

    wait_mock = MagicMock()
    wait_mock.until.return_value = MagicMock()

    def find_element_side(by, xpath):
        if "td[13]" in str(xpath):
            raise NoSuchElementException("no link")
        return MagicMock()

    driver.find_element.side_effect = find_element_side

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("No action button found" in m for m in logs)


# ──────────────────────────────────────────────
# Pre-check: already marked in list view
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_pre_check_already_marked_skips_tab(mock_get_driver):
    """If the list-view checkbox is already checked, skip the user without opening a tab."""
    driver = make_driver()
    driver.window_handles = ["main"]
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = [make_row("12345")]

    # make every find_element return a div whose class contains "checked"
    checked_div = MagicMock()
    checked_div.get_attribute.return_value = "icheckbox_square-blue checked"
    driver.find_element.return_value = checked_div

    wait_mock = MagicMock()
    wait_mock.until.return_value = MagicMock()

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("already marked in list view" in m for m in logs)
    driver.switch_to.window.assert_not_called()


@patch("backend.bkms_user_update.get_chrome_driver")
def test_pre_check_not_marked_proceeds(mock_get_driver):
    """If the list-view checkbox is NOT checked, proceed into the normal flow."""
    driver = make_driver()
    driver.window_handles = ["main"]  # no new tab → triggers 'New tab did not open'
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = [make_row("12345")]

    unchecked_div = MagicMock()
    unchecked_div.get_attribute.return_value = "icheckbox_square-blue"
    driver.find_element.return_value = unchecked_div

    wait_mock = MagicMock()
    wait_mock.until.return_value = MagicMock()

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    # Flow continued past the pre-check — reached the new-tab check
    assert any("New tab did not open" in m for m in logs)


@patch("backend.bkms_user_update.get_chrome_driver")
def test_pre_check_exception_proceeds(mock_get_driver):
    """If the pre-check raises, the normal flow still runs."""
    driver = make_driver()
    driver.window_handles = ["main"]
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = [make_row("12345")]

    from selenium.common.exceptions import NoSuchElementException

    def find_element_side(by, xpath):
        if "td[11]" in xpath:
            raise NoSuchElementException("no cell")
        return MagicMock()

    driver.find_element.side_effect = find_element_side

    wait_mock = MagicMock()
    wait_mock.until.return_value = MagicMock()

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("New tab did not open" in m for m in logs)


# ──────────────────────────────────────────────
# New tab not opened
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_new_tab_not_opened_skips_user(mock_get_driver):
    driver = make_driver()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = [make_row("12345")]
    driver.window_handles = ["main"]  # no new tab

    wait_mock = MagicMock()
    wait_mock.until.return_value = MagicMock()

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("New tab did not open" in m for m in logs)


# ──────────────────────────────────────────────
# Checkbox already checked
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_checkbox_already_checked(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        driver.find_elements.side_effect = [[make_row("12345")]] + [[]] * 10
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("already ticked" in m for m in logs)


# ──────────────────────────────────────────────
# Checkbox unchecked — ticked successfully
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_checkbox_ticked_successfully(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.side_effect = [False, True]  # before/after JS

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        driver.find_elements.side_effect = [[make_row("12345")]] + [[]] * 10
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Checkbox ticked" in m for m in logs)


# ──────────────────────────────────────────────
# Checkbox unchecked — warning when still not checked after JS
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_checkbox_warning_when_not_ticked(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = False  # never gets checked

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        driver.find_elements.side_effect = [[make_row("12345")]] + [[]] * 10
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("WARNING" in m for m in logs)


# ──────────────────────────────────────────────
# Checkbox exception
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_checkbox_exception_skips_user(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = [make_row("12345")]

    wait_mock = MagicMock()
    wait_mock.until.side_effect = [MagicMock(), TimeoutException("timeout")]

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Could not tick checkbox" in m for m in logs)


# ──────────────────────────────────────────────
# Save exception
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_save_exception_skips_user(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox
    driver.find_elements.return_value = [make_row("12345")]

    def find_element_side(by, xpath):
        if "input[4]" in str(xpath):  # SAVE_BUTTON_XPATH
            raise NoSuchElementException("no save")
        return MagicMock()

    driver.find_element.side_effect = find_element_side

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Could not save" in m for m in logs)


# ──────────────────────────────────────────────
# save_and_confirm: confirm dialog appears
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_save_and_confirm_dialog_clicked(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    confirm_btn = MagicMock()
    short_wait = MagicMock()
    short_wait.until.return_value = confirm_btn

    main_wait = MagicMock()
    main_wait.until.return_value = checkbox

    def wait_factory(drv, timeout):
        return short_wait if timeout == 4 else main_wait

    with patch("backend.bkms_user_update.WebDriverWait", side_effect=wait_factory):
        driver.find_elements.side_effect = [[make_row("12345")]] + [[]] * 10
        logs = []
        update_users(["12345"], log_callback=logs.append)

    confirm_btn.click.assert_called()


# ──────────────────────────────────────────────
# save_and_confirm: no confirm dialog
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_save_and_confirm_no_dialog(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    short_wait = MagicMock()
    short_wait.until.side_effect = TimeoutException("no dialog")

    main_wait = MagicMock()
    main_wait.until.return_value = checkbox

    def wait_factory(drv, timeout):
        return short_wait if timeout == 4 else main_wait

    with patch("backend.bkms_user_update.WebDriverWait", side_effect=wait_factory):
        driver.find_elements.side_effect = [[make_row("12345")]] + [[]] * 10
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Saved successfully" in m for m in logs)


# ──────────────────────────────────────────────
# Redirect back to user list mid-loop
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_redirected_url_navigates_back(mock_get_driver):
    driver = make_driver()
    driver.current_url = "https://bk.na.baps.org/somewhere-else"
    driver.window_handles = ["main"]
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = []

    wait_mock = MagicMock()
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"])

    driver.get.assert_any_call("https://bk.na.baps.org/admin/user/userlist")


# ──────────────────────────────────────────────
# Known error: student type
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_student_type_error_handled(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder("12345", ["Please Select Student Type"])

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Student type missing" in m for m in logs)


# ──────────────────────────────────────────────
# Known error: father email only
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_father_email_error_handled(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder("12345", ["Please Enter Father Email"])

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Father email missing" in m for m in logs)

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "12345" in content
    assert "Please Enter Father Email" in content


# ──────────────────────────────────────────────
# Known error: mother email only
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_mother_email_error_handled(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder("12345", ["Please Enter Mother Email"])

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Mother email missing" in m for m in logs)

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "12345" in content
    assert "Please Enter Mother Email" in content


# ──────────────────────────────────────────────
# Known error: both father and mother email
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_both_email_errors_handled(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder(
        "12345", ["Please Enter Father Email", "Please Enter Mother Email"]
    )

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Father email missing" in m for m in logs)
    assert any("Mother email missing" in m for m in logs)

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "12345" in content


# ──────────────────────────────────────────────
# Known error: "Please Enter Mother's Email." (apostrophe variant)
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_mother_email_apostrophe_variant_handled(mock_get_driver, tmp_path, monkeypatch):
    """The page sometimes shows "Please Enter Mother's Email." (with apostrophe)."""
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder("12345", ["Please Enter Mother's Email"])

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Mother email missing" in m for m in logs)
    field_mock = driver.find_element.return_value
    field_mock.send_keys.assert_any_call("mom@gmail.com")

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "Please Enter Mother Email" in content


# ──────────────────────────────────────────────
# Post-save Saturday Sabha checkbox re-verification
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_saturday_sabha_checkbox_reticked_when_unticked_after_save(mock_get_driver, tmp_path, monkeypatch):
    """If the Saturday Sabha checkbox is unticked after saving, re-tick it and log."""
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    # Checkbox via WebDriverWait — initially selected (no JS re-tick needed).
    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    # Post-save re-verification uses driver.find_element(CHECKBOX_XPATH) directly.
    # Return a mock with is_selected = False to simulate the checkbox becoming unticked.
    driver.find_element.return_value.is_selected.return_value = False

    driver.find_elements.side_effect = make_xpath_finder("12345")

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Saturday Sabha checkbox not ticked" in m for m in logs)
    assert any("re-ticked" in m.lower() for m in logs)

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "12345" in content
    assert "Saturday Sabha" in content


@patch("backend.bkms_user_update.get_chrome_driver")
def test_saturday_sabha_checkbox_already_ticked_no_log(mock_get_driver, tmp_path, monkeypatch):
    """If the checkbox is still ticked after save, no re-tick log entry is written."""
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True  # always selected

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder("12345")

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert not any("Saturday Sabha checkbox not ticked" in m for m in logs)
    assert list(tmp_path.rglob("errors_*.log")) == []


@patch("backend.bkms_user_update.get_chrome_driver")
def test_saturday_sabha_post_save_check_exception_passes(mock_get_driver):
    """If driver.find_element raises during post-save checkbox check, it is silently ignored."""
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    def find_element_side(by, xpath):
        if xpath == CHECKBOX_XPATH:
            raise NoSuchElementException("no checkbox")
        return MagicMock()

    driver.find_element.side_effect = find_element_side
    driver.find_elements.side_effect = make_xpath_finder("12345")

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Saved successfully" in m for m in logs)


# ──────────────────────────────────────────────
# Unknown error halts program
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_unknown_error_halts(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    unknown_err_el = MagicMock()
    unknown_err_el.is_displayed.return_value = True
    unknown_err_el.text = "Please Fix Something Unknown"

    # All specific error checks (with quoted text) return [] — no known errors.
    # The final unknown-errors check uses xpath == "//*[contains(text(), 'Please')]"
    # which does NOT contain a single-quoted specific string, so it falls through
    # to the final else and returns the unknown error element.
    def find_elements_side(by, xpath):
        if "tbody/tr" in xpath:
            return [make_row("12345")]
        # Specific error checks contain e.g. "'Please Enter Address'"
        # The unknown errors check is "//*[contains(text(), 'Please')]"
        # We detect the unknown-errors check by checking the xpath equals that exact string
        if xpath == "//*[contains(text(), 'Please')]":
            return [unknown_err_el]
        return []

    driver.find_elements.side_effect = find_elements_side

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345", "67890"], log_callback=logs.append)

    assert any("UNKNOWN ERROR" in m for m in logs)
    assert any("Stopping program" in m for m in logs)
    # Should not process second user after halt
    assert not any("67890" in m for m in logs)


# ──────────────────────────────────────────────
# Post-save check exception
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_post_save_check_exception(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = [
        [make_row("12345")],
        Exception("post-save explosion"),
    ]

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Post-save check failed" in m for m in logs)


# ──────────────────────────────────────────────
# Multiple users processed in sequence
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_multiple_users_all_processed(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = (
        [make_row("AAA")] + [[]] * 9 +
        [make_row("BBB")] + [[]] * 9
    )

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["AAA", "BBB"], log_callback=logs.append)

    assert any("AAA" in m for m in logs)
    assert any("BBB" in m for m in logs)
    assert any("All user IDs processed" in m for m in logs)


# ──────────────────────────────────────────────
# __main__ block
# ──────────────────────────────────────────────

def test_main_block():
    import sys
    import runpy
    mock_driver = MagicMock()
    mock_driver.find_elements.return_value = []
    mock_wait = MagicMock()
    mock_wait.until.return_value = MagicMock()
    original = sys.modules.pop("backend.bkms_user_update", None)
    try:
        with patch("backend.utils.chromeUtils.get_chrome_driver", return_value=mock_driver), \
             patch("backend.utils.constants.BKMS_ID", "test-id"), \
             patch("backend.utils.constants.BKMS_EMAIL", "test@test.com"), \
             patch("backend.utils.constants.BKMS_PASSWORD", "test-pw"), \
             patch("selenium.webdriver.support.ui.WebDriverWait", return_value=mock_wait):
            runpy.run_module("backend.bkms_user_update", run_name="__main__")
    finally:
        # Remove whatever runpy left, then restore the original module so
        # subsequent tests' @patch decorators target the correct module.
        sys.modules.pop("backend.bkms_user_update", None)
        if original is not None:
            sys.modules["backend.bkms_user_update"] = original
    mock_driver.quit.assert_called_once()


# ──────────────────────────────────────────────
# New test: address error cancels, logs, and continues
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_address_error_cancels_logs_and_continues(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    # Stateful side_effect: track which result-row call we're on.
    # User 1 (12345): address error on first has_error check.
    # User 2 (67890): all error checks return [].
    row_call_count = {"n": 0}

    def find_elements_side(by, xpath):
        if "tbody/tr" in xpath:
            row_call_count["n"] += 1
            if row_call_count["n"] == 1:
                return [make_row("12345")]
            else:
                return [make_row("67890")]
        # For user 1's address error check
        if "'Please Enter Address'" in xpath and row_call_count["n"] == 1:
            return [make_error_el()]
        return []

    driver.find_elements.side_effect = find_elements_side

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345", "67890"], log_callback=logs.append)

    assert any("Address missing" in m for m in logs)
    driver.find_element.assert_any_call(By.XPATH, CANCEL_BUTTON_XPATH)
    assert any("Saved successfully" in m and "67890" in m for m in logs)

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "12345" in content
    assert "Please Enter Address" in content


# ──────────────────────────────────────────────
# New test: father first name error
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_father_first_name_error_handled(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder(
        "12345", ["Please Enter Father First Name"]
    )

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Father first name missing" in m for m in logs)

    # Verify fill_field was called with FATHER_FIRST_NAME_XPATH and "Dad"
    call_xpaths = [c.args[1] for c in driver.find_element.call_args_list if len(c.args) >= 2]
    assert FATHER_FIRST_NAME_XPATH in call_xpaths
    # Verify "Dad" was sent to the field
    field_mock = driver.find_element.return_value
    field_mock.send_keys.assert_any_call("Dad")

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "Please Enter Father First Name" in content


# ──────────────────────────────────────────────
# New test: father last name error
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_father_last_name_error_handled(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder(
        "12345", ["Please Enter Father Last Name"]
    )

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Father last name missing" in m for m in logs)

    call_xpaths = [c.args[1] for c in driver.find_element.call_args_list if len(c.args) >= 2]
    assert FATHER_LAST_NAME_XPATH in call_xpaths
    field_mock = driver.find_element.return_value
    field_mock.send_keys.assert_any_call("dad")

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "Please Enter Father Last Name" in content


# ──────────────────────────────────────────────
# New test: mother first name error
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_mother_first_name_error_handled(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder(
        "12345", ["Please Enter Mother First Name"]
    )

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Mother first name missing" in m for m in logs)

    call_xpaths = [c.args[1] for c in driver.find_element.call_args_list if len(c.args) >= 2]
    assert MOTHER_FIRST_NAME_XPATH in call_xpaths
    field_mock = driver.find_element.return_value
    field_mock.send_keys.assert_any_call("mom")

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "Please Enter Mother First Name" in content


# ──────────────────────────────────────────────
# New test: mother last name error
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_mother_last_name_error_handled(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder(
        "12345", ["Please Enter Mother Last Name"]
    )

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Mother last name missing" in m for m in logs)

    call_xpaths = [c.args[1] for c in driver.find_element.call_args_list if len(c.args) >= 2]
    assert MOTHER_LAST_NAME_XPATH in call_xpaths
    field_mock = driver.find_element.return_value
    field_mock.send_keys.assert_any_call("mom")

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "Please Enter Mother Last Name" in content


# ──────────────────────────────────────────────
# New test: multiple name errors in one user
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_multiple_name_errors_in_one_user(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder(
        "12345",
        [
            "Please Enter Father First Name",
            "Please Enter Father Last Name",
            "Please Enter Father Email",
            "Please Enter Mother First Name",
            "Please Enter Mother Last Name",
            "Please Enter Mother Email",
        ],
    )

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert any("Father first name missing" in m for m in logs)
    assert any("Father last name missing" in m for m in logs)
    assert any("Father email missing" in m for m in logs)
    assert any("Mother first name missing" in m for m in logs)
    assert any("Mother last name missing" in m for m in logs)
    assert any("Mother email missing" in m for m in logs)

    error_files = list((tmp_path / "logs" / "user_update").glob("errors_*.log"))
    assert len(error_files) == 1
    content = error_files[0].read_text()
    assert "Please Enter Father First Name" in content
    assert "Please Enter Father Last Name" in content
    assert "Please Enter Father Email" in content
    assert "Please Enter Mother First Name" in content
    assert "Please Enter Mother Last Name" in content
    assert "Please Enter Mother Email" in content


# ──────────────────────────────────────────────
# New test: no error file when no errors
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_no_error_file_when_no_errors(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    driver.find_elements.side_effect = make_xpath_finder("12345")

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345"], log_callback=logs.append)

    assert list(tmp_path.rglob("errors_*.log")) == []


# ──────────────────────────────────────────────
# New test: skipped user still processes next
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_skipped_user_still_processes_next(mock_get_driver, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    row_call_count = {"n": 0}

    def find_elements_side(by, xpath):
        if "tbody/tr" in xpath:
            row_call_count["n"] += 1
            if row_call_count["n"] == 1:
                return [make_row("12345")]
            else:
                return [make_row("67890")]
        if "'Please Enter Address'" in xpath and row_call_count["n"] == 1:
            return [make_error_el()]
        return []

    driver.find_elements.side_effect = find_elements_side

    logs = []
    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        update_users(["12345", "67890"], log_callback=logs.append)

    # Second user should have been processed
    assert any("Processing" in m and "67890" in m for m in logs)
