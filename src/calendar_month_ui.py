import PySimpleGUI as sg
from datetime import datetime, timedelta
import cycle_data_logic
import moon_cache_logic
from ui_constants import UIConstants

class CalendarMonthUI:
    def __init__(self, user_data):
        self.user_data = user_data
        self.moons = user_data.get("moons", {})
        self.now = datetime.now()
        current_monday = self.now - timedelta(days=self.now.weekday())
        self.view_start_date = current_monday - timedelta(weeks=4)
        self.cell_mapping = {}

    def create_month_cell(self, index):
        return sg.Frame("", [[sg.Text("", key=f"-MONTH_TEXT_{index}-", font=('Arial', 12, 'bold'),
                                      justification='right', text_color=UIConstants.TEXT_COLOR,
                                      background_color=UIConstants.BG_COLOR, size=(10, 1))]],
                        border_width=0, background_color=UIConstants.BG_COLOR, relief=sg.RELIEF_FLAT)

    def create_day_cell(self, index):
        cell_content = [
            [sg.Text("", key=f"-DAY_TEXT_{index}-", justification='center', font=('Arial', 10, 'bold'),
                     text_color=UIConstants.TEXT_COLOR, background_color=UIConstants.CELL_BG, size=UIConstants.COL_SIZE)],
            [sg.Image("", key=f"-DAY_IMG_{index}-", enable_events=True, size=(40, 40))]
        ]
        return sg.Frame("", cell_content, key=f"-DAY_FRAME_{index}-", border_width=1, 
                        element_justification='center', background_color=UIConstants.CELL_BG, relief=sg.RELIEF_FLAT)

    def build_layout(self):
        headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_row = [self.create_month_cell(0)]
        for h in headers:
            header_content = [[sg.Text(h, size=UIConstants.COL_SIZE, justification='center',
                                       font=('Arial', 10, 'italic'),
                                       text_color=UIConstants.TEXT_COLOR, background_color=UIConstants.CELL_BG)]]
            header_row.append(sg.Frame("", header_content, border_width=1, element_justification='center',
                                       relief=sg.RELIEF_FLAT, background_color=UIConstants.CELL_BG))

        grid_rows = []
        for row_idx in range(6):
            row = [self.create_month_cell(row_idx)]
            for col_idx in range(7):
                cell_index = (row_idx * 7) + col_idx
                row.append(self.create_day_cell(cell_index))
            grid_rows.append(row)

        return [
            [
                sg.Button("← Oldest", size=(10, 1), button_color=('white', '#404040')),
                sg.Button("↑ Prev Week", size=(12, 1), button_color=('white', '#404040')), 
                sg.Text(f"{self.view_start_date.year}", key="-VIEW_DATE-",
                        font=('Arial', 12, 'bold'), text_color=UIConstants.TEXT_COLOR, background_color=UIConstants.BG_COLOR),
                sg.Button("Next Week ↓", size=(12, 1), button_color=('white', '#404040')),
                sg.Button("Newest →", size=(10, 1), button_color=('white', '#404040')),
            ],
            header_row,
            grid_rows,
            [
                sg.Button("Moon View", size=(12, 1), button_color=('white', '#404040')),
                sg.Button("Year View", size=(12, 1), button_color=('white', '#404040')),
                sg.Button("Exit", size=(12, 1), pad=(0, 20), button_color=('white', '#404040'))
            ]
        ]

    def refresh_grid(self, window):
        # Corrected: Load from separate logic files
        current_cycle_data = cycle_data_logic.load_cycle_data()
        current_moon_data = moon_cache_logic.load_moon_data()
        
        current_date = self.view_start_date
        last_month = None
        today = datetime.now().date()

        for row_idx in range(6):
            this_month = current_date.strftime("%B")
            month_label = this_month if this_month != last_month else ""
            last_month = this_month
            window[f"-MONTH_TEXT_{row_idx}-"].update(month_label, text_color=UIConstants.TEXT_COLOR)

            for col_idx in range(7):
                cell_index = (row_idx * 7) + col_idx
                day_num = current_date.day
                month_key = current_date.strftime("%Y-%m")
                
                # Access moon data using the new dictionary structure
                month_dict = current_moon_data.get(month_key, {})
                day_data = month_dict.get(str(day_num), {})
                image_path = day_data.get("path") if isinstance(day_data, dict) else day_data
                
                is_period = cycle_data_logic.is_period_day(current_date, data=current_cycle_data)
                is_fertile = cycle_data_logic.is_fertile_day(current_date, data=current_cycle_data)
                
                if current_date.date() == today:
                    bg, txt_color = UIConstants.TODAY_BG, UIConstants.TODAY_TEXT
                elif is_period:
                    bg, txt_color = UIConstants.PERIOD_BG, UIConstants.TEXT_COLOR
                elif is_fertile:
                    bg, txt_color = UIConstants.FERTILE_BG, UIConstants.TEXT_COLOR
                else:
                    bg, txt_color = UIConstants.CELL_BG, UIConstants.TEXT_COLOR

                window[f"-DAY_FRAME_{cell_index}-"].Widget.configure(bg=bg)
                window[f"-DAY_TEXT_{cell_index}-"].update(str(day_num), background_color=bg, text_color=txt_color)
                window[f"-DAY_IMG_{cell_index}-"].update(filename=image_path)
                self.cell_mapping[cell_index] = current_date
                current_date += timedelta(days=1)
        
        window["-VIEW_DATE-"].update(f"{self.view_start_date.year}", text_color=UIConstants.TEXT_COLOR)

    def run(self, controller):
        sg.theme('Default1')
        window = sg.Window("Moon Flow", self.build_layout(), 
                           element_justification='center', background_color=UIConstants.BG_COLOR, finalize=True)
        self.refresh_grid(window)
        
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                window.close()
                return "CLOSE"
            if event == "↑ Prev Week":
                self.view_start_date -= timedelta(days=7)
                self.refresh_grid(window)
            elif event == "Next Week ↓":
                self.view_start_date += timedelta(days=7)
                self.refresh_grid(window)
            elif event == "← Oldest":
                self.view_start_date = controller.get_oldest_date()
                self.refresh_grid(window)
            elif event == "Newest →":
                current_monday = self.now - timedelta(days=self.now.weekday())
                self.view_start_date = current_monday - timedelta(weeks=4)
                self.refresh_grid(window)
            elif event == "Year View":
                controller.open_year_view()
            elif event == "Moon View":
                controller.open_moon_view()
            elif event and event.startswith("-DAY_IMG_"):
                cell_index = int(event.replace("-DAY_IMG_", "").replace("-", ""))
                clicked_date = self.cell_mapping.get(cell_index)
                if clicked_date:
                    cycle_data_logic.toggle_period_day(clicked_date)
                    self.refresh_grid(window)
        window.close()
