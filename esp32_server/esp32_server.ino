/*
 * esp32_server.ino
 * An example business logic sketch for using the commander receiver module
*/

#include "commander.h"

#define REFRESH_TIME 100

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
  String command_name = String(command.name());
  if (command_name.equals("ping")) {
    Serial.println("Responding to ping with acknowledgement");
    commander.reply_OK();
    return;
  }

  if (command_name.equals("sum")) {
    int a = command.argument_value<int>("a", 0);
    int b = command.argument_value<int>("b", 0);
    int result = a + b;
    
    DataPayload sum_return;
    sum_return.add_value<int>("result", a + b);
    commander.reply_DATA(sum_return);
    Serial.print("Responding to sum with result: ");
    Serial.println(result);
    return;
  }

  if (command_name.equals("gpio_mode")) {
    if (!command.has_argument<unsigned char>("mode")) {
      Serial.println("Responding to command with error (integer kwarg \"mode\" not provided)");
      commander.reply_ERR("Could not set GPIO mode: valid mode not specified");
      return;
    }

    if (!command.has_argument<unsigned char>("pin")) {
      Serial.println("Responding to command with error (integer kwarg \"pin\" not provided)");
      commander.reply_ERR("Could not set GPIO mode: valid pin not specified");
      return;
    }

    unsigned char mode = command.argument_value<unsigned char>("mode", INPUT);
    unsigned char pin = command.argument_value<unsigned char>("pin", 1);

    pinMode(pin, mode);
    
    Serial.print("Set pin #");
    Serial.print(pin);
    Serial.print(" to ");
    if (mode == INPUT) { Serial.print("input mode"); } else { Serial.print("output mode"); }
    Serial.println();
    commander.reply_OK();
    return;

  }

  if (command_name.equals("gpio_read")) {
    if (!command.has_argument<unsigned char>("pin")) {
      Serial.println("Responding to command with error (integer kwarg \"pin\" not provided)");
      commander.reply_ERR("Could not read GPIO value: valid pin not specified");
      return;
    }

    unsigned char pin = command.argument_value<unsigned char>("pin", 1);
    bool analog = command.argument_value<bool>("analog", false);
    DataPayload payload;

    if (analog) {
      int value = analogRead(pin);

      payload.add_value<int>("value", value);

      Serial.print("Pin #");
      Serial.print(pin);
      Serial.print(" was read as: ");
      Serial.print(value);
      Serial.print(" (analog)");
      Serial.println();

    } 
    
    else {
      int value = digitalRead(pin);
      const char* value_string;

      if (value == HIGH) {  value_string = "HIGH"; } 
      else {                value_string = "LOW";  }

      payload.add_value<const char*>("value", value_string);

      Serial.print("Pin #");
      Serial.print(pin);
      Serial.print(" was read as: ");
      Serial.print(value_string);
      Serial.println();
    }

    commander.reply_DATA(payload);
     return;
  }

  if (command_name.equals("gpio_write")) {
    if (!command.has_argument<unsigned char>("pin")) {
      Serial.println("Responding to command with error (integer kwarg \"pin\" not provided)");
      commander.reply_ERR("Could not write GPIO value: valid pin not specified");
      return;
    }

    if (!command.has_argument<unsigned short>("value")) {
      Serial.println("Responding to command with error (integer kwarg \"value\" not provided)");
      commander.reply_ERR("Could not write GPIO value: valid value not specified");
      return;
    }

    unsigned char pin = command.argument_value<unsigned char>("pin", 1);
    unsigned short value = command.argument_value<unsigned short>("value", 0);
    bool analog = command.argument_value<bool>("analog", false);

    Serial.print("Setting pin #");
    Serial.print(pin);
    Serial.print(" to ");

    if (analog) {
      value = value % 1024;
      Serial.print(value);
      Serial.print(" (analog)");
      analogWrite(pin, value);
    }

    else {
      value = value % 2;
      Serial.print(value);
      digitalWrite(pin, value);

    }
    Serial.println();

    commander.reply_OK();
    return;
  }

  Serial.println("Responding to unknown command with error");
  commander.reply_ERR("Unrecognised command");
}
