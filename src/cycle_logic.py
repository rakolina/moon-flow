import json
import os
from datetime import datetime, timedelta
from astro_logic import get_moon_image_path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, "data", "user_data.json")


def load_user_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_user_data(data):
    data_folder = os.path.join(ROOT_DIR, "data")
    os.makedirs(data_folder, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def initialize_moon_cache():
    """
    Ensures a rolling 5-week window (35 days) is cached.
    This guarantees 4 full weeks of history + the current week.
    """
    now = datetime.now()

    # 1. Calculate the end date (The coming Saturday)
    # Special rule: If today is Saturday, we cache until NEXT Saturday
    if now.weekday() == 5:
        days_until_limit = 7
    else:
        days_until_limit = (5 - now.weekday()) % 7

    end_date = now + timedelta(days=days_until_limit)

    # 2. Calculate the start date (35 days before the end date)
    # 35 days = 5 full weeks. This ensures we always have the 'last two weeks'
    # of the previous month even if we are early in the current month.
    start_date = end_date - timedelta(days=35)

    data = load_user_data()
    needs_update = False

    # 3. Iterate through every day from start_date to end_date
    current_day = start_date
    while current_day <= end_date:
        # Create the month key (e.g., "2026-08")
        month_key = current_day.strftime("%Y-%m")
        day_str = str(current_day.day)

        if month_key not in data:
            data[month_key] = {}

        if day_str not in data[month_key]:
            image_path = get_moon_image_path(current_day)
            data[month_key][day_str] = image_path
            needs_update = True

        current_day += timedelta(days=1)

    if needs_update:
        print(f"Updating moon cache from {start_date.date()} to {end_date.date()}...")
        save_user_data(data)
        print("Cache successfully updated.")
    else:
        print("Rolling 5-week cache is already up to date.")

    return data


if __name__ == "__main__":
    full_data = initialize_moon_cache()
    print(f"Cached months: {list(full_data.keys())}")