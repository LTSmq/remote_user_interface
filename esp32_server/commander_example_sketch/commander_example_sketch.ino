/*
 * commander_example_sketch.ino
*/
#include "commander.h"

#define REFRESH_TIME 2000

Commander commander;

void setup() {
  Serial.begin(115200);
  commander.bootup("Bridge Controller 26", "iheartjokes");
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
  
  commander.reply_OK();
}
