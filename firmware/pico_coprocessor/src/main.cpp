#include <Arduino.h>
#include <Wire.h>
#include <ArduinoJson.h>

// =========================
// PIN DEFINITIONS
// =========================
// UART0: ESP32 သို့ ချိတ်ဆက်ရန်
#define ESP_TX_PIN 0 // Pico ၏ TX -> ESP32 ၏ RX (Pin 18)
#define ESP_RX_PIN 1 // Pico ၏ RX -> ESP32 ၏ TX (Pin 19)

// UART1: Target Device (ဖုန်း) မှ Log များဖတ်ရန်
#define TARGET_UART_TX 8 // Target ၏ RX သို့
#define TARGET_UART_RX 9 // Target ၏ TX မှ

// Diagnostic Pins များ
#define DIODE_ADC_PIN 26 // ADC0 (Pin 26)
#define PWM_OUT_PIN 15   // PWM ထုတ်လွှင့်ရန် (Pin 15)
#define I2C_SDA_PIN 4    // I2C SDA (Pin 4)
#define I2C_SCL_PIN 5    // I2C SCL (Pin 5)
#define CLOCK_IN_PIN 16  // Frequency တိုင်းရန် (Pin 16)

// =========================
// STATE VARIABLES
// =========================
enum Mode {
  MODE_IDLE,
  MODE_DIODE,
  MODE_UART,
  MODE_I2C,
  MODE_CLOCK,
  MODE_PWM
};

Mode currentMode = MODE_IDLE;
unsigned long lastMeasureMs = 0;
bool isPwmRunning = false;

// Clock Variables
volatile uint32_t pulseCount = 0;
void clockIsr() {
    pulseCount++;
}

// UART Log Buffer
String targetLogBuffer = "";

// Function Prototypes
void processCommand(String jsonStr);
void sendLiveProbeValue();
void scanI2C();
void flushTargetLogs();

void setup() {
  Serial.begin(115200); // USB Debug
  
  // ESP32 နှင့် ချိတ်ဆက်ရန် UART0 (115200 Baud)
  Serial1.setTX(ESP_TX_PIN);
  Serial1.setRX(ESP_RX_PIN);
  Serial1.begin(115200);

  // Target Device မှ Log ဖတ်ရန် UART1 (115200 Baud)
  Serial2.setTX(TARGET_UART_TX);
  Serial2.setRX(TARGET_UART_RX);
  Serial2.begin(115200);

  // ADC Resolution ကို Pico ၏ အမြင့်ဆုံး 12-bit (0-4095) သို့ ပြောင်းရန်
  analogReadResolution(12); 
  pinMode(DIODE_ADC_PIN, INPUT);
  
  pinMode(PWM_OUT_PIN, OUTPUT);
  digitalWrite(PWM_OUT_PIN, LOW);

  pinMode(CLOCK_IN_PIN, INPUT_PULLDOWN);

  Serial1.println("{\"status\": \"Pico Initialized\"}");
}

void loop() {
  // ၁။ ESP32 မှတဆင့် App ဆီမှ လာသော Command များကို ဖတ်ရန်
  if (Serial1.available()) {
    String cmd = Serial1.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() > 0) {
      processCommand(cmd);
    }
  }

  // ၂။ လက်ရှိ ရွေးချယ်ထားသော Mode အလိုက် အလုပ်လုပ်ရန်
  unsigned long currentMillis = millis();
  
  if (currentMode == MODE_DIODE) {
    if (currentMillis - lastMeasureMs >= 200) { // ၂၀၀ မီလီစက္ကန့် တခါ တိုင်းမည်
      sendLiveProbeValue();
      lastMeasureMs = currentMillis;
    }
  }
  else if (currentMode == MODE_CLOCK) {
    if (currentMillis - lastMeasureMs >= 500) { // ၅၀၀ မီလီစက္ကန့် တခါ တိုင်းမည်
      uint32_t count = pulseCount;
      pulseCount = 0;
      uint32_t elapsed = currentMillis - lastMeasureMs;
      uint32_t freq = (count * 1000) / elapsed;
      
      StaticJsonDocument<128> doc;
      doc["type"] = "clock";
      doc["freq"] = freq;
      String output;
      serializeJson(doc, output);
      Serial1.println(output);
      
      lastMeasureMs = currentMillis;
    }
  }
  else if (currentMode == MODE_UART) {
    while (Serial2.available()) {
      char c = Serial2.read();
      targetLogBuffer += c;
      
      // Buffer Memory ကို ၅၁၂ လုံးထိသာ ကန့်သတ်ထားသည် (Memory မပြည့်စေရန်)
      if (targetLogBuffer.length() >= 512) {
        flushTargetLogs();
      }
    }
    // Buffer ထဲတွင် စာကျန်နေပြီး အချိန် ၅၀ မီလီစက္ကန့် ကြာသွားပါက ပို့မည်
    if (targetLogBuffer.length() > 0 && currentMillis - lastMeasureMs > 50) {
      flushTargetLogs();
      lastMeasureMs = currentMillis;
    }
  }
}

// App မှ Command များကို JSON ဖြင့် ခွဲခြမ်းစိတ်ဖြာခြင်း
void processCommand(String jsonStr) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, jsonStr);
  if (error) return;

  const char* cmd = doc["command"];
  if (cmd == nullptr) return;

  if (strcmp(cmd, "set_mode") == 0) {
    const char* modeStr = doc["mode"];
    if (modeStr == nullptr) return;

    if (strcmp(modeStr, "diode") == 0) {
      currentMode = MODE_DIODE;
      if (isPwmRunning) { analogWrite(PWM_OUT_PIN, 0); isPwmRunning = false; }
    } 
    else if (strcmp(modeStr, "pwm") == 0) {
      currentMode = MODE_PWM;
      int freq = doc["freq"] | 1000;
      int duty = doc["duty"] | 50;
      
      // PWM ထုတ်လွှင့်ခြင်း
      analogWriteFreq(freq); 
      int pwmVal = (duty * 255) / 100;
      analogWrite(PWM_OUT_PIN, pwmVal);
      isPwmRunning = true;
    } 
    else if (strcmp(modeStr, "i2c_scanner") == 0) {
      currentMode = MODE_I2C;
      scanI2C();
      currentMode = MODE_IDLE; // တစ်ခါ Scan ပြီးလျှင် ရပ်မည်
    } 
    else if (strcmp(modeStr, "uart") == 0) {
      currentMode = MODE_UART;
      targetLogBuffer = "";
    } 
    else if (strcmp(modeStr, "clock") == 0) {
      currentMode = MODE_CLOCK;
      pulseCount = 0;
      attachInterrupt(digitalPinToInterrupt(CLOCK_IN_PIN), clockIsr, RISING);
      lastMeasureMs = millis();
    } 
    else {
      currentMode = MODE_IDLE;
    }
  }
}

// Diode (Live Probe) တန်ဖိုး ဖတ်ရန်
void sendLiveProbeValue() {
  int rawAdc = analogRead(DIODE_ADC_PIN);
  float voltage = (rawAdc / 4095.0) * 3.3; // 12-bit ADC / 3.3V Ref
  
  StaticJsonDocument<128> doc;
  doc["type"] = "live_probe"; 
  
  if (voltage > 3.0) {
    doc["value"] = "OL"; // Open Loop / ချိတ်ဆက်မထားပါ
  } else {
    doc["value"] = String(voltage, 3); // ၃ နေရာထိ ဖြတ်၍ပို့မည်
  }
  
  String output;
  serializeJson(doc, output);
  Serial1.println(output);
}

// I2C Device များ ရှာဖွေရန်
void scanI2C() {
  Wire.setSDA(I2C_SDA_PIN);
  Wire.setSCL(I2C_SCL_PIN);
  Wire.begin();
  
  StaticJsonDocument<512> doc;
  doc["type"] = "i2c"; 
  JsonArray devices = doc.createNestedArray("devices");

  for(byte address = 1; address < 127; address++ ) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      char hexAddr[8];
      sprintf(hexAddr, "0x%02X", address);
      devices.add(hexAddr);
    }
  }
  
  String output;
  serializeJson(doc, output);
  Serial1.println(output);
}

// Target Board မှ Log များကို ESP32 (App) သို့ ပို့ရန်
void flushTargetLogs() {
  if (targetLogBuffer.length() == 0) return;
  
  // JSON အတွက် Special Character များ (", \) ကို Escape လုပ်ခြင်း
  String escaped = targetLogBuffer;
  escaped.replace("\\", "\\\\");
  escaped.replace("\"", "\\\"");
  escaped.replace("\n", "\\n");
  escaped.replace("\r", "\\r");
  
  Serial1.printf("{\"type\":\"uart\",\"log\":\"%s\"}\n", escaped.c_str());
  targetLogBuffer = "";
}
