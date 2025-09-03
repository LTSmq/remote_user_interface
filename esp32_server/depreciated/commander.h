/**
 * commander.h
 * 
 * Provides an ESP32 system connectivity to a remote interface over a WiFi access point
 * 
*/

#ifndef COMMANDER_H
#define COMMANDER_H

#include <ArduinoJson.h>  // Made by Beniot Blachon; install this via the library manager in Arduino IDE
#include <WiFi.h>

#define STANDARD_WAIT_TIME 100  // milliseconds
#define PORT 55555
#define MAX_CLIENTS 1
#define DEFAULT_SSID "Bridge Controller 26"
#define DEFAULT_PASSWORD "password"
#define MESSAGE_DELIMITER '\n'
#define JSON_CAPACITY 256


// Command provides simplified access to a JSON-formatted command string
// It expects the command name to be under the key named "command"
// It expects any necessary arguments to be nested under the key "kwargs"
// e.g. Command( "{ "command": "sum", "kwargs": { "a": 1, "b": 2 } }" )
class Command {
public:
  // Produces a command by parsing the provided JSON string
  // Command will be invalid if the string is not in valid JSON syntax
  Command(const char* from_json_string);

  // Produces an invalid command
  Command();

  // Returns the name of the command if valid or an empty string if invalid
  const char* name();

  // Returns true if the command is valid and false if not
  bool valid();

  // Returns true if the command has an argument of given name and type, false otherwise
  template<typename ArgumentType>
  bool has_argument(const char* argument_name) {
    return json_object["kwargs"][argument_name].is<ArgumentType>();
  }

  // Returns the value of the argument with the given name and type if it is valid, returns the given default value otherwise
  template<typename ArgumentType>
  ArgumentType argument_value(const char* argument_name, ArgumentType default_value) {
    if (Command::has_argument<ArgumentType>(argument_name)) {
      return json_object["kwargs"][argument_name].as<ArgumentType>();
    }

    return default_value;
  }

private:
  // The JSON object being encapsulated
  StaticJsonDocument<JSON_CAPACITY> json_object;
};


// Class used for packing and returning data to the client
// Represents a JSON object, similar to Command
// See Commander::reply_DATA
class DataPayload {
public:
  // Creates an empty payload
  DataPayload();

  // Returns a JSON string corresponding to the values in the payload
  String as_json_string();

  template<typename DataType>
  void add_value(const char* label, DataType value) {
    json_object[label] = value;
  }

  // Adds a nested payload under the given label
  void add_payload(const char* label, DataPayload payload);

private:
  // The JSON object being encapsulated
  StaticJsonDocument<JSON_CAPACITY> json_object;
};


// Class that can form a connection to a remote interface and generate commands based
// on messages received from the interface
class Commander {
public:
  // Creates a new commander that requires `setup` to be called to function
  Commander();

  // Opens a WiFi access point and starts a server using given SSID and password
  void bootup(const char* ssid, const char* password);

  // Disables WiFi and server
  void shutdown();

  // Returns true if a remote interface is currently connected and false if not
  bool connected();

  // Primary function of commander
  // Dequeues and parses the next command sent from the remote interface
  // Command will be invalid if
  //      A. The remote interface sent an invalid JSON string
  //      B. The remote interface has not sent any new messages since last call
  //      C. No remote interface is connected
  Command get_next_command();

  // Note: One of the three reply functions should always be called after calling Commander::get_next_command

  // Sends an acknowledgement message back to the remote interface
  // Returns true if successfully sent or false if not
  bool reply_OK();

  // Sends an error message back to the remote interface including the argument
  // Returns true if successfully sent or false if not
  bool reply_ERR(const char* error_message);

  // Sends a data packet back to the remote interface with the contents of the given data payload
  // Returns true if successfully sent or false if not
  bool reply_DATA(DataPayload data_payload);

private:
  // The Arduino access point server
  WiFiServer server = WiFiServer(PORT, MAX_CLIENTS);

  // The currently connected client
  WiFiClient client;

  // Base reply function
  bool reply(DataPayload payload);
};

#endif  // COMMANDER_H