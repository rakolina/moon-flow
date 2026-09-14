from cycle_logic import initialize_moon_cache
from calendar_ui import run_app


def main():
    print("🚀 Application starting...")
    while True:
        print("📅 Initializing moon cache (this may take a minute on first run)...")
        user_data = initialize_moon_cache()
        print("✅ Moon cache ready!")

        print("🖥️ Attempting to launch UI window...")
        status = run_app(user_data)
        print(f"🏁 App returned status: {status}")

        if status == "CLOSE":
            print("👋 Exiting application.")
            break


if __name__ == "__main__":
    main()
