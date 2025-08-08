/**
 * main.cpp
 * An example main manager program that interfaces with the commander, and therefor the remote user interface
*/

#include <Arduino.h>

#include "commander.cpp"


Commander commander;


void handle_command(Command command) {
    String command_name = command.name();

    if (!command_name.compareTo("ping")) {
        commander.reply_OK();
        return;
    }

    if (!command_name.compareTo("simulate_error")) {
        commander.reply_ERR("An error was requested");
        return;
    }

    if (!command_name.compareTo("sum")){
        bool requirements = (
            command.has_number_argument("a")
            && command.has_number_argument("b")
        );

        if (requirements) {
            double sum = command.argument_value_number("a") + command.argument_value_number("b");
            DataPayload data_payload;
            data_payload.add_number("result", sum); 

            commander.reply_DATA(data_payload);
        }
        else {
            commander.reply_ERR("Missing arguments");
        }
    }
}



void setup() {  // Arduino virtual function for initialisation
    commander.setup(); // Don't forget this
}


void loop() {   // Arduino virtual function for processing
    Command command = commander.get_next_command();

    if (command.valid()) {
        handle_command(command);
    }

    delay(100);
}
