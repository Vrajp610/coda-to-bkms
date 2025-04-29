import time
import asyncio
from selenium.webdriver.common.by import By
from utils.telegramUtils import send_telegram_message
from utils.dateUtils import calculate_week_number, get_this_week_sunday
from utils.chromeUtils import get_chrome_driver
from utils.constants import BKMS_LOGIN_URL, USER_ID, EMAIL, PASSWORD

# --- BKMS login page ---
url = BKMS_LOGIN_URL

# --- Main function: Update attendance in BKMS ---
def update_sheet(attended_kishores, day: str, sabha_held: str, p2_guju: str, date_string: str, prep_cycle_done: str):
   # --- Open Chrome and Navigate to BKMS login ---
   driver = get_chrome_driver()
   driver.get(url)

   # --- Perform Login ---
   print("Logging into BKMS...")
   time.sleep(1)
   driver.find_element(By.ID, "user_id").send_keys(USER_ID)
   time.sleep(0.5)
   driver.find_element(By.ID, "email").send_keys(EMAIL)
   time.sleep(0.5)
   driver.find_element(By.ID, "password").send_keys(PASSWORD)
   print("Please solve CAPTCHA manually (30 seconds). DO NOT CLICK SIGN IN AFTER SOLVING!")
   time.sleep(30)
   driver.find_element(By.CLASS_NAME, "btn-primary").click()
   time.sleep(2)

   # --- Go to Report Attendance Page ---
   driver.get("https://bk.na.baps.org/admin/reports/reportweeksabhaattendance")
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
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[{row_number}]/td[9]/div/span/a').click()
      print(f"Selected {day.title()}")
   else:
      print("Error: Invalid Sabha group entered!")
      return

   time.sleep(3)

   # --- Mark if Sabha was Held ---
   if sabha_held.lower() == "yes":
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[1]/div/ins').click()
      print("Marked: Sabha Held")
   else:
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[2]/div/ins').click()
      print("Marked: Sabha Not Held")
   time.sleep(1)

   # --- Sabha Setup Checklist (Done / Not Done) ---
   print("Filling Sabha Setup Checklist")
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
   print("Filling Content Checklist")
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
   index = -1
   for element in all_kishores:
      index += 1
      name_parts = element.text.split()
      if not name_parts:
         continue
      bkid = name_parts[0]
      if bkid in attended_kishores:
         radio_button = element.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{index}]/td[10]/label/input')
         radio_button.click()
         updated_kishores.append(bkid)

   not_found = [kid for kid in attended_kishores if kid not in updated_kishores]
   if not_found:
      print(f"Kishores not found in system: {not_found}")

   print(f"Successfully marked {len(updated_kishores)} Kishores as Present")

   # --- Save Changes ---
   driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[3]/div/input[1]').click()
   print("Saved attendance successfully!")
   time.sleep(5)

   # --- Send Telegram Success Notification ---
   sunday_date = get_this_week_sunday(date_string)
   telegram_message = f"BKMS Attendance updated for {day.title()} - {sunday_date} ✅"
   asyncio.run(send_telegram_message(telegram_message))
   print(f"Telegram notification sent: {telegram_message}")