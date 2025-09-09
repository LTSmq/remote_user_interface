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

#define SWITCH_LABEL "bridge_position"

RemoteConnection rc;
unsigned char last_read_input;
bool overrides_enabled = false;


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
    rc.update("current_position", switch_down);

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
    response = new ResponseOK(command);
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

  else if (command_name.equals("set_overrides")) {
      if (!command.has_argument<bool>("to")) {
        response = new ResponseERR(command, INVALID_ARGS);
      }
      else {
        bool to = command.get_argument("to", false);
        digitalWrite(LED_PIN, to);
        response = new ResponseOK(command);
        overrides_enabled = to;
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
