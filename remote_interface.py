# remote_interface.py
import socket
import json

BUFFER_SIZE = 2048


class RemoteInterface:
    _response: str
    def __init__(self, host: str, port: int):
        self._socket = socket.socket()
        self._socket.connect((host, port))
        self._result = "..."

    def get_last_result(self) -> str:
        return self._result

    def _intercom(self, message: str) -> str:
        self._socket.send(message.encode())
        return self._socket.recv(BUFFER_SIZE).decode()


    def set_system_property(self, argument: str) -> bool:
        response = self._intercom(f"setsysp {argument}")

        return response.upper() == "OK"


    def fetch(self, info_label: str = "*") -> dict:
        info_string = self._intercom(f"fetch {info_label}")

        if info_string.startswith("ERR"):
            self._result = info_string
            return {}

        try:
            info = json.loads(info_string)
            self._result = json.dumps(info, indent=2)
            return info
        except json.decoder.JSONDecodeError:
            self._result = info_string
            return {}


    def set_target_position(self, position) -> bool:
        try:
            value = float(position)
            value = max(0.0, min(1.0, value))

            position_set = self.set_system_property(f"motor target_position {str(value)}")
            if position_set:
                self._result = f"Target position set to {value}"
            else:
                self._result = f"Controller refused to set motor target position to {value}"

        except ValueError:
            self._result = f"Invalid position: {position}"


