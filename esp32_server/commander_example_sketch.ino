/*
 * commander_example_sketch.ino
*/
#include <string>

#include "commander.h"

#define REFRESH_TIME 2000

Commander commander;

void setup() {
  Serial.begin(115200);
  commander.bootup("iPhone", "iheartjokes");
  Serial.println("Online...");

}

void loop() {
  Command command = commander.get_next_command();
  
  if (command.valid()) {
    handle_command(command);
    Serial.print("Received command: ");
    Serial.println(command.name());
  }

  delay(REFRESH_TIME);

}

void handle_command(Command command) {
  String command_name = String(command.name());
  if (command_name.equals("ping")) {
    commander.reply_OK();
    return;
  }

  if (command_name.equals("sum")) {
    int a = command.argument_value<int>("a", 0);
    int b = command.argument_value<int>("b", 0);
    int result = a + b;

    Serial.print("Has integer argument a: \t");
    Serial.println(command.has_argument<int>("a"));

    Serial.print("Result:\t");
    Serial.println(result);

    DataPayload sum_return;
    sum_return.add_value<int>("result", a + b);
    commander.reply_DATA(sum_return);
    return;
  }

  commander.reply_ERR("Unrecognised command");
}
