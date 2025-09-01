from tkinter import *
from tkinter.ttk import *
from remote_interface import RemoteInterface

from math import sin

MARGIN = 10
REFRESH_RATE = 10  # milliseconds
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

primary_color = "black"
secondary_color = "lime"
typeface = "Courier New"

widget_styles = {
    "TFrame": {
        "background": primary_color,
        "foreground": secondary_color,
    },
    "title.TLabel": {
        "font": (typeface, 16),
        "background": secondary_color,
        "foreground": primary_color,
    },
    "content.TLabel": {
        "font": (typeface, 12),
        "background": primary_color,
        "foreground": secondary_color,
    },
    "TCheckbutton": {
        "background": primary_color,
        "foreground": secondary_color,
        "focuscolor": secondary_color,
    },
}

class InfoPair(Frame):
    def __init__(self, master: Misc, key, value):
        super().__init__(master)

        self.key_label = Label(self, justify="left", style="content.TLabel")
        self.value_label = Label(self, justify="right", style="content.TLabel")

        for label in [self.key_label, self.value_label]:
            label.pack(side="left", expand=True, fill='x')

        self.key = key
        self.value = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key):
        self.key_label.config(text=str(new_key).replace("_", " ").title() + ":")
        self._key = new_key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.value_label.config(text=str(new_value))
        self._value = new_value


class Table(Frame):
    def __init__(self, master: Misc, data: dict):
        super().__init__(master)
        self._rows = []

        for data_title, datum in data.items():
            row = InfoPair(self, data_title, datum)
            self._rows.append(row)
            row.pack(side="top")

    def update_value(self, key, value):
        for row in self._rows:
            if row.key == key:
                row.value = value
                return


class MonitorPanel(Frame):
    def __init__(self, master: Misc):
        super().__init__(master)

        title = Label(self, text="Monitor", justify='center', style="title.TLabel")
        title.pack(side='top')

        example_data = {
            "status": "IDLE",
            "position": 0.0,
            "lights": "GO",
        }

        self.table = Table(self, example_data)
        self.table.pack(side="top")

    def update_info(self, info: dict) -> None:
        pass


class MonitorDisplay(Frame):
    def __init__(self, master: Misc):
        self.width = 512
        self.height = 512
        super().__init__(master, width=self.width, height=self.height)

        title = Label(self, text="Visual Monitor", justify='center', style="title.TLabel")
        title.pack(side='top', expand=False, fill='y')

        self.canvas = Canvas(self, width=self.width, height=self.height, bg=primary_color,
                             highlightcolor=secondary_color, highlightbackground=secondary_color)
        self.canvas.pack(side='top', expand=True)

        self.update_info({"position": 0.0})

    def update_info(self, info: dict) -> None:
        self.canvas.delete("all")

        scale = 0.9
        thickness = 5
        abutment_size = 0.7
        altitude_domain = 0.7
        position = 0.0

        if "position" in info.keys():
            try:
                position = float(info["position"])
            except ValueError:
                pass

        for direction in [1, -1]:
            x = int(direction * scale * self.width * abutment_size / 2) + self.width / 2.0
            y1 = int((1.0 - scale) * self.height)
            y2 = int(scale * self.height)
            self.canvas.create_line(x,y1,x,y2, width=thickness, fill=secondary_color)
        y = self.height / 2.0
        y += (self.height * 0.5 * altitude_domain) * (1.0 - (2.0 * position))
        y = int(y)
        x1 = int((1.0 - scale) * self.width)
        x2 = int(scale * self.width)

        self.canvas.create_line(x1,y,x2,y, width=thickness, fill=secondary_color)


class HistoryPanel(Frame):
    def __init__(self, master: Misc):
        super().__init__(master)

        title = Label(self, text="History", justify='center', style="title.TLabel")
        title.pack(side='top')

        self.listbox = Listbox(self, background=primary_color, borderwidth=0, bg=primary_color, fg=secondary_color,
                               selectbackground=secondary_color, selectforeground=primary_color, font=(typeface, 10),
                               highlightbackground=secondary_color)
        self.listbox.configure(width=96)

        example_logs = [
            "2025-09-19::13:03 - Bridge started closing",
            "2025-09-19::13:06 - Bridge finished closing",
            "2025-09-19::13:10 - New vehicle in waterway detected",
        ]

        self.listbox.insert(END, *example_logs)

        self.listbox.pack(side="top")

    def update_info(self, info: dict) -> None:
        pass


class OverridePanel(Frame):
    def __init__(self, master: Misc):
        super().__init__(master)

        title = Label(self, text="Overrides", justify='center', style="title.TLabel")
        title.pack(side='top')

        self._override_enabled = False
        self.checkbox = Checkbutton(self, style="TCheckbutton", state="OFF")
        self.checkbox.pack(side="top")

    def set_bridge_position(self, position: float) -> None:
        pass


class BridgeControllerGUI(Tk):
    def __init__(self, interface: RemoteInterface, title: str = "Bridge Controller GUI",
                 icon_path: str = ""):
        super().__init__()

        self.interface = interface

        style = Style()
        for style_name, kwargs in widget_styles.items():
            style.configure(style_name, **kwargs)

        self.configure(background=primary_color)

        self.title(title)
        if icon_path != "":
            self.iconbitmap(icon_path)

        self._build()
        self._refresh()

    def _build(self) -> None:
        column_names = ["monitor", "multi_display", "overrides"]
        columns = {}

        for i in range(len(column_names)):
            self.columnconfigure(i, weight=1)

        for column_name in column_names:
            columns[column_name] = Frame(self)

        columns["multi_display"].rowconfigure(0, weight=1)
        columns["multi_display"].rowconfigure(1, weight=1)

        self.monitor_panel = MonitorPanel(columns["monitor"])
        self.monitor_panel.grid(sticky='nsew')

        self.visual_monitor = MonitorDisplay(columns["multi_display"])
        self.visual_monitor.grid(row=0, sticky='nsew')

        self.history_panel = HistoryPanel(columns["multi_display"])
        self.history_panel.grid(row=1, sticky='nsew')

        self.override_panel = OverridePanel(columns["overrides"])
        self.override_panel.grid(sticky="nsew")

        for column in columns.values():
            column.pack(side="left", expand=True, fill="y")

    @property
    def info_subscribers(self) -> list:
        return [self.monitor_panel, self.visual_monitor, self.history_panel]

    def _refresh(self) -> None:
        response = self.interface.execute("poll")

        info = response.get("payload", {})

        for subscriber in self.info_subscribers:
            subscriber.update_info(info)

        self.after(REFRESH_RATE, self._refresh)


if __name__ == "__main__":
    ri = RemoteInterface(simulation=True)

    gui = BridgeControllerGUI(ri, icon_path="graphics/icon.ico")

    gui.minsize(1024, 786)

    gui.mainloop()

    ri.quit()
