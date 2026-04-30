import os
from dotenv import load_dotenv

load_dotenv()

BKMS_LOGIN_URL = "https://bk.na.baps.org/ssologin"
BKMS_REPORT_ATTENDANCE_URL = "https://bk.na.baps.org/admin/reports/reportweeksabhaattendance"
BKMS_ID = os.getenv("BKMS_ID")
BKMS_EMAIL = os.getenv("BKMS_EMAIL")
BKMS_PASSWORD = os.getenv("BKMS_PASSWORD")
MAIN_GROUP_TOKEN = os.getenv('MAIN_GROUP_TELEGRAM_TOKEN')
MAIN_GROUP_CHAT_ID = os.getenv('MAIN_GROUP_TELEGRAM_CHAT_ID')
BKMS_ACCESS_TYPE = os.getenv("BKMS_ACCESS_TYPE", "LocalAdmin")

BKMS_BASE_URL = "https://bk.na.baps.org/"
BKMS_USER_LIST_URL = "https://bk.na.baps.org/admin/user/userlist"
BKMS_GOSHTHI_URL = "https://bk.na.baps.org/admin/reports/karyakargoshthi"

# Kishore Coda Table IDs (set in .env)
SATURDAY_K1_TABLE_ID = os.getenv("SATURDAY_K1_TABLE_ID")
SATURDAY_K2_TABLE_ID = os.getenv("SATURDAY_K2_TABLE_ID")
SUNDAY_K1_TABLE_ID = os.getenv("SUNDAY_K1_TABLE_ID")
SUNDAY_K2_TABLE_ID = os.getenv("SUNDAY_K2_TABLE_ID")

# Bal Coda Table IDs (set in .env)
SATURDAY_BAL_GROUP_0_TABLE_ID = os.getenv("SATURDAY_BAL_GROUP_0_TABLE_ID")
SATURDAY_BAL_GROUP_1_TABLE_ID = os.getenv("SATURDAY_BAL_GROUP_1_TABLE_ID")
SATURDAY_BAL_GROUP_2A_TABLE_ID = os.getenv("SATURDAY_BAL_GROUP_2A_TABLE_ID")
SATURDAY_BAL_GROUP_2B_TABLE_ID = os.getenv("SATURDAY_BAL_GROUP_2B_TABLE_ID")
SATURDAY_BAL_GROUP_3_TABLE_ID = os.getenv("SATURDAY_BAL_GROUP_3_TABLE_ID")
SUNDAY_BAL_GROUP_0_TABLE_ID = os.getenv("SUNDAY_BAL_GROUP_0_TABLE_ID")
SUNDAY_BAL_GROUP_1_TABLE_ID = os.getenv("SUNDAY_BAL_GROUP_1_TABLE_ID")
SUNDAY_BAL_GROUP_2A_TABLE_ID = os.getenv("SUNDAY_BAL_GROUP_2A_TABLE_ID")
SUNDAY_BAL_GROUP_2B_TABLE_ID = os.getenv("SUNDAY_BAL_GROUP_2B_TABLE_ID")
SUNDAY_BAL_GROUP_3_TABLE_ID = os.getenv("SUNDAY_BAL_GROUP_3_TABLE_ID")

# Goshthi Coda Table IDs (set in .env)
GOSHTHI_9_10_TABLE_ID        = os.getenv("GOSHTHI_9_10_TABLE_ID")
GOSHTHI_11_12_TABLE_ID       = os.getenv("GOSHTHI_11_12_TABLE_ID")
GOSHTHI_COLLEGE_1_2_TABLE_ID = os.getenv("GOSHTHI_COLLEGE_1_2_TABLE_ID")
GOSHTHI_COLLEGE_3_4_TABLE_ID = os.getenv("GOSHTHI_COLLEGE_3_4_TABLE_ID")

SEARCH_FIELD_XPATH      = '/html/body/div[2]/div/section[2]/div[1]/form/div/div[3]/div[1]/input'
SEARCH_BUTTON_XPATH     = '/html/body/div[2]/div/section[2]/div[1]/form/div/div[5]/div[2]/input'
RESULT_ROWS_XPATH       = '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr'
CHECKBOX_XPATH          = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[1]/div[4]/div[2]/div/label/div/input'
SAVE_BUTTON_XPATH       = '/html/body/div[2]/div/section[2]/div/form/div[1]/input[4]'
CONFIRM_DIALOG_XPATH    = '/html/body/div[3]/div/div[6]/button[1]'
CANCEL_BUTTON_XPATH     = '/html/body/div[2]/div/section[2]/div/form/div[1]/a'
PARENT_TAB_XPATH        = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/ul/li[2]/a'
FATHER_FIRST_NAME_XPATH = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[1]/div[2]/div/div[1]/div[1]/input'
FATHER_LAST_NAME_XPATH  = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[1]/div[2]/div/div[1]/div[2]/input'
FATHER_EMAIL_XPATH      = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/input'
MOTHER_FIRST_NAME_XPATH = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div[1]/div[1]/input'
MOTHER_LAST_NAME_XPATH  = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div[1]/div[2]/input'
MOTHER_EMAIL_XPATH      = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/input'

SABHA_ROW_MAP = {
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

def get_xpaths(group_type: str = "kishore"):
    """Return XPATHs based on access type (RegionalAdmin or LocalAdmin) and group type (kishore or bal)"""
    access_type = BKMS_ACCESS_TYPE.lower().strip() if BKMS_ACCESS_TYPE else ""
    is_local = "local" in access_type
    group_type = group_type.lower().strip()
    
    # Determine Sabha Wing XPath based on group type
    if "bal" in group_type:
        sabha_wing_xpath = '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[2]'  # Bal
    else:
        sabha_wing_xpath = '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]'  # Kishore (default)
    
    common_xpaths = {
        "sabha_wing": sabha_wing_xpath,
        "year": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]',
        "week": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{}]',
        "sabha_held_yes": '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/div/ins',
        "sabha_held_no": '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label/div/ins',
        "mark_absent": '/html/body/div[2]/div/section[2]/div[2]/div[1]/span/a',
        "save_changes": '/html/body/div[2]/div/section[2]/div[1]/div[12]/form/div[3]/div/input[1]',
    }
    
    if is_local:
        # LocalAdmin XPATHs for Edison centers (Kishore only)
        common_xpaths.update({
            "sabha_center_saturday": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[2]',
            "sabha_center_sunday": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[3]',
            "sabha_group": '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[9]/div/span/a',
        })
    else:
        # RegionalAdmin XPATHs (default) - works for both Kishore and Bal
        common_xpaths.update({
            "sabha_center_saturday": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[13]',
            "sabha_center_sunday": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[14]',
            "sabha_group": '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[9]/div/span[2]/a',
        })
    
    # Add Bal Mandal specific XPATHs
    if "bal" in group_type:
        common_xpaths.update({
            # Combined group reporting
            "combined_groups_yes": '/html/body/div[2]/div/section[2]/div[1]/form/div[2]/label[1]/div/ins',
            "combined_groups_no": '/html/body/div[2]/div/section[2]/div[1]/form/div[2]/label[2]/div/ins',
            
            # Combined group activities
            "combined_smruti_time_yes": '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[1]/label[2]/div/ins',
            "combined_smruti_time_no": '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[1]/label[3]/div/ins',
            "combined_mukhpath_yes": '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[2]/label[2]/div/ins',
            "combined_mukhpath_no": '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[2]/label[3]/div/ins',
            "combined_prep_cycle_yes": '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[3]/label[2]/div/ins',
            "combined_prep_cycle_no": '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[3]/label[3]/div/ins',
            
            # Individual group reporting - Group 0
            "group_0_held_yes": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div/label[2]/div/ins',
            "group_0_held_no": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div/label[3]/div/ins',
            "group_0_smruti_time_yes": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[2]/div[1]/label[2]/div/ins',
            "group_0_smruti_time_no": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[2]/div[1]/label[3]/div/ins',
            "group_0_mukhpath_yes": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[2]/div[2]/label[2]/div/ins',
            "group_0_mukhpath_no": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[2]/div[2]/label[3]/div/ins',
            "group_0_prep_cycle_yes": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[2]/div[3]/label[2]/div/ins',
            "group_0_prep_cycle_no": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[2]/div[3]/label[3]/div/ins',
            
            # Individual group reporting - Group 1
            "group_1_held_yes": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[1]/div/label[2]/div/ins',
            "group_1_held_no": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[1]/div/label[3]/div/ins',
            "group_1_smruti_time_yes": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[2]/div[1]/label[2]/div/ins',
            "group_1_smruti_time_no": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[2]/div[1]/label[3]/div/ins',
            "group_1_mukhpath_yes": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[2]/div[2]/label[2]/div/ins',
            "group_1_mukhpath_no": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[2]/div[2]/label[3]/div/ins',
            "group_1_prep_cycle_yes": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[2]/div[3]/label[2]/div/ins',
            "group_1_prep_cycle_no": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[2]/div[3]/label[3]/div/ins',
            
            # Individual group reporting - Group 2A
            "group_2a_held_yes": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[1]/div/label[2]/div/ins',
            "group_2a_held_no": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[1]/div/label[3]/div/ins',
            "group_2a_smruti_time_yes": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[2]/div[1]/label[2]/div/ins',
            "group_2a_smruti_time_no": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[2]/div[1]/label[3]/div/ins',
            "group_2a_mukhpath_yes": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[2]/div[2]/label[2]/div/ins',
            "group_2a_mukhpath_no": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[2]/div[2]/label[3]/div/ins',
            "group_2a_prep_cycle_yes": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[2]/div[3]/label[2]/div/ins',
            "group_2a_prep_cycle_no": '/html/body/div[2]/div/section[2]/div[1]/div[6]/form/div[2]/div[3]/label[3]/div/ins',
            
            # Individual group reporting - Group 2B
            "group_2b_held_yes": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[1]/div/label[2]/div/ins',
            "group_2b_held_no": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[1]/div/label[3]/div/ins',
            "group_2b_smruti_time_yes": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[2]/div[1]/label[2]/div/ins',
            "group_2b_smruti_time_no": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[2]/div[1]/label[3]/div/ins',
            "group_2b_mukhpath_yes": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[2]/div[2]/label[2]/div/ins',
            "group_2b_mukhpath_no": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[2]/div[2]/label[3]/div/ins',
            "group_2b_prep_cycle_yes": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[2]/div[3]/label[2]/div/ins',
            "group_2b_prep_cycle_no": '/html/body/div[2]/div/section[2]/div[1]/div[8]/form/div[2]/div[3]/label[3]/div/ins',
            
            # Individual group reporting - Group 3
            "group_3_held_yes": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[1]/div/label[2]/div/ins',
            "group_3_held_no": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[1]/div/label[3]/div/ins',
            "group_3_smruti_time_yes": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[2]/div[1]/label[2]/div/ins',
            "group_3_smruti_time_no": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[2]/div[1]/label[3]/div/ins',
            "group_3_mukhpath_yes": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[2]/div[2]/label[2]/div/ins',
            "group_3_mukhpath_no": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[2]/div[2]/label[3]/div/ins',
            "group_3_prep_cycle_yes": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[2]/div[3]/label[2]/div/ins',
            "group_3_prep_cycle_no": '/html/body/div[2]/div/section[2]/div[1]/div[10]/form/div[2]/div[3]/label[3]/div/ins',
            
            # Attendance marking XPATHs
            "bkms_id_xpath": '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[1]',
            "present_checkbox_xpath": '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[10]/label/input',
            "mark_absent_xpath": '/html/body/div[2]/div/section[2]/div[2]/div[1]/span/a',
        })
    
    return common_xpaths

XPATHS = get_xpaths()  # Default to Kishore
XPATHS_BAL = get_xpaths("bal")
TELEGRAM_GROUP_CONFIG = {
    "saturday k1": {
        "token": os.getenv("SAT_K1_TELEGRAM_TOKEN"),
        "chat_id": os.getenv("SAT_K1_TELEGRAM_CHAT_ID"),
    },
    "saturday k2": {
        "token": os.getenv("SAT_K2_TELEGRAM_TOKEN"),
        "chat_id": os.getenv("SAT_K2_TELEGRAM_CHAT_ID"),
    },
    "sunday k1": {
        "token": os.getenv("SUN_K1_TELEGRAM_TOKEN"),
        "chat_id": os.getenv("SUN_K1_TELEGRAM_CHAT_ID"),
    },
    "sunday k2": {
        "token": os.getenv("SUN_K2_TELEGRAM_TOKEN"),
        "chat_id": os.getenv("SUN_K2_TELEGRAM_CHAT_ID"),
    },
}
TELEGRAM_GROUP_MENTIONS = {
    "saturday k1": "@rishipats04 @parthypatel",
    "saturday k2": "@JayprakashPatel @yashp705",
    "sunday k1":   "@mananedison @SharadVP",
    "sunday k2":   "@isthatdhrooo @ParthVinod",
}
BKMS_XPATH_CONFIG = {
    "PATHS": {
        "REGIONAL_XPATH": lambda row: f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{row}]/td[9]/div/span[2]/a',
        "LOCAL_XPATH": lambda row: f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{row}]/td[9]/div/span/a'
    }
}


def get_bal_coda_table_id(day: str, group: str) -> str:
    """Get Bal Coda table ID based on day and group"""
    day_lower = day.lower().strip()
    group_lower = group.lower().strip()
    
    # Normalize day name
    if "sat" in day_lower:
        day_key = "saturday"
    elif "sun" in day_lower:
        day_key = "sunday"
    else:
        return None
    
    # Map day + group to table ID
    bal_tables = {
        "saturday": {
            "group 0": SATURDAY_BAL_GROUP_0_TABLE_ID,
            "group 1": SATURDAY_BAL_GROUP_1_TABLE_ID,
            "group 2a": SATURDAY_BAL_GROUP_2A_TABLE_ID,
            "group 2b": SATURDAY_BAL_GROUP_2B_TABLE_ID,
            "group 3": SATURDAY_BAL_GROUP_3_TABLE_ID,
        },
        "sunday": {
            "group 0": SUNDAY_BAL_GROUP_0_TABLE_ID,
            "group 1": SUNDAY_BAL_GROUP_1_TABLE_ID,
            "group 2a": SUNDAY_BAL_GROUP_2A_TABLE_ID,
            "group 2b": SUNDAY_BAL_GROUP_2B_TABLE_ID,
            "group 3": SUNDAY_BAL_GROUP_3_TABLE_ID,
        }
    }
    
    return bal_tables.get(day_key, {}).get(group_lower)