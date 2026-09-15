import PySimpleGUI as sg
from datetime import datetime, timedelta
import moon_cache_logic
import cycle_data_logic
from calendar_month_ui import CalendarMonthUI
from calendar_year_ui import CalendarYearUI
from calendar_moon_ui import CalendarMoonUI

# --- App Controller ---
class CalendarUI:
    def __init__(self, user_data):
        self.user_data = user_data
        self.month_window = None
        self.year_window = None
        self.moon_window = None
        self.month_ui = None

    def get_oldest_date(self):
        moons = moon_cache_logic.load_moon_data()
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
        if self.year_window is None:
            year_ui = CalendarYearUI(self.user_data)
            self.year_window = year_ui.show()


    def open_moon_view(self):
        if self.moon_window is None:
            moon_ui = CalendarMoonUI(self.user_data)
            self.moon_window = moon_ui.show()

    def run(self):
        # 1. Setup Month View
        self.month_ui = CalendarMonthUI(self.user_data)
        self.month_window = sg.Window("Moon Flow", self.month_ui.build_layout(), 
                                     element_justification='center', 
                                     background_color=sg.theme_background_color(), 
                                     finalize=True)
        
        from ui_constants import UIConstants
        self.month_window.TKroot.configure(bg=UIConstants.BG_COLOR)
        self.month_ui.refresh_grid(self.month_window)
        
        while True:
            window, event, values = sg.read_all_windows()
            
            if window == self.month_window:
                if event in (sg.WIN_CLOSED, "Exit"):
                    self.month_window.close()
                    return "CLOSE"
                
                if event == "↑ Prev Week":
                    self.month_ui.view_start_date -= timedelta(days=7)
                    self.month_ui.refresh_grid(self.month_window)
                elif event == "Next Week ↓":
                    self.month_ui.view_start_date += timedelta(days=7)
                    self.month_ui.refresh_grid(self.month_window)
                elif event == "← Oldest":
                    self.month_ui.view_start_date = self.get_oldest_date()
                    self.month_ui.refresh_grid(self.month_window)
                elif event == "Newest →":
                    current_monday = datetime.now() - timedelta(days=datetime.now().weekday())
                    self.month_ui.view_start_date = current_monday - timedelta(weeks=4)
                    self.month_ui.refresh_grid(self.month_window)
                elif event == "Year View":
                    self.open_year_view()
                elif event == "Moon View":
                    self.open_moon_view()
                elif event and event.startswith("-DAY_IMG_"):
                    cell_index = int(event.replace("-DAY_IMG_", "").replace("-", ""))
                    clicked_date = self.month_ui.cell_mapping.get(cell_index)
                    if clicked_date:
                        cycle_data_logic.toggle_period_day(clicked_date)
                        self.month_ui.refresh_grid(self.month_window)
            
            elif window is not None:
                # This handles the Close buttons of the other windows
                # because they are read via read_all_windows()
                if event in (sg.WIN_CLOSED, "Close Year View", "Close Moon View"):
                    window.close()
                    if window == self.year_window:
                        self.year_window = None
                    elif window == self.moon_window:
                        self.moon_window = None

        
        self.month_window.close()

def run_app(user_data):
    app = CalendarUI(user_data)
    return app.run()
