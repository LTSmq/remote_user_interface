
#include "commander.h"

Commander commander;

void setup() {
  commander.bootup("Bridge Controller 26", "iheartjokes");

}

void loop() {
  Command command = commander.get_next_command();
  if (command.valid()) {
    handle_command(command);
  }

}

void handle_command(Command command) {
  if (String(command.name()).equals("ping")) {
    commander.reply_OK();
  }

  commander.reply_ERR("Unrecognised command");
}
