import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.utils.chromeUtils import get_chrome_driver
from backend.utils.constants import BKMS_LOGIN_URL, BKMS_ID, BKMS_EMAIL, BKMS_PASSWORD

BKMS_BASE_URL = "https://bk.na.baps.org/"
BKMS_USER_LIST_URL = "https://bk.na.baps.org/admin/user/userlist"

SEARCH_FIELD_XPATH  = '/html/body/div[2]/div/section[2]/div[1]/form/div/div[3]/div[1]/input'
SEARCH_BUTTON_XPATH = '/html/body/div[2]/div/section[2]/div[1]/form/div/div[5]/div[2]/input'
RESULT_ROWS_XPATH   = '/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr'
CHECKBOX_XPATH      = '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[1]/div[4]/div[2]/div/label/div/input'
SAVE_BUTTON_XPATH   = '/html/body/div[2]/div/section[2]/div/form/div[1]/input[4]'
CONFIRM_DIALOG_XPATH = '/html/body/div[3]/div/div[6]/button[1]'


def update_users(user_ids: list, log_callback=None):
    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    def has_error(driver, text):
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
        return any(el.is_displayed() for el in elements)

    def save_and_confirm(driver):
        driver.find_element(By.XPATH, SAVE_BUTTON_XPATH).click()
        time.sleep(2)
        try:
            WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, CONFIRM_DIALOG_XPATH))
            ).click()
            time.sleep(2)
        except Exception:
            pass

    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 15)

    # --- Open BKMS and auto-login ---
    driver.get(BKMS_LOGIN_URL)
    time.sleep(1)
    driver.find_element(By.ID, "user_id").send_keys(BKMS_ID)
    time.sleep(0.5)
    driver.find_element(By.ID, "email").send_keys(BKMS_EMAIL)
    time.sleep(0.5)
    driver.find_element(By.ID, "password").send_keys(BKMS_PASSWORD)
    log("Please solve the CAPTCHA. You have 20 seconds. DO NOT click Sign In after solving!")
    for remaining in range(20, 0, -1):
        log(f"__COUNTDOWN__{remaining}")
        time.sleep(1)
    driver.find_element(By.CLASS_NAME, "btn-primary").click()
    time.sleep(2)
    log("Logged in. Resuming automation.")

    # --- Navigate to user list ---
    driver.get(BKMS_USER_LIST_URL)
    time.sleep(2)

    main_window = driver.current_window_handle

    for user_id in user_ids:
        user_id = str(user_id).strip()
        log(f"--- Processing User ID: {user_id} ---")

        # Make sure we are on the user list page
        if driver.current_url != BKMS_USER_LIST_URL:
            driver.get(BKMS_USER_LIST_URL)
            time.sleep(2)

        # --- Fill search field ---
        try:
            search_field = wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_FIELD_XPATH)))
            search_field.clear()
            search_field.send_keys(user_id)
            time.sleep(0.5)
        except Exception as e:
            log(f"  ERROR: Could not find search field for {user_id}: {e}")
            continue

        # --- Click search button ---
        try:
            driver.find_element(By.XPATH, SEARCH_BUTTON_XPATH).click()
            time.sleep(2)
        except Exception as e:
            log(f"  ERROR: Could not click search button for {user_id}: {e}")
            continue

        # --- Find matching row ---
        try:
            rows = driver.find_elements(By.XPATH, RESULT_ROWS_XPATH)
        except Exception as e:
            log(f"  ERROR: Could not read result rows for {user_id}: {e}")
            continue

        if not rows:
            log(f"  No results found for User ID: {user_id}")
            continue

        matched_row_index = None
        for idx, row in enumerate(rows, start=1):
            try:
                if row.find_element(By.XPATH, 'td[1]').text.strip() == user_id:
                    matched_row_index = idx
                    break
            except Exception:
                continue

        if matched_row_index is None:
            log(f"  No row with User ID {user_id} found in results.")
            continue

        log(f"  Found User ID {user_id} at row {matched_row_index}.")

        # --- Click the user detail link (opens new tab) ---
        user_link_xpath = (
            f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody'
            f'/tr[{matched_row_index}]/td[13]/div/span/a'
        )
        try:
            driver.find_element(By.XPATH, user_link_xpath).click()
            time.sleep(2)
        except Exception:
            log(f"  No action button found for {user_id}, skipping.")
            continue

        # --- Switch to the new tab ---
        new_window = next((h for h in driver.window_handles if h != main_window), None)
        if new_window is None:
            log(f"  ERROR: New tab did not open for {user_id}.")
            continue

        driver.switch_to.window(new_window)
        time.sleep(2)

        # --- Tick the checkbox only if not already checked ---
        try:
            checkbox = wait.until(EC.presence_of_element_located((By.XPATH, CHECKBOX_XPATH)))
            if checkbox.is_selected():
                log(f"  Checkbox already ticked for {user_id}, skipping.")
            else:
                driver.execute_script("""
                    var input = document.getElementById('is_saturday_sabha');
                    var container = input.closest('.icheckbox_square-blue');
                    input.checked = true;
                    if (container) {
                        container.setAttribute('aria-checked', 'true');
                        container.classList.add('checked');
                    }
                    $(input).trigger('ifChecked');
                    $(input).trigger('change');
                """)
                time.sleep(0.5)
                if checkbox.is_selected():
                    log(f"  Checkbox ticked for {user_id}.")
                else:
                    log(f"  WARNING: Checkbox may not have been ticked for {user_id}, check manually.")
            time.sleep(0.5)
        except Exception as e:
            log(f"  ERROR: Could not tick checkbox for {user_id}: {e}")
            driver.close()
            driver.switch_to.window(main_window)
            continue

        # --- Save ---
        try:
            save_and_confirm(driver)
        except Exception as e:
            log(f"  ERROR: Could not save for {user_id}: {e}")
            driver.close()
            driver.switch_to.window(main_window)
            continue

        # --- Handle known validation errors then check for unknowns ---
        halt = False
        try:
            needs_retry = False

            if has_error(driver, "Please Select Student Type"):
                log(f"  Student type missing for {user_id}, selecting Commuter...")
                driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/ul/li[5]/a').click()
                time.sleep(1)
                driver.execute_script("$('input[name=\"student_type\"]').first().iCheck('check');")
                time.sleep(0.5)
                needs_retry = True

            father_error = has_error(driver, "Please Enter Father")
            mother_error = has_error(driver, "Please Enter Mother")
            if father_error or mother_error:
                driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/ul/li[2]/a').click()
                time.sleep(1)
                if father_error:
                    log(f"  Father email missing for {user_id}, filling in...")
                    father_field = driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/input')
                    father_field.clear()
                    father_field.send_keys("dad@gmail.com")
                    needs_retry = True
                if mother_error:
                    log(f"  Mother email missing for {user_id}, filling in...")
                    mother_field = driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/input')
                    mother_field.clear()
                    mother_field.send_keys("mom@gmail.com")
                    needs_retry = True

            if needs_retry:
                save_and_confirm(driver)

            # Check for any remaining unknown errors
            known_errors = ["Please Select Student Type", "Please Enter Father", "Please Enter Mother"]
            unknown_errors = [
                el.text.strip()
                for el in driver.find_elements(By.XPATH, "//*[contains(text(), 'Please')]")
                if el.is_displayed() and el.text.strip()
                and not any(k in el.text for k in known_errors)
            ]
            if unknown_errors:
                log(f"  UNKNOWN ERROR(S) for {user_id}: {unknown_errors}")
                log("  Stopping program — add handling for these errors and rerun.")
                halt = True
            else:
                log(f"  Saved successfully for {user_id}.")

        except Exception as e:
            log(f"  ERROR: Post-save check failed for {user_id}: {e}")

        # --- Close the user detail tab and return to main window ---
        driver.close()
        driver.switch_to.window(main_window)
        time.sleep(1)

        if halt:
            break

    log("All user IDs processed.")
    driver.quit()


if __name__ == "__main__":
    USER_IDS = [
        "19477",
        "19478",
        "63040",
    ]
    update_users(USER_IDS)
