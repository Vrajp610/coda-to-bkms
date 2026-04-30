import pytest
from unittest.mock import patch, MagicMock
from backend.bal_mandal import update_bal_sheet


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    import time
    monkeypatch.setattr(time, "sleep", lambda *_: None)


def make_driver():
    driver = MagicMock()
    driver.find_element.return_value = MagicMock()
    driver.find_elements.return_value = []
    driver.execute_script.return_value = "complete"
    return driver


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_sabha_not_held_returns_false(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 3

    result = update_bal_sheet(
        attended_bals=[],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="No",
        smruti_time="No",
        mukhpath="No",
        prep_cycle_done="No",
        individual_groups={},
        captcha_seconds=1,
    )

    assert result["sabha_held"] is False
    assert result["marked_present"] == 0
    assert result["not_marked"] == 0
    assert result["not_found_in_bkms"] == []
    driver.quit.assert_called_once()


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_sabha_held_empty_bals_aborts(mock_week, mock_driver_fn):
    mock_week.return_value = 3
    result = update_bal_sheet(
        attended_bals=[],
        day="Sunday",
        date="June 16",
        sabha_held="yes",
        combined_groups="No",
        smruti_time="No",
        mukhpath="No",
        prep_cycle_done="No",
        individual_groups={},
        captcha_seconds=1,
    )
    assert result["sabha_held"] is True
    assert result["marked_present"] == 0
    mock_driver_fn.assert_not_called()


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_combined_groups_yes(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    attended = [str(i) for i in range(10)]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Saturday",
        date="June 15",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="yes",
        mukhpath="yes",
        prep_cycle_done="yes",
        individual_groups={},
        captcha_seconds=1,
    )

    assert result is not None
    assert result["sabha_held"] is True


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_combined_groups_smruti_no(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    attended = [str(i) for i in range(10)]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Saturday",
        date="June 15",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
    )
    assert result["sabha_held"] is True


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_individual_groups_all_held(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 4

    individual = {
        "group 0": {"held": "Yes", "smruti_time": "Yes", "mukhpath": "No", "prep_cycle": "Yes"},
        "group 1": {"held": "Yes", "smruti_time": "No", "mukhpath": "Yes", "prep_cycle": "No"},
        "group 2a": {"held": "Yes", "smruti_time": "Yes", "mukhpath": "Yes", "prep_cycle": "Yes"},
        "group 2b": {"held": "Yes", "smruti_time": "No", "mukhpath": "No", "prep_cycle": "No"},
        "group 3": {"held": "Yes", "smruti_time": "Yes", "mukhpath": "Yes", "prep_cycle": "Yes"},
    }
    attended = [str(i) for i in range(10)]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Sunday",
        date="June 16",
        sabha_held="yes",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups=individual,
        captcha_seconds=1,
    )
    assert result["sabha_held"] is True


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_individual_groups_none_held(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    individual = {
        "group 0": {"held": "No"},
        "group 1": {"held": "No"},
        "group 2a": {"held": "No"},
        "group 2b": {"held": "No"},
        "group 3": {"held": "No"},
    }
    attended = [str(i) for i in range(10)]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Saturday",
        date="June 15",
        sabha_held="yes",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups=individual,
        captcha_seconds=1,
    )
    assert result["marked_present"] == 0


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_marks_attended_bals(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 3

    def make_row(bkid):
        el = MagicMock()
        el.text = f"{bkid} Some Name"
        el.find_element.return_value = MagicMock()
        return el

    driver.find_elements.return_value = [make_row("101"), make_row("102"), make_row("103")]

    attended = ["101", "102"] + [str(i) for i in range(200, 210)]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Saturday",
        date="June 15",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="yes",
        mukhpath="yes",
        prep_cycle_done="yes",
        individual_groups={},
        captcha_seconds=1,
    )
    assert result["marked_present"] == 2
    assert result["sabha_held"] is True


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_not_found_in_bkms(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 3

    def make_row(bkid):
        el = MagicMock()
        el.text = f"{bkid} Name"
        el.find_element.return_value = MagicMock()
        return el

    driver.find_elements.return_value = [make_row("101"), make_row("102")]

    attended = [str(i) for i in range(10)] + ["999"]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Saturday",
        date="June 15",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="yes",
        mukhpath="yes",
        prep_cycle_done="yes",
        individual_groups={},
        captcha_seconds=1,
    )
    assert "999" in result["not_found_in_bkms"]


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_log_callback(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    logs = []
    update_bal_sheet(
        attended_bals=[],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
        log_callback=logs.append,
    )
    assert any("Logging into BKMS" in m or "no groups held" in m.lower() for m in logs)


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_year_parse_fallback_to_last_option(mock_week, mock_driver_fn, monkeypatch):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    opt1 = MagicMock()
    opt1.text = "2020"
    opt1.click = MagicMock()
    opt2 = MagicMock()
    opt2.text = "2021"
    opt2.click = MagicMock()

    def find_elements(by, xpath):
        if xpath.endswith("/option"):
            return [opt1, opt2]
        return []

    driver.find_elements.side_effect = find_elements
    driver.find_element.return_value = MagicMock()

    import backend.coda as coda_mod
    monkeypatch.setattr(coda_mod, "convert_date", lambda *_: (_ for _ in ()).throw(Exception("parse fail")))

    result = update_bal_sheet(
        attended_bals=["101"],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
    )

    assert result["sabha_held"] is False
    assert opt2.click.call_count == 1
    driver.find_elements("dummy", "dummy")


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_year_option_text_exception_continues(mock_week, mock_driver_fn, monkeypatch):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    class BadTextOpt(MagicMock):
        @property
        def text(self):
            raise Exception("bad text")

    opt_bad = BadTextOpt()
    opt_bad.click = MagicMock()
    opt_good = MagicMock()
    opt_good.text = "2021"
    opt_good.click = MagicMock()

    def find_elements(by, xpath):
        if xpath.endswith("/option"):
            return [opt_bad, opt_good]
        return []

    driver.find_elements.side_effect = find_elements
    driver.find_element.return_value = MagicMock()

    import backend.coda as coda_mod
    monkeypatch.setattr(coda_mod, "convert_date", lambda *_: (_ for _ in ()).throw(Exception("parse fail")))

    result = update_bal_sheet(
        attended_bals=["101", "102", "103", "104", "105", "106"],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
    )

    assert result["sabha_held"] is False
    assert opt_good.click.call_count == 1
    driver.find_elements("dummy", "dummy")


from selenium.webdriver.common.by import By

@patch("backend.bal_mandal._js_click", lambda *args, **kwargs: None)
@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_handles_wait_and_logout_exceptions(mock_week, mock_driver_fn):
    driver = MagicMock()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    opt1 = MagicMock(); opt1.text = "2020"; opt1.click = MagicMock()
    opt2 = MagicMock(); opt2.text = "2021"; opt2.click = MagicMock()

    def find_elements(by, xpath):
        if xpath.endswith("/option"):
            return [opt1, opt2]
        if "tr[@role=\"row\"]" in xpath:
            return []
        return []

    driver.find_elements.side_effect = find_elements
    driver.execute_script.side_effect = Exception("script failed")

    def find_element(by, value):
        if by == By.XPATH and value == '/html/body/div[2]/header/nav/div/ul/li/a':
            raise Exception("logout missing")
        return MagicMock()

    driver.find_element.side_effect = find_element

    result = update_bal_sheet(
        attended_bals=["101", "102", "103", "104", "105", "106"],
        day="Sunday",
        date="June 16",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="yes",
        mukhpath="yes",
        prep_cycle_done="yes",
        individual_groups={},
        captcha_seconds=1,
    )

    assert result["sabha_held"] is True
    assert driver.quit.call_count == 1
    assert opt2.click.call_count == 1
    driver.find_elements("dummy", "dummy")


@patch("backend.bal_mandal._js_click", lambda *args, **kwargs: None)
@patch("backend.bal_mandal.WebDriverWait", side_effect=Exception("wait failure"))
@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_catches_webdriverwait_exception(mock_webdriverwait, mock_driver_fn, mock_week):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    opt1 = MagicMock(); opt1.text = "2025"; opt1.click = MagicMock()
    opt2 = MagicMock(); opt2.text = "2026"; opt2.click = MagicMock()

    def find_elements(by, xpath):
        if xpath.endswith("/option"):
            return [opt1, opt2]
        if "tr[@role=\"row\"]" in xpath:
            return []
        return []

    driver.find_elements.side_effect = find_elements
    driver.find_element.return_value = MagicMock()

    result = update_bal_sheet(
        attended_bals=["101", "102", "103", "104", "105", "106"],
        day="Sunday",
        date="June 16",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="yes",
        mukhpath="yes",
        prep_cycle_done="yes",
        individual_groups={},
        captcha_seconds=1,
    )

    assert result["sabha_held"] is True
    driver.find_elements("dummy", "dummy")


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_captcha_seconds_clamped(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    logs = []
    update_bal_sheet(
        attended_bals=[],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=9999,
        log_callback=logs.append,
    )
    countdown_msgs = [m for m in logs if m.startswith("__COUNTDOWN__")]
    assert len(countdown_msgs) == 300  # clamped to max 300


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_sunday_day_prefix(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    result = update_bal_sheet(
        attended_bals=[],
        day="Sunday Bal Group 0",
        date="June 16",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
    )
    assert result["sabha_held"] is False


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_year_from_coda(mock_week, mock_driver_fn, monkeypatch):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    monkeypatch.setattr("backend.coda.convert_date", lambda s: "2025-06-15T00:00:00.000-07:00")

    opt = MagicMock()
    opt.text = "2025 - Year"
    opt.click = MagicMock()
    driver.find_elements.return_value = [opt]

    update_bal_sheet(
        attended_bals=[],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
    )
    opt.click.assert_called()


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_year_fallback_when_no_match(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    opt = MagicMock()
    opt.text = "2020 - Old Year"
    opt.click = MagicMock()
    driver.find_elements.return_value = [opt]

    update_bal_sheet(
        attended_bals=[],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
    )
    opt.click.assert_called()


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_logout_exception_handled(mock_week, mock_driver_fn):
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2
    driver.find_element.side_effect = [MagicMock()] * 10 + [Exception("Logout failed")]

    result = update_bal_sheet(
        attended_bals=[],
        day="Saturday",
        date="June 15",
        sabha_held="no",
        combined_groups="no",
        smruti_time="no",
        mukhpath="no",
        prep_cycle_done="no",
        individual_groups={},
        captcha_seconds=1,
    )
    assert result is not None


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_row_with_no_text(mock_week, mock_driver_fn):
    """Rows with no name text parts are skipped."""
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    empty_row = MagicMock()
    empty_row.text = ""

    def make_row(bkid):
        el = MagicMock()
        el.text = f"{bkid} Name"
        el.find_element.return_value = MagicMock()
        return el

    driver.find_elements.return_value = [empty_row, make_row("101")]

    attended = [str(i) for i in range(10)]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Saturday",
        date="June 15",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="yes",
        mukhpath="yes",
        prep_cycle_done="yes",
        individual_groups={},
        captcha_seconds=1,
    )
    assert result is not None


@patch("backend.bal_mandal.get_chrome_driver")
@patch("backend.bal_mandal.calculate_week_number")
def test_update_bal_sheet_present_click_exception_handled(mock_week, mock_driver_fn):
    """Exception when clicking present radio is caught silently."""
    driver = make_driver()
    mock_driver_fn.return_value = driver
    mock_week.return_value = 2

    el = MagicMock()
    el.text = "101 Name"
    el.find_element.side_effect = Exception("no element")
    driver.find_elements.return_value = [el]

    attended = [str(i) for i in range(10)] + ["101"]
    result = update_bal_sheet(
        attended_bals=attended,
        day="Saturday",
        date="June 15",
        sabha_held="yes",
        combined_groups="yes",
        smruti_time="yes",
        mukhpath="yes",
        prep_cycle_done="yes",
        individual_groups={},
        captcha_seconds=1,
    )
    assert result["marked_present"] == 0
