# ENGG2000 / ENGG3000 Bridge Project: __Remote Interface__

## Overview
This project involves providing an interface to connect to the controller for the model bridge.
It does so using sockets to form a connection enabling back-and-forth communication between the interface and controller.
It expects to send and receive information using JSON strings. The core logic of this is contained within 
`remote_interface.py`, which serves as the terminal point of communcication. `shell.py` allows for a preset selection of 
commands to be executed via command line using the interface. `controller_simulator.py` is used to mimic what a controller
may respond with until a real controller module is provided.
<fnord>