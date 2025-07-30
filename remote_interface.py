# remote_interface.py
import socket
import json

BUFFER_SIZE = 4096


class RemoteInterface:
    def __init__(self, host: str, port: int):
        # Connect to given host/port
        self._socket = socket.socket()
        self._socket.connect((host, port))

    def execute(self, command_name: str, **kwargs) -> dict:
        # Load command into JSON format
        command = json.dumps({"command": command_name, **kwargs})

        # Dispatch command to server
        self._socket.send(command.encode())

        # Await response
        response = self._socket.recv(BUFFER_SIZE)

        #Ensure response is valid dictionary JSON
        try:
            return json.loads(response)

        except json.JSONDecodeError:
            return { "decoding_error": True } # Dummy error dictionary

