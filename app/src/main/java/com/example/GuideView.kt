package com.example

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun GuideView() {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                "User Guide & Hardware Manual",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(Modifier.height(8.dp))
            Text(
                "Detailed instructions for setting up and using the ESP32 + Pico Diagnostic System.",
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        item {
            GuideSection(
                title = "1. App Usage (Step-by-Step)",
                content = """
                    Step 1: Power on the ESP32 and Raspberry Pi Pico.
                    Step 2: Connect your phone's Wi-Fi to 'ESP_Pico_Diag'.
                    Step 3: Open this App. The connection status should turn 'LINK_ACT'.
                    Step 4: Use the 'Tools' tab to select diagnostic modes (Diode, PWM, I2C, UART).
                    Step 5: Use the 'Smart' tab for memory scanning of multi-pin connectors like LCD sockets.
                """.trimIndent()
            )
        }

        item {
            GuideSection(
                title = "2. Hardware Connection Diagram",
                content = """
                    [ ESP32-S3 ] <--- UART ---> [ Raspberry Pi Pico ]
                    - ESP32 TX (GPIO 17) -> Pico RX (GPIO 1)
                    - ESP32 RX (GPIO 16) -> Pico TX (GPIO 0)
                    - GND -> GND (Common Ground is MANDATORY!)
                    - Power: 5V/3.3V as appropriate.

                    [ Pico to Device Under Test (DUT) ]
                    - Diode Mode (ADC): Pico GP26 (A0) -> Voltage Divider -> DUT Pin
                    - PWM Out: Pico GP15 -> DUT
                    - I2C Scanner: Pico GP4 (SDA), GP5 (SCL) -> DUT I2C Bus
                """.trimIndent()
            )
        }

        item {
            GuideSection(
                title = "3. Required Components (Resistors, Diodes, FETs)",
                content = """
                    - Voltage Divider (For ADC): 
                      To measure up to 5V safely on Pico's 3.3V ADC.
                      Use R1 = 10kΩ, R2 = 20kΩ.
                      Connect DUT -> R1 -> Pico ADC -> R2 -> GND.
                      
                    - Protection Diodes:
                      Use Zener Diodes (3.3V) on Pico input pins to clamp overvoltage.
                      Place between ADC input and GND.

                    - Level Shifters (FETs):
                      For I2C or UART interfacing with 5V logic or 1.8V logic, use bi-directional Logic Level Converters (e.g., BSS138 N-channel MOSFETs) with 10kΩ pull-up resistors on both sides.
                """.trimIndent()
            )
        }

        item {
            GuideSection(
                title = "4. Dos and Don'ts (Safety Guidelines)",
                content = """
                    DO:
                    - Always connect common ground (GND) between ESP32, Pico, and the DUT.
                    - Verify voltages before connecting directly to Pico pins (Max 3.3V).
                    - Use 'Smart Auto' mode carefully, ensuring the probe is steady.

                    DON'T:
                    - NEVER connect high voltage (>3.3V directly, or >5V with divider) to Pico.
                    - DON'T short the PWM output directly to ground; use a series resistor (e.g., 220Ω) if driving LEDs.
                    - DON'T reverse polarity when measuring diode values.
                """.trimIndent()
            )
        }
        
        item {
            Spacer(Modifier.height(80.dp))
        }
    }
}

@Composable
fun GuideSection(title: String, content: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                title,
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
                color = MaterialTheme.colorScheme.secondary
            )
            Spacer(Modifier.height(8.dp))
            Text(
                content,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurface,
                lineHeight = 20.sp
            )
        }
    }
}
