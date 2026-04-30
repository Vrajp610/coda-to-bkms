import os
import pandas as pd
from codaio import Coda
from datetime import datetime
from dotenv import load_dotenv
from backend.utils.constants import (
    GOSHTHI_9_10_TABLE_ID,
    GOSHTHI_11_12_TABLE_ID,
    GOSHTHI_COLLEGE_1_2_TABLE_ID,
    GOSHTHI_COLLEGE_3_4_TABLE_ID,
    SATURDAY_BAL_GROUP_0_TABLE_ID,
    SATURDAY_BAL_GROUP_1_TABLE_ID,
    SATURDAY_BAL_GROUP_2A_TABLE_ID,
    SATURDAY_BAL_GROUP_2B_TABLE_ID,
    SATURDAY_BAL_GROUP_3_TABLE_ID,
    SUNDAY_BAL_GROUP_0_TABLE_ID,
    SUNDAY_BAL_GROUP_1_TABLE_ID,
    SUNDAY_BAL_GROUP_2A_TABLE_ID,
    SUNDAY_BAL_GROUP_2B_TABLE_ID,
    SUNDAY_BAL_GROUP_3_TABLE_ID,
)

load_dotenv()

# Get Coda API Key from environment
api_key = os.getenv("CODA_API_KEY")
if not api_key:
    raise EnvironmentError("CODA_API_KEY is not set in environment variables.")

# Initialize Coda client
coda = Coda(api_key=api_key)

# Coda Doc IDs
# Kishore attendance uses the primary document.
doc_id = os.getenv('CODA_DOC_ID')
# Bal Mandal attendance uses a separate document if configured.
bal_doc_id = os.getenv('BAL_CODA_DOC_ID', doc_id)

attendance = []

#Table IDs
saturday_k1 = os.getenv("SATURDAY_K1_TABLE_ID")
saturday_k2 = os.getenv("SATURDAY_K2_TABLE_ID")
sunday_k1 = os.getenv("SUNDAY_K1_TABLE_ID")
sunday_k2 = os.getenv("SUNDAY_K2_TABLE_ID")

# Bal Table IDs
saturday_bal_group_0 = SATURDAY_BAL_GROUP_0_TABLE_ID
saturday_bal_group_1 = SATURDAY_BAL_GROUP_1_TABLE_ID
saturday_bal_group_2a = SATURDAY_BAL_GROUP_2A_TABLE_ID
saturday_bal_group_2b = SATURDAY_BAL_GROUP_2B_TABLE_ID
saturday_bal_group_3 = SATURDAY_BAL_GROUP_3_TABLE_ID
sunday_bal_group_0 = SUNDAY_BAL_GROUP_0_TABLE_ID
sunday_bal_group_1 = SUNDAY_BAL_GROUP_1_TABLE_ID
sunday_bal_group_2a = SUNDAY_BAL_GROUP_2A_TABLE_ID
sunday_bal_group_2b = SUNDAY_BAL_GROUP_2B_TABLE_ID
sunday_bal_group_3 = SUNDAY_BAL_GROUP_3_TABLE_ID

# Goshthi Table IDs (defined in constants.py, sourced from .env)
goshthi_9_10        = GOSHTHI_9_10_TABLE_ID
goshthi_11_12       = GOSHTHI_11_12_TABLE_ID
goshthi_college_1_2 = GOSHTHI_COLLEGE_1_2_TABLE_ID
goshthi_college_3_4 = GOSHTHI_COLLEGE_3_4_TABLE_ID

MONTH_NUM = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12",
}

def get_goshthi_attendance(table: str, month_int: int, year: str, log=print):
    """Fetch attended BKMS IDs for a month. Coda stores dates as M/D/YYYY (e.g. 1/31/2026)."""
    table_data = coda.list_rows(doc_id, table, use_column_names=True)
    rows = table_data.get('items', [])
    if not rows:
        log(f"  [{table}] No rows returned from Coda")
        return
    df = pd.DataFrame([row['values'] for row in rows])
    log(f"  [{table}] Columns: {list(df.columns)}")
    log(f"  [{table}] Total rows: {len(df)}")

    # Detect date column: check known names first, then scan for M/D/YYYY values
    date_col = None
    for candidate in ['Month', 'Weekend', 'Date', 'Goshthi Date', 'GoShthiDate']:
        if candidate in df.columns:
            date_col = candidate
            log(f"  [{table}] Using '{date_col}' as date column")
            break

    if date_col is None:
        for col in df.columns:
            sample = df[col].dropna().astype(str)
            if sample.str.match(r'^\d{1,2}/\d{1,2}/\d{4}$').any():
                date_col = col
                log(f"  [{table}] Using '{col}' as date column (pattern match)")
                break

    if date_col is None:
        log(f"  [{table}] ERROR: Could not find a date column. Columns: {list(df.columns)}")
        return

    sample_dates = df[date_col].dropna().astype(str).head(3).tolist()
    log(f"  [{table}] Sample '{date_col}' values: {sample_dates}")

    # Detect BKMS ID column
    bkms_col = None
    for candidate in ['BKMS ID', 'BKMS Id', 'BKMSId', 'bkms_id', 'ID', 'User ID']:
        if candidate in df.columns:
            bkms_col = candidate
            break

    if bkms_col is None:
        log(f"  [{table}] ERROR: Could not find BKMS ID column. Columns: {list(df.columns)}")
        return

    # Detect Attended column
    attended_col = None
    for candidate in ['Attended', 'attended', 'Present', 'present']:
        if candidate in df.columns:
            attended_col = candidate
            break

    if attended_col is None:
        log(f"  [{table}] ERROR: Could not find Attended column. Columns: {list(df.columns)}")
        return

    # Filter: attended=True AND date falls in the given month+year.
    # Coda returns ISO timestamps (e.g. "2026-01-31T00:00:00.000-05:00")
    iso_prefix = f"{year}-{month_int:02d}"
    mask = (
        (df[attended_col] == True) &
        df[date_col].astype(str).str.startswith(iso_prefix, na=False)
    )
    filtered = df[mask]
    log(f"  [{table}] Rows after filter: {len(filtered)}")
    if not filtered.empty:
        log(f"  [{table}] Dates matched: {filtered[date_col].unique().tolist()}")

    data = filtered[bkms_col].dropna().tolist()
    data = [int(x) for x in data]
    attendance.extend(data)

def format_goshthi_data(month: str, year: str, log_callback=None):
    log = log_callback if log_callback else print
    global attendance
    attendance = []

    month_num_str = MONTH_NUM.get(month)
    if not month_num_str:
        return "Invalid month entered. Fix it and rerun."

    month_int = int(month_num_str)
    log(f"Fetching Goshthi attendance for {month} {year} (dates like {month_int}/<day>/{year})")

    table_labels = [
        ("Grades 9-10",  goshthi_9_10),
        ("Grades 11-12", goshthi_11_12),
        ("College 1-2",  goshthi_college_1_2),
        ("College 3-4",  goshthi_college_3_4),
    ]
    try:
        for label, table in table_labels:
            if table:
                log(f"Querying {label} ({table})...")
                get_goshthi_attendance(table, month_int, year, log=log)
    except Exception as e:
        log(f"Error: {e}")
        return "The attendance system is broken. Rerun to see if it might be fixed"

    unique_ids = sorted(set(str(x) for x in attendance))
    count = len(unique_ids)
    log(f"Total unique Goshthi attendees: {count}")
    log("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    log(str(unique_ids))
    log("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    return unique_ids, count

def convert_date(date_str):
    """Convert either 'YYYY-MM-DD' or 'Month day' into the expected Coda timestamp."""
    today = datetime.now().date()

    try:
        iso_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return iso_date.strftime("%Y-%m-%dT%H:%M:%S.000-08:00")
    except ValueError:
        pass

    # Try current year, previous year and next year and pick closest to today
    candidate_years = [today.year, today.year - 1, today.year + 1]
    candidates = []
    for y in candidate_years:
        full_date_str = f"{y} {date_str}"
        try:
            d = datetime.strptime(full_date_str, "%Y %B %d").date()
            candidates.append(d)
        except ValueError:
            # If the format doesn't parse (invalid month/day), bubble up error
            raise

    # Choose candidate with minimal distance to today
    chosen = min(candidates, key=lambda d: abs((d - today).days))

    # Return in the expected Coda timestamp format
    formatted_date = chosen.strftime("%Y-%m-%dT%H:%M:%S.000-08:00")
    return formatted_date

def get_attendance(table: str, date: str, doc_id: str = doc_id):
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
        elif sabha_group.lower() == "saturday bal group 0":
            get_attendance(saturday_bal_group_0, date)
        elif sabha_group.lower() == "saturday bal group 1":
            get_attendance(saturday_bal_group_1, date)
        elif sabha_group.lower() == "saturday bal group 2a":
            get_attendance(saturday_bal_group_2a, date)
        elif sabha_group.lower() == "saturday bal group 2b":
            get_attendance(saturday_bal_group_2b, date)
        elif sabha_group.lower() == "saturday bal group 3":
            get_attendance(saturday_bal_group_3, date)
        elif sabha_group.lower() == "sunday bal group 0":
            get_attendance(sunday_bal_group_0, date)
        elif sabha_group.lower() == "sunday bal group 1":
            get_attendance(sunday_bal_group_1, date)
        elif sabha_group.lower() == "sunday bal group 2a":
            get_attendance(sunday_bal_group_2a, date)
        elif sabha_group.lower() == "sunday bal group 2b":
            get_attendance(sunday_bal_group_2b, date)
        elif sabha_group.lower() == "sunday bal group 3":
            get_attendance(sunday_bal_group_3, date)
    except Exception:
        print(Exception)
        return "The attendance system is broken. Rerun to see if it might be fixed"
    
    attendance_count = len(attendance)
    print(f"Attendence: {attendance_count}\nMoving on to updating BKMS\n")
    return attendance, attendance_count

def _fetch_bal_table(label: str, table: str, date_prefix: str, log) -> list[str]:
    """Fetch attended BKMS IDs from a single Bal table for a given date using codaio."""
    if not table:
        return []
    log(f"Querying {label}...")
    try:
        table_data = coda.list_rows(bal_doc_id, table, use_column_names=True)
        rows = table_data.get('items', [])
        df = pd.DataFrame([row['values'] for row in rows])
        df = df[(df['Attended'] == True) & (df['Weekend'].astype(str).str.contains(date_prefix, na=False))]
        ids = df['BKMS ID'].dropna().tolist()
        numeric_ids = sorted(set(int(x) for x in ids))
        ids = [str(x) for x in numeric_ids]
        log(f"  {label}: {len(ids)} attended on {date_prefix}")
        return ids
    except Exception as e:
        log(f"Error fetching {label}: {e}")
        return []


def get_bal_attendance_data(date: str, day: str, log_callback=None):
    """Fetch attendance for all 5 Bal groups in parallel for a given date and day."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    log = log_callback if log_callback else print

    try:
        converted = convert_date(date)
        log("Date Converted for Bal attendance")
    except Exception as e:
        log(f"Date conversion error: {e}")
        return "Invalid date format. Please check and rerun."

    date_prefix = converted.split('T')[0]
    is_saturday = "sat" in day.lower()

    bal_tables = (
        [
            ("Saturday Bal Group 0",  saturday_bal_group_0),
            ("Saturday Bal Group 1",  saturday_bal_group_1),
            ("Saturday Bal Group 2A", saturday_bal_group_2a),
            ("Saturday Bal Group 2B", saturday_bal_group_2b),
            ("Saturday Bal Group 3",  saturday_bal_group_3),
        ]
        if is_saturday
        else [
            ("Sunday Bal Group 0",  sunday_bal_group_0),
            ("Sunday Bal Group 1",  sunday_bal_group_1),
            ("Sunday Bal Group 2A", sunday_bal_group_2a),
            ("Sunday Bal Group 2B", sunday_bal_group_2b),
            ("Sunday Bal Group 3",  sunday_bal_group_3),
        ]
    )

    all_ids: list[str] = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(_fetch_bal_table, label, table, date_prefix, log): label
            for label, table in bal_tables
        }
        for future in as_completed(futures):
            all_ids.extend(future.result())

    unique_ids = sorted(set(all_ids))
    count = len(unique_ids)
    log(f"Total unique Bal attendees: {count}")
    log(str(unique_ids))
    return unique_ids, count
