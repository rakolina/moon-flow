import PySimpleGUI as sg
from datetime import datetime, timedelta
import os
import astro_logic
import cycle_data_logic
import moon_cache_logic
from ui_constants import UIConstants

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class CalendarMoonUI:
    def __init__(self, user_data):
        self.user_data = user_data
        self.now = datetime.now()

    def _get_moon_phase(self, date):
        moon_data = moon_cache_logic.load_moon_data()
        month_key = date.strftime("%Y-%m")
        day_str = str(date.day)
        if month_key in moon_data and day_str in moon_data[month_key]:
            return moon_data[month_key][day_str].get("phase")
        # Fallback to astronomical calculation
        _, phase = astro_logic.get_moon_image_path(date)
        return phase

    def build_layout(self):
        cycle_data = cycle_data_logic.load_cycle_data()

        # Fixed width for all columns to ensure perfect vertical alignment
        COL_WIDTH = 30
        HORIZONTAL_PAD = 5

        # 1. Headers: Moon Phase Images (0-29)
        headers = [sg.Text("", size=(10, 1), background_color=UIConstants.BG_COLOR)]
        for i in range(0, 30):
            img_path = os.path.join(ROOT_DIR, "assets", f"Moon28{i:02d}.png")
            headers.append(sg.Image(filename=img_path, size=(COL_WIDTH, 30), pad=(HORIZONTAL_PAD, 0)))

        # 2. Define Date Range and Find True Start Date (Last New Moon)
        range_start = self.now - timedelta(days=365)

        # Search backwards from range_start to find the first New Moon (phase 0)
        true_start_date = range_start
        for i in range(31): # Look back up to a month
            check_date = range_start - timedelta(days=i)
            if self._get_moon_phase(check_date) == 0:
                true_start_date = check_date
                break

        # 3. Group the range into Lunar Cycles
        cycles = []
        current_cycle = []
        cursor = true_start_date

        while cursor <= self.now:
            phase = self._get_moon_phase(cursor)

            # Start a new cycle if we hit a New Moon (phase 0).
            # Use a slightly higher minimum (26 days) to ensure we don't split
            # a single New Moon event that spans multiple calendar days.
            if phase == 0 and current_cycle and len(current_cycle) >= 26:
                cycles.append(current_cycle)
                current_cycle = []

            current_cycle.append({"date": cursor, "phase": phase})
            cursor += timedelta(days=1)




        if current_cycle:
            cycles.append(current_cycle)

        # 4. Build Grid Rows
        grid_rows = []
        for cycle_idx, cycle_days in enumerate(cycles, 1):
            row = []
            # Determine the alternating background color for blank cells in this cycle
            blank_color = UIConstants.EMPTY_CELL_COLOR_LIGHT if cycle_idx % 2 == 1 else UIConstants.EMPTY_CELL_COLOR_DARK

            # Using the date of the New Moon for the row label
            cycle_start_str = cycle_days[0]["date"].strftime("%Y-%m-%d")
            row.append(sg.Text(f"{cycle_start_str}", font=('Arial', 10, 'bold'), text_color=UIConstants.TEXT_COLOR,
                               background_color=UIConstants.BG_COLOR, size=(12, 1), justification='right', pad=(0, 2)))

            for rel_idx in range(0, 30):
                # Priority: Period > Fertile > Blank
                found_color = blank_color

                # Use the relative index in the cycle as the column position.
                # This ensures 1 cell per day, no duplicates, and no skips.
                if rel_idx < len(cycle_days):
                    day_info = cycle_days[rel_idx]
                    date_obj = day_info["date"]
                    if cycle_data_logic.is_period_day(date_obj, data=cycle_data):
                        found_color = UIConstants.PERIOD_BG
                    elif cycle_data_logic.is_fertile_day(date_obj, data=cycle_data):
                        found_color = UIConstants.FERTILE_BG

                # Using sg.Graph for efficiency
                row.append(sg.Graph((COL_WIDTH, 15), (0,0), (COL_WIDTH, 15),
                                      background_color=found_color, pad=(HORIZONTAL_PAD, 2)))
            grid_rows.append(row)



        layout = [
            [headers],
            *grid_rows,
            [sg.Button("Close Moon View", button_color=('white', '#404040'))]
        ]
        return layout

    def show(self):
        layout = self.build_layout()
        moon_window = sg.Window("Moon Phase Pattern", layout, background_color=UIConstants.BG_COLOR,
                               element_justification='center', finalize=True, resizable=True)
        return moon_window
