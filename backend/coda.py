import os
import pandas as pd
from codaio import Coda
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Get Coda API Key from environment
api_key = os.getenv("CODA_API_KEY")
if not api_key:
    raise EnvironmentError("CODA_API_KEY is not set in environment variables.")

# Initialize Coda client
coda = Coda(api_key=api_key)

#Coda Doc ID
doc_id = os.getenv('CODA_DOC_ID')

attendance = []

#Table IDs
saturday_k1 = os.getenv("SATURDAY_K1_TABLE_ID")
saturday_k2 = os.getenv("SATURDAY_K2_TABLE_ID")
sunday_k1 = os.getenv("SUNDAY_K1_TABLE_ID")
sunday_k2 = os.getenv("SUNDAY_K2_TABLE_ID")

def convert_date(date_str):
    current_year = datetime.now().year

    full_date_str = f"{current_year} {date_str}"
    full_date = datetime.strptime(full_date_str, "%Y %B %d")
    formatted_date = full_date.strftime("%Y-%m-%dT%H:%M:%S.000-08:00")

    return formatted_date

def get_attendance(table: str, date: str):
    table_data = coda.list_rows(doc_id, table, use_column_names=True)

    rows = table_data.get('items', [])
    df = pd.DataFrame([row['values'] for row in rows])

    date = date.split('T')[0]

    df = df[(df.Attended == True) & (df['Weekend'].str.contains(date))]

    data = df["BKMS ID"].dropna().tolist()
    data = [int(x) for x in data]
    data = sorted(data)
    data = [str(x) for x in data]

    attendance.extend(data)

def format_data(sabha_group, date):
    global attendance
    attendance = []

    try:
        date = convert_date(date)
        print("Date Converted\n")
    except Exception:
        print(Exception)
        return "I don't how you did this. But you entered the date wrong! Fix it and rerun"
    
    try:
        if sabha_group.lower() == "saturday k1":
            get_attendance(saturday_k1, date)
        elif sabha_group.lower() == "saturday k2":
            get_attendance(saturday_k2, date)
        elif sabha_group.lower() == "sunday k1":
            get_attendance(sunday_k1, date)
        elif sabha_group.lower() == "sunday k2":
            get_attendance(sunday_k2, date)
    except Exception:
        print(Exception)
        return "The attendance system is broken. Rerun to see if it might be fixed"
    
    attendance_count = len(attendance)
    print(f"Attendence: {attendance_count}\nMoving on to updating BKMS\n")
    print("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    print(attendance)
    print("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    return attendance, attendance_count