# remote_interface.py
import socket
import json
import threading
from json import JSONDecodeError
from typing import Callable, Any

BUFFER_SIZE = 4096
COMMANDER_PORT = 55555
UPDATER_PORT = 55055

UpdateReceiver: type = Callable[[dict], Any]

error_code = {
    "DEBUG": -2,
    "UNSPECIFIED": -1,
    "UNRECOGNISED": 0,
    "INVALID_ARGS": 1,
    "NOT_FOUND": 2,
    "PERMISSION_DENIED": 3,
    "TIMEOUT": 4,
    "INTERNAL_ERROR": 5,
    "BAD_JSON": 6,
}


class RemoteInterfaceHeader:
    def __init__(self, update_receiver: UpdateReceiver = None):
        self.update_receiver = update_receiver
        self._receiving_updates = False

    def execute(self, command_name: str, **kwargs) -> dict:
        raise NotImplementedError("Execution method not defined")

    @property
    def receiving_updates(self) -> bool:
        return self._receiving_updates

    @receiving_updates.setter
    def receiving_updates(self, value: bool) -> None:
        self._receiving_updates = value

    @property
    def update_receiver(self) -> UpdateReceiver:
        return self._update_receiver

    @update_receiver.setter
    def update_receiver(self, value: UpdateReceiver):
        self._update_receiver = value

    def quit(self) -> None:
        raise NotImplementedError("Quit method not defined")

    def _send_update(self, information: dict) -> bool:
        if self.update_receiver is None:
            return False

        self.update_receiver(information)

        return True


class RemoteInterface(RemoteInterfaceHeader):
    def __init__(self, host: str = "192.168.4.1", update_receiver: UpdateReceiver = None):
        super().__init__(update_receiver)

        self._commander_socket = socket.socket()
        self._commander_socket.connect((host, COMMANDER_PORT))

        self._updater_socket = socket.socket()
        self._updater_socket.connect((host, UPDATER_PORT))

        self.receiving_updates = True

    def __del__(self) -> None:
        self._receiving_updates = False
        self._updater_socket.close()
        self._commander_socket.close()

    def execute(self, command_name: str, **kwargs) -> dict:
        # Load command into JSON format
        command = json.dumps({"command": command_name, "kwargs": {**kwargs}}) + "\n"

        # Dispatch command to server
        self._commander_socket.send(command.encode())

        # Await response
        response = self._commander_socket.recv(BUFFER_SIZE)

        #Ensure response is valid dictionary JSON
        try:
            json_response = json.loads(response)
            if "response" not in json_response.keys():
                json_response["response"] = "VOID"
            return json_response

        except json.JSONDecodeError:
            return {
                "response": "ERR",
                "error_code": error_code["BAD_JSON"],
                "source": response,
            }

    @RemoteInterfaceHeader.receiving_updates.setter
    def receiving_updates(self, value: bool) -> None:
        if value == self._receiving_updates:
            return

        self._receiving_updates = value
        if self._receiving_updates:
            updater_thread = threading.Thread(target=self._update_worker)
            updater_thread.start()

    def _update_worker(self) -> None:
        while self._receiving_updates:
            response = self._updater_socket.recv(BUFFER_SIZE)

            try:
                json_response = json.loads(response)
            except JSONDecodeError:
                continue

            self._send_update(json_response)
