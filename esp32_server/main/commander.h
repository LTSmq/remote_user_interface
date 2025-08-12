/**
 * commander.h
 * 
 * Provides an ESP32 system connectivity to a remote interface over a WiFi access point
 * 
*/

#ifndef COMMANDER_H
#define COMMANDER_H

#include <WiFi.h>
#include <cJSON.h>

#define STANDARD_WAIT_TIME 100 // milliseconds
#define PORT 55555
#define MAX_CLIENTS 1
#define DEFAULT_SSID "Bridge Controller 26"
#define DEFAULT_PASSWORD "password"
#define MESSAGE_DELIMITER '\n'

// Used internally for categorizing data types
enum ArgType {
    INVALID,
    BOOL,
    NUMBER,
    STRING,
};


// Internal helper functions
ArgType cJSON_IdentifyArgType(cJSON *json_object, const char* key);
void cJSON_AddOrReplaceItem(cJSON *json_object, const char* key, cJSON* item);


// Command provides simplified access to a JSON-formatted command string
// It expects the command name to be under the key named "command"
// It expects any necessary arguments to be nested under the key "kwargs"
// e.g. Command( "{ "command": "sum", "kwargs": { "a": 1, "b": 2 } }" )
class Command {
public:
    // Produces a command by parsing the provided json string
    // Command will be invalid if the json string is invalid
    Command(const char* from_json_string);

    // Produces an invalid command
    Command();

    // Frees allocated memory
    ~Command();

    // Returns the name of the command if valid or an empty String if invalid
    String name();

    // Returns true if the command is valid and false if not
    bool valid();

    // Returns true of the command has an argument with the given name and false if not
    bool has_argument(const char* argument_name);

    // Returns true of the command has a boolean argument with the given name and false if not
    bool has_boolean_argument(const char* argument_name);

    // Returns true if the command has a number argument with the given name and false if not
    bool has_number_argument(const char* argument_name);

    // Returns true if the command has a number argument with the given name and false if not
    bool has_string_argument(const char* argument_name);

    // Returns the boolean value of the argument with the given name or the default value if the argument is not a valid bool
    bool argument_value_bool(const char* argument_name, bool default_value = false);

    // Returns the number (double) value of the argument with the given name or the default value if the argument is not a valid number
    double argument_value_number(const char* argument_name, double default_value = 0.0);

    // Returns the String value of the argument with the given name or the default value if the argument is not a valid String
    String argument_value_string(const char* argument_name, const char* default_value = "");
    
private:
    // Internally used JSON data structure
    cJSON* json_object;

    // Internally used function to get the arguments
    cJSON* kwargs();

};


// Class used for packing and returning data to the client
// Represents a JSON object, similar to Command
// See Commander::reply_DATA
class DataPayload {
public:
    // Creates an empty payload
    DataPayload();

    // Frees used memory
    ~DataPayload();

    // Returns a JSON string corresponding to the values in the payload
    String as_json_string();

    // Adds the given boolean value to the payload under the given label 
    void add_bool(const char* label, bool value);

    // Adds the given number value to the payload under the given label
    void add_number(const char* label, double value);

    // Adds the given string value to the payload under the given label
    void add_string(const char* label, const char* value);

    // Nests the given payload value under the calling payload under the given label
    void add_payload(const char* label, const DataPayload& payload);

private:
    // Internally used JSON data structure
    cJSON* json_object;
};


// Class that can form a connection to a remote interface and generate commands based
// on messages received from the interface
class Commander {
public:
    // Ensures WiFi system is off
    Commander();

    // Disables WiFi and server
    ~Commander();

    // Opens a WiFi access point and starts a server using given SSID and password
    void setup(const char* ssid, const char* password);

    // Opens a WiFi access point and starts a server using default SSID and password    
    void setup();

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
    bool reply_DATA(const DataPayload& data_payload);

private:
    // The Arduino access point server
    WiFiServer server = WiFiServer(PORT, MAX_CLIENTS);
    
    // The currently connected client
    WiFiClient client;

    // The flag for if the access point/server is currently online
    bool is_setup = false;

    // Base reply function
    bool reply(DataPayload payload);
};

#endif // COMMANDER_H
