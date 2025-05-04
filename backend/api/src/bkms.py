import asyncio
from pyppeteer import launch
from backend.api.src.utils.telegramUtils import send_telegram_message
from backend.api.src.utils.dateUtils import calculate_week_number, get_this_week_sunday
from backend.api.src.utils.constants import BKMS_LOGIN_URL, USER_ID, EMAIL, PASSWORD

async def update_sheet(attended_kishores, day: str, sabha_held: str, p2_guju: str, date_string: str, prep_cycle_done: str):
   """Update attendance in BKMS using Pyppeteer."""
   browser = await launch(
      headless=True,
      args=[
         "--no-sandbox",
         "--disable-setuid-sandbox",
         "--disable-dev-shm-usage",
         "--disable-gpu",
         "--single-process",
         "--disable-extensions",
      ],
   )
   page = await browser.newPage()

   try:
      # --- Navigate to BKMS login ---
      await page.goto(BKMS_LOGIN_URL)
      print("Logging into BKMS...")

      # --- Perform Login ---
      await page.type("#user_id", USER_ID)
      await page.type("#email", EMAIL)
      await page.type("#password", PASSWORD)
      print("Please solve CAPTCHA manually (30 seconds). DO NOT CLICK SIGN IN AFTER SOLVING!")
      await asyncio.sleep(30)
      await page.click(".btn-primary")
      await page.waitForNavigation()

      # --- Go to Report Attendance Page ---
      await page.goto("https://bk.na.baps.org/admin/reports/reportweeksabhaattendance")
      print("Navigated to attendance page.")

      # --- Select Sabha Wing and Year ---
      print("Selecting Sabha Wing and Year")
      await page.select('select[name="sabhaWing"]', "4")  # Kishore
      await page.select('select[name="year"]', "2025")  # 2025

      # --- Select Week based on Entered Date ---
      week_number = calculate_week_number(date_string)
      print(f"Selecting Week {week_number - 1} for {date_string}")
      await page.select('select[name="week"]', str(week_number))

      # --- Select Specific Sabha Group (K1/K2/S1/S2) ---
      sabha_row_map = {
         "saturday k1": 1,
         "saturday k2": 2,
         "sunday k1": 3,
         "sunday k2": 4,
      }
      row_number = sabha_row_map.get(day.lower())
      if row_number:
         await page.click(f'table tbody tr:nth-child({row_number}) td:nth-child(9) a')
         print(f"Selected {day.title()}")
      else:
         print("Error: Invalid Sabha group entered!")
         return

      # --- Mark if Sabha was Held ---
      if sabha_held.lower() == "yes":
         await page.click('label[for="sabhaHeldYes"] input')
         print("Marked: Sabha Held")
      else:
         await page.click('label[for="sabhaHeldNo"] input')
         print("Marked: Sabha Not Held")

      # --- Sabha Setup Checklist ---
      print("Filling Sabha Setup Checklist")
      await page.click('label[for="karyakarMeetingDone"] input')  # Karyakar Meeting - Done
      if prep_cycle_done.lower() == "yes":
         await page.click('label[for="prepCycleDone"] input')
      else:
         await page.click('label[for="prepCycleNotDone"] input')
      await page.click('label[for="preSabhaReviewDone"] input')  # Pre-Sabha Review - Done
      await page.click('label[for="postSabhaReviewDone"] input')  # Post-Sabha Review - Done
      await page.click('label[for="cultureChangeNotDone"] input')  # Culture Change - Not Done

      # --- Content Checklist ---
      print("Filling Content Checklist")
      content_checklist = [
         "bapasAshirwadDone",
         "dhoonPrarthanaDone",
         "presentation1Done",
         "kirtanDone",
         "presentation2Done",
      ]
      for checklist_id in content_checklist:
         await page.click(f'label[for="{checklist_id}"] input')

      # --- Presentation 2 Language ---
      if p2_guju.lower() == "yes":
         await page.click('label[for="p2GujuYes"] input')
         print("Presentation 2 was in Gujarati")
      else:
         await page.click('label[for="p2GujuNo"] input')
         print("Presentation 2 was NOT in Gujarati")

      # --- Mark all Kishores Absent initially ---
      await page.click('a#markAllAbsent')
      print("All Kishores initially marked Absent")

      # --- Update Attendance: Mark Present Kishores ---
      print("Updating attendance...")
      for bkid in attended_kishores:
         await page.evaluate(
               f"""
               () => {{
                  const row = document.querySelector(`tr[data-bkid="{bkid}"]`);
                  if (row) {{
                     const presentRadio = row.querySelector('input[type="radio"][value="present"]');
                     if (presentRadio) presentRadio.click();
                  }}
               }}
               """
         )

      # --- Save Changes ---
      await page.click('input#saveChanges')
      print("Saved attendance successfully!")

      # --- Send Telegram Success Notification ---
      sunday_date = get_this_week_sunday(date_string)
      telegram_message = f"BKMS Attendance updated for {day.title()} - {sunday_date} ✅"
      await send_telegram_message(telegram_message)
      print(f"Telegram notification sent: {telegram_message}")

   except Exception as e:
      print(f"Error: {e}")
   finally:
      await browser.close()