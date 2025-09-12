from functools import partial
from typing import Callable

from remote_interface import RemoteInterfaceHeader, RemoteInterface
from simulation import SimulatedInterface
from host import Host

LIVE = 0
SIMULATED = 1

mode = SIMULATED


def bind(host: Host, binds: dict[str, Callable]):
    pass


def set_position(interface: RemoteInterfaceHeader, to: float):
    interface.execute("set_target_position", to=to)


if __name__ == "__main__":

    ri: RemoteInterfaceHeader = RemoteInterface() if mode == LIVE else SimulatedInterface()
    gui_host = Host()

    bindings: dict[str, Callable] = {

    }

    initial_updates = {
        "current_position": 0.0,
        "target_position": 0.0,
        "bridge_state": "GO",
        "waterway_state": "STOP",
    }
    gui_host.update_information(initial_updates)
    def set_position(to: float):
        gui_host.visual_monitor.bridge_display.target_position = float(to)
        gui_host.update_information({"target_position": to})

    gui_host.control_panel.bridge_position_control.config(command=set_position)

    def set_override_state(to: str):
        gui_host.control_panel.override_state = to
        ri.execute("set_overrides", to=["disabled", "input", "output"].index(to))

    for key, button in gui_host.control_panel.override_buttons.items():
        button.config(command=partial(set_override_state, key))

    def set_traffic_state(sys: str, st: str):
        gui_host.table_monitor.table.assign(f"{sys}_state", st)

    for system, buttons in gui_host.control_panel.output_traffic_buttons.items():
        for state, button in buttons.items():
            button.config(command=partial(set_traffic_state, system, state))
    gui_host.mainloop()
