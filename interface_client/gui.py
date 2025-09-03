from datetime import datetime

from tkinter import *
from tkinter.ttk import *

from remote_interface import RemoteInterfaceHeader, RemoteInterface
from simulation import SimulatedInterface
import bridge_drawer

SYNC_TIME = 50  # milliseconds
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

primary_color = "black"
secondary_color = "lime"
tertiary_color = "lime"

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
    "TButton": {
        "background": secondary_color,
        "foreground": primary_color,
        "focuscolor": tertiary_color,
        "highlightcolor": primary_color,
        "bordercolor": primary_color,
        "font": (typeface, 12),
    },
}


def now() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")

class InfoPair(Frame):
    def __init__(self, master: Misc, key, value):
        super().__init__(master)

        self.key_label = Label(self, justify="left", style="content.TLabel")
        self.value_label = Label(self, justify="right", style="content.TLabel")

        self.key_label.pack(side="left", expand=False)
        self.value_label.pack(side="right", expand=False)

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
        val = str(new_value)
        if type(new_value) is float:
            val = str(round(new_value, 1))
        self.value_label.config(text=val)
        self._value = new_value


class Table(Frame):
    def __init__(self, master: Misc, data: dict):
        super().__init__(master)
        self._rows = []

        for data_title, datum in data.items():
            row = InfoPair(self, data_title, datum)
            self._rows.append(row)
            row.pack(side="top", expand=True, fill='x')

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
        for key, value in info.items():
            self.table.update_value(key, value)


class MonitorDisplay(Frame):
    def __init__(self, master: Misc):
        self.width = 512
        self.height = 512
        super().__init__(master, width=self.width, height=self.height)

        title = Label(self, text="Visualizer", justify='center', style="title.TLabel")
        title.pack(side='top', expand=False, fill='y')

        self.canvas = Canvas(self, width=self.width, height=self.height, bg=primary_color,
                            highlightbackground=secondary_color)
        self.canvas.pack(side='top', expand=True)

        self.update_info({"position": 0.0})

    def update_info(self, info: dict) -> None:
        position = 0.0
        if "position" in info.keys():
            try:
                position = float(info["position"])
            except ValueError:
                return
        else:
            return
        bridge_drawer.primary_color = primary_color
        bridge_drawer.secondary_color = tertiary_color

        bridge_drawer.draw_bridge(self.canvas, position)


class HistoryPanel(Frame):
    def __init__(self, master: Misc):
        super().__init__(master)

        title = Label(self, text="History", justify='center', style="title.TLabel")
        title.pack(side='top')

        self.listbox = Listbox(self, background=primary_color, bg=primary_color, fg=secondary_color,
                               selectbackground=secondary_color, selectforeground=primary_color, font=(typeface, 10),
                               highlightbackground=tertiary_color, highlightcolor=tertiary_color)
        self.listbox.configure(width=64)

        self.listbox.pack(side="top")

    def update_info(self, info: dict) -> None:
        if "event" not in info.keys():
            return

        event = info["event"]

        self.listbox.insert(END,f"{now()} - {str(event)}")
        self.listbox.see(END)


class ControlPanel(Frame):
    def __init__(self, master: Misc):
        super().__init__(master)

        animation_button_container = Frame(self)
        animation_title = Label(animation_button_container, text="Bridge Animation", style="content.TLabel")

        self.raise_button = Button(animation_button_container, text="Raise Bridge")
        self.lower_button = Button(animation_button_container, text="Lower Bridge")

        animation_title.pack(side="top")

        for button in [self.raise_button, self.lower_button]:
            button.pack(side="left", expand=True, fill="y")

        lights_button_container = Frame(self)

        self.go_button = Button(lights_button_container, text="GO")
        self.yield_button = Button(lights_button_container, text="YIELD")
        self.stop_button = Button(lights_button_container, text="STOP")

        lights_title = Label(lights_button_container, text="Traffic Light Control", style="content.TLabel")

        for button in [lights_title, self.go_button, self.yield_button, self.stop_button]:
            button.pack(side="top", expand=True, fill="x")

        for container in [animation_button_container, lights_button_container]:
            container.pack(side="top", expand=True, fill='x')


class OverridePanel(Frame):
    def __init__(self, master: Misc):
        super().__init__(master)

        title = Label(self, text="Overrides", justify='center', style="title.TLabel")

        check_panel = Frame(self)
        self.check_panel_status = InfoPair(check_panel, "system_control", "AUTOMATIC")
        self.enable_override_button = Button(check_panel, text="Enable Overrides")
        self.disable_override_button = Button(check_panel, text="Disable Overrides")

        self.control_panel = ControlPanel(self)

        for content in [title, self.check_panel_status,self.enable_override_button,
                        self.disable_override_button, check_panel]:
            content.pack(side="top", expand=True, fill='x')


class BridgeControllerGUI(Tk):
    def __init__(self, interface: RemoteInterfaceHeader, title: str = "Bridge Controller GUI",
                 icon_path: str = ""):
        super().__init__()

        self.interface = interface
        self.interface.update_receiver = self._update_info

        style = Style()
        style.theme_use("clam")
        for style_name, kwargs in widget_styles.items():
            style.configure(style_name, **kwargs)

        self.configure(background=primary_color)

        self.title(title)
        if icon_path != "":
            self.iconbitmap(icon_path)

        self._build()
        self._update_info({"position": 0.0})
        self._refresh()

    def _update_info(self, information: dict) -> None:
        for subscriber in self.info_subscribers:
            subscriber.update_info(information)

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
        self._bind_override_panel(self.override_panel)
        self.override_panel.grid(sticky="nsew")

        for column in columns.values():
            column.pack(side="left", expand=True, fill="y")

    def _bind_override_panel(self, panel: OverridePanel) -> None:
        cpl = panel.control_panel

        binds = {
            cpl.raise_button:   self.raise_bridge,
            cpl.lower_button:   self.lower_bridge,

            cpl.go_button:      self.lights_go,
            cpl.yield_button:   self.lights_yield,
            cpl.stop_button:    self.lights_stop,

            panel.enable_override_button:   self.enable_overrides,
            panel.disable_override_button:  self.disable_overrides,
        }

        for button, method in binds.items():
            button.configure(command=method)

    def raise_bridge(self) -> None:
        self.set_bridge_position(1.0)

    def lower_bridge(self) -> None:
        self.set_bridge_position(0.0)

    def set_bridge_position(self, position: float) -> None:
        if self.override_panel.check_panel_status.value.upper() == "AUTOMATIC":
            return
        self.interface.execute("set_bridge_position", position=position)

    def lights_go(self):
        self.set_lights("GO")

    def lights_yield(self):
        self.set_lights("YIELD")

    def lights_stop(self):
        self.set_lights("STOP")

    def set_lights(self, code: str):
        if self.override_panel.check_panel_status.value.upper() == "AUTOMATIC":
            return
        self.interface.execute("set_light_condition", light_condition=code)

    def enable_overrides(self):
        self.interface.execute("set_overrides", enabled=True)

        self.override_panel.check_panel_status.value = "MANUAL"
        self.override_panel.control_panel.pack(side="top")

    def disable_overrides(self):
        self.interface.execute("set_overrides", enabled=False)
        self.override_panel.check_panel_status.value = "AUTOMATIC"
        self.override_panel.control_panel.forget()

    def sync_bridge_state(self):
        position_info = self.interface.execute("get_bridge_position")

        self._update_info(position_info["payload"])

    def sync_lights_condition(self):
        lights_info = self.interface.execute("get_light_condition")

        self._update_info(lights_info["payload"])

    @property
    def info_subscribers(self) -> list:
        return [self.monitor_panel, self.visual_monitor, self.history_panel]

    def _refresh(self) -> None:
        self.sync_bridge_state()
        self.sync_lights_condition()
        self.after(SYNC_TIME , self._refresh)

if __name__ == "__main__":
    ri: RemoteInterfaceHeader
    ri = SimulatedInterface()

    gui = BridgeControllerGUI(ri, icon_path="graphics/icon.ico")

    gui.minsize(1024, 786)

    gui.mainloop()

    ri.quit()
