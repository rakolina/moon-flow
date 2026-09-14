import PySimpleGUI as sg
from datetime import datetime, timedelta
import cycle_logic
from calendar_month_ui import CalendarMonthUI
from calendar_year_ui import CalendarYearUI

# --- App Controller ---
class CalendarUI:
    def __init__(self, user_data):
        self.user_data = user_data

    def get_oldest_date(self):
        data = cycle_logic.load_user_data()
        moons = data.get("moons", {})
        if not moons:
            return datetime.now() - timedelta(days=datetime.now().weekday())
        sorted_months = sorted(moons.keys())
        earliest_month_str = sorted_months[0]
        days = [int(d) for d in moons[earliest_month_str].keys()]
        earliest_day = min(days)
        year, month = map(int, earliest_month_str.split('-'))
        oldest_date = datetime(year, month, earliest_day)
        return oldest_date - timedelta(days=oldest_date.weekday())

    def open_year_view(self):
        year_view = CalendarYearUI(self.user_data)
        year_view.show()

    def run(self):
        editor = CalendarMonthUI(self.user_data)
        return editor.run(self)

def run_app(user_data):
    app = CalendarUI(user_data)
    return app.run()
