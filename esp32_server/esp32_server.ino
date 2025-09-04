/*
 * esp32_server.ino
 * An example business logic sketch for using the receiver module
*/

#include "remote_connection.h"

#define SSID "Bridge Controller 26"
#define PASSWORD "iheartjokes"

#define HEARTBEAT_TIME 5000

RemoteConnection rc;


void setup() {
  Serial.begin(115200);
  rc.command_handler = &handle_command;
  rc.open(SSID, PASSWORD);
}


void loop() {
  delay(HEARTBEAT_TIME);
  Serial.print("Heartbeat: ");
  if (rc.update("sync", true)) {
    Serial.print("Updates connected to client");
  }
  else {
    Serial.print("No client to receive updates");
  }
  Serial.println();
}


Response* handle_command(Command command) {
  Response* response = nullptr;
  String command_name = String(command.name());
  
  Serial.print("Received command: ");
  Serial.print(command_name);
  Serial.println();

  if (command_name.equals("ping")) {
    response = new ResponseOK(command);  // Seems to construct using base abstract constructor
  }

  else if (command_name.equals("echo")) {
    if (!command.has_argument<const char*>("message")) {
      response = new ResponseERR(command, INVALID_ARGS);
    }
    else {
      DataPackage package;
      package.add_value<const char*>("message", command.get_argument<const char*>("message", ""));
      response = new ResponseDATA(command, package);
    }
  }

  if (response == nullptr) {
    ResponseERR(command, UNRECOGNISED);
  }

  Serial.print("Responding with: ");
  Serial.print(response->as_json());
  Serial.println();

  return response;
}
