#include <Arduino.h>
#include <Wire.h>
#include <ArduinoJson.h>

// --- PIN DEFINITIONS ---
// UART to ESP32 (Using Serial1)
#define ESP_TX_PIN 0 // Pico TX -> ESP32 RX
#define ESP_RX_PIN 1 // Pico RX -> ESP32 TX

// Diagnostic Pins
#define DIODE_ADC_PIN 26 // A0
#define PWM_OUT_PIN 15
#define I2C_SDA_PIN 4
#define I2C_SCL_PIN 5
#define CLOCK_IN_PIN 16

// Current Mode
enum Mode {
  MODE_IDLE,
  MODE_DIODE,
  MODE_UART,
  MODE_I2C,
  MODE_CLOCK,
  MODE_PWM
};

Mode currentMode = MODE_IDLE;
unsigned long lastDiodeRead = 0;
bool isPwmRunning = false;

// Function Prototypes
void processCommand(String jsonStr);
void sendDiodeValue();
void scanI2C();

void setup() {
  // Built-in USB Serial for debug (optional)
  Serial.begin(115200);
  
  // UART connection to ESP32
  Serial1.setTX(ESP_TX_PIN);
  Serial1.setRX(ESP_RX_PIN);
  Serial1.begin(115200);

  // Pin Setups
  pinMode(DIODE_ADC_PIN, INPUT);
  pinMode(PWM_OUT_PIN, OUTPUT);
  digitalWrite(PWM_OUT_PIN, LOW);
  
  // Wire for I2C scanner
  Wire.setSDA(I2C_SDA_PIN);
  Wire.setSCL(I2C_SCL_PIN);
  Wire.begin();

  Serial1.println("{\"status\": \"Pico Initialized\"}");
}

void loop() {
  // 1. Check for incoming commands from ESP32
  if (Serial1.available()) {
    String cmd = Serial1.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() > 0) {
      processCommand(cmd);
    }
  }

  // 2. Perform background tasks based on current mode
  unsigned long currentMillis = millis();
  
  if (currentMode == MODE_DIODE) {
    if (currentMillis - lastDiodeRead > 200) { // Read every 200ms
      sendDiodeValue();
      lastDiodeRead = currentMillis;
    }
  }
}

void processCommand(String jsonStr) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, jsonStr);
  
  if (error) {
    // Not valid JSON or parse error
    return;
  }

  const char* cmd = doc["cmd"];
  if (cmd == nullptr) return;

  if (strcmp(cmd, "set_mode") == 0) {
    const char* modeStr = doc["mode"];
    if (modeStr != nullptr) {
      if (strcmp(modeStr, "DIODE") == 0) {
        currentMode = MODE_DIODE;
        // Disable PWM if switching away
        if (isPwmRunning) { analogWrite(PWM_OUT_PIN, 0); isPwmRunning = false; }
      } else if (strcmp(modeStr, "PWM") == 0) {
        currentMode = MODE_PWM;
      } else if (strcmp(modeStr, "I2C") == 0) {
        currentMode = MODE_I2C;
      } else if (strcmp(modeStr, "UART") == 0) {
        currentMode = MODE_UART;
      } else if (strcmp(modeStr, "CLOCK") == 0) {
        currentMode = MODE_CLOCK;
      } else {
        currentMode = MODE_IDLE;
      }
    }
  } 
  else if (strcmp(cmd, "pwm_start") == 0) {
    if (currentMode == MODE_PWM) {
      int freq = doc["freq"] | 1000;
      int duty = doc["duty"] | 50;
      
      analogWriteFreq(freq);
      // Pico analogWrite uses 0-255 by default, calculate duty
      int pwmVal = (duty * 255) / 100;
      analogWrite(PWM_OUT_PIN, pwmVal);
      isPwmRunning = true;
    }
  }
  else if (strcmp(cmd, "pwm_stop") == 0) {
    analogWrite(PWM_OUT_PIN, 0);
    isPwmRunning = false;
  }
  else if (strcmp(cmd, "i2c_scan") == 0) {
    scanI2C();
  }
}

void sendDiodeValue() {
  // Read 12-bit ADC (Pico's native resolution is 12-bit, default analogRead range is 0-1023 or 0-4095 depending on core)
  // Let's assume standard 10-bit Arduino analogRead (0-1023) or force 12-bit
  analogReadResolution(12); // 0 - 4095
  int rawAdc = analogRead(DIODE_ADC_PIN);
  
  // Assuming 3.3V reference
  float voltage = (rawAdc / 4095.0) * 3.3;
  
  StaticJsonDocument<128> doc;
  
  // Format for the app - send 3 decimal places
  // If no connection/open loop, might read high (near 3.3V)
  if (voltage > 3.0) {
    doc["diode"] = "OL";
  } else {
    // Send exact float value to be parsed by the App
    // We send as a string to maintain formatting, or the app can parse the float
    // We'll send it as a number (float)
    doc["diode"] = String(voltage, 3); 
  }
  
  String output;
  serializeJson(doc, output);
  Serial1.println(output);
}

void scanI2C() {
  byte error, address;
  int nDevices = 0;
  
  StaticJsonDocument<512> doc;
  JsonArray results = doc.createNestedArray("i2c_scan_result");

  for(address = 1; address < 127; address++ ) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    if (error == 0) {
      char hexAddr[5];
      sprintf(hexAddr, "0x%02X", address);
      results.add(hexAddr);
      nDevices++;
    }
  }
  
  String output;
  serializeJson(doc, output);
  Serial1.println(output);
}
