from tkinter import Tk

from common import *
from monitor import TableMonitor, VisualMonitor, HistoryMonitor


class Host(Tk):
    def __init__(self):
        super().__init__()

        style = Style()
        style.theme_use("clam")
        for style_name, kwargs in widget_styles.items():
            style.configure(style_name, **kwargs)

        column_amount = 3
        self.columns = [Frame(self) for _ in range(column_amount)]

        self.table_monitor = TableMonitor(self.columns[0])
        self.visual_monitor = VisualMonitor(self.columns[1])
        self.history_monitor = HistoryMonitor(self.columns[1])

        for panel in [self.table_monitor, self.visual_monitor, self.history_monitor]:
            panel.pack(side="top")

