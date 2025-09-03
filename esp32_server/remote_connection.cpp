/*
 * remote_connection.cpp
 * Implementation of receiver module
*/

#include "remote_connection.h"

void command_task(void* argument) {
  RemoteConnection* connection_pointer = static_cast<RemoteConnection*>(argument);
  connection_pointer->commander();
}

DataPackage::DataPackage(const char* json_string) {
  DeserializationError error = deserializeJson(json_document, json_string);
  if (!error) json_object = json_document.as<JsonObject>();
}

DataPackage::DataPackage(JsonObject assigned_object) {
  json_object = assigned_object;
}

const char* DataPackage::as_json() {
  serializeJson(json_object, json_string_buffer);
  return json_string_buffer;
}

DataPackage DataPackage::get_package(const char* label) {
  if (!has_package(label)) return DataPackage();
  JsonObject nested_object = json_object[label].as<JsonObject>();
  return DataPackage(nested_object);
}

Command::Command(const char* json_string) {
  DataPackage parsed = DataPackage(json_string);

  _name = String(parsed.get_value<const char*>("command", ""));
  _ticket = parsed.get_value<unsigned short>("ticket", 0);
  arguments = DataPackage(
    parsed.get_value<JsonObject>("kwargs", JsonObject())
  ); 
}

const char* Response::as_json() {
  DataPackage package = format();
  return package.as_json();
}

DataPackage ResponseOK::format() {
  DataPackage response_packet;

  response_packet.add_value("response", "OK");

  return response_packet;
}

ResponseDATA::ResponseDATA(DataPackage data_payload) {
  payload = data_payload;
}

DataPackage ResponseDATA::format() {
  DataPackage response_packet;

  response_packet.add_value("response", "DATA");
  response_packet.add_package("payload", payload);

  return response_packet;
}

DataPackage ResponseERR::format() {
  DataPackage response_packet;

  response_packet.add_value("response", "ERR");
  response_packet.add_value("error_code", reason);

  return response_packet;
}

DataPackage ResponseVOID::format() {
  DataPackage response_packet;

  response_packet.add_value("response", "VOID");

  return response_packet;
}

RemoteConnection::~RemoteConnection() {
  close();
}

void RemoteConnection::open(const char* ssid, const char* password) {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  commander_server.begin();
  updater_server.begin();

  xTaskCreatePinnedToCore(
    command_task,
    "Commander Daemon",
    COMMAND_MONITOR_STACK_ALLOCATION,
    this, 
    1,
    &commander_daemon,
    COMMAND_MONITOR_CORE
  );
}

void RemoteConnection::close() {
  commander_client.stop();
  updater_client.stop();

  WiFi.mode(WIFI_OFF);

  vTaskDelete(commander_daemon);
}

void RemoteConnection::commander() {
  while (true) {
    vTaskDelay(COMMAND_MONITOR_REFRESH_TIME);

    if (!commander_client.connected()) {
      WiFiClient new_client = commander_server.available();

      if (!new_client.connected()) {
        continue;
      }

      commander_client = new_client;
    }

    if (!commander_client.available()) {
      continue;
    }

    char message[JSON_CAPACITY];
    commander_client.readBytesUntil(MESSAGE_DELIMITER, message, JSON_CAPACITY);

    Response* response_pointer;
    if (command_handler == nullptr) {
      commander_client.println(ResponseVOID().as_json());
    }
    else {
      Command command = Command(message);
      commander_client.println(command_handler(command).as_json());
    }
  }
}

bool RemoteConnection::update(DataPackage information) {
  if (!updater_client.connected()) {
    WiFiClient new_client = updater_server.available();

    if (!new_client.connected()) {
      return false;
    }

    updater_client = new_client;
  }

  updater_client.println(information.as_json());

  return true;
}