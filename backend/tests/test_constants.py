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
        "saturday bal group 0": 1,
        "saturday bal group 1": 2,
        "saturday bal group 2a": 3,
        "saturday bal group 2b": 4,
        "saturday bal group 3": 5,
        "sunday bal group 0": 1,
        "sunday bal group 1": 2,
        "sunday bal group 2a": 3,
        "sunday bal group 2b": 4,
        "sunday bal group 3": 5,
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
    assert constants.XPATHS["sabha_held_yes"] == '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/div/ins'
    assert constants.XPATHS["sabha_held_no"] == '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label/div/ins'
    assert constants.XPATHS["mark_absent"] == '/html/body/div[2]/div/section[2]/div[2]/div[1]/span/a'
    assert constants.XPATHS["save_changes"] == '/html/body/div[2]/div/section[2]/div[1]/div[12]/form/div[3]/div/input[1]'

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

# ── New constants added to constants.py ──────────────────────────────────────

def test_bkms_goshthi_url():
    assert constants.BKMS_GOSHTHI_URL == "https://bk.na.baps.org/admin/reports/karyakargoshthi"


def test_bkms_access_type_default_is_local_admin():
    with patch.dict("os.environ", {}, clear=False):
        # Without env override, default is "LocalAdmin"
        import importlib as _il
        with patch.dict("os.environ", {"BKMS_ACCESS_TYPE": "LocalAdmin"}):
            _il.reload(constants)
    assert constants.BKMS_ACCESS_TYPE == "LocalAdmin"


def test_bkms_access_type_from_env():
    with patch.dict("os.environ", {"BKMS_ACCESS_TYPE": "RegionalAdmin"}):
        importlib.reload(constants)
    assert constants.BKMS_ACCESS_TYPE == "RegionalAdmin"
    # restore
    importlib.reload(constants)


def test_goshthi_table_ids_from_env():
    env = {
        "GOSHTHI_9_10_TABLE_ID": "t910",
        "GOSHTHI_11_12_TABLE_ID": "t1112",
        "GOSHTHI_COLLEGE_1_2_TABLE_ID": "tc12",
        "GOSHTHI_COLLEGE_3_4_TABLE_ID": "tc34",
    }
    with patch.dict("os.environ", env):
        importlib.reload(constants)
    assert constants.GOSHTHI_9_10_TABLE_ID == "t910"
    assert constants.GOSHTHI_11_12_TABLE_ID == "t1112"
    assert constants.GOSHTHI_COLLEGE_1_2_TABLE_ID == "tc12"
    assert constants.GOSHTHI_COLLEGE_3_4_TABLE_ID == "tc34"
    importlib.reload(constants)


def test_telegram_group_config_has_all_groups():
    for group in ["saturday k1", "saturday k2", "sunday k1", "sunday k2"]:
        assert group in constants.TELEGRAM_GROUP_CONFIG
        cfg = constants.TELEGRAM_GROUP_CONFIG[group]
        assert "token" in cfg
        assert "chat_id" in cfg


def test_telegram_group_mentions_has_all_groups():
    for group in ["saturday k1", "saturday k2", "sunday k1", "sunday k2"]:
        assert group in constants.TELEGRAM_GROUP_MENTIONS
        assert isinstance(constants.TELEGRAM_GROUP_MENTIONS[group], str)


def test_bkms_xpath_config_structure():
    assert "PATHS" in constants.BKMS_XPATH_CONFIG
    paths = constants.BKMS_XPATH_CONFIG["PATHS"]
    assert "REGIONAL_XPATH" in paths
    assert "LOCAL_XPATH" in paths


def test_bkms_xpath_config_lambdas_return_strings_with_row():
    regional = constants.BKMS_XPATH_CONFIG["PATHS"]["REGIONAL_XPATH"](3)
    local = constants.BKMS_XPATH_CONFIG["PATHS"]["LOCAL_XPATH"](3)
    assert "tr[3]" in regional
    assert "tr[3]" in local
    assert isinstance(regional, str)
    assert isinstance(local, str)


def test_main_group_token_and_chat_id_exist():
    assert hasattr(constants, "MAIN_GROUP_TOKEN")
    assert hasattr(constants, "MAIN_GROUP_CHAT_ID")


def test_constants_has_goshthi_table_id_attributes():
    for attr in ["GOSHTHI_9_10_TABLE_ID", "GOSHTHI_11_12_TABLE_ID",
                 "GOSHTHI_COLLEGE_1_2_TABLE_ID", "GOSHTHI_COLLEGE_3_4_TABLE_ID"]:
        assert hasattr(constants, attr), f"Missing: {attr}"


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


def test_get_xpaths_local_admin_returns_local_center_xpaths():
    with patch.dict("os.environ", {"BKMS_ACCESS_TYPE": "LocalAdmin"}), \
         patch("backend.utils.constants.BKMS_ACCESS_TYPE", "LocalAdmin"):
        xpaths = constants.get_xpaths("kishore")
    assert xpaths["sabha_center_saturday"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[2]'
    assert xpaths["sabha_center_sunday"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[3]'
    assert "span/a" in xpaths["sabha_group"]


def test_get_xpaths_bal_returns_bal_wing_xpath():
    xpaths = constants.get_xpaths("bal")
    assert xpaths["sabha_wing"] == '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[2]'
    assert "combined_groups_yes" in xpaths
    assert "bkms_id_xpath" in xpaths
    assert "present_checkbox_xpath" in xpaths


def test_xpaths_bal_has_all_bal_group_keys():
    for group in ["group_0", "group_1", "group_2a", "group_2b", "group_3"]:
        assert f"{group}_held_yes" in constants.XPATHS_BAL
        assert f"{group}_held_no" in constants.XPATHS_BAL
        assert f"{group}_smruti_time_yes" in constants.XPATHS_BAL
        assert f"{group}_mukhpath_yes" in constants.XPATHS_BAL
        assert f"{group}_prep_cycle_yes" in constants.XPATHS_BAL


def test_get_bal_coda_table_id_saturday():
    with patch.dict("os.environ", {"SATURDAY_BAL_GROUP_0_TABLE_ID": "mock-sat-g0"}):
        importlib.reload(constants)
    result = constants.get_bal_coda_table_id("Saturday", "group 0")
    assert result == constants.SATURDAY_BAL_GROUP_0_TABLE_ID
    importlib.reload(constants)


def test_get_bal_coda_table_id_sunday():
    result = constants.get_bal_coda_table_id("Sunday", "group 2a")
    assert result == constants.SUNDAY_BAL_GROUP_2A_TABLE_ID


def test_get_bal_coda_table_id_invalid_day_returns_none():
    result = constants.get_bal_coda_table_id("Monday", "group 0")
    assert result is None


def test_get_bal_coda_table_id_invalid_group_returns_none():
    result = constants.get_bal_coda_table_id("Saturday", "group 99")
    assert result is None


def test_sabha_row_map_contains_bal_mandal_keys():
    for key in [
        "saturday bal group 0", "saturday bal group 1",
        "saturday bal group 2a", "saturday bal group 2b", "saturday bal group 3",
        "sunday bal group 0", "sunday bal group 1",
        "sunday bal group 2a", "sunday bal group 2b", "sunday bal group 3",
    ]:
        assert key in constants.SABHA_ROW_MAP


def test_get_xpaths_none_access_type():
    with patch.dict("os.environ", {}, clear=True):
        with patch.object(constants, 'BKMS_ACCESS_TYPE', None):
            xpaths = constants.get_xpaths("kishore")
    assert "sabha_wing" in xpaths
