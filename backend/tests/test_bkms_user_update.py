import pytest
from unittest.mock import patch, MagicMock, call
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from backend.bkms_user_update import update_users


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
        driver.find_elements.return_value = [make_row("99999")]
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
        driver.find_elements.return_value = [make_row("99999")]
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
    mock_get_driver.return_value = driver

    visible_el = MagicMock()
    visible_el.is_displayed.return_value = True
    visible_el.text = "Please Select Student Type"

    wait_mock = MagicMock()
    checkbox = MagicMock()
    checkbox.is_selected.return_value = True
    wait_mock.until.return_value = checkbox

    # Simulate: search returns a row, opens tab, checkbox already checked,
    # save succeeds, and student-type error is found then not found after retry.
    call_counts = {"find_elements": 0}

    def find_elements_side_effect(by, xpath):
        call_counts["find_elements"] += 1
        if "Please" in xpath:
            # First call: student type error; second: no unknown errors
            if call_counts["find_elements"] <= 2:
                return [visible_el]
            return []
        return [make_row("12345")]

    driver.find_elements.side_effect = find_elements_side_effect
    driver.window_handles = ["main", "new"]

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
    driver.find_elements.return_value = [make_row("12345")]

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    no_error_el = MagicMock()
    no_error_el.is_displayed.return_value = False

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        driver.find_elements.side_effect = [
            [make_row("12345")],  # search results
            [],                    # has_error: student type
            [],                    # has_error: father
            [],                    # has_error: mother
            [],                    # unknown errors check
        ]
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
        driver.find_elements.side_effect = [
            [make_row("12345")],
            [], [], [], [],
        ]
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
        driver.find_elements.side_effect = [
            [make_row("12345")],
            [], [], [], [],
        ]
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
        driver.find_elements.side_effect = [
            [make_row("12345")],
            [], [], [], [],
        ]
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
        driver.find_elements.side_effect = [
            [make_row("12345")],
            [], [], [], [],
        ]
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

    student_err_el = MagicMock()
    student_err_el.is_displayed.return_value = True
    student_err_el.text = "Please Select Student Type"

    call_counts = {"n": 0}

    def find_elements_side(by, xpath):
        call_counts["n"] += 1
        if "Please" in xpath:
            if call_counts["n"] <= 2:
                return [student_err_el]
            return []
        return [make_row("12345")]

    driver.find_elements.side_effect = find_elements_side

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Student type missing" in m for m in logs)


# ──────────────────────────────────────────────
# Known error: father email only
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_father_email_error_handled(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    father_err_el = MagicMock()
    father_err_el.is_displayed.return_value = True
    father_err_el.text = "Please Enter Father email"

    call_counts = {"n": 0}

    def find_elements_side(by, xpath):
        call_counts["n"] += 1
        if "Please" in xpath:
            if call_counts["n"] <= 3:
                return [father_err_el]
            return []
        return [make_row("12345")]

    driver.find_elements.side_effect = find_elements_side

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Father email missing" in m for m in logs)


# ──────────────────────────────────────────────
# Known error: mother email only
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_mother_email_error_handled(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    mother_err_el = MagicMock()
    mother_err_el.is_displayed.return_value = True
    mother_err_el.text = "Please Enter Mother email"

    def find_elements_side(by, xpath):
        if "Please Enter Mother" in str(xpath):
            return [mother_err_el]
        if "Please" in str(xpath):
            return []  # no student type or father error
        return [make_row("12345")]

    driver.find_elements.side_effect = find_elements_side

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Mother email missing" in m for m in logs)


# ──────────────────────────────────────────────
# Known error: both father and mother
# ──────────────────────────────────────────────

@patch("backend.bkms_user_update.get_chrome_driver")
def test_both_email_errors_handled(mock_get_driver):
    driver = make_driver()
    driver.window_handles = ["main", "new"]
    mock_get_driver.return_value = driver

    checkbox = MagicMock()
    checkbox.is_selected.return_value = True

    both_err_el = MagicMock()
    both_err_el.is_displayed.return_value = True
    both_err_el.text = "Please Enter Father and Mother"

    call_counts = {"n": 0}

    def find_elements_side(by, xpath):
        call_counts["n"] += 1
        if "Please" in xpath:
            if call_counts["n"] <= 4:
                return [both_err_el]
            return []
        return [make_row("12345")]

    driver.find_elements.side_effect = find_elements_side

    wait_mock = MagicMock()
    wait_mock.until.return_value = checkbox

    with patch("backend.bkms_user_update.WebDriverWait", return_value=wait_mock):
        logs = []
        update_users(["12345"], log_callback=logs.append)

    assert any("Father email missing" in m for m in logs)
    assert any("Mother email missing" in m for m in logs)


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

    def find_elements_side(by, xpath):
        if "Please" in xpath:
            return [unknown_err_el]
        return [make_row("12345")]

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

    driver.find_elements.side_effect = [
        [make_row("AAA")], [], [], [], [],
        [make_row("BBB")], [], [], [], [],
    ]

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
    sys.modules.pop("backend.bkms_user_update", None)
    with patch("backend.utils.chromeUtils.get_chrome_driver", return_value=mock_driver), \
         patch("backend.utils.constants.BKMS_ID", "test-id"), \
         patch("backend.utils.constants.BKMS_EMAIL", "test@test.com"), \
         patch("backend.utils.constants.BKMS_PASSWORD", "test-pw"), \
         patch("selenium.webdriver.support.ui.WebDriverWait", return_value=mock_wait):
        runpy.run_module("backend.bkms_user_update", run_name="__main__", alter_sys=True)
    mock_driver.quit.assert_called_once()
