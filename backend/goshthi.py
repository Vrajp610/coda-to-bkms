import time
from calendar import monthrange
from datetime import datetime as _dt
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from backend.utils.chromeUtils import get_chrome_driver
from backend.utils.constants import (
    BKMS_LOGIN_URL, BKMS_ID, BKMS_EMAIL, BKMS_PASSWORD,
    BKMS_GOSHTHI_URL, BKMS_ACCESS_TYPE,
)
from backend.utils.sendNotifications import send_notifications, TELEGRAM_ENABLED


def update_goshthi(
    attended_ids: list,
    month: str,
    year: str,
    goshthi_held: str,
    hangout: str,
    workshop: str,
    captcha_seconds: int = 10,
    log_callback=None,
):
    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    # Early exit: goshthi was held but Coda has no/minimal attendance
    if goshthi_held.lower() == "yes" and (not attended_ids or len(attended_ids) <= 3):
        msg = (
            f"Goshthi attendance ({month} {year}) is not marked in Coda. "
            f"Please update Coda so BKMS can be updated. ❌"
        )
        notification_result = send_notifications(msg)
        telegram_status = (
            "Telegram notification sent"
            if notification_result["all_sent"]
            else "Telegram notification failed"
        ) if TELEGRAM_ENABLED else "[TELEGRAM DISABLED - Simulated]"
        log(f"{telegram_status}: {msg}")
        return {
            "marked_present": 0,
            "not_marked": 0,
            "marked_present_ids": [],
            "not_marked_ids": [],
            "not_found_in_bkms": [],
            "goshthi_held": True,
        }

    driver = get_chrome_driver()
    driver.get(BKMS_LOGIN_URL)

    log("Logging into BKMS...")
    driver.find_element(By.ID, "user_id").send_keys(BKMS_ID)
    driver.find_element(By.ID, "email").send_keys(BKMS_EMAIL)
    driver.find_element(By.ID, "password").send_keys(BKMS_PASSWORD)
    captcha_wait = max(1, int(captcha_seconds))
    log(f"Please solve the CAPTCHA. You have {captcha_wait} seconds. DO NOT click Sign In after solving!")
    for remaining in range(captcha_wait, 0, -1):
        log(f"__COUNTDOWN__{remaining}")
        time.sleep(1)
    driver.find_element(By.CLASS_NAME, "btn-primary").click()
    time.sleep(0.5)
    log("Logged in. Resuming automation.")

    # Navigate to Goshthi report page
    driver.get(BKMS_GOSHTHI_URL)
    time.sleep(0.5)

    # Select Year
    Select(
        driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div/div[1]/div[1]/select')
    ).select_by_value(year)
    time.sleep(0.2)

    # Select Month
    Select(
        driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div/div[1]/div[2]/select')
    ).select_by_value(month)
    time.sleep(0.2)

    # Select Center: Edison (dropdown position differs by access type)
    is_local = "local" in (BKMS_ACCESS_TYPE.lower().strip() if BKMS_ACCESS_TYPE else "")
    center_xpath = (
        '/html/body/div[2]/div/section[2]/div[1]/form/div/div[1]/div[4]/select/option[2]'
        if is_local
        else '/html/body/div[2]/div/section[2]/div[1]/form/div/div[1]/div[3]/select/option[2]'
    )
    driver.find_element(By.XPATH, center_xpath).click()
    time.sleep(0.2)

    # Click Search
    driver.find_element(
        By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div/div[2]/div/input'
    ).click()
    time.sleep(1)

    # Click Action on the result row
    driver.find_element(
        By.XPATH, '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr/td[15]/div/span/a'
    ).click()
    time.sleep(1)

    # ── Goshthi NOT held ──────────────────────────────────────────────────────
    if goshthi_held.lower() == "no":
        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[2]/div/ins'
        ).click()
        log("Marked: Goshthi Not Held")
        time.sleep(1)
        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[5]/div[3]/div/input'
        ).click()
        log("Saved successfully!")
        time.sleep(3)
        _logout(driver, log)
        msg = f"BKMS Goshthi updated for {month} {year} ✅ (Goshthi not held)"
        notification_result = send_notifications(msg)
        telegram_status = (
            "Telegram notification sent"
            if notification_result["all_sent"]
            else "Telegram notification failed"
        ) if TELEGRAM_ENABLED else "[TELEGRAM DISABLED - Simulated]"
        log(f"{telegram_status}: {msg}")
        return {
            "marked_present": 0,
            "not_marked": 0,
            "marked_present_ids": [],
            "not_marked_ids": [],
            "not_found_in_bkms": [],
            "goshthi_held": False,
        }

    # ── Goshthi WAS held ──────────────────────────────────────────────────────
    driver.find_element(
        By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[1]/div/ins'
    ).click()
    log("Marked: Goshthi Held")
    time.sleep(0.2)

    # Was this a Hangout?
    if hangout.lower() == "yes":
        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[2]/label[1]/div/ins'
        ).click()
        log("Marked: Was a Hangout")
    else:
        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[2]/label[2]/div/ins'
        ).click()
        log("Marked: Not a Hangout")
    time.sleep(0.2)

    # Was a Karyakar Workshop held?
    if workshop.lower() == "yes":
        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/label[1]/div/ins'
        ).click()
        log("Marked: Workshop Held")
    else:
        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/label[2]/div/ins'
        ).click()
        log("Marked: No Workshop")
    time.sleep(0.2)

    # ── Set Goshthi Date to last day of the selected month ───────────────────
    month_int = _dt.strptime(month, "%B").month
    last_day = monthrange(int(year), month_int)[1]
    date_str = f"{month_int:02d}/{last_day:02d}/{year}"
    log(f"Setting Goshthi Date to {date_str}")

    date_input = driver.find_element(
        By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[5]/div[2]/div[2]/input'
    )
    # Type directly — avoids the datepicker opening on the wrong month
    driver.execute_script("arguments[0].value = '';", date_input)
    date_input.send_keys(date_str)
    # Press Tab to confirm the value and close any datepicker popup
    date_input.send_keys(Keys.TAB)
    time.sleep(0.2)
    log(f"Goshthi Date set to {date_str}")

    # ── Mark attendance with pagination ───────────────────────────────────────
    marked_present = []
    all_bkms_ids = set()   # every ID seen across all pages (used for loop detection)
    page = 1

    while True:
        log(f"Processing page {page}...")
        rows = driver.find_elements(
            By.XPATH,
            '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr',
        )
        if not rows:
            break

        # Loop detection: if the first row's ID was already processed, we've wrapped around
        try:
            first_id_on_page = driver.find_element(
                By.XPATH,
                '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[1]/td[1]',
            ).text.strip()
            if first_id_on_page and first_id_on_page in all_bkms_ids:
                log(f"Loop detected on page {page} — all pages processed.")
                break
        except Exception:
            break

        for idx in range(1, len(rows) + 1):
            try:
                bkms_id = driver.find_element(
                    By.XPATH,
                    f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{idx}]/td[1]',
                ).text.strip()
                if not bkms_id:
                    continue
                all_bkms_ids.add(bkms_id)

                if bkms_id in attended_ids:
                    driver.find_element(
                        By.XPATH,
                        f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{idx}]/td[8]/label/input',
                    ).click()
                    marked_present.append(bkms_id)
                else:
                    driver.find_element(
                        By.XPATH,
                        f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{idx}]/td[9]/label/input',
                    ).click()
                time.sleep(0.05)
            except Exception as e:
                log(f"Error on row {idx}: {e}")
                continue

        log(f"Page {page} done — {len(all_bkms_ids)} total members processed so far.")

        # Try to advance to next page — Next button is always the last li in the pagination
        try:
            next_li = driver.find_element(
                By.XPATH,
                '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[3]/div[2]/div/ul/li[last()]',
            )
            li_class = next_li.get_attribute('class') or ''
            next_a = next_li.find_element(By.TAG_NAME, 'a')
            aria_disabled = next_a.get_attribute('aria-disabled') or ''

            if 'disabled' in li_class or aria_disabled == 'true':
                log("Reached last page (Next button disabled).")
                break

            next_a.click()
            time.sleep(0.8)
            page += 1
        except Exception:
            log("No next page button found — done.")
            break

    not_found_in_bkms = [kid for kid in attended_ids if kid not in all_bkms_ids]
    not_marked = [kid for kid in attended_ids if kid not in marked_present]

    if not_found_in_bkms:
        log(f"Not found in BKMS Goshthi: {', '.join(not_found_in_bkms)}")
        log(f"__NOT_FOUND__{'|'.join(not_found_in_bkms)}")
    if not_marked:
        log(f"Found in BKMS but not marked: {', '.join(not_marked)}")
        log(f"__NOT_MARKED__{'|'.join(not_marked)}")

    log(f"Successfully marked {len(marked_present)} members as Present")

    # Save
    driver.find_element(
        By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[5]/div[3]/div/input'
    ).click()
    log("Saved Goshthi attendance successfully!")
    time.sleep(1.5)

    _logout(driver, log)

    msg = f"BKMS Goshthi updated for {month} {year} ✅\n{len(marked_present)} marked present."
    if not_found_in_bkms:
        msg += f"\n\nIn Coda but not found in BKMS:\n{', '.join(not_found_in_bkms)}"
    notification_result = send_notifications(msg)
    telegram_status = "Telegram notification sent" if notification_result["all_sent"] else "Telegram notification failed"
    log(f"{telegram_status}: {msg.replace(chr(10), ' | ')}")

    return {
        "marked_present": len(marked_present),
        "not_marked": len(not_marked),
        "marked_present_ids": marked_present,
        "not_marked_ids": not_marked,
        "not_found_in_bkms": not_found_in_bkms,
        "goshthi_held": True,
    }


def _logout(driver, log):
    try:
        driver.find_element(By.XPATH, '/html/body/div[2]/header/nav/div/ul/li/a').click()
        time.sleep(0.3)
        driver.find_element(
            By.XPATH, '/html/body/div[2]/header/nav/div/ul/li/ul/li[2]/div[2]/a'
        ).click()
        log("Logged out of BKMS")
    except Exception:
        pass
    driver.quit()
    log("Closed Chrome")
