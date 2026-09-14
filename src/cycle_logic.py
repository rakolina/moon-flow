import json
import os
from datetime import datetime, timedelta
from astro_logic import get_moon_image_path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, "data", "user_data.json")

def load_user_data():
    """Loads user data from JSON file, ensuring correct structure."""
    if not os.path.exists(DATA_FILE):
        return {"moons": {}, "period_days": [], "fertile_days": []}
    
    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
            
            # Ensure all keys exist
            data.setdefault("moons", {})
            data.setdefault("period_days", [])
            data.setdefault("fertile_days", [])
            return data
        except (json.JSONDecodeError, IOError):
            return {"moons": {}, "period_days": [], "fertile_days": []}

def save_user_data(data):
    """Saves user data to JSON file."""
    data_folder = os.path.join(ROOT_DIR, "data")
    os.makedirs(data_folder, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_fertile_window(period_days):
    """
    Groups all marked period days into clusters.
    Each cluster (consecutive days) represents one period.
    The first day of every cluster triggers a fertile window (Days 10-15).
    """
    if not period_days:
        return []

    # 1. Convert strings to datetime and sort them
    sorted_days = sorted([datetime.strptime(d, "%Y-%m-%d") for d in period_days])
    
    # 2. Group consecutive days into clusters
    clusters = []
    if sorted_days:
        current_cluster = [sorted_days[0]]
        for i in range(1, len(sorted_days)):
            # If the day is consecutive (diff = 1), it belongs to the current period
            if (sorted_days[i] - sorted_days[i-1]).days == 1:
                current_cluster.append(sorted_days[i])
            else:
                # Gap found: start a new period cluster
                clusters.append(current_cluster)
                current_cluster = [sorted_days[i]]
        clusters.append(current_cluster)

    # 3. Calculate fertile window for the START of EVERY cluster
    all_fertile_dates = []
    for cluster in clusters:
        # The first day of the cluster is the start of the period
        start_of_period = cluster[0]
        
        # Generate the window (Days 10, 11, 12, 13, 14, 15)
        for day_offset in range(10, 16):
            fertile_date = start_of_period + timedelta(days=day_offset)
            all_fertile_dates.append(fertile_date.strftime("%Y-%m-%d"))
        
    return all_fertile_dates

def toggle_period_day(date_obj):
    """
    Toggles a day and recalculates all fertile windows based on all recorded periods.
    """
    data = load_user_data()
    date_str = date_obj.strftime("%Y-%m-%d")
    
    if date_str in data["period_days"]:
        data["period_days"].remove(date_str)
    else:
        data["period_days"].append(date_str)
    
    # Recalculate the entire fertility history
    data["fertile_days"] = calculate_fertile_window(data["period_days"])
    
    save_user_data(data)
    return data

def is_period_day(date_obj, data=None):
    """Checks if date is a period day using provided data or loading from file."""
    if data is None:
        data = load_user_data()
    return date_obj.strftime("%Y-%m-%d") in data["period_days"]

def is_fertile_day(date_obj, data=None):
    """Checks if date is a fertile day using provided data or loading from file."""
    if data is None:
        data = load_user_data()
    return date_obj.strftime("%Y-%m-%d") in data["fertile_days"]

def initialize_moon_cache():
    """Caches moon data and forces a fertility recalculation to fix old JSON versions."""
    now = datetime.now()
    start_date = now - timedelta(days=180)
    end_date = now + timedelta(days=180)

    user_data = load_user_data()
    
    # FORCE recalculation of fertility on startup to ensure any old data is updated
    # to the new multi-cluster logic.
    user_data["fertile_days"] = calculate_fertile_window(user_data["period_days"])
    
    moons = user_data.get("moons", {})
    needs_update = False

    current_day = start_date
    while current_day <= end_date:
        month_key = current_day.strftime("%Y-%m")
        day_str = str(current_day.day)

        if month_key not in moons:
            moons[month_key] = {}

        if day_str not in moons[month_key]:
            image_path = get_moon_image_path(current_day)
            moons[month_key][day_str] = image_path
            needs_update = True

        current_day += timedelta(days=1)

    if needs_update or True: # Always save to update fertility windows
        user_data["moons"] = moons
        save_user_data(user_data)

    return user_data
