# ESP32-S3 + Raspberry Pi Pico Diagnostic Tool Architecture

## Overview
To build the ultimate mobile phone repair diagnostic tool, we are combining the strengths of two powerful microcontrollers:
1. **ESP32-S3**: Acts as the Wireless Communication Hub (Wi-Fi/BLE) and handles OTA updates, WebSockets, and overall system management.
2. **Raspberry Pi Pico (RP2040)**: Acts as the Precision Co-Processor. The RP2040 has highly accurate ADCs, Programmable I/O (PIO) for high-speed logic analysis, and robust hardware PWM/Timers.

## Hardware Connection
The ESP32-S3 and Pico communicate with each other via a high-speed UART link.

```text
[ Android App ] <--(Wi-Fi / BLE)--> [ ESP32-S3 ] <--(UART Bridge)--> [ Raspberry Pi Pico ]
```

### Wiring Between ESP32-S3 and Pico:
- **ESP32 TX (Pin 17)**  -> **Pico RX (Pin 1)**
- **ESP32 RX (Pin 16)**  -> **Pico TX (Pin 0)**
- **ESP32 GND** -> **Pico GND**
- *(Optional)* ESP32 3.3V -> Pico 3V3 (If powering Pico from ESP32, ensure ESP32 regulator can handle the load).

### Pico Pinout (Probing Interface):
- **Pin 26 (ADC0)**: Diode / Voltage Measurement (Highly accurate 12-bit ADC).
- **Pin 15 (PWM)**: PWM Signal Injector (To test LCD backlights, charge pumps, etc.).
- **Pin 16 (Digital In)**: Clock / Frequency Counter.
- **Pin 4 (SDA), Pin 5 (SCL)**: I2C Scanner for checking dead I2C lines (Touch, FaceID, Cameras).
- **Pin 2, 3 (UART1)**: Target Device UART Monitor (Reading boot logs from dead phones).

## Features & Capabilities
1. **Precision Diode/Voltage Mode**: Using Pico's 12-bit ADC for accurate voltage drop measurements.
2. **PWM Signal Injector**: Generate precise PWM signals (adjustable frequency & duty cycle) to force-enable circuits like backlight drivers.
3. **High-Speed Clock Counter**: Measure oscillators (e.g., 32.768kHz sleep clocks, 19.2MHz main clocks) reliably.
4. **I2C & SPI Scanning**: Detect if slave devices on the phone's logic board are responding.
5. **Logic Analyzer (Future)**: Using Pico's PIO to capture fast boot sequences and analyze protocols.

## Software Architecture
- **Pico Firmware (Arduino/C++)**: Listens for JSON commands on UART0, executes hardware measurements, and replies with JSON data.
- **ESP32 Firmware**: Manages the Wi-Fi Access Point/BLE, WebSocket server, and acts as a transparent bridge, passing JSON back and forth between the App and the Pico.
- **Android App**: The main user interface with real-time graphs, advanced controls for PWM, and organized data visualization.
