# control_panel.py
from tkinter.constants import HORIZONTAL

from common import *


class ControlPanel(Frame):
    def __init__(self, master: Misc, **kwargs):
        traffic_states = ["GO", "YIELD", "STOP"]
        traffic_systems = ["bridge", "waterway"]
        traffic_positions = ["a_side", "crossing", "b_side"]

        super().__init__(master, **kwargs)
        self.title = Title(self, "Control Panel")
        self.title.pack(**title_packing)

        control_packing = {"expand": True, "fill": "x"}

        self.override_panel = Frame(self)
        self.override_status = InfoPair(self.override_panel, "Override Mode", "Disabled")
        self.override_status.pack(**control_packing)

        override_modes = ["disabled", "input", "output"]
        self.override_buttons = {mode: Button(self.override_panel, text=mode.title()) for mode in override_modes}
        for button in self.override_buttons.values():
            button.pack(side="left", **control_packing)
        self.override_panel.pack(side="top", fill="x", padx=theme["standard_margin"])

        self.output_panel = Frame(self)
        output_panel_label = Label(self.output_panel, text="Output Control")
        output_panel_label.pack(**control_packing)

        bridge_position_panel = Frame(self.output_panel)
        bridge_position_label = Label(bridge_position_panel, text="Bridge Position")
        bridge_position_label.pack(**control_packing)
        bridge_slider_panel = Frame(bridge_position_panel)

        self.bridge_position_control = Scale(bridge_slider_panel, from_=0.0, to=1.0, orient=HORIZONTAL)

        Label(bridge_slider_panel, text="LOWERED").pack(side="left")
        self.bridge_position_control.pack(side="left", expand=True, fill="x", padx=theme["standard_margin"])
        Label(bridge_slider_panel, text="RAISED").pack(side="left")

        bridge_slider_panel.pack(**control_packing)
        bridge_position_panel.pack(**control_packing, pady=theme["standard_margin"])

        traffic_control_panel = Frame(self.output_panel)
        traffic_control_label = Label(traffic_control_panel, text="Traffic Control")
        traffic_control_label.pack(**control_packing)

        traffic_button_panel = Frame(traffic_control_panel)

        traffic_system_labels = [Label(traffic_button_panel, text=system.title(), justify="center") for system in traffic_systems]
        self.output_traffic_buttons = {
            system: {state: Button(traffic_button_panel, text=state) for state in traffic_states}
            for system in traffic_systems
        }

        button_list = []
        for button_dict, system_label in zip(self.output_traffic_buttons.values(), traffic_system_labels):
            button_list.append(system_label)
            for button in button_dict.values():
                button_list.append(button)

        row = 0
        column = 0
        for element in button_list:
            element.grid(row=row, column=column, sticky='nsew')
            row += 1
            if row > len(traffic_states):
                row = 0
                column += 1

        [traffic_button_panel.columnconfigure(i, weight=1) for i in range(column)]
        [traffic_button_panel.rowconfigure(i, weight=1) for i in range(row)]

        traffic_button_panel.pack(**control_packing)
        traffic_control_panel.pack(**control_packing, pady=theme["standard_margin"])

        self.input_panel = Frame(self)
        input_panel_label = Label(self.input_panel, text="Input Control")
        input_panel_label.pack(**control_packing)

        input_traffic_panel = Frame(self.input_panel)
        self.input_traffic_checks = {
            system: {position: Checkbutton(input_traffic_panel) for position in traffic_positions}
            for system in traffic_systems
        }
        Label(input_traffic_panel, text="Traffic Sensors").grid(row=0, column=0, sticky="ew")
        for i in range(len(traffic_systems)):
            Label(input_traffic_panel, text=to_readable(traffic_systems[i])).grid(row=0, column=i+1, sticky="ew")
        for i in range(len(traffic_positions)):
            Label(input_traffic_panel, text=to_readable(traffic_positions[i])).grid(row=i+1, column=0, sticky="ew")
        row = 1
        column = 1
        for _system, check_buttons in self.input_traffic_checks.items():
            for _position, check_button in check_buttons.items():
                check_button.grid(row=row, column=column, sticky="ew")
                column += 1
                if column - 1>= len(traffic_systems):
                    column = 1
                    row += 1

        [input_traffic_panel.columnconfigure(i, weight=1) for i in range(len(traffic_systems) + 1)]
        [input_traffic_panel.rowconfigure(i, weight=1) for i in range(len(traffic_positions) + 1)]

        input_traffic_panel.pack(fill="both", expand=True, pady=theme["standard_margin"])

        self.override_state = "disabled"


    @property
    def override_state(self) -> str:
        return self._override_state

    @override_state.setter
    def override_state(self, value: str):
        show = {
            "input": self.input_panel,
            "output": self.output_panel,
        }

        for panel in show.values():
            panel.forget()

        self.override_status.label_value.config(text=value.title())

        for name, panel in show.items():
            if value == name:
                panel.pack(fill="x", padx=theme["standard_margin"], pady=theme["standard_margin"])
        self._override_state = value
