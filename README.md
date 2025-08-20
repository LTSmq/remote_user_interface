# Remote User Interface
This repository concerns the remote user interface system for the bridge controller. One folder `interface_client` concerns the means to send commands to the microcontroller from a remote client
i.e. is the actual remote user interface. The other folder `esp32_server` concerns the onboard receiver module for the ESP32 such that it can easilly receive and interpret commands. 


### How to use the remote interface
The folder `esp32_server` contains an Arduino sketch dependant on the other files in the folder. With this sketch uploaded to an ESP32, it will open an access point (WiFi hotspot).
Users connect to this hotspot with their device running the Python script `shell.py` found in the inteface folder; if connected to the access point, the shell script should automatically connect
and begin accepting input from the user. 
<br> 
The command system accepts any command with any arbitrary amount of named arguments. The shell expects the first word of the input string to be the name of the command being called.
After the name, any number of arguments can be specified using the equals sign `=` for key-value pairing and a space between arguments to delimit them.
For instance, using the sum command to find the sum of 1 and 2 looks like `> sum a=1 b=2`.
<br>
The example sketch currently only contains 2 valid commands `ping` and `sum`, but the design enables more commands to be added easily for the product. 
