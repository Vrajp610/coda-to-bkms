import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from selenium.common.exceptions import NoSuchElementException
from backend.bkms import update_sheet

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    driver.find_element.return_value = MagicMock()
    driver.find_elements.return_value = []
    return driver

@pytest.fixture
def attended_kishores():
    return ["1001", "1002", "1003", "1004", "1005", "1006"]

@pytest.fixture
def all_kishores_elements():
    def make_element(bkid):
        el = MagicMock()
        el.text = f"{bkid} Name"
        el.find_element.return_value = MagicMock()
        return el
    return [make_element("1001"), make_element("1002"), make_element("1003"), 
            make_element("1004"), make_element("1005"), make_element("9999")]

@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    import time
    monkeypatch.setattr(time, "sleep", lambda *_: None)

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
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

    assert result["marked_present"] == 5
    assert result["not_marked"] == 1
    assert result["not_found_in_bkms"] == ["1006"]
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_invalid_sabha_group_returns_none(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver
):
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 2
    mock_get_sunday.return_value = "2024-06-09"

    result = update_sheet(
        attended_kishores=["1001", "1002", "1003", "1004", "1005", "1006"],
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
@patch("backend.bkms.send_notifications")
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
    assert result["sabha_held"] == False
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
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

    mock_driver.find_elements.return_value = [make_element("1001"), make_element("1002"), make_element("1003")]

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
    assert result["sabha_held"] == False
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
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

    mock_driver.find_elements.return_value = [make_element("1001"), make_element("1002"), make_element("1003")]

    result = update_sheet(
        attended_kishores=["1001", "1002"],
        day="Saturday K2",
        sabha_held="no",
        p2_guju="yes",
        date_string="2024-06-05",
        prep_cycle_done="no"
    )
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    assert result["sabha_held"] == False
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
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

    mock_driver.find_elements.return_value = [make_element("1001"), make_element("1002"), make_element("1003"), 
                                               make_element("1004"), make_element("1005"), make_element("1006")]

    result = update_sheet(
        attended_kishores=["1001", "1002", "1003", "1004", "1005", "1007"],
        day="Sunday K2",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )
    assert result["marked_present"] == 5
    assert result["not_marked"] == 1
    assert result["not_found_in_bkms"] == ["1007"]
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
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
    assert result["marked_present"] == 5
    assert result["not_marked"] == 1
    assert result["not_found_in_bkms"] == ["1006"]
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
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
    el3 = MagicMock()
    el3.text = "1002 Name"
    el3.find_element.return_value = MagicMock()
    el4 = MagicMock()
    el4.text = "1003 Name"
    el4.find_element.return_value = MagicMock()
    el5 = MagicMock()
    el5.text = "1004 Name"
    el5.find_element.return_value = MagicMock()
    el6 = MagicMock()
    el6.text = "1005 Name"
    el6.find_element.return_value = MagicMock()
    el7 = MagicMock()
    el7.text = "1006 Name"
    el7.find_element.return_value = MagicMock()
    mock_driver.find_elements.return_value = [el1, el2, el3, el4, el5, el6, el7]

    result = update_sheet(
        attended_kishores=["1001", "1002", "1003", "1004", "1005", "1006"],
        day="Sunday K1",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )
    assert result["marked_present"] == 6
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_handles_click_exception_and_prints_not_marked(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, capsys
):
    mock_get_driver.return_value = mock_driver = MagicMock()
    mock_week_number.return_value = 10
    mock_get_sunday.return_value = "2024-06-09"

    el1 = MagicMock()
    el1.text = "1001 Name"
    el1.find_element.side_effect = NoSuchElementException("Mocked failure")
    el2 = MagicMock()
    el2.text = "1002 Name"
    el2.find_element.side_effect = NoSuchElementException("Mocked failure")
    el3 = MagicMock()
    el3.text = "1003 Name"
    el3.find_element.side_effect = NoSuchElementException("Mocked failure")
    el4 = MagicMock()
    el4.text = "1004 Name"
    el4.find_element.side_effect = NoSuchElementException("Mocked failure")
    el5 = MagicMock()
    el5.text = "1005 Name"
    el5.find_element.side_effect = NoSuchElementException("Mocked failure")
    el6 = MagicMock()
    el6.text = "1006 Name"
    el6.find_element.side_effect = NoSuchElementException("Mocked failure")

    mock_driver.find_elements.return_value = [el1, el2, el3, el4, el5, el6]

    result = update_sheet(
        attended_kishores=["1001", "1002", "1003", "1004", "1005", "1006"],
        day="Sunday K1",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )

    assert result["marked_present"] == 0
    assert result["not_marked"] == 6
    assert result["not_found_in_bkms"] == []
    assert result["sabha_held"] == True

    captured = capsys.readouterr()
    assert "Kishores found in BKMS but not marked present:" in captured.out


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_all_checklist_clicks_and_p2_guju_yes(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver
):
    mock_driver = MagicMock()
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 2
    mock_get_sunday.return_value = "2024-06-09"

    mock_driver.find_elements.return_value = []
    result = update_sheet(
        attended_kishores=[],
        day="Saturday K2",
        sabha_held="yes",
        p2_guju="yes",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_all_checklist_clicks_and_p2_guju_no(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver
):
    mock_driver = MagicMock()
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 2
    mock_get_sunday.return_value = "2024-06-09"

    mock_driver.find_elements.return_value = []
    result = update_sheet(
        attended_kishores=[],
        day="Sunday K2",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="no"
    )
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_kishore_not_marked_and_not_found(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, capsys
):
    mock_driver = MagicMock()
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 2
    mock_get_sunday.return_value = "2024-06-09"

    el1 = MagicMock()
    el1.text = "1001 Name"
    el1.find_element.side_effect = Exception("Click failed")
    el2 = MagicMock()
    el2.text = "1002 Name"
    el2.find_element.return_value = MagicMock()
    el3 = MagicMock()
    el3.text = "1003 Name"
    el3.find_element.return_value = MagicMock()
    el4 = MagicMock()
    el4.text = "1004 Name"
    el4.find_element.return_value = MagicMock()
    el5 = MagicMock()
    el5.text = "1005 Name"
    el5.find_element.return_value = MagicMock()
    el6 = MagicMock()
    el6.text = "1006 Name"
    el6.find_element.return_value = MagicMock()
    mock_driver.find_elements.return_value = [el1, el2, el3, el4, el5, el6]

    result = update_sheet(
        attended_kishores=["1001", "1002", "1003", "1004", "1005", "1007"],
        day="Saturday K1",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )
    assert result["marked_present"] == 4
    assert result["not_marked"] == 2
    assert result["not_found_in_bkms"] == ["1007"]
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()

    captured = capsys.readouterr()
    assert "Kishores found in BKMS but not marked present: ['1001']" in captured.out
    assert "Did not mark 2 Kishores as they were not found in BKMS" in captured.out or "Kishores not found in BKMS:" in captured.out


@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_prints_and_returns_for_all_paths(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, capsys
):
    mock_driver = MagicMock()
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 2
    mock_get_sunday.return_value = "2024-06-09"

    mock_driver.find_elements.return_value = []
    result = update_sheet(
        attended_kishores=["1001", "1002", "1003", "1004", "1005", "1006"],
        day="Sunday K2",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="yes"
    )
    assert result["marked_present"] == 0
    assert result["not_marked"] == 6
    assert result["not_found_in_bkms"] == ["1001", "1002", "1003", "1004", "1005", "1006"]
    assert result["sabha_held"] == True
    mock_send_telegram.assert_called_once()

    captured = capsys.readouterr()
    assert "Did not mark 6 Kishores as they were not found in BKMS" in captured.out
    assert "Kishores not found in BKMS:" in captured.out

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_uses_prep_cycle_label3_when_prep_cycle_no(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver
):
    from selenium.webdriver.common.by import By
    mock_get_driver.return_value = mock_driver
    mock_week_number.return_value = 1
    mock_get_sunday.return_value = "2024-06-09"

    # ensure find_elements returns something so loop can run (not required for this assert)
    mock_driver.find_elements.return_value = []

    expected_xpath = '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[2]/label[3]/div/ins'

    update_sheet(
        attended_kishores=["1001", "1002", "1003", "1004", "1005", "1006"],
        day="Saturday K1",
        sabha_held="yes",
        p2_guju="no",
        date_string="2024-06-05",
        prep_cycle_done="no"
    )

    # verify that the exact XPATH for the "prep cycle NOT done" option was clicked
    calls = mock_driver.find_element.call_args_list
    assert any(call[0] == (By.XPATH, expected_xpath) for call in calls), "Expected label[3] XPATH not clicked"

@patch("backend.bkms.get_chrome_driver")
@patch("backend.bkms.calculate_week_number")
@patch("backend.bkms.get_this_week_sunday")
@patch("backend.bkms.send_notifications")
def test_update_sheet_clicks_p2_guju_label2_and_prints(
    mock_send_telegram, mock_get_sunday, mock_week_number, mock_get_driver, mock_driver, capsys
):
   from selenium.webdriver.common.by import By
   mock_get_driver.return_value = mock_driver
   mock_week_number.return_value = 12
   mock_get_sunday.return_value = "2024-06-09"

   # no table rows required for this assertion
   mock_driver.find_elements.return_value = []

   expected_xpath = '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[6]/label[2]/div/ins'

   update_sheet(
      attended_kishores=["1001", "1002", "1003", "1004", "1005", "1006"],
      day="Saturday K1",
      sabha_held="yes",
      p2_guju="yes",
      date_string="2024-06-05",
      prep_cycle_done="yes"
   )

   calls = mock_driver.find_element.call_args_list
   assert any(call[0] == (By.XPATH, expected_xpath) for call in calls), "Expected Presentation 2 (Gujarati) XPATH not clicked"

   captured = capsys.readouterr()
   assert "Presentation 2 was in Gujarati" in captured.out