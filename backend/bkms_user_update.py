import os
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.utils.chromeUtils import get_chrome_driver
from backend.utils.constants import (
    BKMS_LOGIN_URL, BKMS_ID, BKMS_EMAIL, BKMS_PASSWORD,
    BKMS_USER_LIST_URL,
    SEARCH_FIELD_XPATH, SEARCH_BUTTON_XPATH, RESULT_ROWS_XPATH,
    CHECKBOX_XPATH, SAVE_BUTTON_XPATH, CONFIRM_DIALOG_XPATH,
    CANCEL_BUTTON_XPATH, PARENT_TAB_XPATH,
    FATHER_FIRST_NAME_XPATH, FATHER_LAST_NAME_XPATH, FATHER_EMAIL_XPATH,
    MOTHER_FIRST_NAME_XPATH, MOTHER_LAST_NAME_XPATH, MOTHER_EMAIL_XPATH,
)


def update_users(user_ids: list, log_callback=None):
    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    def has_error(driver, text):
        # Use double quotes in XPath when the text itself contains a single quote
        if "'" in text:
            xpath = f'//*[contains(text(), "{text}")]'
        else:
            xpath = f"//*[contains(text(), '{text}')]"
        elements = driver.find_elements(By.XPATH, xpath)
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

    def fill_field(driver, xpath, value):
        field = driver.find_element(By.XPATH, xpath)
        field.clear()
        field.send_keys(value)

    error_records = {}  # user_id -> list of error strings

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

        # --- Pre-check: skip if the Saturday Sabha checkbox is already marked ---
        pre_check_xpath = (
            f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody'
            f'/tr[{matched_row_index}]/td[11]/div'
        )
        try:
            check_div = driver.find_element(By.XPATH, pre_check_xpath)
            classes = check_div.get_attribute("class") or ""
            if "checked" in classes:
                log(f"  User {user_id} is already marked in list view — skipping.")
                continue
        except Exception:
            pass  # If the pre-check fails, proceed with the normal flow

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
            user_errors = []
            skipped = False

            # --- Address error: cancel, log, and move on ---
            if has_error(driver, "Please Enter Address"):
                user_errors.append("Please Enter Address.")
                log(f"  Address missing for {user_id}, cancelling and logging.")
                driver.find_element(By.XPATH, CANCEL_BUTTON_XPATH).click()
                time.sleep(1)
                error_records[user_id] = user_errors
                skipped = True

            if not skipped:
                if has_error(driver, "Please Select Student Type"):
                    log(f"  Student type missing for {user_id}, selecting Commuter...")
                    driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div/form/div[3]/div[1]/ul/li[5]/a').click()
                    time.sleep(1)
                    driver.execute_script("$('input[name=\"student_type\"]').first().iCheck('check');")
                    time.sleep(0.5)
                    needs_retry = True

                # --- Father/Mother name and email errors ---
                father_first_error  = has_error(driver, "Please Enter Father First Name")
                father_last_error   = has_error(driver, "Please Enter Father Last Name")
                father_email_error  = has_error(driver, "Please Enter Father Email")
                mother_first_error  = has_error(driver, "Please Enter Mother First Name")
                mother_last_error   = has_error(driver, "Please Enter Mother Last Name")
                mother_email_error  = (has_error(driver, "Please Enter Mother Email") or
                                       has_error(driver, "Please Enter Mother's Email"))

                any_father = father_first_error or father_last_error or father_email_error
                any_mother = mother_first_error or mother_last_error or mother_email_error

                if any_father or any_mother:
                    driver.find_element(By.XPATH, PARENT_TAB_XPATH).click()
                    time.sleep(1)

                    if father_first_error:
                        user_errors.append("Please Enter Father First Name.")
                        log(f"  Father first name missing for {user_id}, filling in 'Dad'...")
                        fill_field(driver, FATHER_FIRST_NAME_XPATH, "Dad")
                        needs_retry = True
                    if father_last_error:
                        user_errors.append("Please Enter Father Last Name.")
                        log(f"  Father last name missing for {user_id}, filling in 'dad'...")
                        fill_field(driver, FATHER_LAST_NAME_XPATH, "dad")
                        needs_retry = True
                    if father_email_error:
                        user_errors.append("Please Enter Father Email.")
                        log(f"  Father email missing for {user_id}, filling in...")
                        fill_field(driver, FATHER_EMAIL_XPATH, "dad@gmail.com")
                        needs_retry = True
                    if mother_first_error:
                        user_errors.append("Please Enter Mother First Name.")
                        log(f"  Mother first name missing for {user_id}, filling in 'mom'...")
                        fill_field(driver, MOTHER_FIRST_NAME_XPATH, "mom")
                        needs_retry = True
                    if mother_last_error:
                        user_errors.append("Please Enter Mother Last Name.")
                        log(f"  Mother last name missing for {user_id}, filling in 'mom'...")
                        fill_field(driver, MOTHER_LAST_NAME_XPATH, "mom")
                        needs_retry = True
                    if mother_email_error:
                        user_errors.append("Please Enter Mother Email.")
                        log(f"  Mother email missing for {user_id}, filling in...")
                        fill_field(driver, MOTHER_EMAIL_XPATH, "mom@gmail.com")
                        needs_retry = True

                if needs_retry:
                    save_and_confirm(driver)

                # --- Verify Saturday Sabha checkbox is still ticked after all saves ---
                try:
                    final_checkbox = driver.find_element(By.XPATH, CHECKBOX_XPATH)
                    if not final_checkbox.is_selected():
                        log(f"  WARNING: Saturday Sabha checkbox not ticked for {user_id} after save — re-ticking...")
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
                        save_and_confirm(driver)
                        user_errors.append("Saturday Sabha checkbox not ticked after save — re-ticked.")
                        log(f"  Saturday Sabha re-ticked and saved for {user_id}.")
                except Exception:
                    pass

                if user_errors:
                    error_records[user_id] = user_errors

                # Check for any remaining unknown errors
                known_errors = [
                    "Please Select Student Type",
                    "Please Enter Father First Name", "Please Enter Father Last Name", "Please Enter Father Email",
                    "Please Enter Mother First Name", "Please Enter Mother Last Name",
                    "Please Enter Mother Email", "Please Enter Mother's Email",
                    "Please Enter Address",
                ]
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

    if error_records:
        log_dir = os.path.join("logs", "user_update")
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        error_path = os.path.join(log_dir, f"errors_{timestamp}.log")
        with open(error_path, "w") as f:
            for uid, errors in error_records.items():
                f.write(f"{uid}: {', '.join(errors)}\n")
        log(f"Errors written to {error_path}")

    driver.quit()


if __name__ == "__main__":
    USER_IDS = [
        "19477",
        "19478",
        "63040",
    ]
    update_users(USER_IDS)
