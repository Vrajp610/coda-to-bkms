import pytest
import backend.utils.constants as constants

def test_bkms_login_url():
    assert constants.BKMS_LOGIN_URL == "https://bk.na.baps.org/ssologin"

def test_bkms_report_attendance_url():
    assert constants.BKMS_REPORT_ATTENDANCE_URL == "https://bk.na.baps.org/admin/reports/reportweeksabhaattendance"

def test_user_credentials():
    assert constants.USER_ID == "3001"
    assert constants.EMAIL == "vrajptl0610@gmail.com"
    assert constants.PASSWORD == "12345678"

def test_sabha_row_map_keys_and_values():
    expected = {
        "saturday k1": 1,
        "saturday k2": 2,
        "sunday k1": 3,
        "sunday k2": 4,
    }
    assert constants.SABHA_ROW_MAP == expected

def test_sabha_row_map_contains_all_keys():
    for key in ["saturday k1", "saturday k2", "sunday k1", "sunday k2"]:
        assert key in constants.SABHA_ROW_MAP

def test_sabha_row_map_values_are_int():
    for value in constants.SABHA_ROW_MAP.values():
        assert isinstance(value, int)

def test_xpaths_keys():
    expected_keys = {
        "sabha_wing",
        "year",
        "week",
        "sabha_group",
        "sabha_held_yes",
        "sabha_held_no",
        "mark_absent",
        "save_changes",
    }
    assert set(constants.XPATHS.keys()) == expected_keys

def test_xpaths_values():
    assert constants.XPATHS["sabha_wing"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]'
    assert constants.XPATHS["year"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]'
    assert constants.XPATHS["week"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{}]'
    assert constants.XPATHS["sabha_group"] == '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[9]/div/span/a'
    assert constants.XPATHS["sabha_held_yes"] == '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[1]/div/ins'
    assert constants.XPATHS["sabha_held_no"] == '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[2]/div/ins'
    assert constants.XPATHS["mark_absent"] == '/html/body/div[2]/div/section[2]/div[2]/div[1]/span/a'
    assert constants.XPATHS["save_changes"] == '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[3]/div/input[1]'

def test_xpath_week_format():
    week_xpath = constants.XPATHS["week"]
    assert week_xpath.format(5) == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[5]'
    assert week_xpath.format(1) == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[1]'

def test_xpath_sabha_group_format():
    sabha_group_xpath = constants.XPATHS["sabha_group"]
    assert sabha_group_xpath.format(2) == '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[2]/td[9]/div/span/a'
    assert sabha_group_xpath.format(4) == '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[4]/td[9]/div/span/a'

def test_xpaths_all_are_strings():
    for value in constants.XPATHS.values():
        assert isinstance(value, str)

def test_no_extra_keys_in_xpaths():
    allowed_keys = {
        "sabha_wing",
        "year",
        "week",
        "sabha_group",
        "sabha_held_yes",
        "sabha_held_no",
        "mark_absent",
        "save_changes",
    }
    for key in constants.XPATHS.keys():
        assert key in allowed_keys

def test_constants_module_has_expected_attributes():
    attrs = dir(constants)
    for attr in [
        "BKMS_LOGIN_URL",
        "BKMS_REPORT_ATTENDANCE_URL",
        "USER_ID",
        "EMAIL",
        "PASSWORD",
        "SABHA_ROW_MAP",
        "XPATHS"
    ]:
        assert attr in attrs