from datetime import datetime, timedelta

def calculate_week_number(date_string: str):
    """Calculate the BKMS week number from a given date string."""
    current_year = datetime.now().year
    full_date_str = f"{current_year} {date_string}"
    full_date = datetime.strptime(full_date_str, "%Y %B %d")

    # Find first Sunday of the year
    first_jan = datetime(current_year, 1, 1)
    first_sunday = first_jan + timedelta(days=(6 - first_jan.weekday()) % 7)

    if full_date < first_sunday:
        return 1  # Before first Sunday of the year

    # How many full weeks have passed since the first Sunday
    weeks_passed = (full_date - first_sunday).days // 7
    week_number = weeks_passed + 1  # +1 because first Sunday is Week 1

    return week_number + 1

def get_this_week_sunday(date_string: str):
    """Format the given date string to MM/DD/YYYY."""
    current_year = datetime.now().year
    full_date_str = f"{date_string}, {current_year}"
    full_date = datetime.strptime(full_date_str, "%B %d, %Y")
    return full_date.strftime("%-m/%-d/%Y")