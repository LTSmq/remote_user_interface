/**
 * main.cpp
 * An example main manager program that interfaces with the commander, and therefore the remote user interface
 * 
*/

#include "commander.h"
#include <Arduino.h>

#define SERIAL_BAUD 115200

Commander commander;


// Identifies command and executes, including responding to 
void handle_command(Command command) {
    String command_name = command.name();

    Serial.write(printf("Received command: %s\n", command_name));

    // Ping command responds with standard OK
    if (command_name.equals("ping")) {
        commander.reply_OK();
        Serial.write("Responeded to ping with acknowledgement\n");
        return;
    }
    
    // Simulate error always returns an error
    if (command_name.equals("simulate_error")) {
        commander.reply_ERR("An error was requested");
        Serial.write("Responded to simiulate_error with error response\n");
        return;
    }

    // Requires 2 number arguments "a" and "b"
    // Returns the sum of numbers or error message if numbers not provided
    if (command_name.equals("sum")){
        bool has_arguments = (
            command.has_number_argument("a")
            && command.has_number_argument("b")
        );

        if (has_arguments) {
            double sum = command.argument_value_number("a") + command.argument_value_number("b");
            DataPayload data_payload;
            data_payload.add_number("result", sum); 

            commander.reply_DATA(data_payload);
            Serial.write("Responded to sum with result\n");
        }
        else {
            commander.reply_ERR("Missing arguments");
            Serial.write("Responded to sum with error (missing arguments)\n");
        }
        return;
    }

    // Accepts 1 number value "pin_number" and 1 boolean value "high" 
    // Sets the given pin number to output mode and sets it to high if the "high" argument is true, else low (GPIO)
    if (command_name.equals("set_pin_output")) {
        bool has_arguments = (
            command.has_number_argument("pin_number")
            && command.has_boolean_argument("high")
        );

        if (!has_arguments) {
            commander.reply_ERR("Missing arguments");
            Serial.write("Responded to set_pin_output with error (missing arguments)\n");
            return;
        }

        uint8_t pin_number = static_cast<uint8_t>(command.argument_value_number("pin_number"));
        bool is_high = command.argument_value_bool("high");

        uint8_t voltage = is_high ? HIGH : LOW;

        pinMode(pin_number, OUTPUT);
        digitalWrite(pin_number, voltage);

        commander.reply_OK();
        Serial.write("Responded to set_pin_output with acknowledgement (successfully set pin voltage)");

        return;
    }

    // If not returned yet, the command was not recognised
    commander.reply_ERR("Unrecognised command");
    Serial.write(printf("Responded to %s with error (unrecognised command)", command_name));
}


void setup() {  // Arduino virtual function for initialisation
    Serial.begin(SERIAL_BAUD);
    Serial.write("Receiver test program online\n");

    Serial.write("Setting up commander module...");
    commander.setup();
    Serial.write(" done\n");

}


void loop() {   // Arduino virtual function for processing
    Command command = commander.get_next_command();

    if (command.valid()) {
        handle_command(command);
    }

    delay(100);
}
