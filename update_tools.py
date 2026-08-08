import re

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

# Make sure HardwareMode is imported or handled, though it's in the same package (com.example).
# So we just need to replace ToolsView.

start_str = "fun ToolsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {"
end_str = "fun StatusLogsView"
idx_start = content.find(start_str)
idx_end = content.find("@Composable\n" + end_str)

new_tools_view = """fun ToolsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // --- 1. Mode Selection UI ---
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Hardware Mode (2 Probes)", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.height(16.dp))
                    
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f), RoundedCornerShape(12.dp))
                            .padding(4.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        val modes = listOf(
                            Triple(HardwareMode.DIODE, "Diode", "⚡"),
                            Triple(HardwareMode.UART, "UART", "📟"),
                            Triple(HardwareMode.I2C, "I2C", "🔎")
                        )
                        
                        modes.forEach { (mode, label, icon) ->
                            val isSelected = uiState.hardwareMode == mode
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .height(40.dp)
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(if (isSelected) MaterialTheme.colorScheme.primaryContainer else Color.Transparent)
                                    .clickable { viewModel.setHardwareMode(mode) },
                                contentAlignment = Alignment.Center
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(icon, fontSize = 14.sp)
                                    Spacer(Modifier.width(4.dp))
                                    Text(
                                        label, 
                                        fontWeight = if(isSelected) FontWeight.Bold else FontWeight.Medium,
                                        color = if(isSelected) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // --- 2. Dynamic Data Display based on Hardware Mode ---
        item {
            Crossfade(targetState = uiState.hardwareMode, animationSpec = androidx.compose.animation.core.tween(300)) { currentMode ->
                when (currentMode) {
                    HardwareMode.DIODE -> DiodeModeView(viewModel, uiState)
                    HardwareMode.UART -> UartModeView(viewModel, uiState)
                    HardwareMode.I2C -> I2cModeView(viewModel, uiState)
                }
            }
        }
        
        // Connection section at the bottom of tools view for quick access
        item {
            ConnectionCard(viewModel, uiState)
        }
    }
}

@Composable
fun DiodeModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // Live Scan Card (DMM Style)
        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(16.dp).fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Live Probe (Zero-Lag)", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.height(4.dp))
                    Text("Real-time voltage/resistance", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Row(verticalAlignment = Alignment.Bottom) {
                    Text(uiState.liveProbeValue, fontSize = 36.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.onSurface)
                    if (uiState.liveProbeValue != "--" && uiState.liveProbeValue != "0.00") {
                        Text("V", fontSize = 18.sp, modifier = Modifier.padding(bottom = 6.dp, start = 4.dp), color = MaterialTheme.colorScheme.onSurface)
                    }
                }
            }
        }
        
        // Diode Smart Comparison
        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(16.dp).fillMaxSize(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Diode Mode", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.height(12.dp))
                    Row(verticalAlignment = Alignment.Bottom) {
                        // Smart Comparison Logic
                        val currentVal = uiState.diodeValue.toFloatOrNull()
                        val referenceVal = 0.450f // Standard Good Board Reference
                        val isBad = currentVal != null && kotlin.math.abs(currentVal - referenceVal) > 0.1f
                        val displayColor = if (isBad) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurface
                        
                        Text(uiState.diodeValue, fontSize = 28.sp, fontWeight = FontWeight.Medium, fontFamily = FontFamily.Monospace, color = displayColor)
                        if (uiState.diodeValue != "--") {
                            Text("V", fontSize = 16.sp, modifier = Modifier.padding(bottom = 4.dp), color = displayColor)
                        }
                    }
                    if (uiState.diodeValue != "--") {
                        Text("Ref: 0.450V (±0.1V)", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                Button(
                    onClick = { viewModel.sendDiode() },
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Read")
                }
            }
        }
    }
}

@Composable
fun UartModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("UART Commands", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
            Spacer(Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(
                    onClick = { viewModel.sendUartStart() },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                ) {
                    Text("Start")
                }
                Button(
                    onClick = { viewModel.sendUartStop() },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                ) {
                    Text("Stop")
                }
            }
            Spacer(Modifier.height(16.dp))
            Text("Tip: View detailed UART boot logs in the 'Status' tab.", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun I2cModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp).fillMaxWidth()) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("I2C Scanner (2 Probes)", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                OutlinedButton(
                    onClick = { viewModel.sendI2c() },
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Scan")
                }
            }
            Spacer(Modifier.height(16.dp))
            
            if (uiState.i2cDevices.isEmpty()) {
                Text("No devices found.", color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(8.dp))
            } else {
                FlowRow(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    uiState.i2cDevices.forEach { device ->
                        Surface(
                            color = MaterialTheme.colorScheme.primaryContainer,
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text(
                                device, 
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                                fontSize = 16.sp, 
                                fontFamily = FontFamily.Monospace,
                                color = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ConnectionCard(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Connection Mode", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
            Spacer(Modifier.height(16.dp))
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f), RoundedCornerShape(12.dp))
                    .padding(4.dp)
            ) {
                val isWifi = uiState.connectionMode == ConnectionMode.WIFI
                val isBle = uiState.connectionMode == ConnectionMode.BLE
                
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .height(40.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(if (isWifi) MaterialTheme.colorScheme.primaryContainer else Color.Transparent)
                        .clickable { viewModel.connectWifi() },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "Wi-Fi", 
                        fontWeight = if(isWifi) FontWeight.Bold else FontWeight.Medium,
                        color = if(isWifi) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .height(40.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(if (isBle) MaterialTheme.colorScheme.primaryContainer else Color.Transparent)
                        .clickable { viewModel.connectBle() },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "Bluetooth", 
                        fontWeight = if(isBle) FontWeight.Bold else FontWeight.Medium,
                        color = if(isBle) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            AnimatedVisibility(visible = uiState.connectionMode == ConnectionMode.WIFI) {
                Column {
                    Spacer(Modifier.height(16.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(
                            value = uiState.wifiIp,
                            onValueChange = { viewModel.updateWifiIp(it) },
                            label = { Text("IP Address") },
                            modifier = Modifier.weight(2f),
                            singleLine = true
                        )
                        OutlinedTextField(
                            value = uiState.wifiPort,
                            onValueChange = { viewModel.updateWifiPort(it) },
                            label = { Text("Port") },
                            modifier = Modifier.weight(1f),
                            singleLine = true
                        )
                    }
                    Spacer(Modifier.height(12.dp))
                    Button(
                        onClick = { viewModel.connectWifi() },
                        modifier = Modifier.fillMaxWidth().height(48.dp),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text("Connect to Wi-Fi")
                    }
                }
            }
        }
    }
}
"""

new_content = content[:idx_start] + new_tools_view + "\n" + content[idx_end:]

# Ensure FlowRow import is present
if "import androidx.compose.foundation.layout.FlowRow" not in new_content:
    new_content = new_content.replace('import androidx.compose.foundation.layout.*', 'import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.layout.FlowRow\nimport androidx.compose.foundation.layout.ExperimentalLayoutApi')


with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(new_content)

