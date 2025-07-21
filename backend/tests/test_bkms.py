import pytest
from unittest.mock import patch, MagicMock
from backend.bkms import update_sheet

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    driver.find_element.return_value = MagicMock()
    driver.find_elements.return_value = []
    return driver

@pytest.fixture
def attended_kishores():
    return ["1001", "1002", "1003"]

@pytest.fixture
def all_kishores_elements():
    def make_element(bkid):
        el = MagicMock()
        el.text = f"{bkid} Name"
        el.find_element.return_value = MagicMock()
        return el
    return [make_element("1001"), make_element("1002"), make_element("9999")]

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_marks_attendance_and_returns_result(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver,
    mock_driver, attended_kishores, all_kishores_elements
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 5
    mock_get_sunday.return_value = "2024-06-09"
    mock_driver.find_elements.return_value = all_kishores_elements

    result = update_sheet(
        attended_kishores=attended_kishores,
        day="Saturday K1",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )

    assert result["marked_present"] == 2
    assert result["not_marked"] == 1
    assert result["not_found_in_bkms"] == ["1003"]
    mock_send_telegram.assert_awaited()

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_invalid_sabha_group_returns_none(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 2
    mock_get_sunday.return_value = "2024-06-09"

    result = update_sheet(
        attended_kishores=["1001"],
        day="invalid group",
        sabha_held="yes",
        p2_guju="yes",
        date_string="2024-06-05",
        prep_cycle_done="no"
    )
    assert result is None
    mock_send_telegram.assert_not_called()

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_handles_no_attended_kishores(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 3
    mock_get_sunday.return_value = "2024-06-09"
    mock_driver.find_elements.return_value = []

    result = update_sheet(
        attended_kishores=[],
        day="Sunday K2",
        sabha_held="no",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="no"
    )
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    mock_send_telegram.assert_awaited()

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_marks_all_absent(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 4
    mock_get_sunday.return_value = "2024-06-09"
    def make_element(bkid):
        el = MagicMock()
        el.text = f"{bkid} Name"
        el.find_element.return_value = MagicMock()
        return el
    all_kishores_elements = [make_element("1001"), make_element("1002"), make_element("1003")]
    mock_driver.find_elements.return_value = all_kishores_elements

    result = update_sheet(
        attended_kishores=[],
        day="Sunday K1",
        sabha_held="no",
        p2_guju="yes",
        date_string="2024-06-05",
        prep_cycle_done="no"
    )
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    mock_send_telegram.assert_awaited()

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_p2_guju_yes_and_prep_cycle_no(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver, attended_kishores
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 6
    mock_get_sunday.return_value = "2024-06-09"
    def make_element(bkid):
        el = MagicMock()
        el.text = f"{bkid} Name"
        el.find_element.return_value = MagicMock()
        return el
    all_kishores_elements = [make_element("1001"), make_element("1002"), make_element("1003")]
    mock_driver.find_elements.return_value = all_kishores_elements

    result = update_sheet(
        attended_kishores=["1001", "1002"],
        day="Saturday K2",
        sabha_held="no",
        p2_guju="yes",
        date_string="2024-06-05",
        prep_cycle_done="no"
    )
    assert result["marked_present"] == 2
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    mock_send_telegram.assert_awaited()

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_not_marked_logic(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 7
    mock_get_sunday.return_value = "2024-06-09"
    def make_element(bkid):
        el = MagicMock()
        el.text = f"{bkid} Name"
        el.find_element.return_value = MagicMock()
        return el
    all_kishores_elements = [make_element("1001"), make_element("1002"), make_element("1003")]
    mock_driver.find_elements.return_value = all_kishores_elements

    result = update_sheet(
        attended_kishores=["1001", "1002", "1004"],
        day="Sunday K2",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )
    assert result["marked_present"] == 2
    assert result["not_marked"] == 1
    assert result["not_found_in_bkms"] == ["1004"]
    mock_send_telegram.assert_awaited()

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_case_insensitivity(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver, attended_kishores, all_kishores_elements
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 8
    mock_get_sunday.return_value = "2024-06-09"
    mock_driver.find_elements.return_value = all_kishores_elements

    result = update_sheet(
        attended_kishores=attended_kishores,
        day="sAtUrDaY k1",
        sabha_held="YeS",
        p2_guju="nO",
        date_string="2024-06-05",
        prep_cycle_done="YeS"
    )
    assert result["marked_present"] == 2
    assert result["not_marked"] == 1
    assert result["not_found_in_bkms"] == ["1003"]
    mock_send_telegram.assert_awaited()

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_skips_empty_row(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 9
    mock_get_sunday.return_value = "2024-06-09"
    el1 = MagicMock()
    el1.text = ""
    el1.find_element.return_value = MagicMock()
    el2 = MagicMock()
    el2.text = "1001 Name"
    el2.find_element.return_value = MagicMock()
    mock_driver.find_elements.return_value = [el1, el2]

    result = update_sheet(
        attended_kishores=["1001"],
        day="Sunday K1",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )
    assert result["marked_present"] == 1
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    mock_send_telegram.assert_awaited()

import pytest
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import NoSuchElementException

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_telegram_message")
def test_update_sheet_handles_click_exception_and_prints_not_marked(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, capsys
):
    mock_get_driver.return_value = mock_driver = MagicMock()
    mock_week_number.return_value = 10
    mock_get_sunday.return_value = "2024-06-09"

    el = MagicMock()
    el.text = "1001 Name"
    el.find_element.side_effect = NoSuchElementException("Mocked failure")

    mock_driver.find_elements.return_value = [el]

    result = update_sheet(
        attended_kishores=["1001"],
        day="Sunday K1",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )

    assert result["marked_present"] == 0
    assert result["not_marked"] == 1
    assert result["not_found_in_bkms"] == []

    captured = capsys.readouterr()
    assert "Kishores found in BKMS but not marked present: ['1001']" in captured.out