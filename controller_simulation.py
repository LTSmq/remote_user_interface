import socket
import threading
import time
import json

REFRESH_TIME = 0.1
BUFFER_SIZE = 2048



class ControllerSimulation:
    def __init__(self, host: str, port: int) -> None:
        self._socket = socket.socket()
        self._socket.bind((host, port))

        self.systems = {  # Example systems
            "motor": {
                "status": "idle",
                "target_position": "0.0",
            },
            "laser": {
                "status": "active",
                "road_inbound_traffic": "5",
                "water_inbound_traffic": "1",
            },
            "barricade": {
                "status": "inactive",
            }
        }

        listener_thread = threading.Thread(target=self._listen_for_messages)
        listener_thread.start()


    def _listen_for_messages(self):
        self._socket.listen()
        connection, source_address = self._socket.accept()

        listening = True
        while listening:
            instruction = connection.recv(BUFFER_SIZE).decode()
            instruction_parts = instruction.split(" ", 1)
            command = instruction_parts[0]
            argument = instruction_parts[1] if len(instruction_parts) > 1 else ""

            if command == "setsysp":
                try:
                    system_name, system_property, value = argument.split(" ", 3)
                    if system_property in self.systems[system_name]:
                        self.systems[system_name][system_property] = value
                        connection.send("OK".encode())
                    else:
                        connection.send(f'ERR: "{system_name}" has no property "{system_property}"'.encode())
                except ValueError:
                    connection.send(f"ERR: Invalid argument for system override: {argument}".encode())

            elif command == "fetch":
                for system_name, system_properties in self.systems.items():
                    if system_name == argument:
                        system_dict = {"name": system_name, **system_properties}
                        response = json.dumps(system_dict)
                        connection.send(response.encode())
                        break
                else:
                    connection.send(f"ERR: System not found: {argument}".encode())
