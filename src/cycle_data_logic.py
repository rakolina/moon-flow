import json
import os
from datetime import datetime, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CYCLE_DATA_FILE = os.path.join(ROOT_DIR, "data", "cycle_data.json")

def load_cycle_data():
    """Loads the period and fertility data from JSON."""
    if not os.path.exists(CYCLE_DATA_FILE):
        return {"period_days": [], "fertile_days": []}
    with open(CYCLE_DATA_FILE, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
            data.setdefault("period_days", [])
            data.setdefault("fertile_days", [])
            return data
        except (json.JSONDecodeError, IOError):
            return {"period_days": [], "fertile_days": []}

def save_cycle_data(cycle_data):
    """Saves the period and fertility data to JSON."""
    data_folder = os.path.join(ROOT_DIR, "data")
    os.makedirs(data_folder, exist_ok=True)
    with open(CYCLE_DATA_FILE, "w") as f:
        json.dump(cycle_data, f, indent=4)

def calculate_fertile_window(period_days):
    """Groups all marked period days into clusters and calculates fertile windows."""
    if not period_days:
        return []

    sorted_days = sorted([datetime.strptime(d, "%Y-%m-%d") for d in period_days])
    clusters = []
    if sorted_days:
        current_cluster = [sorted_days[0]]
        for i in range(1, len(sorted_days)):
            if (sorted_days[i] - sorted_days[i-1]).days == 1:
                current_cluster.append(sorted_days[i])
            else:
                clusters.append(current_cluster)
                current_cluster = [sorted_days[i]]
        clusters.append(current_cluster)

    all_fertile_dates = []
    for cluster in clusters:
        start_of_period = cluster[0]
        for day_offset in range(10, 16):
            fertile_date = start_of_period + timedelta(days=day_offset)
            all_fertile_dates.append(fertile_date.strftime("%Y-%m-%d"))
    return all_fertile_dates

def toggle_period_day(date_obj):
    """Toggles a day and updates the cycle data file."""
    cycle_data = load_cycle_data()
    date_str = date_obj.strftime("%Y-%m-%d")
    
    if date_str in cycle_data["period_days"]:
        cycle_data["period_days"].remove(date_str)
    else:
        cycle_data["period_days"].append(date_str)
    
    cycle_data["fertile_days"] = calculate_fertile_window(cycle_data["period_days"])
    save_cycle_data(cycle_data)
    return cycle_data

def is_period_day(date_obj, data=None):
    if data is None:
        data = load_cycle_data()
    period_days = data.get("period_days", []) if isinstance(data, dict) else []
    return date_obj.strftime("%Y-%m-%d") in period_days

def is_fertile_day(date_obj, data=None):
    if data is None:
        data = load_cycle_data()
    fertile_days = data.get("fertile_days", []) if isinstance(data, dict) else []
    return date_obj.strftime("%Y-%m-%d") in fertile_days
