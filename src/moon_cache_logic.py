import json
import os
from datetime import datetime, timedelta
from astro_logic import get_moon_image_path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOON_DATA_FILE = os.path.join(ROOT_DIR, "data", "moon_cache.json")

def load_moon_data():
    """
    Loads the moon phase cache. 
    If file is missing, empty, or invalid, returns an empty dictionary.
    Does NOT touch cycle_data.json.
    """
    if not os.path.exists(MOON_DATA_FILE):
        return {}
    
    try:
        with open(MOON_DATA_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}

def save_moon_data(moons):
    """Saves ONLY the moon phase cache to moon_cache.json."""
    data_folder = os.path.join(ROOT_DIR, "data")
    os.makedirs(data_folder, exist_ok=True)
    with open(MOON_DATA_FILE, "w") as f:
        json.dump(moons, f, indent=4)

def initialize_moon_cache():
    """
    Ensures the moon cache exists and is populated.
    Operates strictly on moon_cache.json.
    Re-populates the cache entirely to ensure consistent mapping.
    """
    now = datetime.now()
    start_date = now - timedelta(days=180)
    end_date = now + timedelta(days=180)

    moons = {}
    needs_update = False

    current_day = start_date
    while current_day <= end_date:
        month_key = current_day.strftime("%Y-%m")
        day_str = str(current_day.day)

        if month_key not in moons:
            moons[month_key] = {}

        image_path, phase_idx = get_moon_image_path(current_day)
        moons[month_key][day_str] = {
            "path": image_path,
            "phase": phase_idx
        }
        needs_update = True
        current_day += timedelta(days=1)

    if needs_update:
        save_moon_data(moons)

    return moons
