from skyfield.api import load, utc  # Added 'utc' here
from datetime import datetime


def get_moon_image_path(date=None):
    """
    Calculates the moon phase for a given date and returns
    the path to the corresponding image file (Moon2801.jpg to Moon2828.jpg).
    """
    # 1. Handle the date and ensure it has a timezone (UTC)
    if date is None:
        # Create current time directly in UTC
        date = datetime.now(utc)
    else:
        # If a date was passed in, force it to be UTC
        if date.tzinfo is None:
            date = date.replace(tzinfo=utc)

    # 2. Load the astronomy data
    planets = load('de421.bsp')
    ts = load.timescale()
    t = ts.from_datetime(date)

    earth = planets['earth']
    sun = planets['sun']
    moon = planets['moon']

    # 3. Get positions
    e = earth.at(t)
    m = e.observe(moon).apparent()
    s = e.observe(sun).apparent()

    # 4. Calculate the phase angle (0 to 360 degrees)
    phase_angle = m.separation_from(s).radians
    degrees = (phase_angle * 180 / 3.14159) % 360

    # 5. Map the 360 degrees to a number between 1 and 28
    day_index = int((degrees / 360) * 28) + 1

    if day_index > 28:
        day_index = 28

    return f"assets/Moon28{day_index:02d}*.jpg"


# --- Test it ---
if __name__ == "__main__":
    today_image = get_moon_image_path()
    print(f"Today's image file: {today_image}")

    # Test a specific date
    test_date = datetime(2026, 1, 1)
    print(f"Image for Jan 1, 2026: {get_moon_image_path(test_date)}")
