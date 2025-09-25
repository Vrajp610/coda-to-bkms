import os

BKMS_LOGIN_URL = "https://bk.na.baps.org/ssologin"
BKMS_REPORT_ATTENDANCE_URL = "https://bk.na.baps.org/admin/reports/reportweeksabhaattendance"
BKMS_ID = os.getenv("BKMS_ID")
BKMS_EMAIL = os.getenv("BKMS_EMAIL")
BKMS_PASSWORD = os.getenv("BKMS_PASSWORD")
SABHA_ROW_MAP = {
    "saturday k1": 1,
    "saturday k2": 2,
    "sunday k1": 3,
    "sunday k2": 4,
}
XPATHS = {
    "sabha_wing": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]',
    "year": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]',
    "week": '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{}]',
    "sabha_group": '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{}]/td[9]/div/span/a',
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
MAIN_GROUP_TOKEN = os.getenv('MAIN_GROUP_TELEGRAM_TOKEN')
MAIN_GROUP_CHAT_ID = os.getenv('MAIN_GROUP_TELEGRAM_CHAT_ID')