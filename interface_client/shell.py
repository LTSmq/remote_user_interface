import json

from remote_interface import RemoteInterface

host = "192.168.4.1"  # ESP32 default WiFi server host
port = 55555  # I have selected 55555 because it is easy to remember

ri = RemoteInterface(host, port)

recognised_commands: dict[str, dict[str, type]] = {
    "ping": {},
    "simulate_error": {},
    "sum": {"a": float, "b": float},
    "set_pin_output": {"pin_number": int, "high": bool},
}


def preparse_args(arguments: list[str]) -> list:
    preparsed_arguments = []

    semantically_true = ["true", "t", "yes", "y", "high", "h"]
    semantically_false = ["false", "f", "no", "n", "low", "l"]

    for argument in arguments:
        if argument.lower() in semantically_true:
            preparsed_arguments.append(True)
        elif argument.lower() in semantically_false:
            preparsed_arguments.append(False)
        else:
            try:
                preparsed_arguments.append(float(argument))
            except ValueError:
                preparsed_arguments.append(argument)
    
    return preparsed_arguments


IN_LOOP = True
while IN_LOOP:
    command_string = input("> ")
    tokens = command_string.split(" ")

    command_name = tokens[0]

    if command_name == "quit":
        ri.quit()
        break
        
    if command_name not in recognised_commands:
        print(f"Unrecognised command: {command_name}")
        continue
    
    provided_arguments = tokens[1:]
    provided_arguments = preparse_args(provided_arguments)
    provided_argument_count = len(provided_arguments)

    required_arguments = recognised_commands[command_name]
    required_argument_count = len(required_arguments)

    if provided_argument_count < required_argument_count:
        print(f"'{command_name}' requires {required_argument_count} argument(s) but only {provided_argument_count} provided")
        continue
    
    kwargs = {}
    invalid_arguments = False

    for argument_name, provided_value, expected_type in zip(required_arguments.keys(), provided_arguments, required_arguments.values()):
        if provided_value is not expected_type:
            invalid_arguments = True
            break
        
        kwargs[argument_name] = provided_arguments
    
    if invalid_arguments:
        continue
    
    ri.execute(command_name, **kwargs)

