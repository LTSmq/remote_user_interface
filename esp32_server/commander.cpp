/*
  commander.cpp
*/

#include "commander.h"


Command::Command() {
  ;  // No action taken; json_object will read as invalid from its default constructor
}

Command::Command(const char* json_string) {
  ArduinoJson::DeserializationError error = deserializeJson(json_object, json_string);
  Serial.println(json_string);
  if (error) {
    json_object.clear();
  }
}

bool Command::valid() {
  const char* this_name = Command::name();
  return !String(this_name).equals("");
}


const char* Command::name() {
  
  return json_object["command"].as<const char*>();
}


DataPayload::DataPayload() {
  ;  // No action necessary as default constructor for json object creates empty document
}

String DataPayload::as_json_string() {
  String json_string;
  serializeJson(DataPayload::json_object, json_string);
  return json_string;
}

void DataPayload::add_payload(const char* label, DataPayload payload) {
  JsonObject nested_object = json_object.createNestedObject(label);
  nested_object.set(payload.json_object.as<JsonObject>());
}


Commander::Commander() {
  WiFi.mode(WIFI_OFF);
}

void Commander::bootup(const char* ssid  = DEFAULT_SSID, const char* password = DEFAULT_PASSWORD) {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  Commander::server.begin();
}

void Commander::shutdown() {
  WiFi.mode(WIFI_OFF);

  server.stop();
}

bool Commander::connected() {
  return client.connected();
}

Command Commander::get_next_command() {
  if (!Commander::client.connected()) {
    WiFiClient new_client = server.available();

    if (!new_client.connected()) {
      return Command();  // Invalid command
    }

    client = new_client;
  }

  if (!Commander::client.available()) {
    return Command();  // Invalid command
  }

  char message[JSON_CAPACITY] = {0};
  Commander::client.readBytesUntil(MESSAGE_DELIMITER, message, JSON_CAPACITY);

  return Command(message);
}

bool Commander::reply_OK() {
  DataPayload message_payload;
  message_payload.add_value<const char*>("response", "OK");
  return Commander::reply(message_payload);
}

bool Commander::reply_ERR(const char* error_message) {
  DataPayload message_payload;
  message_payload.add_value<const char*>("response", "ERR");
  message_payload.add_value<const char*>("error_message", error_message);
  return Commander::reply(message_payload);
}

bool Commander::reply_DATA(DataPayload data_payload) {
  DataPayload message_payload;
  message_payload.add_value<const char*>("response", "DATA");
  message_payload.add_payload("payload", data_payload);
  return Commander::reply(message_payload);
}

bool Commander::reply(DataPayload message_payload) {
  if (!client.connected()) {
    return false;
  }
  String json_message = message_payload.as_json_string();
  client.write(json_message.c_str());
  return true;
}
