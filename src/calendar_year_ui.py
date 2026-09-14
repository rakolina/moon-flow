import PySimpleGUI as sg
from datetime import datetime
import calendar
import cycle_data_logic
import moon_cache_logic
from ui_constants import UIConstants

class CalendarYearUI:
    def __init__(self, user_data):
        self.user_data = user_data
        self.moons = user_data.get("moons", {})
        self.now = datetime.now()

    def create_month_panel(self, month_idx, data):
        month_name = calendar.month_name[month_idx]
        month_days = calendar.monthcalendar(self.now.year, month_idx)
        
        month_layout = [[sg.Text(month_name, font=('Arial', 12, 'bold'), text_color=UIConstants.TEXT_COLOR, 
                                  background_color=UIConstants.BG_COLOR, justification='center', expand_x=True)]]
        
        weekdays = ["M", "T", "W", "T", "F", "S", "S"]
        day_headers = []
        for wd in weekdays:
            day_headers.append(sg.Text(wd, font=('Arial', 8), text_color=UIConstants.TEXT_COLOR, 
                                       background_color=UIConstants.CELL_BG, size=(4, 1), justification='center'))
        month_layout.append(day_headers)

        for week in month_days:
            week_row = []
            for day in week:
                if day == 0:
                    week_row.append(sg.Text("", size=(4, 2), background_color=UIConstants.BG_COLOR))
                else:
                    date_obj = datetime(self.now.year, month_idx, day)
                    is_period = cycle_data_logic.is_period_day(date_obj, data=data)
                    is_fertile = cycle_data_logic.is_fertile_day(date_obj, data=data)
                    
                    bg = UIConstants.PERIOD_BG if is_period else (UIConstants.FERTILE_BG if is_fertile else UIConstants.CELL_BG)
                    month_key = date_obj.strftime("%Y-%m")
                    img = data.get("moons", {}).get(month_key, {}).get(str(day))
                    week_row.append(sg.Image(filename=img, background_color=bg, size=(20, 20)))
            month_layout.append(week_row)
        
        return sg.Frame("", month_layout, border_width=1, background_color=UIConstants.BG_COLOR, element_justification='center')

    def show(self):
        # Combine data for the view
        data = {
            "moons": moon_cache_logic.load_moon_data(),
            "period_days": cycle_data_logic.load_cycle_data()["period_days"],
            "fertile_days": cycle_data_logic.load_cycle_data()["fertile_days"]
        }
        
        year_grid = []
        for row_idx in range(4):
            row = []
            for col_idx in range(3):
                month_idx = (row_idx * 3) + col_idx + 1
                if month_idx <= 12:
                    row.append(self.create_month_panel(month_idx, data))
            year_grid.append(row)

        layout = [
            [sg.Text(f"Year View {self.now.year}", font=('Arial', 16, 'bold'), text_color=UIConstants.TEXT_COLOR, 
                     background_color=UIConstants.BG_COLOR, expand_x=True, justification='center')],
            [sg.Column(year_grid, scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True, background_color=UIConstants.BG_COLOR)],
            [sg.Button("Close Year View", button_color=('white', '#404040'))]
        ]

        year_window = sg.Window("Yearly Moon View", layout, background_color=UIConstants.BG_COLOR, 
                               element_justification='center', finalize=True, resizable=True)
        
        while True:
            event, values = year_window.read()
            if event in (sg.WIN_CLOSED, "Close Year View"):
                break
        year_window.close()
