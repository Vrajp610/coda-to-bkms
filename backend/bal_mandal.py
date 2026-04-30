import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.utils.dateUtils import calculate_week_number
from backend.utils.chromeUtils import get_chrome_driver
from backend.utils.constants import (
    BKMS_LOGIN_URL, BKMS_ID, BKMS_EMAIL, BKMS_PASSWORD,
    BKMS_REPORT_ATTENDANCE_URL,
    XPATHS_BAL, SABHA_ROW_MAP,
)


def _js_click(driver, xpath, wait=10):
    """Wait for element to be present, scroll into view, then JS-click it."""
    el = WebDriverWait(driver, wait).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    driver.execute_script("arguments[0].click();", el)


# Groups in order: (display label, individual_groups key, SABHA_ROW_MAP key prefix)
_BAL_GROUPS = [
    ("Group 0",  "group 0"),
    ("Group 1",  "group 1"),
    ("Group 2A", "group 2a"),
    ("Group 2B", "group 2b"),
    ("Group 3",  "group 3"),
]

# Maps group_key ("group 0", "group 2a", ...) to the XPATHS_BAL key prefix
# e.g. "group 0" -> "group_0", "group 2a" -> "group_2a"
def _xpath_prefix(group_key: str) -> str:
    return group_key.replace(" ", "_")


def update_bal_sheet(
    attended_bals,
    day: str,
    date: str,
    sabha_held: str,
    combined_groups: str,
    smruti_time: str,
    mukhpath: str,
    prep_cycle_done: str,
    individual_groups: dict,
    captcha_seconds: int = 20,
    log_callback=None,
):
    """Update Bal Mandal attendance in BKMS for all 5 groups of the selected day."""

    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    captcha_seconds = max(1, min(int(captcha_seconds), 300))

    # Abort early if sabha was held but Coda has no attendance
    if sabha_held.lower() == "yes" and (not attended_bals or len(attended_bals) <= 5):
        log("Coda attendance is empty or too small. Please update Coda and rerun.")
        return {
            "marked_present": 0,
            "not_marked": 0,
            "marked_present_ids": [],
            "not_marked_ids": [],
            "not_found_in_bkms": [],
            "sabha_held": True,
        }

    day_prefix = "saturday" if "sat" in day.lower() else "sunday"

    # --- Open Chrome and Navigate to BKMS login ---
    driver = get_chrome_driver()
    driver.get(BKMS_LOGIN_URL)

    # --- Login ---
    log("Logging into BKMS...")
    driver.find_element(By.ID, "user_id").send_keys(BKMS_ID)
    driver.find_element(By.ID, "email").send_keys(BKMS_EMAIL)
    driver.find_element(By.ID, "password").send_keys(BKMS_PASSWORD)
    log(f"Please solve the CAPTCHA. You have {captcha_seconds} seconds. DO NOT click Sign In after solving!")
    for remaining in range(captcha_seconds, 0, -1):
        log(f"__COUNTDOWN__{remaining}")
        time.sleep(1)
    driver.find_element(By.CLASS_NAME, "btn-primary").click()
    time.sleep(0.5)
    log("Logged in. Resuming automation.")

    # --- Go to Report Attendance Page ---
    driver.get(BKMS_REPORT_ATTENDANCE_URL)
    time.sleep(0.3)

    # --- Select Sabha Wing (Bal) ---
    log("Selecting Sabha Wing and Center")
    driver.find_element(By.XPATH, XPATHS_BAL["sabha_wing"]).click()
    time.sleep(0.2)

    # --- Select Sabha Center ---
    if day_prefix == "saturday":
        driver.find_element(By.XPATH, XPATHS_BAL["sabha_center_saturday"]).click()
    else:
        driver.find_element(By.XPATH, XPATHS_BAL["sabha_center_sunday"]).click()
    time.sleep(0.2)

    # --- Select Year ---
    try:
        from backend.coda import convert_date
        year = int(convert_date(date).split("T")[0].split("-")[0])
    except Exception:
        from datetime import datetime as _dt
        year = _dt.now().year

    year_select_xpath = '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select'
    year_options = driver.find_elements(By.XPATH, f"{year_select_xpath}/option")
    selected = False
    for opt in year_options:
        try:
            if opt.text.strip().startswith(str(year)):
                opt.click()
                selected = True
                break
        except Exception:
            continue
    if not selected and year_options:
        year_options[-1].click()
    time.sleep(0.2)

    # --- Select Week ---
    week_number = calculate_week_number(date)
    log(f"Selecting Week {week_number - 1} for {day}")
    driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{week_number}]').click()
    time.sleep(0.3)

    # --- Enter attendance page: click Action for row 1 once (all groups are on the same page) ---
    log("Entering Bal attendance page...")
    _js_click(driver, XPATHS_BAL["sabha_group"].format(1))
    time.sleep(1.5)

    # --- Top-level "Was at least one group sabha held?" toggle ---
    if sabha_held.lower() != "yes":
        _js_click(driver, XPATHS_BAL["sabha_held_no"])
        time.sleep(0.3)
        log("No groups held — saving and exiting.")
        _js_click(driver, '/html/body/div[2]/div/section[2]/div[1]/div[12]/form/div[3]/div/input[1]')
        log("Saving...")
        time.sleep(5)
        log("Saved")
        try:
            driver.find_element(By.XPATH, '/html/body/div[2]/header/nav/div/ul/li/a').click()
            time.sleep(0.3)
            driver.find_element(By.XPATH, '/html/body/div[2]/header/nav/div/ul/li/ul/li[2]/div[2]/a').click()
            log("Logged out of BKMS")
        except Exception:
            log("Logout step skipped (could not find logout button)")
        driver.quit()
        log("Closed Chrome")
        return {
            "marked_present": 0,
            "not_marked": 0,
            "marked_present_ids": [],
            "not_marked_ids": [],
            "not_found_in_bkms": [],
            "sabha_held": False,
        }

    _js_click(driver, XPATHS_BAL["sabha_held_yes"])
    time.sleep(0.2)
    log("Marked: at least one group sabha held")

    any_group_held = False

    # --- If combined groups reporting ---
    if combined_groups.lower() == "yes":
        log("--- Combined Groups Reporting ---")
        # Click the combined group checkbox
        _js_click(driver, '/html/body/div[2]/div/section[2]/div[1]/form/div[2]/label[1]/div/ins')
        time.sleep(0.2)
        log("Marked: combined group reporting enabled")

        # Click the 3 activity options based on combined values
        smruti_xpath = '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[1]/label[2]/div/ins' if smruti_time.lower() == "yes" else '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[1]/label[3]/div/ins'
        _js_click(driver, smruti_xpath)
        time.sleep(0.15)
        log(f"Smruti Time: {smruti_time}")

        mukhpath_xpath = '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[2]/label[2]/div/ins' if mukhpath.lower() == "yes" else '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[2]/label[3]/div/ins'
        _js_click(driver, mukhpath_xpath)
        time.sleep(0.15)
        log(f"Mukhpath: {mukhpath}")

        prep_xpath = '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[3]/label[2]/div/ins' if prep_cycle_done.lower() == "yes" else '/html/body/div[2]/div/section[2]/div[1]/form/div[4]/div[2]/div[3]/label[3]/div/ins'
        _js_click(driver, prep_xpath)
        time.sleep(0.15)
        log(f"Prep Cycle: {prep_cycle_done}")

        any_group_held = True
    else:
        # --- Individual group reporting: select No for combined reporting first ---
        _js_click(driver, '/html/body/div[2]/div/section[2]/div[1]/form/div[2]/label[2]/div/ins')
        time.sleep(0.2)
        log("Marked: combined group reporting disabled")

        # --- Fill in held / activities for each group (individual reporting) ---
        for group_label, group_key in _BAL_GROUPS:
            log(f"--- Filling {day} Bal {group_label} ---")
            prefix = _xpath_prefix(group_key)  # e.g. "group_0", "group_2a"

            gdata = individual_groups.get(group_key, {})
            group_sabha_held = gdata.get("held", "No")
            group_smruti   = gdata.get("smruti_time", "No")
            group_mukhpath = gdata.get("mukhpath", "No")
            group_prep     = gdata.get("prep_cycle", "No")

            if group_sabha_held.lower() != "yes":
                _js_click(driver, XPATHS_BAL[f"{prefix}_held_no"])
                time.sleep(0.15)
                log(f"{group_label}: Sabha not held")
            else:
                any_group_held = True
                _js_click(driver, XPATHS_BAL[f"{prefix}_held_yes"])
                time.sleep(0.2)

                smruti_key = f"{prefix}_smruti_time_yes" if group_smruti.lower() == "yes" else f"{prefix}_smruti_time_no"
                _js_click(driver, XPATHS_BAL[smruti_key])
                time.sleep(0.15)

                mukhpath_key = f"{prefix}_mukhpath_yes" if group_mukhpath.lower() == "yes" else f"{prefix}_mukhpath_no"
                _js_click(driver, XPATHS_BAL[mukhpath_key])
                time.sleep(0.15)

                prep_key = f"{prefix}_prep_cycle_yes" if group_prep.lower() == "yes" else f"{prefix}_prep_cycle_no"
                _js_click(driver, XPATHS_BAL[prep_key])
                time.sleep(0.15)

                log(f"{group_label}: Sabha held, activities filled")

    # --- Mark attendance (only if at least one group was held) ---
    all_found_bkids = set()
    all_marked = []

    if any_group_held:
        # Mark all absent first
        _js_click(driver, XPATHS_BAL["mark_absent"])
        log("All Bals initially marked Absent")
        time.sleep(0.3)

        # Mark present for attended bals
        table_body = '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody'
        all_bals = driver.find_elements(By.XPATH, f'{table_body}/tr[@role="row"]')
        index = -1
        for element in all_bals:
            index += 1
            name_parts = element.text.split()
            if not name_parts:
                continue
            bkid = name_parts[0]
            all_found_bkids.add(bkid)
            if bkid in attended_bals:
                try:
                    radio = element.find_element(By.XPATH, f'{table_body}/tr[{index}]/td[10]/label/input')
                    radio.click()
                    all_marked.append(bkid)
                    time.sleep(0.1)
                except Exception as e:
                    pass

        log(f"Marked {len(all_marked)} Bals present")

    # --- Save (single save covers all groups) ---
    _js_click(driver, XPATHS_BAL["save_changes"])
    log("Saving all groups...")
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass
    time.sleep(5)
    log("Saved all groups")

    # --- Logout ---
    try:
        driver.find_element(By.XPATH, '/html/body/div[2]/header/nav/div/ul/li/a').click()
        time.sleep(0.3)
        driver.find_element(By.XPATH, '/html/body/div[2]/header/nav/div/ul/li/ul/li[2]/div[2]/a').click()
        log("Logged out of BKMS")
    except Exception:
        log("Logout step skipped (could not find logout button)")

    driver.quit()
    log("Closed Chrome")

    not_found_in_bkms = [b for b in attended_bals if b not in all_found_bkids]
    if not_found_in_bkms:
        log(f"Bals not found in BKMS across all groups: {not_found_in_bkms}")

    log(f"Total Bals marked present: {len(all_marked)}")

    not_marked_ids = [b for b in attended_bals if b not in all_marked and b not in not_found_in_bkms]

    return {
        "marked_present": len(all_marked),
        "not_marked": len(attended_bals) - len(all_marked),
        "marked_present_ids": all_marked,
        "not_marked_ids": not_marked_ids,
        "not_found_in_bkms": not_found_in_bkms,
        "sabha_held": sabha_held.lower() == "yes",
    }
