# monitor.py
from tkinter import Listbox, END

from common import *
from bridge_display import BridgeDisplay  # A canvas override


class Monitor(Frame):
    def __init__(self, master: Misc, initial_information: dict = None):
        super().__init__(master)
        if initial_information is None:
            self._information = {}
        else:
            self._information = initial_information

    def update_information(self, information: dict):
        pass


class TableMonitor(Monitor):  # Displays information in a key-value table
    def __init__(self, master: Misc, initial_information: dict = None):
        super().__init__(master, initial_information)
        self.title = Title(self, "Monitor")

        self.title.pack(**title_packing)
        self.table = self.Table(self, initial_information)
        self.table.pack(expand=True, fill="both")

    class Table(Frame):
        def __init__(self, master: Misc, info: dict = None):
            super().__init__(master)
            self.rows = []

            if info is not None:
                for key, value in info.items():
                    self.assign(key, value)

        def assign(self, key, value):
            snake_key = to_snake_case(key)
            for row in self.rows:
                if to_snake_case(row.label_key.cget("text")) == snake_key:
                    row.label_value.config(text=value)
                    break
            else:
                new_row = InfoPair(self, to_readable(snake_key), value)
                self.rows.append(new_row)
                new_row.pack(side="top", anchor="n", expand=False, fill="x", padx=theme["standard_margin"])

    def update_information(self, information: dict):
        for key, value in information.items():
            self.table.assign(key, value)


class VisualMonitor(Monitor):  # Displays information in a graphic
    def __init__(self, master: Misc, initial_information: dict = None):
        super().__init__(master, initial_information)
        self.title = Title(self, "Visualizer")
        self.title.pack(**title_packing)
        self.bridge_display = BridgeDisplay(self, 0.0)
        self.bridge_display.pack(expand=True, fill="both")

    def update_information(self, information: dict):
        expected_position_key = "current_position"
        if expected_position_key in information.keys():
            self.bridge_display.set_position(information[expected_position_key])


class HistoryMonitor(Monitor):  # Adds to a log every time information is updated
    def __init__(self, master: Misc, initial_information: dict = None):
        super().__init__(master, initial_information)
        self.title = Title(self, "History")
        self.title.pack(**title_packing)
        self.listbox = Listbox(self, background=theme["primary_color"], foreground=theme["secondary_color"],
                               selectbackground=theme["secondary_color"], selectforeground=theme["primary_color"],
                               highlightbackground=theme["tertiary_color"], highlightcolor=theme["tertiary_color"],
                               font=(theme["standard_typeface"], theme["standard_font_size"]))
        self.listbox.pack(expand=True, fill="both")

    def insert(self, string: str):
        self.listbox.insert(END, string)
        self.listbox.see(END)

    def update_information(self, information: dict):
        current_time = now()

        for key, value in information.items():
            string = f"({current_time}) \"{to_readable(key)}\" updated to \"{value}\""
            self.insert(string)
