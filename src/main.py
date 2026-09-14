from moon_cache_logic import initialize_moon_cache
from calendar_ui import run_app

def main():
    while True:
        # 1. Sync and load the moon data from JSON
        # This handles the wide window cache (6 months back/forward)
        user_data = initialize_moon_cache()

        # 2. Pass that data into the UI
        status = run_app(user_data)
        
        if status == "CLOSE":
            break
        # if status == "REFRESH", the loop continues and re-runs run_app with updated data

if __name__ == "__main__":
    main()
