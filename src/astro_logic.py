from skyfield.api import load as skyfield_load
from datetime import datetime
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- slow loads ---
PLANETS = skyfield_load('de421.bsp')
TS = skyfield_load.timescale()
EARTH = PLANETS['earth']
SUN = PLANETS['sun']
MOON = PLANETS['moon']


def get_moon_image_path(date=None):
    """
    Calculates the moon phase using ecliptic longitude.
    Returns a tuple: (image_path, day_index)
    """
    local_tz = datetime.now().astimezone().tzinfo
    if date is None:
        date = datetime.now().astimezone()
    else:
        if date.tzinfo is None:
            date = date.replace(tzinfo=local_tz)

    t = TS.from_datetime(date)

    e = EARTH.at(t)
    m = e.observe(MOON).apparent()
    s = e.observe(SUN).apparent()

    m_lon = m.ecliptic_latlon()[1].degrees
    s_lon = s.ecliptic_latlon()[1].degrees

    phase_angle = (m_lon - s_lon) % 360

    # Map the angle to 0-29 images.
    # Using a 30-day mapping to minimize duplicates by ensuring the image window
    # is slightly smaller than the average daily moon movement (~12.19 degrees).
    day_index = int((phase_angle / 360) * 30)
    day_index = min(max(day_index, 0), 29)

    image_path = os.path.join(ROOT_DIR, "assets", f"Moon28{day_index:02d}.png")
    
    return image_path, day_index


def save_moon_data_to_json(date_obj, image_path, json_file_path):
    """
    Saves image path and phase index to JSON.
    """
    month_key = date_obj.strftime("%Y-%m")
    day_key = str(date_obj.day)

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {}
    else:
        all_data = {}

    if month_key not in all_data:
        all_data[month_key] = {}

    # Use a dictionary to store both pieces of info
    all_data[month_key][day_key] = {
        "path": image_path,
        "phase": 0 # This would be passed in if called from outside
    }

    with open(json_file_path, 'w') as f:
        json.dump(all_data, f, indent=4)


if __name__ == "__main__":
    today = datetime.now()
    path, phase = get_moon_image_path(today)
    print(f"Today's image: {path} (Phase: {phase})")
