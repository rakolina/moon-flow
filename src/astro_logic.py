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
    Maps the 29.53 day cycle to 28 images using rounding for smoother transitions.
    """
    local_tz = datetime.now().astimezone().tzinfo
    if date is None:
        date = datetime.now().astimezone()
    else:
        if date.tzinfo is None:
            date = date.replace(tzinfo=local_tz)

    t = TS.from_datetime(date)

    # Get the positions of the sun and moon as seen from earth
    e = EARTH.at(t)
    m = e.observe(MOON).apparent()
    s = e.observe(SUN).apparent()

    # Convert to Ecliptic coordinates to get the 0-360 degree orbital position
    m_lon = m.ecliptic_latlon()[1].degrees
    s_lon = s.ecliptic_latlon()[1].degrees

    # Calculate the phase angle (0 at New Moon, 180 at Full Moon)
    phase_angle = (m_lon - s_lon) % 360

    # FIX: Use round() instead of int() to map the angle to 1-28 images.
    # This prevents "clumping" and distributes the inevitable duplicates
    # more naturally across the 29.5 day cycle.
    day_index = round((phase_angle / 360) * 27) + 1

    # Safety cap to ensure we stay within the 1-28 range
    day_index = min(max(day_index, 1), 28)

    return os.path.join(ROOT_DIR, "assets", f"Moon28{day_index:02d}.png")


def save_moon_data_to_json(date_obj, image_path, json_file_path):
    """
    Saves image path to JSON. Using a dictionary ensures that
    the same date is never stored twice (no structural duplicates).
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

    # This assignment OVERWRITES any existing entry for that day,
    # which is the primary fix for JSON duplicates.
    all_data[month_key][day_key] = image_path

    with open(json_file_path, 'w') as f:
        json.dump(all_data, f, indent=4)


if __name__ == "__main__":
    today = datetime.now()
    path = get_moon_image_path(today)
    print(f"Today's image: {path}")

    json_path = os.path.join(ROOT_DIR, "moon_data.json")
    save_moon_data_to_json(today, path, json_path)
    print(f"Successfully updated {json_path}")