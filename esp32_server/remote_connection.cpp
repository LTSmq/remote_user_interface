/*
 * remote_connection.cpp
 * Implementation of receiver module
*/

#include "remote_connection.h"

void command_task(void* argument) {
  RemoteConnection* connection_pointer = static_cast<RemoteConnection*>(argument);
  connection_pointer->commander();
}

DataPackage::DataPackage() {
  json_object = json_document.to<JsonObject>();
}

DataPackage::DataPackage(const char* json_string) {
  DeserializationError error = deserializeJson(json_document, json_string);
  if (!error) json_object = json_document.as<JsonObject>();
}

DataPackage::DataPackage(JsonObject assigned_object) {
  json_object = assigned_object;
}

String DataPackage::as_json() {
  serializeJson(json_object, json_string_buffer);
  return String(json_string_buffer);
}

void DataPackage::add_package(const char* label, DataPackage nested) {
  add_json(label, nested.as_json().c_str());
}


bool DataPackage::add_json(const char* label, const char* json_string) {
  StaticJsonDocument<JSON_CAPACITY> subdocument;
  DeserializationError error = deserializeJson(subdocument, json_string);
  if (error) {
    return false;
  }

  JsonObject nested = json_object.createNestedObject(label);
  nested.set(subdocument.as<JsonObject>()); 

  return true;
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
  JsonObject kwargs = parsed.json_object["kwargs"].as<JsonObject>();
  if (kwargs) {
    for (JsonPair member : kwargs) {
      arguments.add_value(member.key().c_str(), member.value());
    }
  }
}

String Response::as_json() {
  DataPackage package = format();
  package.add_value("ticket", command.ticket());
  return package.as_json();
}

Response::Response(Command given_command):
  command(given_command)
{}

DataPackage Response::format() {
  DataPackage package;
  package.add_value("response", "ERR");
  package.add_value("error_code", INTERNAL_ERROR);
  return package;
}

DataPackage ResponseOK::format() {
  DataPackage response_packet;

  response_packet.add_value("response", "OK");

  return response_packet;
}

ResponseDATA::ResponseDATA(Command given_command, DataPackage data_payload): Response(given_command) {
  saved_payload = data_payload.as_json();
}
  
DataPackage ResponseDATA::format() {
  DataPackage response_packet;
  
  response_packet.add_json("payload", saved_payload.c_str());
  response_packet.add_value("response", "DATA");

  return response_packet;
}

ResponseERR::ResponseERR(Command given_command, ErrorCode code):
  Response(given_command),
  reason(code)
{}

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

RemoteConnection::RemoteConnection() {};

RemoteConnection::~RemoteConnection() {
  close();
}

void RemoteConnection::open(const char* ssid, const char* password) {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  commander_server = WiFiServer(COMMANDER_PORT, SINGLE_CLIENT_ONLY);
  updater_server = WiFiServer(UPDATER_PORT, SINGLE_CLIENT_ONLY);

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
  if (commander_daemon != NULL) vTaskDelete(commander_daemon);
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

    String message = commander_client.readStringUntil(MESSAGE_DELIMITER);
    Command command = Command(message.c_str());

    if (command_handler == nullptr) {
      commander_client.println(ResponseVOID(command).as_json());
    }
    else {
      Response* response = command_handler(command);
      if (response == nullptr) {
        response = new ResponseVOID(command);
      }
      String message = String(response->as_json());
      commander_client.print(message);

      delete response;
    }
  }
}

bool RemoteConnection::update(DataPackage information) {
  if (!updater_client.connected()) {
    if (!updater_server.hasClient()) return false;
    WiFiClient new_client = updater_server.available();
    if (!new_client || !new_client.connected()) {
      return false;
    }
    updater_client = new_client;
    
  }
  
  if (updater_client.availableForWrite()) return false; 
  
  updater_client.println(information.as_json());
  return true;
}