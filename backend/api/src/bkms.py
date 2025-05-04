import asyncio
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
from .utils.telegramUtils import send_telegram_message
from .utils.dateUtils import calculate_week_number, get_this_week_sunday
from .utils.chromeUtils import get_page
from .utils.constants import BKMS_LOGIN_URL, USER_ID, EMAIL, PASSWORD

async def update_sheet(attended_kishores, day: str, sabha_held: str, p2_guju: str, date_string: str, prep_cycle_done: str):
   """Update attendance in BKMS using Pyppeteer."""
   page, browser = await get_page()
   try:
      # Navigate to BKMS login page
      await page.goto(BKMS_LOGIN_URL, timeout=60000)
      print("Logging into BKMS...")

      # Perform login
      await page.type("#user_id", USER_ID)
      await page.type("#email", EMAIL)
      await page.type("#password", PASSWORD)
      print("Please solve CAPTCHA manually (30 seconds). DO NOT CLICK SIGN IN AFTER SOLVING!")
      await asyncio.sleep(30)
      await page.click(".btn-primary")
      await page.waitForNavigation()

      # Navigate to attendance page
      await page.goto("https://bk.na.baps.org/admin/reports/reportweeksabhaattendance", timeout=60000)
      print("Navigated to attendance page.")

      # Select Sabha Wing and Year
      await page.select('select[name="sabhaWing"]', "Kishore")
      await page.select('select[name="year"]', "2025")

      # Select Week based on Entered Date
      week_number = calculate_week_number(date_string)
      print(f"Selecting Week {week_number - 1} for {date_string}")
      await page.select('select[name="week"]', str(week_number))

      # Select Specific Sabha Group (K1/K2/S1/S2)
      sabha_row_map = {
         "saturday k1": 1,
         "saturday k2": 2,
         "sunday k1": 3,
         "sunday k2": 4
      }
      row_number = sabha_row_map.get(day.lower())
      if row_number:
         await page.click(f'tr:nth-child({row_number}) td:nth-child(9) span a')
         print(f"Selected {day.title()}")
      else:
         print("Error: Invalid Sabha group entered!")
         return

      # Mark if Sabha was Held
      if sabha_held.lower() == "yes":
         await page.click('label[for="sabhaHeldYes"]')
         print("Marked: Sabha Held")
      else:
         await page.click('label[for="sabhaHeldNo"]')
         print("Marked: Sabha Not Held")

      # Sabha Setup Checklist
      print("Filling Sabha Setup Checklist")
      await page.click('label[for="karyakarMeetingDone"]')  # Karyakar Meeting - Done
      if prep_cycle_done.lower() == "yes":
         await page.click('label[for="prepCycleDone"]')
      else:
         await page.click('label[for="prepCycleNotDone"]')
      await page.click('label[for="preSabhaReviewDone"]')  # Pre-Sabha Review - Done
      await page.click('label[for="postSabhaReviewDone"]')  # Post-Sabha Review - Done
      await page.click('label[for="cultureChangeNotDone"]')  # Culture Change - Not Done

      # Content Checklist
      print("Filling Content Checklist")
      content_checklist = [
         'label[for="bapasAshirwadDone"]',
         'label[for="dhoonPrarthanaDone"]',
         'label[for="presentation1Done"]',
         'label[for="kirtanDone"]',
         'label[for="presentation2Done"]'
      ]
      for selector in content_checklist:
         await page.click(selector)

      # Presentation 2 Language
      if p2_guju.lower() == "yes":
         await page.click('label[for="presentation2Guju"]')
         print("Presentation 2 was in Gujarati")
      else:
         await page.click('label[for="presentation2NotGuju"]')
         print("Presentation 2 was NOT in Gujarati")

      # Sabha Goshti Marked Not Done
      await page.click('label[for="sabhaGoshtiNotDone"]')

      # Mark all Kishores Absent initially
      await page.click('button#markAllAbsent')
      print("All Kishores initially marked Absent")

      # Update Attendance: Mark Present Kishores
      print("Updating attendance...")
      for bkid in attended_kishores:
         try:
               await page.click(f'input[data-bkid="{bkid}"]')
               print(f"Marked Kishore {bkid} as Present")
         except Exception:
               print(f"Kishore {bkid} not found in the system.")

      # Save Changes
      await page.click('button#saveChanges')
      print("Saved attendance successfully!")

      # Send Telegram Success Notification
      sunday_date = get_this_week_sunday(date_string)
      telegram_message = f"BKMS Attendance updated for {day.title()} - {sunday_date} ✅"
      await send_telegram_message(telegram_message)
      print(f"Telegram notification sent: {telegram_message}")

   except TimeoutError:
      print("Timeout occurred while updating attendance.")
   finally:
      await browser.close()