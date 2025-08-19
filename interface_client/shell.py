# shell.py
# A rudimentary user interface for the remote interface
# Users provide a method name and keyword arguments in Python syntax

from shlex import split as tokenize 

from remote_interface import RemoteInterface

host = "192.168.4.1"  # ESP32 default WiFi server host
port = 55555  # I have selected 55555 because it is easy to remember

ri = RemoteInterface(host, port)


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
        info_string += "-" * longest_key_length - len(key)

        info_string + "-" * minimum_margin
        
        info_string += "> " + value
        print(info_string)    


while True:
    user_input = input("> ")
    command_name, kwargs = parse_input(user_input)

    if command_name.lower() in ["quit", "exit", "logout"]:
        break
    
    response = ri.execute(command_name.lower(), **kwargs)
    print(response)
    if not "response" in response.keys(): 
        continue

    response_type = response["response"]
    if response_type == "ERR":
        print(f"Error: {response["error_message"]}")
    
    elif response_type == "DATA":
        print_payload(response["payload"])

