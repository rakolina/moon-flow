from tkinter.constants import CURRENT

import PySimpleGUI as sg
from datetime import datetime, timedelta
import moon_cache_logic
import cycle_data_logic
from calendar_month_ui import CalendarMonthUI
from calendar_year_ui import CalendarYearUI
from calendar_moon_ui import CalendarMoonUI

PREV_WEEK = "↑ Prev Week"

NEXT_WEEK = "Next Week ↓"

MOON_VIEW = "Moon View"

YEAR_VIEW = "Year View"

OLDEST = "← Oldest"

CURRENT = "Current"


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
            self.year_window = sg.Window("Yearly Moon View", year_ui.build_layout(), 
                                         background_color=sg.theme_background_color(), # Placeholder, using constants in build_layout
                                         element_justification='center', finalize=True, resizable=True)
            # Fix background color for the window since theme might differ
            from ui_constants import UIConstants
            self.year_window.TKroot.configure(bg=UIConstants.BG_COLOR)

    def open_moon_view(self):
        if self.moon_window is None:
            moon_ui = CalendarMoonUI(self.user_data)
            self.moon_window = sg.Window("Moon Phase Pattern", moon_ui.build_layout(), 
                                         background_color=sg.theme_background_color(),
                                         element_justification='center', finalize=True, resizable=True)
            from ui_constants import UIConstants
            self.moon_window.TKroot.configure(bg=UIConstants.BG_COLOR)

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
            # Read events from ALL active windows
            window, event, values = sg.read_all_windows()
            
            if window == self.month_window:
                if event in (sg.WIN_CLOSED, "Exit"):
                    self.month_window.close()
                    return "CLOSE"
                
                if event == PREV_WEEK:
                    self.month_ui.view_start_date -= timedelta(days=7)
                    self.month_ui.refresh_grid(self.month_window)
                elif event == NEXT_WEEK:
                    self.month_ui.view_start_date += timedelta(days=7)
                    self.month_ui.refresh_grid(self.month_window)
                elif event == OLDEST:
                    self.month_ui.view_start_date = self.get_oldest_date()
                    self.month_ui.refresh_grid(self.month_window)
                elif event == CURRENT:
                    current_monday = datetime.now() - timedelta(days=datetime.now().weekday())
                    self.month_ui.view_start_date = current_monday - timedelta(weeks=4)
                    self.month_ui.refresh_grid(self.month_window)
                elif event == YEAR_VIEW:
                    self.open_year_view()
                elif event == MOON_VIEW:
                    self.open_moon_view()
                elif event and event.startswith("-DAY_IMG_"):
                    cell_index = int(event.replace("-DAY_IMG_", "").replace("-", ""))
                    clicked_date = self.month_ui.cell_mapping.get(cell_index)
                    if clicked_date:
                        cycle_data_logic.toggle_period_day(clicked_date)
                        self.month_ui.refresh_grid(self.month_window)
            
            elif window == self.year_window:
                if event in (sg.WIN_CLOSED, "Close Year View"):
                    self.year_window.close()
                    self.year_window = None
            
            elif window == self.moon_window:
                if event in (sg.WIN_CLOSED, "Close Moon View"):
                    self.moon_window.close()
                    self.moon_window = None
            
            else:
                # Unrecognized window closed
                window.close()

def run_app(user_data):
    app = CalendarUI(user_data)
    return app.run()
