# remote_interface.py
import socket
import json
import time
from datetime import datetime

BUFFER_SIZE = 4096


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d::%H:%M:%S.%f")


class RemoteInterface:
    def __init__(self, host: str = "192.168.4.1", port: int = 55555, simulation: bool = False):
        # Connect to given host/port
        self._simulation= simulation
        if simulation:
            self.bridge_position = 0.0
            self.bridge_target_position = self.bridge_position
            self.bridge_motion_speed = 0.000001  # Per milisecond

            self.logs = [now() + " - Connection Established"]

        else:
            self._socket = socket.socket()
            self._socket.connect((host, port))


    def execute(self, command_name: str, **kwargs) -> dict:
        if self._simulation:
            return self.simulation_execute(command_name, **kwargs)
        
        # Load command into JSON format
        command = json.dumps({"command": command_name, "kwargs": {**kwargs}}) + "\n"

        # Dispatch command to server
        self._socket.send(command.encode())

        # Await response
        response = self._socket.recv(BUFFER_SIZE)

        #Ensure response is valid dictionary JSON
        try:
            json_response = json.loads(response)
            if "response" not in json_response.keys():
                json_response["response"] = "ERR"
                json_response["error_message"] = ("Response type not provided by server; "
                                                  "defaulted to error")
            return json_response

        except json.JSONDecodeError:
            return {
                "response": "ERR",
                "error_message": "Unable to decode server response in JSON format",
                "source": response,
            }

    def simulated_status(self) -> str:
        if self.bridge_position == 0.0:
            return "IDLE"
        elif self.bridge_position == 1.0:
            return "RAISED"
        else:
            return "ACTIVE"

    def simulated_lights(self) -> str:
        if self.bridge_position==0.0 and self.bridge_target_position != 0.0:
            return "YIELD"
        elif self.bridge_position==0.0:
            return "GO"
        else:
            return "STOP"
    
    def simulation_execute(self, command_name: str, **kwargs) -> dict:
        if command_name == "poll":
            distance_covered = time.perf_counter() * self.bridge_motion_speed
            difference = self.bridge_target_position - self.bridge_position
            direction = 0
            if difference > 0.0:
                direction = 1
            elif difference < 0.0:
                direction = -1

            original_target_position = self.bridge_target_position

            self.bridge_position += distance_covered * direction
            if self.bridge_position < 0.0:
                self.bridge_position = 0.0
            elif self.bridge_position > 1.0:
                self.bridge_position = 1.0

            if self.bridge_position != original_target_position:
                if self.bridge_position == self.bridge_target_position:
                    self.logs.append(f"{now()} - Bridge target position reached")

            dump_logs = self.logs.copy()
            self.logs = []

            return {"response": "DATA", "payload": {
                "status": self.simulated_status(),
                "position": self.bridge_position,
                "lights": self.simulated_lights(),
                "logs": dump_logs,
            }}

        if command_name == "ping":
            return {"response": "OK"}

        if command_name == "set_bridge_position":
            self.bridge_target_position = kwargs["position"]
            self.logs.append(f"{now()} - Bridge target position set to {self.bridge_target_position}")
            return {"response": "OK"}

        return {"response": "ERR", "error_message": "Command not recognised"}

    def quit(self):
        if not self._simulation:
            self._socket.shutdown()
