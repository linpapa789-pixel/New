#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// =========================
// Wi-Fi & BLE Settings
// =========================
static const char* AP_SSID     = "ESP_Diag_Tool";
static const char* AP_PASSWORD = "password123";

static const IPAddress AP_IP(192, 168, 4, 1);
static const IPAddress AP_GW(192, 168, 4, 1);
static const IPAddress AP_MASK(255, 255, 255, 0);

// BLE Service & Characteristic UUIDs
#define BLE_DEVICE_NAME        "Mobile_Tool_ESP32"
#define SERVICE_UUID           "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID_RX "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CHARACTERISTIC_UUID_TX "beb5483f-36e1-4688-b7f5-ea07361b26a8"

// Web & WebSocket Server
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// BLE Variables
BLEServer* pBleServer = nullptr;
BLECharacteristic* pTxCharacteristic = nullptr;
bool bleClientConnected = false;

// =========================
// Hardware Pins (ESP32-S3)
// =========================
static constexpr int UART_RX_PIN   = 16;
static constexpr int UART_TX_PIN   = 17;
static constexpr int I2C_SDA_PIN   = 21;
static constexpr int I2C_SCL_PIN   = 22;
static constexpr int DIODE_ADC_PIN = 4; // CRITICAL FIX: Pin 4 (ADC1) for ESP32-S3

// =========================
// App State & Buffers
// =========================
enum class AppMode : uint8_t {
  IDLE,
  DIODE,
  UART,
  I2C_SCANNER
};

static volatile AppMode currentMode = AppMode::IDLE;
static bool uartRunning = false;
static uint32_t uartBaud = 115200;
static unsigned long lastLiveProbeMs = 0;

// ADC Smoothing (Exponential Moving Average Filter)
static float emaVoltage = 0.0f;
static bool emaInitialized = false;
static constexpr float EMA_ALPHA = 0.3f; // Smoothing factor

// UART Data Batching Buffer
static String uartBatchBuffer = "";
static unsigned long lastUartSendMs = 0;

// =========================
// Helpers & Core Functions
// =========================

// Read ADC with 5-sample averaging + Exponential Moving Average (EMA) filter
static float readDiodeVoltageSmoothed() {
  uint32_t totalMv = 0;
  for (int i = 0; i < 5; i++) {
    totalMv += analogReadMilliVolts(DIODE_ADC_PIN);
    delayMicroseconds(100);
  }
  float currentV = (totalMv / 5.0f) / 1000.0f;

  if (!emaInitialized) {
    emaVoltage = currentV;
    emaInitialized = true;
  } else {
    emaVoltage = (EMA_ALPHA * currentV) + ((1.0f - EMA_ALPHA) * emaVoltage);
  }
  return emaVoltage;
}

// Send JSON string over both WebSocket and BLE
static void sendTextAll(const char* json) {
  // 1. WebSocket broadcast
  ws.textAll(json);

  // 2. BLE notify if client is connected
  if (bleClientConnected && pTxCharacteristic != nullptr) {
    pTxCharacteristic->setValue((uint8_t*)json, strlen(json));
    pTxCharacteristic->notify();
  }
}

static void sendDiodeValue(const char* type) {
  char out[128];
  float v = readDiodeVoltageSmoothed();
  snprintf(out, sizeof(out), "{\"type\":\"%s\",\"value\":\"%.2f\"}", type, v);
  sendTextAll(out);
}

static void sendLiveProbe() {
  char out[128];
  float v = readDiodeVoltageSmoothed();
  snprintf(out, sizeof(out), "{\"type\":\"live_probe\",\"value\":\"%.2f\"}", v);
  sendTextAll(out);
}

static void sendI2CScanResult() {
  StaticJsonDocument<1024> doc;
  doc["type"] = "i2c";
  JsonArray devices = doc.createNestedArray("devices");

  // Safe 7-bit I2C scanner
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    uint8_t error = Wire.endTransmission();
    if (error == 0) {
      char buf[8];
      snprintf(buf, sizeof(buf), "0x%02X", addr);
      devices.add(buf);
    }
  }

  char out[1024];
  size_t n = serializeJson(doc, out, sizeof(out));
  if (n > 0) {
    sendTextAll(out);
  }
}

static void startUart(uint32_t baud) {
  if (uartRunning) {
    Serial2.flush();
    Serial2.end();
    uartRunning = false;
  }

  uartBaud = baud;
  Serial2.begin(uartBaud, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  uartRunning = true;
  currentMode = AppMode::UART;
  uartBatchBuffer = "";
  lastUartSendMs = millis();
}

static void stopUart() {
  if (uartRunning) {
    Serial2.flush();
    Serial2.end();
    uartRunning = false;
  }

  uartBatchBuffer = "";
  if (currentMode == AppMode::UART) {
    currentMode = AppMode::IDLE;
  }
}

// Flush batched UART logs to protect communication buffer from crashing during fast boot logs
static void flushUartBatch() {
  if (uartBatchBuffer.length() == 0) return;

  StaticJsonDocument<1024> doc;
  doc["type"] = "uart_log";
  doc["log"] = uartBatchBuffer;

  char out[1024];
  size_t n = serializeJson(doc, out, sizeof(out));
  if (n > 0) {
    sendTextAll(out);
  }
  uartBatchBuffer = "";
  lastUartSendMs = millis();
}

static void processUartInput() {
  if (!uartRunning) return;

  while (Serial2.available() > 0) {
    char c = (char)Serial2.read();
    if (c == '\r') continue;

    uartBatchBuffer += c;
    // Batch threshold: flush if buffer reaches 512 chars
    if (uartBatchBuffer.length() >= 512) {
      flushUartBatch();
    }
  }

  // Time threshold: flush if 50ms passed and buffer is non-empty
  if (uartBatchBuffer.length() > 0 && (millis() - lastUartSendMs >= 50)) {
    flushUartBatch();
  }
}

static void setModeFromString(const char* mode) {
  if (!mode) {
    currentMode = AppMode::IDLE;
    return;
  }

  if (strcmp(mode, "diode") == 0) {
    currentMode = AppMode::DIODE;
    lastLiveProbeMs = 0; // Immediate trigger
  } else if (strcmp(mode, "uart") == 0) {
    currentMode = AppMode::UART;
  } else if (strcmp(mode, "i2c_scanner") == 0) {
    currentMode = AppMode::I2C_SCANNER;
  } else {
    currentMode = AppMode::IDLE;
  }
}

static void handleIncomingJson(uint8_t* data, size_t len) {
  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, data, len);
  if (err) return;

  const char* cmd = doc["cmd"] | nullptr;
  const char* command = doc["command"] | nullptr;

  if (command && strcmp(command, "set_mode") == 0) {
    const char* mode = doc["mode"] | nullptr;
    setModeFromString(mode);
    return;
  }

  if (!cmd) return;

  if (strcmp(cmd, "diode") == 0) {
    sendDiodeValue("diode");
    return;
  }

  if (strcmp(cmd, "i2c") == 0) {
    currentMode = AppMode::I2C_SCANNER;
    sendI2CScanResult();
    return;
  }

  if (strcmp(cmd, "uart_start") == 0) {
    uint32_t baud = doc["baud"] | 115200;
    startUart(baud);
    return;
  }

  if (strcmp(cmd, "uart_stop") == 0) {
    stopUart();
    return;
  }
}

// =========================
// BLE Callbacks
// =========================
class BleServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override {
      bleClientConnected = true;
      Serial.println("BLE Client Connected");
    }

    void onDisconnect(BLEServer* pServer) override {
      bleClientConnected = false;
      Serial.println("BLE Client Disconnected, restarting advertising...");
      BLEDevice::startAdvertising();
    }
};

class BleRxCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) override {
      std::string rxValue = pCharacteristic->getValue();
      if (rxValue.length() > 0) {
        handleIncomingJson((uint8_t*)rxValue.data(), rxValue.length());
      }
    }
};

// =========================
// WebSocket Callback
// =========================
static void onWsEvent(AsyncWebSocket* serverPtr,
                      AsyncWebSocketClient* client,
                      AwsEventType type,
                      void* arg,
                      uint8_t* data,
                      size_t len) {
  (void)serverPtr;
  (void)client;

  switch (type) {
    case WS_EVT_CONNECT:
      Serial.println("WebSocket Client Connected");
      break;
    case WS_EVT_DISCONNECT:
      Serial.println("WebSocket Client Disconnected");
      break;
    case WS_EVT_DATA: {
      AwsFrameInfo* info = (AwsFrameInfo*)arg;
      if (!info) return;
      if (info->opcode == WS_TEXT && info->final && info->index == 0 && info->len == len) {
        handleIncomingJson(data, len);
      }
      break;
    }
    default:
      break;
  }
}

// =========================
// Arduino Setup & Loop
// =========================
void setup() {
  Serial.begin(115200);
  delay(300);

  // ADC setup for diode measurement (ESP32-S3 Pin 4 / ADC1)
  analogReadResolution(12);
  analogSetPinAttenuation(DIODE_ADC_PIN, ADC_11db);
  pinMode(DIODE_ADC_PIN, INPUT);

  // I2C setup
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(100000);

  // Wi-Fi SoftAP
  WiFi.mode(WIFI_AP);
  WiFi.setSleep(false);
  WiFi.softAPConfig(AP_IP, AP_GW, AP_MASK);

  bool apOk = WiFi.softAP(AP_SSID, AP_PASSWORD);
  if (!apOk) {
    Serial.println("SoftAP start failed");
  }
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  // WebSocket Server Setup
  ws.onEvent(onWsEvent);
  server.addHandler(&ws);

  server.on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
    request->send(200, "text/plain", "ESP32 Diagnostic Tool Running");
  });

  server.begin();
  Serial.println("HTTP + WebSocket Server Started");

  // BLE Server Setup
  BLEDevice::init(BLE_DEVICE_NAME);
  pBleServer = BLEDevice::createServer();
  pBleServer->setCallbacks(new BleServerCallbacks());

  BLEService *pService = pBleServer->createService(SERVICE_UUID);

  pTxCharacteristic = pService->createCharacteristic(
                        CHARACTERISTIC_UUID_TX,
                        BLECharacteristic::PROPERTY_NOTIFY
                      );
  pTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic *pRxCharacteristic = pService->createCharacteristic(
                                           CHARACTERISTIC_UUID_RX,
                                           BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
                                         );
  pRxCharacteristic->setCallbacks(new BleRxCallbacks());

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("BLE Server Advertising Started");

  currentMode = AppMode::IDLE;
}

void loop() {
  ws.cleanupClients();

  // Stream live probe voltage every 100ms in Diode Mode
  if (currentMode == AppMode::DIODE) {
    unsigned long now = millis();
    if (now - lastLiveProbeMs >= 100) {
      lastLiveProbeMs = now;
      sendLiveProbe();
    }
  }

  // Continuously process and batch UART logs
  processUartInput();

  delay(1);
}
