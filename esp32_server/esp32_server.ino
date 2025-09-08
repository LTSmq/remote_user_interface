/*
 * esp32_server.ino
 * An example business logic sketch for using the receiver module
*/

#include "remote_connection.h"

#define SSID "Bridge Controller 26"
#define PASSWORD "iheartjokes"

#define INPUT_REFRESH_TIME 50

#define LED_PIN 5
#define SWITCH_PIN 23

RemoteConnection rc;
unsigned char last_read_input;


void setup() {
  Serial.begin(115200);
  rc.command_handler = &handle_command;
  rc.open(SSID, PASSWORD);

  pinMode(LED_PIN, OUTPUT);
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  last_read_input = digitalRead(SWITCH_PIN);
}


void loop() {
  unsigned char switch_down = digitalRead(SWITCH_PIN);

  if (switch_down != last_read_input) {
    last_read_input = switch_down;
    bool is_on = switch_down == LOW ;
    rc.update("switch_on", is_on);

    if (is_on) {
      Serial.println("Switch on");
    }

    else {
      Serial.println("Switch off");
    }
  }
  delay(INPUT_REFRESH_TIME);
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
    } else {
      DataPackage package;
      package.add_value<const char*>("message", command.get_argument<const char*>("message", ""));
      response = new ResponseDATA(command, package);
    }
  }

  else if (command_name.equals("raise_error")) {
    ErrorCode code = command.get_argument("code", DEBUG);
    response = new ResponseERR(command, code);
  }

  else if (command_name.equals("set_light")) {
    if (!command.has_argument<unsigned char>("to")) {
      response = new ResponseERR(command, INVALID_ARGS);
    } else {
      unsigned char to = command.get_argument("to", LOW);

      digitalWrite(LED_PIN, to);
      response = new ResponseOK(command);
    }
  }

  else {
    response = new ResponseERR(command, UNRECOGNISED);
  }

  Serial.print("Responding with: ");
  Serial.print(response->as_json());
  Serial.println();

  return response;
}
