# ESP32 Diagnostic Tool - Hardware & Software Guidelines

## 1. Overview
This tool is a comprehensive diagnostic toolkit using an ESP32-S3 microcontroller, paired with an Android Application for real-time monitoring and control. It supports multiple diagnostic modes including:
- **Diode/Voltage Probe:** Measures voltages up to ~3.3V (with ADC) and detects short circuits.
- **UART Monitor:** Reads serial data and displays logs on the app.
- **I2C Scanner:** Scans the I2C bus for connected devices.
- **Clock Frequency Monitor (NEW):** Measures the frequency of an incoming signal (e.g., clock signals, PWM, oscillators).

## 2. Hardware Diagram & Pinout

### ESP32-S3 Pin Configuration:
- **Pin 4 (ADC1):** Diode/Voltage Probe input. *Connect to the test point to measure voltage.*
- **Pin 5 (Digital Input):** Clock/Frequency Probe input. *Connect to the clock signal source to measure its frequency in Hz.*
- **Pin 21 (SDA):** I2C Data Line.
- **Pin 22 (SCL):** I2C Clock Line.
- **TX/RX (Hardware Serial2):** Used for UART logging (Default RX=16, TX=17 on standard ESP32, but verify for your specific S3 board).

### Basic Wiring Diagram:
```text
[ ESP32-S3 Board ]
       |
       |-- (Pin 4)  -----[ Probe 1 ]---> Test Point (Voltage/Diode)
       |
       |-- (Pin 5)  -----[ Probe 2 ]---> Test Point (Clock/PWM Signal)
       |
       |-- (Pin 21) -----> I2C SDA (Target Device)
       |-- (Pin 22) -----> I2C SCL (Target Device)
       |
       |-- (GND)    -----> Common Ground (Target Device GND)
```

**⚠️ Important Hardware Notes:**
1. **Voltage Limit:** ESP32 ADC pins can only measure up to **3.3V**. Do NOT connect Pin 4 or Pin 5 to voltages higher than 3.3V without a voltage divider, as it will damage the ESP32.
2. **Common Ground:** Always connect the GND of the ESP32 to the GND of the circuit you are testing.
3. **Pull-Down Resistor:** Pin 5 is configured with an internal pull-down resistor (`INPUT_PULLDOWN`) for the Clock probe to prevent floating signals when disconnected.

## 3. Clock Frequency Monitor (Details)
### How it works:
- **Hardware Interrupt:** Pin 5 triggers a hardware interrupt on the `RISING` edge of the incoming signal.
- **Counting:** The ISR (Interrupt Service Routine) safely increments a pulse counter using FreeRTOS critical sections.
- **Measurement:** Every 500ms, the ESP32 calculates the frequency (`freq = (count * 1000) / elapsed_time`) and sends a JSON packet to the app: `{"type":"clock","freq":1000}`.
- **App UI:** The Android app receives this packet and displays it in real-time in the new **Clock** tab, with a sleek digital readout.

## 4. Short Circuit Detection (Diode Mode)
- In Diode Mode, if the voltage measured on Pin 4 drops below **0.05V**, the Android App will automatically trigger a continuous warning beep to indicate a short circuit to Ground.

## 5. Connectivity
- **Wi-Fi Mode:** The ESP32 creates a Hotspot named `ESP_Diag_Tool` (Password: `12345678`). Connect your phone to this network and use the App's Settings to connect via WebSocket (Default IP: `192.168.4.1`, Port: `81`).
- **Bluetooth (BLE) Mode:** The ESP32 advertises as `Mobile_Tool_ESP32`. You can connect to it directly through the App's Tool tab.

## 6. App Usage
- **Tools Tab:** Switch between Diode, UART, and I2C modes. Monitor voltage and short circuits.
- **Clock Tab:** Dedicated UI to view the live frequency of the signal connected to Pin 5.
- **Flash Tab:** OTA (Over-The-Air) flashing utility.
- **Status Tab:** View system logs, UART raw logs, and export them.
- **Settings Tab:** Configure Wi-Fi IP/Port, toggle Dark mode, and read basic instructions.
