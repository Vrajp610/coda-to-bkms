import time
import asyncio
from selenium.webdriver.common.by import By
from backend.utils.telegramUtils import send_telegram_message
from backend.utils.dateUtils import calculate_week_number, get_this_week_sunday
from backend.utils.chromeUtils import get_chrome_driver
from backend.utils.constants import BKMS_LOGIN_URL, BKMS_ID, BKMS_EMAIL, BKMS_PASSWORD, BKMS_REPORT_ATTENDANCE_URL, TELEGRAM_GROUP_CONFIG, TELEGRAM_GROUP_MENTIONS

# --- Main function: Update attendance in BKMS ---
def update_sheet(attended_kishores, day: str, sabha_held: str, p2_guju: str, date_string: str, prep_cycle_done: str):
   # If sabha was held but Coda attendance is empty, notify and abort BEFORE opening Chromium
   if sabha_held.lower() == "yes" and (not attended_kishores or len(attended_kishores) == 0):
      sunday_date = get_this_week_sunday(date_string)
      base_msg = f"{day.title()} attendance ({sunday_date}) is not marked in Coda. Please update Coda so BKMS can be updated. ❌"
      mentions = TELEGRAM_GROUP_MENTIONS.get(day.lower(), "")
      telegram_message = f"{base_msg}\n\n{mentions}" if mentions else base_msg
      # Send to group-specific channel if configured
      group_cfg = TELEGRAM_GROUP_CONFIG.get(day.lower())
      if group_cfg and group_cfg.get("token") and group_cfg.get("chat_id"):
         asyncio.run(send_telegram_message(telegram_message, token=group_cfg["token"], chat_id=group_cfg["chat_id"]))
      # Always send to central channel
      asyncio.run(send_telegram_message(telegram_message))
      print(f"Telegram notification sent: {telegram_message}")
      return {
         "marked_present": 0,
         "not_marked": 0,
         "not_found_in_bkms": []
      }

   # --- Open Chrome and Navigate to BKMS login ---
   driver = get_chrome_driver()
   driver.get(BKMS_LOGIN_URL)

   # --- Perform Login ---
   print("Logging into BKMS...")
   time.sleep(1)
   driver.find_element(By.ID, "user_id").send_keys(BKMS_ID)
   time.sleep(0.5)
   driver.find_element(By.ID, "email").send_keys(BKMS_EMAIL)
   time.sleep(0.5)
   driver.find_element(By.ID, "password").send_keys(BKMS_PASSWORD)
   print("Please solve CAPTCHA manually (60 seconds). DO NOT CLICK SIGN IN AFTER SOLVING!")
   time.sleep(60)
   driver.find_element(By.CLASS_NAME, "btn-primary").click()
   time.sleep(2)

   # --- Go to Report Attendance Page ---
   driver.get(BKMS_REPORT_ATTENDANCE_URL)
   time.sleep(2)

   # --- Select Sabha Wing and Year ---
   print("Selecting Sabha Wing and Year")
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]').click()  # Kishore
   time.sleep(1)
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]').click()  # 2025
   time.sleep(1)

   # --- Select Week based on Entered Date ---
   week_number = calculate_week_number(date_string)
   print(f"Selecting Week {week_number - 1} for {date_string}")
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{week_number}]').click()
   time.sleep(2)

   # --- Select Specific Sabha Group (K1/K2/S1/S2) ---
   sabha_row_map = {
      "saturday k1": 1,
      "saturday k2": 2,
      "sunday k1": 3,
      "sunday k2": 4
   }
   row_number = sabha_row_map.get(day.lower())
   if row_number:
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{row_number}]/td[9]/div/span[2]/a').click()
      print(f"Selected {day.title()}")
   else:
      print("Error: Invalid Sabha group entered!")
      return

   time.sleep(3)

   # --- Sabha WAS NOT held ---
   if sabha_held.lower() == "no":
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[2]/div/ins').click()
      print("Marked: Sabha Not Held")
      time.sleep(2)

      # --- Save Changes Immediately ---
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[3]/div/input[1]').click()
      print("Saved attendance successfully!")
      time.sleep(2)

      # --- Send Telegram Success Notification ---
      sunday_date = get_this_week_sunday(date_string)
      base_msg = f"BKMS Attendance updated for {day.title()} - {sunday_date} ✅ as Sabha not held!"
      mentions = TELEGRAM_GROUP_MENTIONS.get(day.lower(), "")
      telegram_message = f"{base_msg}\n\n{mentions}" if mentions else base_msg
      group_cfg = TELEGRAM_GROUP_CONFIG.get(day.lower())
      if group_cfg and group_cfg.get("token") and group_cfg.get("chat_id"):
         asyncio.run(send_telegram_message(telegram_message, token=group_cfg["token"], chat_id=group_cfg["chat_id"]))
      asyncio.run(send_telegram_message(telegram_message))
      print(f"Telegram notification sent: {telegram_message}")

      return {
         "marked_present": 0,
         "not_marked": 0,
         "not_found_in_bkms": []
      }

   # --- Sabha WAS held, continue with full checklist ---
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[1]/div/ins').click()
   print("Marked: Sabha Held")
   time.sleep(1)

   # --- Sabha Setup Checklist (Done / Not Done) ---
   print("Filling Meeting And Preparations Section in BKMS")
   
   # Karyakar Meeting - Done
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[1]/label[2]/div/ins').click()

   # 2 Week Prep Cycle - Dynamic based on input
   if prep_cycle_done.lower() == "yes":
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[2]/label[2]/div/ins').click()
   else:
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[2]/label[3]/div/ins').click()

   # Pre-Sabha Review - Done
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[3]/label[2]/div/ins').click()

   # Post-Sabha Review - Done
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[4]/label[2]/div/ins').click()

   # Culture Change - Not Done
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[5]/label[3]/div/ins').click()

   # --- Content Checklist (Sabha Activities) ---
   print("Filling Syllabus Usage Section in BKMS")
   content_xpaths = [
      (1, 2),  # Bapa's Ashirwad - Done
      (2, 2),  # Dhoon & Prarthana - Done
      (3, 2),  # Presentation 1 - Done
      (4, 2),  # Kirtan - Done
      (5, 2)   # Presentation 2 - Done
   ]
   for content_idx, label_idx in content_xpaths:
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[{content_idx}]/label[{label_idx}]/div/ins').click()

   # --- Presentation 2 Language (Gujarati or not) ---
   if p2_guju.lower() == "yes":
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[6]/label[2]/div/ins').click()
      print("Presentation 2 was in Gujarati")
   else:
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[6]/label[3]/div/ins').click()
      print("Presentation 2 was NOT in Gujarati")

   # --- Sabha Goshti Marked Not Done ---
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[7]/label[3]/div/ins').click()

   # --- Mark all Kishores Absent initially ---
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[2]/div[1]/span/a').click()
   print("All Kishores initially marked Absent")
   time.sleep(2)

   # --- Update Attendance: Mark Present Kishores ---
   all_kishores = driver.find_elements(By.XPATH, '//tr[@role="row"]')
   updated_kishores = []
   table_bkids = set()
   index = -1
   for element in all_kishores:
      index += 1
      name_parts = element.text.split()
      if not name_parts:
         continue
      bkid = name_parts[0]
      table_bkids.add(bkid)
      if bkid in attended_kishores:
         try:
            radio_button = element.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{index}]/td[10]/label/input')
            radio_button.click()
            updated_kishores.append(bkid)
            time.sleep(0.5)
         except Exception as e:
            pass
   
   # Find kishores that are present in the BKMS but not marked as present (should be empty unless logic above changes)
   not_marked = [kid for kid in attended_kishores if kid in table_bkids and kid not in updated_kishores]
   if not_marked:
      print(f"Kishores found in BKMS but not marked present: {not_marked}")

   print(f"Successfully marked {len(updated_kishores)} Kishores as Present")

   # Find kishores from attended_kishores that are not present in BKMS at all
   not_found_in_bkms = [kid for kid in attended_kishores if kid not in table_bkids]
   if not_found_in_bkms:
      print(f"Did not mark {len(attended_kishores) - len(updated_kishores)} Kishores as they were not found in BKMS")
   print(f"Kishores not found in BKMS: {', '.join(str(kid) for kid in not_found_in_bkms)}")

   # --- Save Changes ---
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[3]/div/input[1]').click()
   print("Saved attendance successfully!")
   time.sleep(5)

   # --- Send Telegram Success Notification ---
   sunday_date = get_this_week_sunday(date_string)
   base_msg = f"BKMS Attendance updated for {day.title()} - {sunday_date} ✅"
   mentions = TELEGRAM_GROUP_MENTIONS.get(day.lower(), "")
   telegram_message = f"{base_msg}\n\n{mentions}" if mentions else base_msg
   group_cfg = TELEGRAM_GROUP_CONFIG.get(day.lower())
   if group_cfg and group_cfg.get("token") and group_cfg.get("chat_id"):
      asyncio.run(send_telegram_message(telegram_message, token=group_cfg["token"], chat_id=group_cfg["chat_id"]))
   asyncio.run(send_telegram_message(telegram_message))
   print(f"Telegram notification sent: {telegram_message}")

   # --- Return attendance marking results instead of sending Telegram ---
   return {
      "marked_present": len(updated_kishores),
      "not_marked": len(attended_kishores) - len(updated_kishores),
      "not_found_in_bkms": not_found_in_bkms
   }