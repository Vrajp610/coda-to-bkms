from datetime import datetime, timedelta

def _parse_input_date(date_string: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%B %d"):
        try:
            parsed = datetime.strptime(date_string, fmt)
            if fmt == "%B %d":
                parsed = parsed.replace(year=datetime.now().year)
            return parsed
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {date_string}")

def calculate_week_number(date_string: str):
    """Calculate the BKMS week number from a given date string."""
    full_date = _parse_input_date(date_string)
    current_year = full_date.year

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
    full_date = _parse_input_date(date_string)
    return full_date.strftime("%-m/%-d/%Y")
