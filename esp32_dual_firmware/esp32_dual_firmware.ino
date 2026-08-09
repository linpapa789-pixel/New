#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// =========================
// Wi-Fi & BLE Settings
// =========================
static const char* AP_SSID     = "ESP_Pico_Diag";
static const char* AP_PASSWORD = "password123";

static const IPAddress AP_IP(192, 168, 4, 1);
static const IPAddress AP_GW(192, 168, 4, 1);
static const IPAddress AP_MASK(255, 255, 255, 0);

#define BLE_DEVICE_NAME        "Pro_Diag_Tool"
#define SERVICE_UUID           "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID_RX "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CHARACTERISTIC_UUID_TX "beb5483f-36e1-4688-b7f5-ea07361b26a8"

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

BLEServer* pBleServer = nullptr;
BLECharacteristic* pTxCharacteristic = nullptr;
bool bleClientConnected = false;

// =========================
// Pico Connection Pins (FIXED FOR ESP32-S3 N16R8)
// =========================
// ပြဿနာဖြစ်စေသော Pin 16 နှင့် 17 အစား လွတ်ကင်းသော Pin 18 နှင့် 19 ကို အစားထိုးထားပါသည်
static constexpr int PICO_UART_RX = 18; // Connect to Pico TX
static constexpr int PICO_UART_TX = 19; // Connect to Pico RX
String picoBuffer = "";

// Send JSON string over both WebSocket and BLE
static void sendTextAll(const char* json) {
  ws.textAll(json);
  if (bleClientConnected && pTxCharacteristic != nullptr) {
    pTxCharacteristic->setValue((uint8_t*)json, strlen(json));
    pTxCharacteristic->notify();
  }
}

// Pass incoming App JSON directly to Pico
static void handleAppCommand(const char* json) {
  Serial1.println(json); // Send to Pico via UART1
}

// Parse BLE/WS payload
static void parseIncomingBytes(uint8_t* data, size_t len) {
    // Null terminate to pass as string
    char buf[512];
    if (len >= sizeof(buf)) len = sizeof(buf) - 1;
    memcpy(buf, data, len);
    buf[len] = '\0';
    handleAppCommand(buf);
}

// =========================
// BLE Callbacks
// =========================
class BleServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override {
      bleClientConnected = true;
      Serial.println("BLE Connected");
    }
    void onDisconnect(BLEServer* pServer) override {
      bleClientConnected = false;
      Serial.println("BLE Disconnected");
      BLEDevice::startAdvertising();
    }
};

class BleRxCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) override {
      String rxValue = pCharacteristic->getValue();
      if (rxValue.length() > 0) {
        parseIncomingBytes((uint8_t*)rxValue.c_str(), rxValue.length());
      }
    }
};

// =========================
// WebSocket Callback
// =========================
static void onWsEvent(AsyncWebSocket* serverPtr, AsyncWebSocketClient* client, AwsEventType type, void* arg, uint8_t* data, size_t len) {
  if (type == WS_EVT_DATA) {
    AwsFrameInfo* info = (AwsFrameInfo*)arg;
    if (info->opcode == WS_TEXT && info->final && info->index == 0 && info->len == len) {
      parseIncomingBytes(data, len);
    }
  }
}

// =========================
// Arduino Setup & Loop
// =========================
void setup() {
  // Debug UART
  Serial.begin(115200); 
  
  // UART1 to Pico (Using New Safe Pins)
  Serial1.begin(115200, SERIAL_8N1, PICO_UART_RX, PICO_UART_TX);

  // Wi-Fi SoftAP Setup
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_GW, AP_MASK);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.println("SoftAP Started");

  // WebSocket Setup
  ws.onEvent(onWsEvent);
  server.addHandler(&ws);
  server.begin();

  // BLE Setup
  BLEDevice::init(BLE_DEVICE_NAME);
  pBleServer = BLEDevice::createServer();
  pBleServer->setCallbacks(new BleServerCallbacks());
  
  BLEService *pService = pBleServer->createService(SERVICE_UUID);
  pTxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_NOTIFY);
  pTxCharacteristic->addDescriptor(new BLE2902());
  
  BLECharacteristic *pRxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_RX, BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  pRxCharacteristic->setCallbacks(new BleRxCallbacks());
  
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  BLEDevice::startAdvertising();
  
  Serial.println("System Ready!");
}

void loop() {
  ws.cleanupClients();

  // Forward Pico logs/data to App via WebSocket and BLE
  while (Serial1.available()) {
      char c = Serial1.read();
      if (c == '\n') {
          if (picoBuffer.length() > 0) {
             sendTextAll(picoBuffer.c_str());
             picoBuffer = "";
          }
      } else {
          picoBuffer += c;
          
          // Buffer Memory Protection (Limits length to 512 bytes)
          if (picoBuffer.length() >= 512) {
              sendTextAll(picoBuffer.c_str());
              picoBuffer = "";
          }
      }
  }
  delay(1);
}
