import PySimpleGUI as sg
from datetime import datetime, timedelta
import os
import cycle_data_logic
import moon_cache_logic
from ui_constants import UIConstants

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class CalendarMoonUI:
    def __init__(self, user_data):
        self.user_data = user_data
        self.now = datetime.now()

    def build_layout(self):
        cycle_data = cycle_data_logic.load_cycle_data()
        moon_data = moon_cache_logic.load_moon_data()
        
        # 1. Headers: Replace numbers with Moon Phase Images (1-28)
        headers = []
        for i in range(1, 29):
            img_path = os.path.join(ROOT_DIR, "assets", f"Moon28{i:02d}.png")
            # We use a smaller size for headers to ensure the view remains compact
            headers.append(sg.Image(filename=img_path, size=(30, 30), pad=(2, 0)))
        
        # 2. Group the year into Lunar Cycles
        cycles = []
        current_cycle = []
        
        start_of_year = datetime(self.now.year, 1, 1)
        end_of_year = datetime(self.now.year, 12, 31)
        
        cursor = start_of_year
        while cursor <= end_of_year:
            month_key = cursor.strftime("%Y-%m")
            day_str = str(cursor.day)
            month_moons = moon_data.get(month_key, {})
            day_info = month_moons.get(day_str, {})
            phase = day_info.get("phase") if isinstance(day_info, dict) else None
            
            if phase is not None:
                if phase == 1 and current_cycle:
                    cycles.append(current_cycle)
                    current_cycle = []
                current_cycle.append({"date": cursor, "phase": phase})
            cursor += timedelta(days=1)
        
        if current_cycle:
            cycles.append(current_cycle)

        # 3. Build Grid Rows
        grid_rows = []
        for cycle_idx, cycle_days in enumerate(cycles, 1):
            row = []
            month_name = "Cycle" # Simplified label for the cycle
            row.append(sg.Text(f"Cycle {cycle_idx}", font=('Arial', 10, 'bold'), text_color=UIConstants.TEXT_COLOR, 
                               background_color=UIConstants.BG_COLOR, size=(10, 1), justification='right', pad=(0, 2)))
            
            for phase_idx in range(1, 29):
                found_color = UIConstants.CELL_BG
                for day_info in cycle_days:
                    if day_info["phase"] == phase_idx:
                        date_obj = day_info["date"]
                        if cycle_data_logic.is_period_day(date_obj, data=cycle_data):
                            found_color = UIConstants.PERIOD_BG
                            break
                        elif cycle_data_logic.is_fertile_day(date_obj, data=cycle_data):
                            found_color = UIConstants.FERTILE_BG
                
                row.append(sg.Frame("", [[sg.Text("", size=(3, 1), background_color=found_color)]], 
                                      border_width=0, background_color=found_color, pad=(1, 2)))
            grid_rows.append(row)

        layout = [
            [sg.Text("Lunar Pattern View", font=('Arial', 16, 'bold'), text_color=UIConstants.TEXT_COLOR, 
                     background_color=UIConstants.BG_COLOR, expand_x=True, justification='center')],
            [sg.Text("Columns represent the 28 Moon Phases", font=('Arial', 10, 'italic'), 
                     text_color='gray', background_color=UIConstants.BG_COLOR, justification='center')],
            [headers],
            *grid_rows,
            [sg.Button("Close Moon View", button_color=('white', '#404040'))]
        ]
        return layout

    def show(self):
        layout = self.build_layout()
        moon_window = sg.Window("Moon Phase Pattern", layout, background_color=UIConstants.BG_COLOR, 
                               element_justification='center', finalize=True, resizable=True)
        
        while True:
            event, values = moon_window.read()
            if event in (sg.WIN_CLOSED, "Close Moon View"):
                break
        moon_window.close()
