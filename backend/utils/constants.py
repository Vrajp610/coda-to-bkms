import os

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
}
XPATHS = {
    "sabha_wing": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]',
    "sabha_center_saturday": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[13]',
    "sabha_center_sunday": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[2]/select/option[14]',
    "year": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]',
    "week": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{}]',
    "sabha_group": '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[9]/div/span[2]/a',
    "sabha_held_yes": '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[1]/div/ins',
    "sabha_held_no": '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[2]/div/ins',
    "mark_absent": '/html/body/div[2]/div/section[2]/div[2]/div[1]/span/a',
    "save_changes": '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[3]/div/input[1]',
}
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