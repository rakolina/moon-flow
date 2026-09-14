import PySimpleGUI as sg
from datetime import datetime, timedelta


class CalendarUI:
    BG_COLOR = '#555555'
    CELL_BG = '#666666'
    TEXT_COLOR = 'gray'
    EMPTY_CELL_COLOR = '#444444'
    # Constant to ensure absolute alignment across headers and cells
    COL_SIZE = (8, 1)

    def __init__(self, all_data):
        self.all_data = all_data
        self.now = datetime.now()

        if self.now.weekday() == 5:  # It is Saturday
            days_until_sat = 7
        else:
            days_until_sat = (5 - self.now.weekday()) % 7

        this_saturday = self.now + timedelta(days=days_until_sat)
        this_monday = this_saturday - timedelta(days=5)
        self.grid_start = this_monday - timedelta(weeks=3)

    def create_month_cell(self, text):
        """Structural container for the month label."""
        return sg.Frame("", [[sg.Text(text, font=('Arial', 12, 'bold'),
                                      justification='right', text_color=self.TEXT_COLOR,
                                      background_color=self.BG_COLOR, size=(10, 1))]],
                        border_width=0, background_color=self.BG_COLOR, relief=sg.RELIEF_FLAT)

    def create_day_cell(self, date_obj):
        """Creates a date cell with a specific internal structure."""
        day = date_obj.day
        month_key = date_obj.strftime("%Y-%m")
        month_dict = self.all_data.get(month_key, {})
        image_path = month_dict.get(str(day), None)

        if image_path:
            btn_image = image_path
            btn_color = (self.CELL_BG, self.CELL_BG)
        else:
            btn_image = None
            btn_color = (self.EMPTY_CELL_COLOR, self.EMPTY_CELL_COLOR)

        btn_params = {
            "image_filename": btn_image,
            "key": f"-DATE{date_obj.strftime('%Y%m%d')}-",
            "border_width": 0,
            "button_color": btn_color,
        }

        if not btn_image:
            btn_params["size"] = self.COL_SIZE

        cell_content = [
            [sg.Text(str(day), justification='center', font=('Arial', 10, 'bold'),
                     text_color=self.TEXT_COLOR, background_color=self.CELL_BG, size=self.COL_SIZE)],
            [sg.Button("", **btn_params)]
        ]
        return sg.Frame("", cell_content, border_width=1, element_justification='center',
                        background_color=self.CELL_BG, relief=sg.RELIEF_FLAT)

    def build_layout(self):
        # 1. Header Row
        headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_row = [self.create_month_cell("")]

        for h in headers:
            # FIX: Reduced to a single-row structure to halve the height.
            # We keep the size=self.COL_SIZE to ensure width alignment.
            header_content = [
                [sg.Text(h, size=self.COL_SIZE, justification='center',
                         font=('Arial', 10, 'italic'),
                         text_color=self.TEXT_COLOR, background_color=self.CELL_BG)]
            ]
            header_row.append(
                sg.Frame("", header_content, border_width=1, element_justification='center',
                         relief=sg.RELIEF_FLAT, background_color=self.CELL_BG)
            )

        # 2. Create exactly 4 Rows
        grid_rows = []
        current_date = self.grid_start
        last_month = None

        for week in range(4):
            this_month = current_date.strftime("%B")
            month_label = this_month if this_month != last_month else ""
            last_month = this_month

            row = [self.create_month_cell(month_label)]
            for _ in range(7):
                row.append(self.create_day_cell(current_date))
                current_date += timedelta(days=1)
            grid_rows.append(row)

        # 3. Final Assembly
        layout = [
            header_row,
            *grid_rows,
            [sg.Button("Exit", pad=(0, 20), button_color=('white', '#404040'))]
        ]
        return layout

    def run(self):
        sg.theme('Default1')
        window = sg.Window(
            "Moon Flow",
            self.build_layout(),
            element_justification='center',
            background_color=self.BG_COLOR
        )
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                break
            if event and event.startswith("-DATE"):
                date_str = event.replace("-DATE", "").replace("-", "")
                print(f"User clicked on date: {date_str}")
        window.close()


def run_app(all_data):
    ui = CalendarUI(all_data)
    ui.run()

