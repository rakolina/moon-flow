import PySimpleGUI as sg
from datetime import datetime, timedelta


class CalendarUI:
    BG_COLOR = '#555555'
    TEXT_COLOR = 'gray'

    def __init__(self, all_data):
        self.all_data = all_data
        self.now = datetime.now()

        # 1. Define the Rolling Window
        # Calculate coming Saturday
        if self.now.weekday() == 5:  # Saturday
            days_until_sat = 7
        else:
            days_until_sat = (5 - self.now.weekday()) % 7

        self.end_date = self.now + timedelta(days=days_until_sat)
        # Go back 35 days (5 weeks) from that Saturday
        self.start_date = self.end_date - timedelta(days=35)
        # Ensure the grid starts on a Monday
        self.grid_start = self.start_date - timedelta(days=self.start_date.weekday())

    def create_day_cell(self, date_obj):
        """Creates a cell for a specific date object."""
        day = date_obj.day
        month_key = date_obj.strftime("%Y-%m")

        # Lookup the image from the cached JSON data
        month_dict = self.all_data.get(month_key, {})
        image_path = month_dict.get(str(day), None)
        btn_image = image_path if image_path else None

        return sg.Column([
            [sg.Text(str(day), justification='center', font=('Arial', 10, 'bold'),
                     text_color=self.TEXT_COLOR, background_color=self.BG_COLOR)],
            [sg.Button("", image_filename=btn_image, key=f"-DATE{date_obj.strftime('%Y%m%d')}-",
                       border_width=0, button_color=(self.BG_COLOR, self.BG_COLOR))]
        ], element_justification='center', background_color=self.BG_COLOR)

    def build_layout(self):
        # 1. Create the Header Row
        headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_row = [sg.Text("", size=(5, 1), visible=False)]  # Spacer for the month label column
        header_row += [sg.Text(h, size=(5, 1), justification='center',
                               font=('Arial', 10, 'italic'),
                               text_color=self.TEXT_COLOR, background_color=self.BG_COLOR)
                       for h in headers]

        # 2. Create the Rolling Grid Rows
        grid_rows = []
        current_date = self.grid_start

        # Loop until we reach the end_date
        while current_date <= self.end_date:
            # Calculate the month label for the first day of this week
            month_label = current_date.strftime("%B")  # e.g., "September"

            # Start the row with the month label
            row = [sg.Text(month_label, font=('Arial', 12, 'bold'),
                           justification='right', text_color=self.TEXT_COLOR,
                           background_color=self.BG_COLOR, size=(10, 1))]

            # Add the 7 days of the week
            for _ in range(7):
                row.append(self.create_day_cell(current_date))
                current_date += timedelta(days=1)

            grid_rows.append(row)

        # 3. Final Layout Assembly
        layout = [
            [sg.Text("Moon Flow - Rolling View", font=('Arial', 16, 'bold'),
                     justification='center', expand_x=True,
                     text_color=self.TEXT_COLOR, background_color=self.BG_COLOR)],
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
