#include <Arduino.h>
#include <Wire.h>

// =========================
// PICO PINS
// =========================
static constexpr int UART0_TX_PIN = 0; // To ESP32 RX
static constexpr int UART0_RX_PIN = 1; // To ESP32 TX

static constexpr int TARGET_UART_TX = 2; // Target TX (Not used for receiving, just for completeness)
static constexpr int TARGET_UART_RX = 3; // Target Boot Logs

static constexpr int I2C_SDA_PIN = 4;
static constexpr int I2C_SCL_PIN = 5;

static constexpr int PWM_INJECT_PIN = 15;
static constexpr int CLOCK_PROBE_PIN = 16;
static constexpr int DIODE_ADC_PIN = 26; // ADC0

// =========================
// STATE
// =========================
enum class AppMode {
    IDLE,
    DIODE,
    UART_MONITOR,
    I2C_SCANNER,
    CLOCK,
    PWM_INJECT
};

AppMode currentMode = AppMode::IDLE;

// Clock variables
volatile uint32_t pulseCount = 0;
unsigned long lastClockMeasureMs = 0;

// UART Buffer
String jsonBuffer = "";
String targetLogBuffer = "";
unsigned long lastTargetLogMs = 0;

void clockIsr() {
    pulseCount++;
}

void setup() {
    // Communication with ESP32
    Serial1.setTX(UART0_TX_PIN);
    Serial1.setRX(UART0_RX_PIN);
    Serial1.begin(115200);

    // Target UART
    Serial2.setTX(TARGET_UART_TX);
    Serial2.setRX(TARGET_UART_RX);
    Serial2.begin(115200);

    // ADC Resolution (Pico supports 12-bit)
    analogReadResolution(12);

    // Pins
    pinMode(CLOCK_PROBE_PIN, INPUT_PULLDOWN);
    pinMode(PWM_INJECT_PIN, OUTPUT);
    digitalWrite(PWM_INJECT_PIN, LOW);
}

void handleCommand(String json) {
    if (json.indexOf("\"command\":\"set_mode\"") > 0) {
        if (json.indexOf("\"mode\":\"diode\"") > 0) {
            currentMode = AppMode::DIODE;
            digitalWrite(PWM_INJECT_PIN, LOW);
        } else if (json.indexOf("\"mode\":\"uart\"") > 0) {
            currentMode = AppMode::UART_MONITOR;
        } else if (json.indexOf("\"mode\":\"i2c_scanner\"") > 0) {
            currentMode = AppMode::I2C_SCANNER;
        } else if (json.indexOf("\"mode\":\"clock\"") > 0) {
            currentMode = AppMode::CLOCK;
            pulseCount = 0;
            attachInterrupt(digitalPinToInterrupt(CLOCK_PROBE_PIN), clockIsr, RISING);
        } else if (json.indexOf("\"mode\":\"pwm\"") > 0) {
            currentMode = AppMode::PWM_INJECT;
            // Basic PWM set, default 1kHz 50%
            analogWriteFreq(1000);
            analogWrite(PWM_INJECT_PIN, 127); // 8-bit default PWM on Pico Arduino core
        } else {
            currentMode = AppMode::IDLE;
        }
    }
}

void loop() {
    // Read from ESP32
    while (Serial1.available()) {
        char c = Serial1.read();
        if (c == '\n') {
            handleCommand(jsonBuffer);
            jsonBuffer = "";
        } else {
            jsonBuffer += c;
        }
    }

    // Execute Mode Actions
    unsigned long now = millis();

    if (currentMode == AppMode::DIODE) {
        if (now - lastClockMeasureMs >= 200) {
            lastClockMeasureMs = now;
            // 12-bit ADC = 4095. Max Voltage = 3.3V
            int raw = analogRead(DIODE_ADC_PIN);
            float voltage = (raw / 4095.0) * 3.3;
            Serial1.printf("{\"type\":\"diode\",\"v\":%.4f}\n", voltage);
        }
    }
    else if (currentMode == AppMode::CLOCK) {
        if (now - lastClockMeasureMs >= 500) {
            uint32_t count = pulseCount;
            pulseCount = 0;
            uint32_t elapsed = now - lastClockMeasureMs;
            lastClockMeasureMs = now;
            uint32_t freq = (count * 1000) / elapsed;
            Serial1.printf("{\"type\":\"clock\",\"freq\":%lu}\n", freq);
        }
    }
    else if (currentMode == AppMode::I2C_SCANNER) {
        // Run once then idle
        Wire.setSDA(I2C_SDA_PIN);
        Wire.setSCL(I2C_SCL_PIN);
        Wire.begin();
        
        String devices = "[";
        bool first = true;
        for (byte address = 1; address < 127; address++) {
            Wire.beginTransmission(address);
            byte error = Wire.endTransmission();
            if (error == 0) {
                if (!first) devices += ",";
                char hexStr[8];
                snprintf(hexStr, sizeof(hexStr), "\"0x%02X\"", address);
                devices += hexStr;
                first = false;
            }
        }
        devices += "]";
        Serial1.printf("{\"type\":\"i2c_result\",\"devices\":%s}\n", devices.c_str());
        currentMode = AppMode::IDLE;
    }
    else if (currentMode == AppMode::UART_MONITOR) {
        // Read Target Logs
        while (Serial2.available()) {
            char c = Serial2.read();
            targetLogBuffer += c;
        }
        if (targetLogBuffer.length() > 0 && now - lastTargetLogMs > 50) {
            // Escape JSON safely
            String escaped = targetLogBuffer;
            escaped.replace("\\", "\\\\");
            escaped.replace("\"", "\\\"");
            escaped.replace("\n", "\\n");
            escaped.replace("\r", "\\r");
            
            Serial1.printf("{\"type\":\"uart\",\"log\":\"%s\"}\n", escaped.c_str());
            targetLogBuffer = "";
            lastTargetLogMs = now;
        }
    }
}
