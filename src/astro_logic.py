from skyfield.api import load
from datetime import datetime


def get_moon_image_path(date=None):
    """
    Calculates the moon phase for a given date using the OS local timezone
    and returns the path to the corresponding image file.
    """
    # 1. Get the local system timezone
    local_tz = datetime.now().astimezone().tzinfo

    # 2. Handle the date and ensure it is timezone-aware
    if date is None:
        # Create current time with the system's local timezone
        date = datetime.now().astimezone()
    else:
        # If a date was passed in, attach the system's local timezone to it
        if date.tzinfo is None:
            date = date.replace(tzinfo=local_tz)

    # 3. Load the astronomy data
    planets = load('de421.bsp')
    ts = load.timescale()
    t = ts.from_datetime(date)

    earth = planets['earth']
    sun = planets['sun']
    moon = planets['moon']

    # 4. Get positions
    e = earth.at(t)
    m = e.observe(moon).apparent()
    s = e.observe(sun).apparent()

    # 5. Calculate the phase angle (0 to 360 degrees)
    phase_angle = m.separation_from(s).radians
    degrees = (phase_angle * 180 / 3.14159) % 360

    # 6. Map the 360 degrees to a number between 1 and 28
    day_index = int((degrees / 360) * 28) + 1

    if day_index > 28:
        day_index = 28

    return f"assets/Moon28{day_index:02d}*.jpg"


# --- Test it ---
if __name__ == "__main__":
    today_image = get_moon_image_path()
    print(f"Today's image file (Local Time): {today_image}")

    # Test a specific date
    test_date = datetime(2026, 9, 26)
    print(f"Image for Jan 1, 2026 (Local Time): {get_moon_image_path(test_date)}")
