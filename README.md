# Remote User Interface
This repository concerns the remote user interface system for the bridge controller. One folder `interface_client` concerns the means to send commands to the microcontroller from a remote client
i.e. is the actual remote user interface. The other folder `esp32_server` concerns the onboard receiver module for the ESP32 such that it can easilly receive and interpret commands. This system does not implement any business logic required for the bridge project, only provides a system to communicate commands between a remote user (such as via a nearby laptop) and the ESP32 microcontroller; It does not define any commands and expects users to implement the command responses as required. 

### How to use the remote interface example
The folder `esp32_server` contains an Arduino sketch dependant on the other files in the folder. With this sketch uploaded to an ESP32, it will open an access point (WiFi hotspot).
Users connect to this hotspot with their device running the Python script `shell.py` found in the inteface folder; if connected to the access point, the shell script should automatically connect
and begin accepting input from the user. 
<br> 
The command system accepts any command with any arbitrary amount of named arguments. The shell expects the first word of the input string to be the name of the command being called.
After the name, any number of arguments can be specified using the equals sign `=` for key-value pairing and a space between arguments to delimit them.
For instance, using the sum command to find the sum of 1 and 2 looks like `> sum a=1 b=2`.
<br>
The example sketch currently only contains 2 valid commands `ping` and `sum`, but the design enables more commands to be added easily for the product. 

## API
The two components of the client-server model have distinct programming interfaces; the client Python and the server in C++. <br>
To install the remote interface Python script, simply pull `remote_interface.py` into your project. <br>
To install the ESP server script, place `commander.h` and `commander.cpp` into your Arduino sketch folder. This module will also require `<ArduinoJson>` to be installed to the Arduino IDE, which can be done via the library manager. <br> 
### Client
`remote_interface.py` contains the class `RemoteInterface`. It is constructed by `RemoteInterface(host: str = "192.168.4.1", port: int = 55555, dummy: bool = false)`
  - `host: str` is the host IPv4 address. This is usually default WiFi access point address `"192.168.4.1"`.
  - `port: int` is the port for the host. The default port is `55555`.
  - `dummy: bool` signifies if the interface should be a dummy for testing; when `true`, it will not establish a connection and respond `OK` to all requests.

The class contains 2 methods
 - `RemoteInterface.execute(command_name: str, **kwargs) -> dict` - sends the command with provided name to the host (esp32) as well as other keyword arguments provided. Returns a dictionary value representing the host's response; the response type (string) is stored under key `"response"` e.g. `response["response"]`. There are 3 expected response codes: `OK`, `ERR` and `DATA`
   - `OK` indicates the command was received and acknowledged.
   - `ERR` indicates the command did not process correctly; the dictionary should contain information about the error under the key `"error_message"` e.g. `response["error_message"]`.
   - `DATA` indicates the command was received and acknowledged and has provided data in response. The data exists as a nested dictionary within the response dictionary under the key `"payload"` e.g. `response["payload"]`.

Examples: `remote_interface.execute("set_lights", enabled=True)`, `remote_interface.execute("set_position", position=0.5)`, `remote_interface.execute("poll")`

 - `RemoteInterface.quit()` - disconnects the interface from the host

### Server
In Arduino IDE sketches, this module is dependant on `<ArduinoJson>` to parse / format commands as JSON strings for communications between the two modules.
The server is given a receiver module titled "Commander" as declared in header `commander.h` and implemented in `commander.cpp`. Documentation of this module can also be read in the comments in `commander.h`. This module contains 3 class definitions:
 - `Command` represents a command received by the host. It may also represent that, when fetching for a the next command, the command is invalid
   - `bool Command::valid()`: returns `true` if the command is valid, `false` otherwise
   - `const char* Command::name()`: returns name of the command as a string
   - `bool Command::has_argument<T>(const char* argument_name)`: returns `true` if the command has an argument of given name and type `T`, `false` otherwise
   - `T Command::argument_value<T>(const char* argument_name, T default_value)`: returns the value of the argument of given name and type `T` if it exists, or the value of the given default otherwise

- `DataPayload` represents a data packet to be sent back to the client as per their request.
  - `DataPayload()` creates a new empty instance.
  - `void DataPayload::add_value<T>(const char* label, T value)`: adds a value to the payload under the given label with given value of provided type `T`. `T` should be a `bool`, a C integer type (`char`, `short`, `int`, `long`), a C real type (`float`, `double`), or a C string type (`const char*`).
  - `void DataPayload::add_payload(const char* label, DataPayload payload)`: adds a nested payload under the given label.

- `Commander` represents the host connection to the client that automatically parses the received messages into `Command` instances
  - `void Commander::bootup(const char* ssid, const char* password)`: starts the WiFi access point and server with given SSID and password
  - `void Commander::shutdown()`: disables the WiFi access point and server
  - `Command Commander::get_next_command()`: returns the next command in queue; will be an invalid commmand instance if no new commands have been provided since last check.
  - `bool Commander::reply_OK()`: acknowledges the client's last sent command. Returns `true` if the reply was sent successfully, `false` otherwise. Use `Commander::reply_DATA` instead if the command is one that requests information
  - `bool Commander::reply_ERR(const char* error_message)`: notifies the client that the last fetched command could not be fufilled; reason for failure should be provided in the `error_message` parameter. Returns `true` if the reply was sent successfully, `false` otherwise.
  - `bool Commander::reply_DATA(DataPayload data_payload)`: acknowledges the client's last sent command and sends data packed in `data_payload`.
