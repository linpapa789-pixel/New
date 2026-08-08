#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsServer.h>

// Wi-Fi AP Credentials
const char* ssid = "ESP_Pico_Diag";
const char* password = "";

// WebSocket Server on port 81
WebSocketsServer webSocket = WebSocketsServer(81);

// UART for communicating with Pi Pico
// ESP32-S3 TX = 17, RX = 16
HardwareSerial PicoSerial(1);

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[%u] Disconnected!\n", num);
            break;
        case WStype_CONNECTED: {
            IPAddress ip = webSocket.remoteIP(num);
            Serial.printf("[%u] Connected from %d.%d.%d.%d url: %s\n", num, ip[0], ip[1], ip[2], ip[3], payload);
            webSocket.sendTXT(num, "{\"status\": \"connected\", \"device\": \"ESP32-S3 Bridge\"}");
        }
            break;
        case WStype_TEXT:
            // Received JSON from Android App -> Forward to Pico
            Serial.printf("App: %s\n", payload);
            PicoSerial.println((char*)payload);
            break;
        case WStype_BIN:
            break;
    }
}

void setup() {
    Serial.begin(115200); // Debug serial
    
    // Initialize UART to Pico (Baud rate 115200, TX=17, RX=16)
    PicoSerial.begin(115200, SERIAL_8N1, 16, 17);

    Serial.println("\nStarting ESP32-S3 Bridge...");

    // Setup Wi-Fi Access Point
    WiFi.softAP(ssid, password);
    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);

    // Start WebSocket Server
    webSocket.begin();
    webSocket.onEvent(webSocketEvent);
}

void loop() {
    webSocket.loop();

    // Check if Pico sent any data -> Forward to Android App
    if (PicoSerial.available()) {
        String picoMsg = PicoSerial.readStringUntil('\n');
        picoMsg.trim();
        if (picoMsg.length() > 0) {
            webSocket.broadcastTXT(picoMsg);
            Serial.print("Pico: ");
            Serial.println(picoMsg);
        }
    }
}
