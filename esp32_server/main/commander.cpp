/**
 * commander.cpp
 * For functionality description see commander.h
*/
#include "commander.h"

#include <cJSON.h>  // ESP32-IDF component
#include <WiFi.h>  // Arduino module


ArgType cJSON_IdentifyArgType(cJSON *json_object, const char* key) {
    if (json_object == nullptr) {
        return ArgType::INVALID;
    }

    cJSON* json_subobject = cJSON_GetObjectItem(json_object, key);

    if (cJSON_IsBool(json_subobject))   { return ArgType::BOOL; }
    if (cJSON_IsNumber(json_subobject)) { return ArgType::NUMBER; }
    if (cJSON_IsString(json_subobject)) { return ArgType::STRING; }

    return ArgType::INVALID;
}


void cJSON_AddOrReplaceItem(cJSON *json_object, const char* key, cJSON* item) {
    if (cJSON_HasObjectItem(json_object, key)) {
        cJSON_ReplaceItemInObject(json_object, key, item);
    } else {
        cJSON_AddItemToObject(json_object, key, item);
    }
}


bool bool_from(cJSON* json_object, const char* key, bool default_value) {
    bool value = default_value;

    if (json_object) {
        cJSON* string_json_subobject = cJSON_GetObjectItem(json_object, key);
        if (cJSON_IsBool(string_json_subobject)) {
            value = (bool) cJSON_IsTrue(string_json_subobject);
        }
    }

    return value;
}


String string_from(cJSON* json_object, const char* key, const char* default_value) {
    String value = String(default_value);

    if (json_object) {
        cJSON* string_json_subobject = cJSON_GetObjectItem(json_object, key);
        if (cJSON_IsString(string_json_subobject)) {
            value = String(cJSON_GetStringValue(string_json_subobject));
        }
    }

    return value;
}


double number_from(cJSON* json_object, const char* key, double default_value) {
    double value = default_value;
    
    if (json_object) {
        cJSON* string_json_subobject = cJSON_GetObjectItem(json_object, key);
        if (cJSON_IsNumber(string_json_subobject)) {
            value = cJSON_GetNumberValue(string_json_subobject);
        }
    }

    return value;
}


Command::Command(const char* from_json_string) {
    if (from_json_string) {
        json_object = cJSON_Parse(from_json_string);
    }
    else {
        json_object = nullptr;
    }
}

Command::Command() {
    json_object = nullptr;
}

Command::~Command() {
    cJSON_Delete(json_object);
}

String Command::name() {
    return string_from(json_object, "command", "");
}

bool Command::valid() {
    return json_object != nullptr;
}

bool Command::has_argument(const char* argument_name) {
    cJSON* kw = kwargs();
    return (kw != nullptr) && (cJSON_GetObjectItem(kw, argument_name) != nullptr);
}

bool Command::has_boolean_argument(const char* argument_name) {
    cJSON* kw = kwargs();
    return kw && cJSON_IdentifyArgType(kw, argument_name) == ArgType::BOOL;
}

bool Command::has_number_argument(const char* argument_name) {
    cJSON* kw = kwargs();
    return kw && cJSON_IdentifyArgType(kw, argument_name) == ArgType::NUMBER;
}

bool Command::has_string_argument(const char* argument_name) {
    cJSON* kw = kwargs();
    return kw && cJSON_IdentifyArgType(kw, argument_name) == ArgType::STRING;
}

bool Command::argument_value_bool(const char* argument_name, bool default_value) {
    return bool_from(kwargs(), argument_name, default_value);
}

double Command::argument_value_number(const char* argument_name, double default_value) {
    return number_from(kwargs(), argument_name, default_value);
}

String Command::argument_value_string(const char* argument_name, const char* default_value) {
    return string_from(kwargs(), argument_name, default_value);
}

cJSON* Command::kwargs() {
    return cJSON_GetObjectItem(json_object, "kwargs");
}


DataPayload::DataPayload() {
    json_object = cJSON_CreateObject();
}

DataPayload::~DataPayload() {
    cJSON_Delete(json_object);
}

String DataPayload::as_json_string() {
    return String(cJSON_Print(json_object));
}

void DataPayload::add_bool(const char* label, bool value) {
    cJSON_AddOrReplaceItem(json_object, label, cJSON_CreateBool((cJSON_bool) value));
}

void DataPayload::add_number(const char* label, double value) {
    cJSON_AddOrReplaceItem(json_object, label, cJSON_CreateNumber(value));
}

void DataPayload::add_string(const char* label, const char* value) {
    cJSON_AddOrReplaceItem(json_object, label, cJSON_CreateString(value));
}

void DataPayload::add_payload(const char* label, const DataPayload& payload) {
    if (&payload == this) { return; }  // Self-containing forbidden

    cJSON_AddOrReplaceItem(json_object, label, cJSON_Duplicate(payload.json_object, true));
}


Commander::~Commander() {
    shutdown();
}

Commander::Commander() {
    // Ensure wifi is disabled until setup
    WiFi.mode(WIFI_OFF);
}

Command Commander::get_next_command() {
    // Invalid if not setup yet
    if (!is_setup) { return Command(); }

    // Check if the client is connected
    if (!client.connected()) {
        // Search for a new client if the current one is disconnected
        WiFiClient new_client = server.accept();

        // Check if a new client was found
        if (new_client) {
            // Remember new client if it was found
            client = new_client;
        }
        else {
            // Invalid if no connected clients
            return Command();
        }
    }

    // Check if client has submitted any requests
    if (!client.available()) {
        // Invalid if client has not submitted any requests
        return Command(); 
    }

    // Get the client's message assuming a standard delimiter
    String message = client.readStringUntil(MESSAGE_DELIMITER);

    // Return parsed message as command
    return Command(message.c_str());
}

bool Commander::connected() {
    return is_setup && client.connected();
}

bool Commander::reply_OK() {
    DataPayload payload;

    payload.add_string("response", "OK");

    return reply(payload);
}

bool Commander::reply_ERR(const char* error_message) {
    DataPayload payload;

    payload.add_string("response", "ERR");
    payload.add_string("error_message", error_message);

    return reply(payload);
}

bool Commander::reply_DATA(const DataPayload& data_payload) {
    DataPayload message_payload;

    message_payload.add_string("response", "DATA");
    message_payload.add_payload("payload", data_payload);

    return reply(message_payload);
}

void Commander::setup(const char* ssid, const char* password) {
    // Open the Access point
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, password);

    // Wait a bit for the point to establish
    delay(STANDARD_WAIT_TIME);

    // Open the server
    server.begin();

    // Mark setup flag as true
    is_setup = true;
}

void Commander::shutdown() {
    server.close();
    WiFi.mode(WIFI_OFF);
    is_setup = false;
}

bool Commander::reply(DataPayload payload) {
    if (!client.connected()) {
        return false;
    }

    String message = payload.as_json_string() + MESSAGE_DELIMITER; 
    client.write(message.c_str());

    return true;
}
