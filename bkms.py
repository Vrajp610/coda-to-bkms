from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
import datetime

today = datetime.date.today()
week_number = today.isocalendar().week

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)
service = webdriver.ChromeService()

day = "saturday"
url = "https://bk.na.baps.org/ssologin"

def update_sheet(attended_kishores, day: str, sabha_held: str, p2_guju: str):
   driver = webdriver.Chrome(service=service, options=options)

   driver.get(url)

   time.sleep(1)
   print("Logging In to BKMS\n")
   user_id = driver.find_element(By.ID, "user_id") 
   user_email = driver.find_element(By.ID, "email") 
   user_password = driver.find_element(By.ID, "password") 

   user_id.send_keys("3001")
   time.sleep(0.5)
   user_email.send_keys("vrajptl0610@gmail.com")
   time.sleep(0.5)
   user_password.send_keys("12345678")
   print("DO THE CAPTCHA (you have 30 sec) BUT DO NOT CLICK 'Sign In'\n")
   
   time.sleep(30)
   driver.find_element(By.CLASS_NAME, "btn-primary").click()
   time.sleep(2)
   driver.get("https://bk.na.baps.org/admin/reports/reportweeksabhaattendance")
   time.sleep(3)
   
   print("Logged in to BKMS if captcha was solved\n")
   
   if day.lower() == "saturday k1":
      print("Selecting sabha wing\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]').click()
      time.sleep(1)
      print("Selected Sabha wing\n")
      time.sleep(2)
      print("Selecting year\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]').click()
      time.sleep(1)
      print("Selected year\n")
      time.sleep(2)
      print("Selecting Sabha Week\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{week_number + 1}]').click()
      time.sleep(1)
      print("Selected Sabha Week\n")
      time.sleep(2)
      print("Selecting Saturday K1\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[9]/div/span/a').click()
      print("Selected Saturday K1\n")
   elif day.lower() == "saturday k2":
      print("Selecting sabha wing\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]').click()
      time.sleep(1)
      print("Selected Sabha wing\n")
      time.sleep(2)
      print("Selecting year\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]').click()
      time.sleep(1)
      print("Selected year\n")
      time.sleep(2)
      print("Selecting Sabha Week\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{week_number + 1}]').click()
      time.sleep(1)
      print("Selected Sabha Week\n")
      time.sleep(2)
      print("Selecting Saturday K2\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[2]/td[9]/div/span/a').click()
      print("Selected Saturday K2\n")
   elif day.lower() == "sunday k1":
      print("Selecting sabha wing\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]').click()
      time.sleep(1)
      print("Selected Sabha wing\n")
      time.sleep(2)
      print("Selecting year\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]').click()
      time.sleep(1)
      print("Selected year\n")
      time.sleep(2)
      print("Selecting Sabha Week\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{week_number + 1}]').click()
      time.sleep(1)
      print("Selected Sabha Week\n")
      time.sleep(2)
      print("Selecting Sunday K1\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[3]/td[9]/div/span/a').click()
      print("Selected Sunday K1\n")
   elif day.lower() == "sunday k2":
      print("Selecting sabha wing\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[3]/select/option[4]').click()
      time.sleep(1)
      print("Selected Sabha wing\n")
      time.sleep(2)
      print("Selecting year\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[4]/select/option[9]').click()
      time.sleep(1)
      print("Selected year\n")
      time.sleep(2)
      print("Selecting Sabha Week\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div[1]/div[5]/select/option[{week_number + 1}]').click()
      time.sleep(1)
      print("Selected Sabha Week\n")
      time.sleep(2)
      print("Selecting Sunday K2\n")
      driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/table/tbody/tr[4]/td[9]/div/span/a').click()
      print("Selected Sunday K2\n")
   
   time.sleep(3)

   #Check whether sabha was held or not
   if sabha_held.lower() == "yes":
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[1]/div/ins').click()
      print("Sabha was held\n")
   else:
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/form/div[1]/label[2]/div/ins').click()
      print("Sabha was not held\n")
   time.sleep(2)
   
   #Karyakar Meeting
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[1]/label[2]/div/ins').click()
   print("Karyakar Meeting Done\n")
   #2 Week Prep Cycle
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[2]/label[3]/div/ins').click()
   print("2 Week Prep Cycle Not Done\n")
   #Pre-Sabha Review
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[3]/label[2]/div/ins').click()
   print("Pre-Sabha Review Done\n")
   #Post-Sabha Review
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[4]/label[2]/div/ins').click()
   print("Post-Sabha Review Done\n")
   #Culture Change
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/form/div[3]/div/div[5]/label[3]/div/ins').click()
   print("Culture Change Not Done\n")
   #Bapa’s Ashirwaad
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[1]/label[2]/div/ins').click()
   print("Bapa's Ashirwaad Done\n")
   #Dhoon & Prarthana
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[2]/label[2]/div/ins').click()
   print("Dhoon & Prarthana Done\n")
   #Presentation 1
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[3]/label[2]/div/ins').click()
   print("Presentation 1 Done\n")
   #Kirtan
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[4]/label[2]/div/ins').click()
   print("Kirtan Done\n")
   #Presentation 2
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[5]/label[2]/div/ins').click()
   print("Presentation 2 Done\n")

   #Presentation done in Gujarati or not?
   if p2_guju.lower() == "yes":
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[6]/label[2]/div/ins').click()
      print("Presentation 2 was done in Gujarati\n")
   else:
      driver.find_element(By.XPATH, '/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[6]/label[3]/div/ins').click()
      print("Presentation 2 was not done in Gujarati\n")

   #Sabha Goshti
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[2]/form/div/div[7]/label[3]/div/ins').click()
   print("Sabha Goshti Not Done\n")

   #Mark all as absent
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[2]/div[1]/span/a').click()
   print("Marked all Kishores as absent\n")
   time.sleep(2)
   print("Selecting Kishores")


   all_kishores = driver.find_elements(By.XPATH, '//tr[@role="row"]')
   updated_kishores = []
   no_found_kishores = []
   
   index = -1
   count = 0
   for element in all_kishores:
    index += 1
    name = element.text
    name_parts = name.split()
    bkid = name_parts[0]

    if bkid in attended_kishores:
        count += 1
        radio_button = element.find_element(
            By.XPATH,
            f'/html/body/div[2]/div/section[2]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{index}]/td[10]/label/input'
        )
        radio_button.click()
        updated_kishores.append(bkid)
         
   for kishore in attended_kishores:
      if not kishore in updated_kishores:
         no_found_kishores.append(kishore)

   print("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
   print(f'These kishores attended sabha but were not in BKMS: {no_found_kishores}')
   print(f"Everythings Done!\nClicked {count} kishores")
   time.sleep(3)
   driver.find_element(By.XPATH, f'/html/body/div[2]/div/section[2]/div[1]/div[4]/form/div[3]/div/input[1]').click()
   time.sleep(5)
   print("Saved Changes and All Kishores who attended sabha are marked as present")