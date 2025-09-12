# host.py
from tkinter import Tk

from common import *

from monitor import TableMonitor, VisualMonitor, HistoryMonitor
from control_panel import ControlPanel

class Host(Tk):
    def __init__(self):
        super().__init__()
        self.minsize(*WINDOW_SIZE)
        self.attributes("-fullscreen", True)
        self.config(bg=theme["primary_color"])
        style = Style()
        style.theme_use("clam")
        for style_name, kwargs in widget_styles.items():
            style.configure(style_name, **kwargs)

        self.table_monitor = TableMonitor(self)
        self.visual_monitor = VisualMonitor(self)
        self.history_monitor = HistoryMonitor(self)
        self.control_panel = ControlPanel(self)

        self.monitors = [self.table_monitor, self.visual_monitor, self.history_monitor]

        column_sizes = [1, 5, 1]
        for column_index in range(len(column_sizes)):
            self.columnconfigure(column_index, weight=column_sizes[column_index])

        row_sizes = [3, 1]
        for row_index in range(len(row_sizes)):
            self.rowconfigure(row_index, weight=row_sizes[row_index])

        layout = {
            self.table_monitor:     {"row": 0,  "column": 0},
            self.visual_monitor:    {"row": 0,  "column": 1},
            self.history_monitor:   {"row": 1,  "column": 1},
            self.control_panel:     {"row": 0,  "column": 2},
        }

        for panel, info in layout.items():
            panel.grid(sticky="nsew", **info)

    def update_information(self, information: dict):
        for monitor in self.monitors:
            monitor.update_information(information)


if __name__ == "__main__":
    host = Host()
    host.update_information({"current_position": 0.0, "bridge_lights": "GO"})
    host.mainloop()
