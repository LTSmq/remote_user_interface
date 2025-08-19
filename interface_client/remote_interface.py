# remote_interface.py
import socket
import json

BUFFER_SIZE = 4096


class RemoteInterface:
    def __init__(self, host: str, port: int, dummy: bool = False):
        # Connect to given host/port
        self._dummy = dummy
        if not dummy:
            self._socket = socket.socket()
            self._socket.connect((host, port))

    def execute(self, command_name: str, **kwargs) -> dict:
        if self._dummy:
            return { "response": "OK" }
        
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

    def quit(self):
        self._socket.disconnect()
