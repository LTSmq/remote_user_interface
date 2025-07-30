from controller_simulation import ControllerSimulation
from remote_interface import RemoteInterface

HOST = "127.0.0.1"
PORT = 55555
WELCOME_MESSAGE = (
    "Welcome to the program that can operate the bridge remotely"
)

server_simulation = ControllerSimulation(HOST, PORT)

ri = RemoteInterface(HOST, PORT)

command_register = {
    "fetch": ri.fetch,
    "setsysp": ri.set_system_property,
    "stp": ri.set_target_position,
}

print(WELCOME_MESSAGE)
IN_LOOP = True
while IN_LOOP:
    instruction = input("> ")

    instruction_parts = instruction.split(" ", 1)
    command = instruction_parts[0].lower()
    argument = instruction_parts[1] if len(instruction_parts) > 1 else ""

    if command == "quit":
        break

    if command not in command_register.keys():
        print(f"Command not found: {command}")
        continue

    # This currently assumes the user is correctly formatting the input arguments
    if argument == "":
        command_register[command]()
    else:
        command_register[command](argument)

    print(ri.get_last_result())
