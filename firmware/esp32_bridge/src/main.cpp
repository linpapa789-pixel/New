#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsServer.h>

// =========================
// Wi-Fi AP Credentials
// =========================
const char* ssid = "ESP_Pico_Diag";
const char* password = "password123";

// WebSocket Server (Port 80 သည် Android App နှင့် ချိတ်ဆက်ရန်ဖြစ်သည်)
WebSocketsServer webSocket = WebSocketsServer(80);

// =========================
// PICO CONNECTION (UART)
// =========================
// မှတ်ချက်: N16R8 PSRAM နှင့် မငြိစေရန် Pin 18 နှင့် 19 ကို အသုံးပြုထားပါသည်
HardwareSerial PicoSerial(1);
const int PICO_RX_PIN = 18; // Pico ၏ TX သို့ ချိတ်ရန်
const int PICO_TX_PIN = 19; // Pico ၏ RX သို့ ချိတ်ရန်

// WebSocket မှ Data ဝင်လာပါက လုပ်ဆောင်မည့် အပိုင်း
void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[%u] App Disconnected!\n", num);
            break;
        case WStype_CONNECTED: {
            IPAddress ip = webSocket.remoteIP(num);
            Serial.printf("[%u] App Connected from %d.%d.%d.%d\n", num, ip[0], ip[1], ip[2], ip[3]);
            // ချိတ်ဆက်အောင်မြင်ကြောင်း App သို့ အသိပေးခြင်း
            webSocket.sendTXT(num, "{\"status\": \"connected\", \"device\": \"ESP32-S3 Bridge\"}");
        }
            break;
        case WStype_TEXT:
            // Android App မှ JSON Command ဝင်လာပါက Pico သို့ UART မှတဆင့် တိုက်ရိုက်ပို့ပေးသည်
            payload[length] = '\0'; // Null-terminate
            Serial.printf("From App: %s\n", payload);
            PicoSerial.println((char*)payload);
            break;
        case WStype_BIN:
        case WStype_ERROR:
        case WStype_FRAGMENT_TEXT_START:
        case WStype_FRAGMENT_BIN_START:
        case WStype_FRAGMENT:
        case WStype_FRAGMENT_FIN:
            break;
    }
}

void setup() {
    // Debug အတွက် USB Serial
    Serial.begin(115200); 
    delay(500);
    
    Serial.println("\n--- Starting ESP32-S3 Bridge (N16R8) ---");

    // Pico နှင့် ချိတ်ဆက်မည့် UART ကို စတင်ခြင်း
    PicoSerial.begin(115200, SERIAL_8N1, PICO_RX_PIN, PICO_TX_PIN);

    // Wi-Fi Access Point ကို စတင်ခြင်း
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, password);
    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);

    // WebSocket Server ကို စတင်ခြင်း
    webSocket.begin();
    webSocket.onEvent(webSocketEvent);
    Serial.println("WebSocket Server started on port 80");
}

void loop() {
    // WebSocket Client များကို အမြဲစစ်ဆေးနေရန်
    webSocket.loop();

    // Pico ဘက်မှ Data (ဥပမာ - Live Diode, I2C results, UART logs) ဝင်လာပါက
    if (PicoSerial.available()) {
        String picoMsg = PicoSerial.readStringUntil('\n');
        picoMsg.trim();
        
        if (picoMsg.length() > 0) {
            // Android App များအားလုံးဆီသို့ ပြန်လည် ဖြန့်ဝေ (Broadcast) ပေးသည်
            webSocket.broadcastTXT(picoMsg);
            // Debug အတွက် Serial Monitor တွင် ပြသသည်
            Serial.print("From Pico: ");
            Serial.println(picoMsg);
        }
    }
}
