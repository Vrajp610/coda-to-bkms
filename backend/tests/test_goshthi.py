import pytest
from unittest.mock import patch, MagicMock, call
from backend.goshthi import update_goshthi, _logout


# ── Early exit (no Chrome launched) ──────────────────────────────────────────

@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
def test_early_exit_empty_attended_ids(mock_sleep, mock_send):
    result = update_goshthi([], "January", "2026", "yes", "no", "no")
    mock_send.assert_called_once()
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    assert result["goshthi_held"] is True


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
def test_early_exit_three_or_fewer_ids(mock_sleep, mock_send):
    result = update_goshthi(["1", "2", "3"], "February", "2026", "yes", "no", "no")
    mock_send.assert_called_once()
    assert result["marked_present"] == 0
    assert result["goshthi_held"] is True


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
def test_early_exit_uses_log_callback(mock_sleep, mock_send):
    logs = []
    update_goshthi([], "March", "2026", "yes", "no", "no", log_callback=logs.append)
    assert any("Telegram notification sent" in m for m in logs)


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
def test_early_exit_goshthi_held_no_does_not_early_exit(mock_sleep, mock_send):
    """goshthi_held='no' skips the early exit regardless of attended_ids length."""
    with patch("backend.goshthi.get_chrome_driver") as mock_driver_fn, \
         patch("backend.goshthi.Select"):
        driver = MagicMock()
        mock_driver_fn.return_value = driver
        driver.find_elements.return_value = []  # no rows → break immediately
        driver.find_element.return_value.text = ""

        result = update_goshthi([], "April", "2026", "no", "no", "no")
        assert result["goshthi_held"] is False


# ── Goshthi NOT held ──────────────────────────────────────────────────────────

@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_not_held_returns_correct_result(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver

    attended = ["100", "200", "300", "400"]
    result = update_goshthi(attended, "May", "2026", "no", "no", "no")

    assert result["goshthi_held"] is False
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    mock_send.assert_called_once()
    driver.quit.assert_called_once()


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_not_held_notification_message(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver

    update_goshthi(["1", "2", "3", "4"], "June", "2026", "no", "no", "no")

    sent_msg = mock_send.call_args[0][0]
    assert "June 2026" in sent_msg
    assert "not held" in sent_msg


# ── Goshthi WAS held ─────────────────────────────────────────────────────────

def _make_held_driver(attended_ids, bkms_ids_in_system):
    """Build a mock Selenium driver that presents bkms_ids_in_system across one page."""
    driver = MagicMock()

    # find_elements: first call → rows list, second call → empty (end of pages)
    rows = [MagicMock() for _ in bkms_ids_in_system]
    driver.find_elements.side_effect = [rows, []]

    # find_element: text returns BKMS IDs only for table cell (td[1]) lookups.
    # Login-phase and navigation calls receive empty text so they don't consume the sequence.
    # First td[1] call: loop detection (tr[1]/td[1])
    # Subsequent td[1] calls: one per row
    id_sequence = [bkms_ids_in_system[0]] + bkms_ids_in_system
    call_idx = [0]

    def fake_find_element(*args, **kwargs):
        m = MagicMock()
        locator = args[1] if len(args) > 1 else ""
        if isinstance(locator, str) and "/td[1]" in locator:
            m.text = id_sequence[call_idx[0]] if call_idx[0] < len(id_sequence) else ""
            call_idx[0] += 1
        else:
            m.text = ""
        m.get_attribute.return_value = ""  # li_class='' → not disabled
        return m

    driver.find_element.side_effect = fake_find_element
    return driver


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_marks_present_correctly(mock_get_driver, mock_select, mock_sleep, mock_send):
    bkms_in_system = ["1001", "1002", "1003"]
    attended = ["1001", "1003", "9999", "8888"]  # >3 to skip early exit
    driver = _make_held_driver(attended, bkms_in_system)
    mock_get_driver.return_value = driver

    result = update_goshthi(attended, "July", "2026", "yes", "no", "no")

    assert result["goshthi_held"] is True
    assert result["marked_present"] == 2   # "1001" and "1003"
    assert "9999" in result["not_found_in_bkms"]
    assert "8888" in result["not_found_in_bkms"]
    mock_send.assert_called_once()
    driver.quit.assert_called_once()


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_hangout_yes_workshop_yes(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = []  # no rows → single-pass
    driver.find_element.return_value.text = ""
    driver.find_element.return_value.get_attribute.return_value = ""

    result = update_goshthi(["1", "2", "3", "4"], "August", "2026", "yes", "yes", "yes")
    assert result["goshthi_held"] is True


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_hangout_no_workshop_no(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = []
    driver.find_element.return_value.text = ""
    driver.find_element.return_value.get_attribute.return_value = ""

    result = update_goshthi(["1", "2", "3", "4"], "September", "2026", "yes", "no", "no")
    assert result["goshthi_held"] is True


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_no_rows_results_empty(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = []  # no rows → immediately done
    driver.find_element.return_value.text = ""
    driver.find_element.return_value.get_attribute.return_value = ""

    attended = ["1001", "1002", "1003", "1004"]
    result = update_goshthi(attended, "October", "2026", "yes", "no", "no")

    assert result["marked_present"] == 0
    assert set(result["not_found_in_bkms"]) == set(attended)


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_loop_detection_stops_pagination(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver

    # Both pages start with the same ID → loop detected on page 2
    pages = [[MagicMock()], [MagicMock()]]
    driver.find_elements.side_effect = pages

    call_idx = [0]
    id_sequence = ["2001", "2001", "2001"]  # loop detection will fire on page 2
    def fake_find_element(*args, **kwargs):
        m = MagicMock()
        m.text = id_sequence[min(call_idx[0], len(id_sequence) - 1)]
        call_idx[0] += 1
        m.get_attribute.return_value = ""
        return m
    driver.find_element.side_effect = fake_find_element

    attended = ["2001", "2002", "2003", "2004"]
    result = update_goshthi(attended, "November", "2026", "yes", "no", "no")
    # Loop detection should stop after page 1
    assert result["marked_present"] == 1  # "2001" matched on page 1


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_next_button_disabled_stops_pagination(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver

    rows = [MagicMock()]
    driver.find_elements.side_effect = [rows]

    call_idx = [0]
    def fake_find_element(*args, **kwargs):
        m = MagicMock()
        m.text = "3001"
        call_idx[0] += 1
        # Make the Next li report as 'disabled'
        m.get_attribute.side_effect = lambda attr: "disabled" if attr == "class" else ""
        return m
    driver.find_element.side_effect = fake_find_element

    attended = ["3001", "3002", "3003", "3004"]
    result = update_goshthi(attended, "December", "2026", "yes", "no", "no")
    # Only one page processed, then stopped by disabled Next button
    assert result["marked_present"] == 1


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_row_exception_continues(mock_get_driver, mock_select, mock_sleep, mock_send):
    """Exception on a row should be caught and iteration continues."""
    driver = MagicMock()
    mock_get_driver.return_value = driver

    rows = [MagicMock(), MagicMock()]
    driver.find_elements.side_effect = [rows, []]

    call_idx = [0]
    id_sequence = ["4001", "4001", "4002"]
    def fake_find_element(*args, **kwargs):
        locator = args[1] if len(args) > 1 else ""
        # Raise on the second row's BKMS ID lookup (tr[2]/td[1])
        if isinstance(locator, str) and "tr[2]/td[1]" in locator:
            call_idx[0] += 1
            raise Exception("element not found")
        m = MagicMock()
        if isinstance(locator, str) and "/td[1]" in locator:
            m.text = id_sequence[min(call_idx[0], len(id_sequence) - 1)]
            call_idx[0] += 1
        else:
            m.text = ""
        m.get_attribute.return_value = ""
        return m
    driver.find_element.side_effect = fake_find_element

    attended = ["4001", "4002", "4003", "4004"]
    # Should not raise; should complete successfully
    result = update_goshthi(attended, "January", "2025", "yes", "no", "no")
    assert isinstance(result, dict)


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_notification_includes_not_found(mock_get_driver, mock_select, mock_sleep, mock_send):
    bkms_in_system = ["5001"]
    attended = ["5001", "9999", "8888", "7777"]
    driver = _make_held_driver(attended, bkms_in_system)
    mock_get_driver.return_value = driver

    update_goshthi(attended, "February", "2025", "yes", "no", "no")

    sent_msg = mock_send.call_args[0][0]
    assert "9999" in sent_msg or "8888" in sent_msg or "7777" in sent_msg


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_log_callback_receives_messages(mock_get_driver, mock_select, mock_sleep, mock_send):
    driver = MagicMock()
    mock_get_driver.return_value = driver
    driver.find_elements.return_value = []
    driver.find_element.return_value.text = ""
    driver.find_element.return_value.get_attribute.return_value = ""

    logs = []
    update_goshthi(["1", "2", "3", "4"], "March", "2025", "yes", "no", "no",
                   log_callback=logs.append)
    assert any(msg for msg in logs)


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_no_next_button_raises_stops_pagination(mock_get_driver, mock_select, mock_sleep, mock_send):
    """If finding the Next button raises, pagination stops gracefully."""
    driver = MagicMock()
    mock_get_driver.return_value = driver

    rows = [MagicMock()]
    driver.find_elements.side_effect = [rows]

    def fake_find_element(*args, **kwargs):
        locator = args[1] if len(args) > 1 else ""
        # Raise only when looking for the Next pagination button
        if isinstance(locator, str) and "li[last()]" in locator:
            raise Exception("no next button")
        m = MagicMock()
        m.text = "6001"
        m.get_attribute.return_value = ""
        return m
    driver.find_element.side_effect = fake_find_element

    attended = ["6001", "6002", "6003", "6004"]
    result = update_goshthi(attended, "April", "2025", "yes", "no", "no")
    assert isinstance(result, dict)


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_loop_detection_exception_breaks(mock_get_driver, mock_select, mock_sleep, mock_send):
    """Exception during loop detection should break pagination gracefully (lines 192-193)."""
    driver = MagicMock()
    mock_get_driver.return_value = driver

    rows = [MagicMock()]
    driver.find_elements.side_effect = [rows]

    def fake_find_element(*args, **kwargs):
        locator = args[1] if len(args) > 1 else ""
        if isinstance(locator, str) and "/td[1]" in locator:
            raise Exception("loop detection element missing")
        m = MagicMock()
        m.text = ""
        m.get_attribute.return_value = ""
        return m
    driver.find_element.side_effect = fake_find_element

    attended = ["7001", "7002", "7003", "7004"]
    result = update_goshthi(attended, "May", "2025", "yes", "no", "no")
    assert isinstance(result, dict)
    assert result["marked_present"] == 0


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_empty_bkms_id_is_skipped(mock_get_driver, mock_select, mock_sleep, mock_send):
    """Empty bkms_id in a row should be skipped via continue (line 202)."""
    driver = MagicMock()
    mock_get_driver.return_value = driver

    rows = [MagicMock(), MagicMock()]
    driver.find_elements.side_effect = [rows, []]

    call_idx = [0]
    # loop detection → "7001", row 1 → "" (skip), row 2 → "7001"
    id_seq = ["7001", "", "7001"]

    def fake_find_element(*args, **kwargs):
        locator = args[1] if len(args) > 1 else ""
        m = MagicMock()
        if isinstance(locator, str) and "/td[1]" in locator:
            m.text = id_seq[call_idx[0]] if call_idx[0] < len(id_seq) else ""
            call_idx[0] += 1
        else:
            m.text = ""
        m.get_attribute.return_value = ""
        return m
    driver.find_element.side_effect = fake_find_element

    attended = ["7001", "7002", "7003", "7004"]
    result = update_goshthi(attended, "June", "2025", "yes", "no", "no")
    assert result["marked_present"] == 1


@patch("backend.goshthi.send_notifications")
@patch("backend.goshthi.time.sleep")
@patch("backend.goshthi.Select")
@patch("backend.goshthi.get_chrome_driver")
def test_goshthi_held_not_marked_is_logged(mock_get_driver, mock_select, mock_sleep, mock_send):
    """ID found in BKMS but checkbox click fails → goes into not_marked (lines 251-252)."""
    driver = MagicMock()
    mock_get_driver.return_value = driver

    rows = [MagicMock()]
    driver.find_elements.side_effect = [rows, []]

    call_idx = [0]
    id_seq = ["8001", "8001"]  # loop detection + row 1

    def fake_find_element(*args, **kwargs):
        locator = args[1] if len(args) > 1 else ""
        if isinstance(locator, str) and "td[8]" in locator:
            raise Exception("checkbox not found")
        m = MagicMock()
        if isinstance(locator, str) and "/td[1]" in locator:
            m.text = id_seq[min(call_idx[0], len(id_seq) - 1)]
            call_idx[0] += 1
        else:
            m.text = ""
        m.get_attribute.return_value = ""
        return m
    driver.find_element.side_effect = fake_find_element

    attended = ["8001", "8002", "8003", "8004"]
    logs = []
    result = update_goshthi(attended, "July", "2025", "yes", "no", "no", log_callback=logs.append)
    assert result["marked_present"] == 0
    assert result["not_marked"] == 1
    assert any("__NOT_MARKED__" in m for m in logs)


# ── _logout ───────────────────────────────────────────────────────────────────

@patch("backend.goshthi.time.sleep")
def test_logout_success(mock_sleep):
    driver = MagicMock()
    logs = []
    _logout(driver, logs.append)
    driver.quit.assert_called_once()
    assert any("Logged out" in m for m in logs)
    assert any("Closed Chrome" in m for m in logs)


@patch("backend.goshthi.time.sleep")
def test_logout_exception_is_swallowed(mock_sleep):
    driver = MagicMock()
    driver.find_element.side_effect = Exception("element gone")
    logs = []
    _logout(driver, logs.append)
    driver.quit.assert_called_once()
    assert any("Closed Chrome" in m for m in logs)
    # "Logged out" not in logs since exception was raised before that log
    assert not any("Logged out" in m for m in logs)
