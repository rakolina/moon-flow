from cycle_logic import initialize_moon_cache
from calendar_ui import run_app


def main():
    # 1. Sync and load the moon data from JSON
    # This handles the 5-week rolling cache we built
    month_moons = initialize_moon_cache()

    # 2. Pass that data into the UI
    run_app(month_moons)


if __name__ == "__main__":
    main()