import socket
import json
import threading

BUFFER_SIZE = 4096

class ControllerSimulation:
    def __init__(self, host: str, port: int) -> None:
        self._socket = socket.socket()
        self._socket.bind((host, port))

        self._listening_thread = threading.Thread(target=self._listen_procedure)
        self._listening_thread.start()

        self.response = ""
        self.data = {
            "bridge_state": "CLOSED",
        }

    def get_commands(self) -> list:
        return [
            self.open_bridge,
            self.close_bridge,
            self.set_position,
            self.get_bridge_state,
        ]

    def _listen_procedure(self) -> None:
        self._socket.listen()
        connection, _source_address = self._socket.accept()

        command_registry = {}
        for method in self.get_commands():
            command_registry[method.__name__] = method

        receiving_messages = True
        while receiving_messages:
            message = connection.recv(BUFFER_SIZE).decode()
            try:
                command = json.loads(message)
                command_name = command["command"]
                if command_name in command_registry.keys():
                    del command["command"]
                    try:
                        self.response = {"response": "OK"}
                        command_registry[command_name](**command)
                    except TypeError:
                        self.response = {"response": "ERR", "error_message": f"Invalid arguments for command {command_name}"}
                else:
                    self.response = {"response": "ERR", "error_message": f"Command not found: {command_name}"}
            except json.JSONDecodeError:
                self.response = {"response": "ERR", "error_message": "Invalid command format"}

            connection.send(json.dumps(self.response).encode())

    # Below are some example functionalities the controller might have

    def open_bridge(self):
        # This is where the opening bridge logic would be implemented
        self.data["bridge_state"] = "OPENED"

    def close_bridge(self):
        # This is where the closing bridge logic would be implemented
        self.data["bridge_state"] = "CLOSED"

    def set_position(self, position: str) -> None:
        try:
            value = max(0.0, min(1.0, float(position)))
            match value:
                case 0.0:
                    self.data["bridge_state"] = "CLOSED"
                case 1.0:
                    self.data["bridge_state"] = "OPENED"
                case _:
                    self.data["bridge_state"] = "SUSPENDED"

            self.response = {"response": "OK"}
        except ValueError:
            self.response = {"response": "ERR", "error_message": f"Invalid brightness value: {position}"}

    def get_bridge_state(self) -> str:
        bridge_state = self.data["bridge_state"]
        self.response = {"response": "DATA", "payload": {"bridge_state": bridge_state}}
        return bridge_state
