  /*
  * remote_connection.h
  * Generation 2 of receiver module for ESP32 bridge controller
  */

  #ifndef REMOTE_CONNECTION
  #define REMOTE_CONNECTION

  #include <WiFi.h>
  #include <ArduinoJson.h>  // By Beniot Blanchon; Install via library manager in Arduino IDE

  #define MESSAGE_DELIMITER '\n'
  #define JSON_CAPACITY 4096

  #define COMMAND_MONITOR_REFRESH_TIME 50 / portTICK_PERIOD_MS
  #define COMMAND_MONITOR_STACK_ALLOCATION 1000
  #define COMMAND_MONITOR_CORE 1

  #define COMMANDER_PORT 55555
  #define UPDATER_PORT 55055
  #define SINGLE_CLIENT_ONLY 1

  enum ErrorCode {
    DEBUG = -2,
    UNSPECIFIED = -1,  // default
    UNRECOGNISED,
    INVALID_ARGS,
    NOT_FOUND,
    PERMISSION_DENIED,
    TIMEOUT,
    INTERNAL_ERROR,
  };

  enum ConnectionType {
    COMMANDER,
    UPDATER,
  };

  // To pack arbitrary information in a key-value format
  class DataPackage {
    public:
      DataPackage();  // Creates an empty package
      DataPackage(const char* json_string);  // Populates package with JSON data
      DataPackage(JsonObject);

      DataPackage get_package(const char* label);
      const char* as_json();

      void delete_value(const char* label) {
        json_object.remove(label);
      };

      template <typename Type>
      void add_value(const char* label, Type value) {
        json_object[label] = value;
      };

      bool has_package(const char* label) {
        return json_object[label].is<JsonObject>();
      }

      void add_package(const char* label, DataPackage nested) {
        json_object[label] = nested.json_object;
      }

      template <typename Type>
      bool has_value(const char* label) {
        return json_object.containsKey(label) && json_object[label].is<Type>();
      };

      template <typename Type>
      Type get_value(const char* label, Type default_value) {
        if (!has_value<Type>(label)) return default_value;

        return json_object[label].as<Type>();
      };

    protected:
      JsonObject json_object;
      StaticJsonDocument<JSON_CAPACITY> json_document;
      char json_string_buffer[JSON_CAPACITY];
  };

  // For the control system to interpret 
  class Command {
    public:
      Command(const char* json_string);  // Create a command with a JSON string

      const char* name() {
        return _name.c_str();
      };

      unsigned short ticket() {
        return _ticket;
      }

      template <typename Type>
      bool has_argument(const char* argument_name) {
        return arguments.has_value<Type>(argument_name);
      };

      template <typename Type>
      bool get_argument(const char* argument_name, Type default_value) {
        return arguments.get_value<Type>(argument_name, default_value);
      };
    
    protected:
      String _name;
      DataPackage arguments;
      unsigned short _ticket;

  };

  // For the control system to respond to commands with
  class Response {  // Abstract
    public:
      const char* as_json();
    
    protected:
      virtual DataPackage format();
  };

  // Acknowledgement that command was received and understood
  class ResponseOK: public Response {  // Positive response
    public:
      ResponseOK();
    
    protected:
      DataPackage format() override;
  };

  // Acknowledgement that command was received and understood, including information requested by command
  class ResponseDATA: public Response {  // Positive response
    public:
      ResponseDATA(DataPackage);
    
    protected:
      DataPackage format() override;
      DataPackage payload;
  };

  // Acknowledgement command was received but rejected
  class ResponseERR: public Response {  // Negative response
    public:
      ResponseERR(ErrorCode);
    
    protected:
      DataPackage format() override;
      ErrorCode reason;
  };

  // Acknowledgement command was received by socket but not acknowledged by control logic; for debug use
  class ResponseVOID: public Response {  // Negative response
    public:
      ResponseVOID();
    
    protected:
      DataPackage format() override;
  };


  class RemoteConnection {
    public:
      Response (*command_handler)(Command) = nullptr;  // The pointer to the function expected to handle incoming commands and provide response

      RemoteConnection();
      ~RemoteConnection();

      void open(const char* ssid, const char* password);  // Opens the connection
      void close();  // Closes the connection
      bool connected(ConnectionType);  // Returns true if the given connection type is connected, false otherwise

      bool update(DataPackage information);  // For the controller logic to push information back to the remote interface

      void commander();  // To be called in a task

    protected:
      WiFiServer commander_server = WiFiServer(COMMANDER_PORT, SINGLE_CLIENT_ONLY);
      WiFiClient commander_client;

      WiFiServer updater_server = WiFiServer(UPDATER_PORT, SINGLE_CLIENT_ONLY);
      WiFiClient updater_client;

      
      TaskHandle_t commander_daemon = NULL;

  };

  #endif
