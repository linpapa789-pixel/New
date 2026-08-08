#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <Wire.h>

// =========================
// Wi-Fi / WebSocket Settings
// =========================
static const char* AP_SSID     = "ESP_Diag_Tool";
static const char* AP_PASSWORD = "password123";

static const IPAddress AP_IP(192, 168, 4, 1);
static const IPAddress AP_GW(192, 168, 4, 1);
static const IPAddress AP_MASK(255, 255, 255, 0);

// WebSocket endpoint: ws://192.168.4.1:80/ws
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// =========================
// Hardware Pins
// =========================
static constexpr int UART_RX_PIN  = 16;
static constexpr int UART_TX_PIN  = 17;
static constexpr int I2C_SDA_PIN  = 21;
static constexpr int I2C_SCL_PIN  = 22;
static constexpr int DIODE_ADC_PIN = 32;

// =========================
// State
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

// UART line buffer for log forwarding
static char uartLine[256];
static size_t uartLineLen = 0;

// =========================
// Helpers
// =========================
static float readDiodeVoltage() {
  // Reads the ADC and converts to volts.
  // analogReadMilliVolts() is supported by current ESP32 Arduino cores.
  uint32_t mv = analogReadMilliVolts(DIODE_ADC_PIN);
  return mv / 1000.0f;
}

static void sendTextAll(const char* json) {
  // AsyncWebSocket manages client lifetimes internally.
  // cleanupClients() is called in loop() to avoid stale references.
  ws.textAll(json);
}

static void sendDiodeValue(const char* type) {
  char out[128];
  float v = readDiodeVoltage();
  snprintf(out, sizeof(out), "{\"type\":\"%s\",\"value\":\"%.2f\"}", type, v);
  sendTextAll(out);
}

static void sendLiveProbe() {
  char out[128];
  float v = readDiodeVoltage();
  snprintf(out, sizeof(out), "{\"type\":\"live_probe\",\"value\":\"%.2f\"}", v);
  sendTextAll(out);
}

static void sendI2CScanResult() {
  // Typical device counts are small, so 1KB is enough for practical use.
  StaticJsonDocument<1024> doc;
  doc["type"] = "i2c";
  JsonArray devices = doc.createNestedArray("devices");

  // Scan standard 7-bit address range.
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

  // Serial2 on ESP32-S3 with explicit RX/TX pins.
  Serial2.begin(uartBaud, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  uartRunning = true;
  currentMode = AppMode::UART;
}

static void stopUart() {
  if (uartRunning) {
    Serial2.flush();
    Serial2.end();
    uartRunning = false;
  }

  uartLineLen = 0;
  if (currentMode == AppMode::UART) {
    currentMode = AppMode::IDLE;
  }
}

static void sendUartLog(const char* line) {
  StaticJsonDocument<384> doc;
  doc["type"] = "uart_log";
  doc["log"] = line;

  char out[384];
  size_t n = serializeJson(doc, out, sizeof(out));
  if (n > 0) {
    sendTextAll(out);
  }
}

static void processUartInput() {
  if (!uartRunning) return;

  while (Serial2.available() > 0) {
    char c = (char)Serial2.read();

    if (c == '\r') {
      continue;
    }

    if (c == '\n') {
      if (uartLineLen > 0) {
        uartLine[uartLineLen] = '\0';
        sendUartLog(uartLine);
        uartLineLen = 0;
      }
      continue;
    }

    if (uartLineLen < sizeof(uartLine) - 1) {
      uartLine[uartLineLen++] = c;
    } else {
      // Buffer full: flush partial line to avoid losing long streams completely.
      uartLine[uartLineLen] = '\0';
      sendUartLog(uartLine);
      uartLineLen = 0;
    }
  }
}

static void setModeFromString(const char* mode) {
  if (!mode) {
    currentMode = AppMode::IDLE;
    return;
  }

  if (strcmp(mode, "diode") == 0) {
    currentMode = AppMode::DIODE;
    lastLiveProbeMs = 0; // send immediately after mode switch
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
  if (err) {
    return;
  }

  // Support both shapes requested by the app:
  // 1) {"cmd":"..."}
  // 2) {"command":"set_mode","mode":"..."}
  const char* cmd = doc["cmd"] | nullptr;
  const char* command = doc["command"] | nullptr;

  if (command && strcmp(command, "set_mode") == 0) {
    const char* mode = doc["mode"] | nullptr;
    setModeFromString(mode);
    return;
  }

  if (!cmd) {
    return;
  }

  if (strcmp(cmd, "diode") == 0) {
    // One-shot diode reading
    sendDiodeValue("diode");
    // If the UI has already set mode to diode, loop() will stream live probes.
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
      // No per-client state is allocated, which helps avoid leaks.
      break;

    case WS_EVT_DISCONNECT:
      // AsyncWebSocket cleans up client objects internally.
      break;

    case WS_EVT_DATA: {
      AwsFrameInfo* info = (AwsFrameInfo*)arg;
      if (!info) return;

      // Handle only complete text frames.
      if (info->opcode == WS_TEXT && info->final && info->index == 0 && info->len == len) {
        handleIncomingJson(data, len);
      }
      break;
    }

    case WS_EVT_ERROR:
    case WS_EVT_PONG:
    case WS_EVT_BIN:
    default:
      break;
  }
}

// =========================
// Arduino Setup / Loop
// =========================
void setup() {
  Serial.begin(115200);
  delay(300);

  // ADC setup for diode measurement
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

  // WebSocket
  ws.onEvent(onWsEvent);
  server.addHandler(&ws);

  // Optional health endpoint
  server.on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
    request->send(200, "text/plain",
                  "ESP32 Diagnostic Tool running. Connect to ws://192.168.4.1:80/ws");
  });

  server.begin();
  Serial.println("HTTP + WebSocket server started");

  currentMode = AppMode::IDLE;
}

void loop() {
  ws.cleanupClients();

  // Live probe streaming every 100ms when UI is in diode mode
  if (currentMode == AppMode::DIODE) {
    unsigned long now = millis();
    if (now - lastLiveProbeMs >= 100) {
      lastLiveProbeMs = now;
      sendLiveProbe();
    }
  }

  // Forward UART logs continuously
  processUartInput();

  delay(1);
}
