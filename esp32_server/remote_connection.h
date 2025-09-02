/*
 * remote_connection.h
 * Generation 2 of receiver module for ESP32 bridge controller
*/
#ifndef REMOTE_CONNECTION
#define REMOTE_CONNECTION

#include <WiFi.h>
#include <ArduinoJson.h>  // By Beniot Blanchon; Install via library manager in Arduino IDE

enum ErrorCode {
  UNSPECIFIED,  // default
  UNRECOGNISED,
  INVALID_ARGS,
  NOT_FOUND,
  PERMISSION_DENIED,
  // Any other conditions for rejecting commands, please tell me...
};

// To pack arbitrary information in a key-value format
class DataPackage {
  // Todo...
};

// For the control system to interpret 
class Command: public DataPackage {
  // Todo...
};

// For the control system to respond to commands with
class Response: public DataPackage {  // Abstract
  virtual JsonObject format();
  // Todo...
};

// Acknowledgement that command was received and understood
class ResponseOK: public Response {  // Positive response
  // Todo...
};

// Acknowledgement that command was received and understood, including information requested by command
class ResponseDATA: public Response {  // Positive response
  // Todo...
};

// Acknowledgement command was received but rejected
class ResponseERR: public Response {  // Negative response
  // Todo...
};

// Acknowledgement command was received by socket but not acknowledged by control logic; for debug use
class ResponseVOID: public Response {  // Negative response
  // Todo...
};

// For the control system to push information about status updates
class Update: public Response {
  // Todo...
};

class RemoteConnection {
  public:
    Response* (*command_handler)(Command);  // The pointer to the function expected to handle incoming commands and provide response

    RemoteConnection();

    bool update(Update);  // For the controller logic to push information back to the remote interface

  protected:
    WiFiServer commander_server;
    WiFiClient commander_client;

    WiFiServer updater_server;
    WiFiClient updater_client;

};

#endif
