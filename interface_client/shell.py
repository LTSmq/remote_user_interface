# shell.py
# A rudimentary user interface for the remote interface
# Users provide a method name and keyword arguments in Python syntax

from shlex import split as tokenize
from tkinter import Tk, Listbox, END
from threading import Thread

from interface_client.remote_interface import error_code
from remote_interface import RemoteInterface

UPDATE_WINDOW_SIZE = 786, 786

class UpdateWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("Bridge Updates")
        self.iconbitmap("graphics/icon.ico")
        self.minsize(*UPDATE_WINDOW_SIZE)

        self.listbox = Listbox(highlightcolor="white", background="black", foreground="white",
                               font=("Consolas", 16))
        self.listbox.pack(expand=True, fill="both")

    def display_update(self, information: dict):
        self.listbox.insert(END, str(information))
        self.listbox.see(END)


def parse_input(user_input: str):
    spaced_signs = [" =", "= ", "  "]
    for spaced_sign in spaced_signs:
        while spaced_sign in user_input:
            user_input = user_input.replace(spaced_sign, spaced_sign.replace(" ", ""))

    tokens = tokenize(user_input)
    if not tokens:
        return None, {}

    command = tokens[0]
    kwargs = {}

    for token in tokens[1:]:
        if '=' in token:
            key, value = token.split('=', 1)
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.lower() in ["high", "on"]:
                value = 1
            elif value.lower() in ["low", "off"]:
                value = 0
            elif value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            kwargs[key] = value
        else:
            print(f"Warning: ignoring invalid token '{token}' (no '=')")

    return command, kwargs


def print_payload(payload: dict):
    if payload is None:
        payload = {}

    minimum_margin = 8

    keys = []
    values = []

    longest_key_length = 0

    for key, value in payload.items():
        key_str = str(key)
        value_str = str(value)

        if len(key_str) > longest_key_length:
            longest_key_length = len(key_str)
    
        keys.append(key_str)
        values.append(value_str)
    
    for key, value in zip(keys, values):
        info_string = key + " "
        info_string += "-" * (longest_key_length - len(key))

        info_string += "-" * minimum_margin
        
        info_string += "> " + value
        print(info_string)    


if __name__ == "__main__":
    ri = RemoteInterface()
    uw = UpdateWindow()

    ri.update_receiver = uw.display_update

    inputting = True
    def input_thread():
        while inputting:
            user_input = input("> ")
            command_name, kwargs = parse_input(user_input)

            if command_name.lower() in ["quit", "exit", "logout"]:
                break

            response = ri.execute(command_name.lower(), **kwargs)
            print(str(response))
            if not "response" in response.keys():
                continue
            response_type = response["response"]
            if response_type == "ERR":
                message = "UNSPECIFIED"
                for condition, code in error_code.items():
                    if code == response["error_code"]:
                        message = condition
                        break

                print(f"Error: {message}")

            elif response_type == "DATA":
                print_payload(response["payload"])
        uw.destroy()

    Thread(target=input_thread).start()
    uw.mainloop()
    inputting = False
    ri.quit()

