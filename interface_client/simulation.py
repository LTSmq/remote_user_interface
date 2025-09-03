import threading
from tabnanny import check
from time import perf_counter as check_timer
from time import sleep as wait
from random import random

from remote_interface import RemoteInterfaceHeader, UpdateReceiver, error_code

SIMULATION_TICK_TIME = 0.01
YIELD_PAUSE = 3.0
STOP_PAUSE = 2.0

def move_towards(current: float, target: float, amount: float):
    difference = target - current
    distance = abs(difference)
    if distance <= amount:
        return target
    return current + amount * (difference / distance)


def event_simulation(time: float, chance: float) -> int:
    resolution = 1000

    time *= resolution
    chance /= resolution

    occurrences  = 0

    for _ in range(round(time)):
        if random() <= chance:
            occurrences += 1

    return occurrences


def acknowledgement() -> dict:
    return {"response": "OK"}


def error(error_type: str) -> dict:
    return {"response": "ERR", "error_code": error_code[error_type]}


def data(payload: dict) -> dict:
    return {"resposne": "DATA", "payload": payload}

class SimulatedInterface(RemoteInterfaceHeader):
    def __init__(self, update_receiver: UpdateReceiver = None):
        super().__init__(update_receiver)
        self.receiving_updates = True

        self.bridge_position = 0.0
        self.bridge_target_position = 0.0
        self.bridge_speed = 0.2

        self.light_condition = "GO"

        self.overrides_enabled = False

        self._simulating = True
        simulation = threading.Thread(target=self._simulate)
        simulation.start()

    def execute(self, command_name: str, **kwargs) -> dict:
        if command_name == "ping":
            return acknowledgement()

        if command_name == "set_bridge_position":
            if not self.overrides_enabled:
                return error("PERMISSION_DENIED")

            if "position" not in kwargs.keys():
                return error("INVALID_ARGS")
            try:
                self.bridge_target_position = float(kwargs["position"])
                self._send_update({"event": f"Bridge target position set to {self.bridge_target_position}"})
                return acknowledgement()
            except ValueError:
                return error("INVALID_ARGS")

        if command_name == "get_bridge_position":
            return data({"position": self.bridge_position})

        if command_name == "get_light_condition":
            return data({"lights": self.light_condition})

        if command_name == "set_light_condition":
            if not self.overrides_enabled:
                return error("PERMISSION_DENIED")
            try:
                self.light_condition = kwargs["light_condition"]
            except ValueError:
                return error("INVALID_ARGS")

            return acknowledgement()

        if command_name == "set_overrides":
            try:
                self.overrides_enabled = bool(kwargs["enabled"])
            except ValueError:
                return error("INVALID_ARGS")

            return acknowledgement()

        return error("UNRECOGNISED")

    def quit(self):
        self._simulating = False

    def _simulate(self):
        last_time = 0.0
        while self._simulating:
            time = check_timer()
            self._simulate_frame(time - last_time)
            last_time = time
            wait(SIMULATION_TICK_TIME)

    def _simulate_frame(self, delta: float) -> None:
        self._simulate_bridge_movement(delta)

    def _simulate_bridge_movement(self, delta: float):
        if not self.overrides_enabled:
            if self.bridge_position == 0.0:
                self.light_condition = "GO"
            else:
                self.light_condition = "STOP"

        original_bridge_position = self.bridge_position

        self.bridge_position = move_towards(
            current=self.bridge_position,
            target=self.bridge_target_position,
            amount=self.bridge_speed * delta,
        )

        if self.bridge_position != original_bridge_position:
            if self.bridge_position == self.bridge_target_position:
                self._send_update({"event": "Bridge reached target position"})
