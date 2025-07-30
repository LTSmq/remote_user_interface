import json

from controller_simulation import ControllerSimulation
from remote_interface import RemoteInterface

# Load config
with open("config.JSON") as config_json_file:
    config = json.load(config_json_file)

if config["use_simulation"]:
    # Set to simulation mode if specified by config
    host = "127.0.0.1"
    port = 55555
    ControllerSimulation(host, port)
else:
    # Get port and host from user for production use
    host = input("Enter host address: ")
    port = input("Enter port: ")

# Create an interface instance
ri = RemoteInterface(host, port)

# List available commands
commands = [
    {
        "names": ["open", "open_bridge"],
        "function": lambda: ri.execute("open_bridge"),
    },
    {
        "names": ["close", "close_bridge"],
        "function": lambda: ri.execute("close_bridge"),
    },
    {
        "names": ["position", "set_position"],
        "function": lambda position: ri.execute("set_position", position=position)
    },
    {
        "names": ["bridge_state", "get_bridge_state", "gbs"],
        "function": lambda: ri.execute("get_bridge_state"),
    },
]

# Enter command-line loop
IN_LOOP = True
while IN_LOOP:
    # Get command input
    command_line = input("> ")

    # Split by token (space delimited)
    command_parts = command_line.split(" ")

    # Assume the first token is the command name
    command_name = command_parts[0]

    # Find a match
    for command in commands:
        if command_name in command["names"]:
            try:
                # Execute match
                print(command["function"](*command_parts[1:]))
            except TypeError:
                # Warn about invalid args
                print("Invalid arguments for command")
            break
    else:
        # Warn about invalid command
        print(f"Command not recognised: {command_name}")

