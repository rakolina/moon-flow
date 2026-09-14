import PySimpleGUI as sg
from datetime import datetime
import cycle_data_logic
import moon_cache_logic
from ui_constants import UIConstants

class CalendarMoonUI:
    def __init__(self, user_data):
        self.user_data = user_data
        self.now = datetime.now()

    def build_layout(self):
        # Use combined data for the view
        cycle_data = cycle_data_logic.load_cycle_data()
        moon_data = moon_cache_logic.load_moon_data()
        
        headers = []
        for i in range(1, 29):
            headers.append(sg.Text(str(i), font=('Arial', 8, 'bold'), text_color=UIConstants.TEXT_COLOR, 
                                    background_color=UIConstants.CELL_BG, size=(4, 1), justification='center'))
        
        grid_rows = []
        for month_idx in range(1, 13):
            row = []
            month_name = datetime(self.now.year, month_idx, 1).strftime("%B")
            row.append(sg.Text(month_name, font=('Arial', 10, 'bold'), text_color=UIConstants.TEXT_COLOR, 
                               background_color=UIConstants.BG_COLOR, size=(10, 1), justification='right', pad=(0, 2)))
            
            for phase_idx in range(1, 29):
                month_key = f"{self.now.year}-{month_idx:02d}"
                month_moons = moon_data.get(month_key, {})
                found_color = UIConstants.CELL_BG
                
                for day_str, img_path in month_moons.items():
                    if f"Moon28{phase_idx:02d}.png" in img_path:
                        date_obj = datetime(self.now.year, month_idx, int(day_str))
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
            [sg.Text("X-Axis: Moon Phase (1-28) | Y-Axis: Month", font=('Arial', 10, 'italic'), 
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
