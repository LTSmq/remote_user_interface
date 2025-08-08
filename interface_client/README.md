# ENGG2000 / ENGG3000 Bridge Project: __Remote Interface__

## Overview
This project involves providing an interface to connect to the controller for the model bridge.
It does so using sockets to form a connection enabling back-and-forth communication between the interface and controller.
It expects to send and receive information using JSON strings. The core logic of this is contained within 
`remote_interface.py`, which serves as the terminal point of communcication. `shell.py` allows for a preset selection of 
commands to be executed via command line using the interface. `controller_simulator.py` is used to mimic what a controller
may respond with until a real controller module is provided.

<fnord>

## Features and Priorities
There are currently 3 tiers of functionalities to implement, with most critical (per meeting design specifications) first
and most superfluous last. 

### Priority 1
- [X] Provide socket connectivity between a remote controlling application and the bridge controller (Local Area Network)
- [X] Provide rudimentary user interface (command line)
- [ ] Allow users to view the status of the bridge; see if the bridge is set to open or close or in operation
- [ ] View the status of the operational subsystems (sensors, controls)
- [ ] Allow users to open or close the bridge

### Priority 2
- [ ] Allow users to manually control subsystems, such as the motor or barricade systems
- [ ] Provide automatic warnings/reconfirmations/refusals for unsafe operations, such as opening bridge without barricading
- [ ] Provide an emergency shutdown procedure

### Priority 3
- [ ] Provide a graphical user interface (GUI), such as a desktop app or webpage
- [ ] Provide a login system to restrict access to only authorised users
- [ ] Secure communications between interface and controller, such as with end-to-end encryption or transport layer security


## Controller Interfacing

The remote interface expects to send and receive messages between itself and the controller with a standardised messaging
format. This implementation follows a client-server model in which the remote interface acts as the client and the controller
the server; The controller should only produce information upon request rather than a continual datastream to the interface. 

In this implementation, the remote interface should expect messaging to be done in JSON. This helps to keep things simple,
structured and compatible. 

### Command format
The remote interface will send requests to the controller, either for fetching information or calling for functionality to
be executed. These requests are referred to as commands. The interface and controller systems should be in agreeance about 
which commands are valid, what they do and what additional arguments are possible/necessary. 
<br>
In JSON, the name of the command should be provided as the value of the key titled `"command"`. Any additional arguments
should be provided under additional keys named after the argument they represent. <br>
Example:
```JSON
[
  {"command": "open_bridge"},
  {"command": "get_bridge_state"},
  {"command": "set_bridge_position", "position": 0.5}
]
```

### Response format
The remote interface expects every command to be met with a response. There are 3 types of expected responses: `"OK"`, `"DATA"`,
`"ERR"`. The response type should be included in the JSON string sent back from the controller as the value of the key labelled
`"response"`.

#### OK Response
Response type `"OK"` indicates the command was received and processed successfully. No further information is required. 
<br>
Example:
```JSON
{"response": "OK"}
```

#### DATA Response
Response type `"DATA"` indicates the command was received and processed successfully, recognised as a request for information.
Responses with this type should include another key titled `"payload"`. Keep in mind multiple keys can be nested within JSON
values, so multiple values can be returned by `"payload"`
<br>
Example:
```JSON
[
  {"response": "DATA", "payload": true},
  {"response": "DATA", "payload": {"position": 0.5, "last_update_time": "2025-08-05::11:46:01"}}
]
```

### ERR Response
Response type `"ERR"` indicates the previous command encountered an error when executing. The reason for failing should be briefly
provided by the value of key `"error_message"`. 
<br>
Example:
```JSON
[
  {"response": "ERR", "error_message": "Command not recognised"},
  {"response": "ERR", "error_message": "Invalid arguments provided"},
  {"response": "ERR", "error_message": "Bridge motor offline"}
]
```
Additional error codes regarding the nature of the failure (bad input, service offline, refused for safety safeguards) are also
recommended in future development.
