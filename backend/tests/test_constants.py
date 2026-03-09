import backend.utils.constants as constants
from unittest.mock import patch
import importlib

def test_bkms_login_url():
    assert constants.BKMS_LOGIN_URL == "https://bk.na.baps.org/ssologin"

def test_bkms_report_attendance_url():
    assert constants.BKMS_REPORT_ATTENDANCE_URL == "https://bk.na.baps.org/admin/reports/reportweeksabhaattendance"

@patch.dict("os.environ", {
    "BKMS_ID": "test-id",
    "BKMS_EMAIL": "test@example.com",
    "BKMS_PASSWORD": "test-pass"
})
def test_user_credentials():
    importlib.reload(constants)
    assert constants.BKMS_ID == "test-id"
    assert constants.BKMS_EMAIL == "test@example.com"
    assert constants.BKMS_PASSWORD == "test-pass"

def test_sabha_row_map_keys_and_values():
    expected = {
        "saturday k1": 1,
        "saturday k2": 2,
        "sunday k1": 1,
        "sunday k2": 2,
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
        "sabha_center_saturday",
        "sabha_center_sunday",
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
    assert constants.XPATHS["sabha_center_saturday"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[13]'
    assert constants.XPATHS["sabha_center_sunday"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[14]'
    assert constants.XPATHS["year"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]'
    assert constants.XPATHS["week"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{}]'
    assert constants.XPATHS["sabha_group"] == '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[9]/div/span[2]/a'
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
    assert sabha_group_xpath.format(1) == '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[9]/div/span[2]/a'
    assert sabha_group_xpath.format(2) == '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[2]/td[9]/div/span[2]/a'

def test_xpaths_all_are_strings():
    for value in constants.XPATHS.values():
        assert isinstance(value, str)

def test_no_extra_keys_in_xpaths():
    allowed_keys = {
        "sabha_wing",
        "sabha_center_saturday",
        "sabha_center_sunday",
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
        "BKMS_ID",
        "BKMS_EMAIL",
        "BKMS_PASSWORD",
        "SABHA_ROW_MAP",
        "XPATHS",
        "BKMS_BASE_URL",
        "BKMS_USER_LIST_URL",
        "SEARCH_FIELD_XPATH",
        "SEARCH_BUTTON_XPATH",
        "RESULT_ROWS_XPATH",
        "CHECKBOX_XPATH",
        "SAVE_BUTTON_XPATH",
        "CONFIRM_DIALOG_XPATH",
        "CANCEL_BUTTON_XPATH",
        "PARENT_TAB_XPATH",
        "FATHER_FIRST_NAME_XPATH",
        "FATHER_LAST_NAME_XPATH",
        "FATHER_EMAIL_XPATH",
        "MOTHER_FIRST_NAME_XPATH",
        "MOTHER_LAST_NAME_XPATH",
        "MOTHER_EMAIL_XPATH",
    ]:
        assert attr in attrs


# ──────────────────────────────────────────────
# New constants: BKMS_BASE_URL and BKMS_USER_LIST_URL
# ──────────────────────────────────────────────

def test_bkms_base_url():
    assert constants.BKMS_BASE_URL == "https://bk.na.baps.org/"

def test_bkms_user_list_url():
    assert constants.BKMS_USER_LIST_URL == "https://bk.na.baps.org/admin/user/userlist"


# ──────────────────────────────────────────────
# Individual XPATH constant value tests
# ──────────────────────────────────────────────

def test_search_field_xpath():
    assert constants.SEARCH_FIELD_XPATH == '/html/body/div[2]/div/section[2]/div[1]/form/div/div[3]/div[1]/input'

def test_search_button_xpath():
    assert constants.SEARCH_BUTTON_XPATH == '/html/body/div[2]/div/section[2]/div[1]/form/div/div[5]/div[2]/input'

def test_result_rows_xpath():
    assert constants.RESULT_ROWS_XPATH == '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr'

def test_checkbox_xpath():
    assert constants.CHECKBOX_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[1]/div[4]/div[2]/div/label/div/input'

def test_save_button_xpath():
    assert constants.SAVE_BUTTON_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[1]/input[4]'

def test_confirm_dialog_xpath():
    assert constants.CONFIRM_DIALOG_XPATH == '/html/body/div[3]/div/div[6]/button[1]'

def test_cancel_button_xpath():
    assert constants.CANCEL_BUTTON_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[1]/a'

def test_parent_tab_xpath():
    assert constants.PARENT_TAB_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/ul/li[2]/a'

def test_father_first_name_xpath():
    assert constants.FATHER_FIRST_NAME_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[1]/div[2]/div/div[1]/div[1]/input'

def test_father_last_name_xpath():
    assert constants.FATHER_LAST_NAME_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[1]/div[2]/div/div[1]/div[2]/input'

def test_father_email_xpath():
    assert constants.FATHER_EMAIL_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/input'

def test_mother_first_name_xpath():
    assert constants.MOTHER_FIRST_NAME_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div[1]/div[1]/input'

def test_mother_last_name_xpath():
    assert constants.MOTHER_LAST_NAME_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div[1]/div[2]/input'

def test_mother_email_xpath():
    assert constants.MOTHER_EMAIL_XPATH == '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/input'


# ──────────────────────────────────────────────
# All new XPATH constants are strings
# ──────────────────────────────────────────────

def test_all_new_xpath_constants_are_strings():
    xpath_attrs = [
        "SEARCH_FIELD_XPATH",
        "SEARCH_BUTTON_XPATH",
        "RESULT_ROWS_XPATH",
        "CHECKBOX_XPATH",
        "SAVE_BUTTON_XPATH",
        "CONFIRM_DIALOG_XPATH",
        "CANCEL_BUTTON_XPATH",
        "PARENT_TAB_XPATH",
        "FATHER_FIRST_NAME_XPATH",
        "FATHER_LAST_NAME_XPATH",
        "FATHER_EMAIL_XPATH",
        "MOTHER_FIRST_NAME_XPATH",
        "MOTHER_LAST_NAME_XPATH",
        "MOTHER_EMAIL_XPATH",
    ]
    for attr in xpath_attrs:
        assert isinstance(getattr(constants, attr), str), f"{attr} should be a string"
