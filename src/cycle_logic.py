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
    Ensures the moon cache covers the entire range required by the UI.
    Targets the end of the current calendar week (Sunday) plus a buffer.
    """
    now = datetime.now()

    # 1. Target the COMING SUNDAY
    # weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    days_until_sunday = (6 - now.weekday())

    # If today is Sunday, we want to cache until NEXT Sunday to avoid
    # the grid feeling "expired" on Monday morning.
    if days_until_sunday == 0:
        days_until_sunday = 7

    # 2. End Date = Coming Sunday + 7 day buffer
    # The buffer ensures the trailing edges of the UI grid are always filled.
    end_date = now + timedelta(days=days_until_sunday + 7)

    # 3. Start Date = 40 days before the end date
    # This covers the 4-week UI history plus plenty of overlap.
    start_date = end_date - timedelta(days=40)

    data = load_user_data()
    needs_update = False

    # 4. Populate every single day in the window
    current_day = start_date
    while current_day <= end_date:
        month_key = current_day.strftime("%Y-%m")
        day_str = str(current_day.day)

        if month_key not in data:
            data[month_key] = {}

        # Only calculate if the day is actually missing
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
        print("Moon cache is already up to date.")

    return data


if __name__ == "__main__":
    full_data = initialize_moon_cache()
    print(f"Cached months: {list(full_data.keys())}")