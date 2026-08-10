package com.example

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.*
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.*
import androidx.compose.ui.Alignment
import kotlinx.coroutines.delay

@Composable
fun DiagnosticScreen(
    viewModel: DiagnosticViewModel,
    onRequestBluetoothPermission: () -> Unit
) {
    val state by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        onRequestBluetoothPermission()
    }

    MaterialTheme(
        colorScheme = if (state.isDarkTheme) darkColorScheme(
            primary = Color(0xFF4CAF50),
            onPrimary = Color.White,
            secondary = Color(0xFF2196F3),
            background = Color(0xFF121212),
            onBackground = Color(0xFFE0E0E0),
            surface = Color(0xFF1E1E1E),
            onSurface = Color(0xFFE0E0E0),
        ) else lightColorScheme(
            primary = Color(0xFF2E7D32),
            onPrimary = Color.White,
            secondary = Color(0xFF1976D2),
            background = Color(0xFFFAFAFA),
            onBackground = Color(0xFF212121),
            surface = Color.White,
            onSurface = Color(0xFF212121),
        )
    ) {
        Scaffold(
            modifier = Modifier.fillMaxSize(),
            containerColor = MaterialTheme.colorScheme.background,
            topBar = { TopAppBar(state, viewModel) },
            bottomBar = { BottomNavigationBar(state, viewModel) }
        ) { innerPadding ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
            ) {
                when (state.activeTab) {
                    0 -> ToolsTab(state, viewModel)
                    1 -> SmartRecordTab(state, viewModel)
                    2 -> ClockTab(state)
                    3 -> StatusTab(state, viewModel)
                }
            }
        }
    }
}

@Composable
fun TopAppBar(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    TopAppBar(
        title = {
            Text(
                "ESP32 Diagnostic Tool",
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp
            )
        },
        actions = {
            val statusColor = when (state.connectionState) {
                ConnectionState.CONNECTED -> Color(0xFF4CAF50)
                ConnectionState.CONNECTING -> Color(0xFFFFC107)
                ConnectionState.DISCONNECTED -> Color(0xFFF44336)
            }
            val statusText = when (state.connectionState) {
                ConnectionState.CONNECTED -> "ချိတ်ဆက်ပြီး"
                ConnectionState.CONNECTING -> "ချိတ်ဆက်နေဆဲ"
                ConnectionState.DISCONNECTED -> "ဖြတ်ထား"
            }
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(end = 8.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .background(statusColor, CircleShape)
                )
                Spacer(Modifier.width(6.dp))
                Text(statusText, fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }

            IconButton(onClick = { viewModel.toggleTheme() }) {
                Icon(
                    if (state.isDarkTheme) Icons.Default.LightMode else Icons.Default.DarkMode,
                    contentDescription = "အပြင်အဆင်ပြောင်း"
                )
            }

            var showMenu by remember { mutableStateOf(false) }
            IconButton(onClick = { showMenu = true }) {
                Icon(Icons.Default.MoreVert, contentDescription = "အခြားရွေးချယ်စရာ")
            }
            DropdownMenu(
                expanded = showMenu,
                onDismissRequest = { showMenu = false }
            ) {
                DropdownMenuItem(
                    text = { Text("USB / ဖန်းဝဲတင်ခြင်း") },
                    onClick = { viewModel.setActiveTab(4); showMenu = false }
                )
                DropdownMenuItem(
                    text = { Text("အကူအညီ / လမ်းညွှန်") },
                    onClick = { viewModel.setActiveTab(5); showMenu = false }
                )
                DropdownMenuItem(
                    text = { Text("မှတ်တမ်းရှင်းမည်") },
                    onClick = { viewModel.clearLogs(); showMenu = false }
                )
            }
        }
    )
}

@Composable
fun BottomNavigationBar(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    NavigationBar {
        val items = listOf(
            0 to "ကိရိယာ" to Icons.Default.Build,
            1 to "မှတ်တမ်း" to Icons.Default.ListAlt,
            2 to "နာရီကြိမ်နှုန်း" to Icons.Default.Timer,
            3 to "အခြေအနေ" to Icons.Default.Info
        )
        items.forEach { (pair, icon) ->
            val (index, label) = pair
            NavigationBarItem(
                selected = state.activeTab == index,
                onClick = { viewModel.setActiveTab(index) },
                icon = { Icon(icon, contentDescription = label) },
                label = { Text(label, fontSize = 12.sp) }
            )
        }
    }
}

@Composable
fun ToolsTab(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f))
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("ချိတ်ဆက်မှု", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(12.dp))

                if (state.connectionMode != ConnectionMode.BLE) {
                    OutlinedTextField(
                        value = state.wifiIp,
                        onValueChange = { viewModel.updateWifiIp(it) },
                        label = { Text("IP လိပ်စာ") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(
                        value = state.wifiPort,
                        onValueChange = { viewModel.updateWifiPort(it) },
                        label = { Text("Port") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                    Spacer(Modifier.height(12.dp))
                }

                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = { viewModel.connectWifi() },
                        enabled = state.connectionState != ConnectionState.CONNECTING,
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Wifi, null, Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Wi-Fi ချိတ်ဆက်")
                    }
                    Button(
                        onClick = { viewModel.connectBle() },
                        enabled = state.connectionState != ConnectionState.CONNECTING,
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Bluetooth, null, Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("ဘလူးတုသ်")
                    }
                }
                Button(
                    onClick = { viewModel.disconnect() },
                    enabled = state.connectionState == ConnectionState.CONNECTED,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFB71C1C))
                ) {
                    Text("ချိတ်ဆက်မှုဖြတ်ရန်")
                }
            }
        }

        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(16.dp)) {
                Text("စမ်းသပ်မှု အမျိုးအစား", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(12.dp))
                val modes = listOf(
                    HardwareMode.DIODE to "Diode တိုင်းတာခြင်း",
                    HardwareMode.UART to "UART ဒေတာဖတ်ခြင်း",
                    HardwareMode.I2C to "I2C စကင်ဖတ်ခြင်း",
                    HardwareMode.PWM to "PWM အချက်ပြမှု"
                )
                modes.forEach { (mode, label) ->
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .clickable { viewModel.setHardwareMode(mode) }
                            .padding(vertical = 10.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = state.hardwareMode == mode,
                            onClick = { viewModel.setHardwareMode(mode) }
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(label, style = MaterialTheme.typography.bodyLarge)
                    }
                }
            }
        }

        if (state.hardwareMode == HardwareMode.DIODE) {
            DiodePanel(state, viewModel)
        }
        if (state.hardwareMode == HardwareMode.UART) {
            UartPanel(state, viewModel)
        }
        if (state.hardwareMode == HardwareMode.I2C) {
            I2CPanel(state, viewModel)
        }
        if (state.hardwareMode == HardwareMode.PWM) {
            PwmPanel(state, viewModel)
        }
    }
}

@Composable
fun DiodePanel(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    val displayValue = state.diodeValue
    val isOL = displayValue == "OL"
    val floatVal = if (!isOL) displayValue.toFloatOrNull() else null

    val valueColor = when {
        isOL -> Color(0xFF2196F3)
        floatVal != null && floatVal < 0.05f -> Color(0xFFF44336)
        floatVal != null && floatVal > state.diodeReferenceValue + 0.05f -> Color(0xFFFF9800)
        floatVal != null && floatVal >= state.diodeReferenceValue - 0.05f -> Color(0xFF4CAF50)
        else -> MaterialTheme.colorScheme.onSurface
    }
    val bgAlpha = if (floatVal != null && floatVal < 0.05f) 0.15f else 0.05f
    val bgColor = valueColor.copy(alpha = bgAlpha)

    Card(
        Modifier.fillMaxWidth(),
        border = BorderStroke(2.dp, valueColor.copy(alpha = 0.7f)),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            Modifier
                .fillMaxWidth()
                .background(bgColor)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                "Diode တန်ဖိုး",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(Modifier.height(12.dp))
            Text(
                displayValue,
                style = MaterialTheme.typography.displayLarge,
                fontSize = 52.sp,
                fontWeight = FontWeight.Bold,
                color = valueColor
            )
            Text(
                "Volt",
                style = MaterialTheme.typography.bodyLarge,
                color = valueColor.copy(alpha = 0.8f),
                modifier = Modifier.padding(top = 4.dp)
            )

            Spacer(Modifier.height(16.dp))

            Text(
                "ရည်ညွှန်းတန်ဖိုး: %.3f V".format(state.diodeReferenceValue),
                style = MaterialTheme.typography.bodyMedium
            )
            Slider(
                value = state.diodeReferenceValue,
                onValueChange = { viewModel.setDiodeReferenceValue(it) },
                valueRange = 0.1f..0.8f,
                steps = 69,
                modifier = Modifier.padding(horizontal = 16.dp)
            )

            Spacer(Modifier.height(16.dp))

            Button(
                onClick = { viewModel.sendDiode() },
                enabled = state.connectionState == ConnectionState.CONNECTED,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Refresh, null, Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text("တိုင်းတာရန် နှိပ်ပါ", fontSize = 16.sp)
            }
        }
    }
}

@Composable
fun UartPanel(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Text("UART ဒေတာ", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = { viewModel.sendUartStart() },
                    enabled = state.connectionState == ConnectionState.CONNECTED,
                    modifier = Modifier.weight(1f)
                ) { Text("စတင်ဖတ်ရန်") }
                Button(
                    onClick = { viewModel.sendUartStop() },
                    enabled = state.connectionState == ConnectionState.CONNECTED,
                    modifier = Modifier.weight(1f)
                ) { Text("ရပ်ရန်") }
                Button(
                    onClick = { viewModel.toggleUartPause() },
                    modifier = Modifier.weight(1f)
                ) { Text(if (state.isUartPaused) "ဆက်လက်ဖတ်ရန်" else "ခေတ္တရပ်ရန်") }
            }

            Spacer(Modifier.height(12.dp))

            Text("Baud Rate: ${state.uartBaudRate}", style = MaterialTheme.typography.bodyMedium)
            val baudList = listOf(9600, 19200, 38400, 57600, 115200)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                baudList.forEach { b ->
                    FilterChip(
                        selected = state.uartBaudRate == b,
                        onClick = { viewModel.setUartBaudRate(b) },
                        label = { Text(b.toString()) }
                    )
                }
            }

            Spacer(Modifier.height(12.dp))

            Card(
                Modifier
                    .fillMaxWidth()
                    .height(220.dp)
                    .padding(vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.2f)
                )
            ) {
                Column(Modifier.padding(12.dp).verticalScroll(rememberScrollState())) {
                    if (state.uartLogs.isEmpty()) {
                        Text(
                            "ဒေတာမရသေးပါ။ စတင်ဖတ်ရန် ခလုတ်ကိုနှိပ်ပါ။",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            fontSize = 14.sp
                        )
                    } else {
                        state.uartLogs.forEach { log ->
                            Text(
                                "[${log.time}] ${log.message}",
                                fontSize = 13.sp,
                                fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                                modifier = Modifier.padding(vertical = 2.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun I2CPanel(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Text("I2C စကင်ဖတ်ခြင်း", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(12.dp))
            Button(
                onClick = { viewModel.sendI2c() },
                enabled = state.connectionState == ConnectionState.CONNECTED,
                modifier = Modifier.fillMaxWidth().height(52.dp)
            ) {
                Icon(Icons.Default.Search, null)
                Spacer(Modifier.width(8.dp))
                Text("စကင်ဖတ်စတင်ရန်")
            }
            Spacer(Modifier.height(16.dp))
            Text(
                if (state.i2cDevices.isEmpty()) "စက်ပစ္စည်းမတွေ့ရှိသေးပါ"
                else "တွေ့ရှိခဲ့သော စက်များ-",
                style = MaterialTheme.typography.bodyMedium
            )
            Spacer(Modifier.height(8.dp))
            state.i2cDevices.forEach { addr ->
                Card(
                    Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
                ) {
                    Text(
                        "  • လိပ်စာ: $addr",
                        modifier = Modifier.padding(12.dp),
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
        }
    }
}

@Composable
fun PwmPanel(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Text("PWM အချက်ပြမှု", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(12.dp))

            Text("ကြိမ်နှုန်း: ${state.pwmFreq} Hz", style = MaterialTheme.typography.bodyLarge)
            Slider(
                value = state.pwmFreq.toFloat(),
                onValueChange = { },
                onValueChangeFinished = { viewModel.sendPwmConfig(state.pwmFreq, state.pwmDuty) },
                valueRange = 50f..5000f,
                steps = 98,
                modifier = Modifier.padding(horizontal = 8.dp)
            )

            Text("အလုပ်ချိန်ရာခိုင်နှုန်း: ${state.pwmDuty} %", style = MaterialTheme.typography.bodyLarge)
            Slider(
                value = state.pwmDuty.toFloat(),
                onValueChange = { },
                onValueChangeFinished = { viewModel.sendPwmConfig(state.pwmFreq, state.pwmDuty) },
                valueRange = 0f..100f,
                steps = 19,
                modifier = Modifier.padding(horizontal = 8.dp)
            )

            Button(
                onClick = { viewModel.sendPwmConfig(state.pwmFreq, state.pwmDuty) },
                enabled = state.connectionState == ConnectionState.CONNECTED,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            ) {
                Text("ဆက်တင်များပေးပို့ရန်")
            }
        }
    }
}

@Composable
fun SmartRecordTab(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(16.dp)) {
                Text("Smart Pin မှတ်တမ်း", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(12.dp))

                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = { viewModel.setSmartRecordMode(SmartRecordMode.MANUAL) },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (state.smartRecordMode == SmartRecordMode.MANUAL)
                                MaterialTheme.colorScheme.primary
                            else MaterialTheme.colorScheme.surfaceVariant
                        )
                    ) { Text("ကိုယ်တိုင်") }
                    Button(
                        onClick = { viewModel.setSmartRecordMode(SmartRecordMode.AUTO) },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (state.smartRecordMode == SmartRecordMode.AUTO)
                                MaterialTheme.colorScheme.primary
                            else MaterialTheme.colorScheme.surfaceVariant
                        )
                    ) { Text("အလိုအလျောက်") }
                }

                Spacer(Modifier.height(12.dp))

                Button(
                    onClick = { viewModel.toggleSmartRecording() },
                    modifier = Modifier.fillMaxWidth().height(52.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (state.isRecordingStarted) Color(0xFFB71C1C)
                        else Color(0xFF2E7D32)
                    )
                ) {
                    Text(if (state.isRecordingStarted) "မှတ်တမ်းရပ်တန့်ရန်" else "မှတ်တမ်းစတင်ရန်", fontSize = 16.sp)
                }

                Spacer(Modifier.height(16.dp))

                val total = state.pinRecords.size
                val pass = state.pinRecords.count { it.status == PinStatus.PASS }
                val fail = state.pinRecords.count { it.status == PinStatus.FAIL }
                val short = state.pinRecords.count { it.status == PinStatus.SHORT }

                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                    StatItem("$total", "စုစုပေါင်း")
                    StatItem("$pass", "အဆင်ပြေ", Color(0xFF4CAF50))
                    StatItem("$fail", "မကိုက်ညီ", Color(0xFFFF9800))
                    StatItem("$short", "ရှော့", Color(0xFFF44336))
                }
            }
        }

        state.pinRecords.forEachIndexed { idx, record ->
            val cardBg = when (record.status) {
                PinStatus.PASS -> Color(0xFF4CAF50).copy(alpha = 0.15f)
                PinStatus.FAIL -> Color(0xFFFF9800).copy(alpha = 0.15f)
                PinStatus.SHORT -> Color(0xFFF44336).copy(alpha = 0.15f)
                PinStatus.PENDING -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.2f)
            }
            val borderColor = when (record.status) {
                PinStatus.PASS -> Color(0xFF4CAF50)
                PinStatus.FAIL -> Color(0xFFFF9800)
                PinStatus.SHORT -> Color(0xFFF44336)
                PinStatus.PENDING -> Color.Transparent
            }
            val isCurrent = state.isRecordingStarted && idx == state.currentPinIndex

            Card(
                Modifier
                    .fillMaxWidth()
                    .then(if (isCurrent) Modifier.border(BorderStroke(3.dp, MaterialTheme.colorScheme.primary), RoundedCornerShape(12.dp)) else Modifier),
                colors = CardDefaults.cardColors(containerColor = cardBg),
                border = if (!isCurrent) BorderStroke(1.dp, borderColor.copy(alpha = 0.6f)) else null,
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            "Pin ${record.pinNumber} — ${record.name}",
                            fontWeight = if (isCurrent) FontWeight.Bold else FontWeight.Medium
                        )
                        Text("ရည်ညွှန်း: %.3f V".format(record.referenceValue), fontSize = 13.sp)
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        val mv = record.measuredValue
                        if (mv != null) {
                            val diff = mv - record.referenceValue
                            val diffStr = if (diff >= 0) "+%.3f".format(diff) else "%.3f".format(diff)
                            Text("%.3f V".format(mv), fontWeight = FontWeight.Bold, fontSize = 15.sp)
                            Text("ကွာခြား: $diffStr V", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        } else {
                            Text("-- V", fontSize = 15.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text("မတိုင်းတ yet", fontSize = 12.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun StatItem(value: String, label: String, color: Color = MaterialTheme.colorScheme.onSurface) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, fontWeight = FontWeight.Bold, fontSize = 18.sp, color = color)
        Text(label, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
fun ClockTab(state: DiagnosticUiState) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Card(
            Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.secondaryContainer
            )
        ) {
            Column(
                Modifier
                    .fillMaxWidth()
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "နာရီကြိမ်နှုန်း",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSecondaryContainer
                )
                Spacer(Modifier.height(24.dp))
                Text(
                    "%,d".format(state.clockFreq),
                    style = MaterialTheme.typography.displayLarge,
                    fontSize = 56.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSecondaryContainer
                )
                Text(
                    "Hz",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.8f),
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
fun StatusTab(state: DiagnosticUiState, viewModel: DiagnosticViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("စနစ် မှတ်တမ်း", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(12.dp))

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { viewModel.clearLogs() }) {
                Icon(Icons.Default.Delete, null, Modifier.size(18.dp))
                Spacer(Modifier.width(6.dp))
                Text("ရှင်းလင်းမည်")
            }
            Button(onClick = { }) {
                Icon(Icons.Default.Save, null, Modifier.size(18.dp))
                Spacer(Modifier.width(6.dp))
                Text("သိမ်းဆည်းမည်")
            }
        }

        Spacer(Modifier.height(12.dp))

        Card(
            Modifier
                .fillMaxWidth()
                .weight(1f)
                .verticalScroll(rememberScrollState())
        ) {
            Column(Modifier.padding(12.dp)) {
                if (state.appLogs.isEmpty()) {
                    Text(
                        "မှတ်တမ်းမရှိသေးပါ။ ချိတ်ဆက်မှုစတင်ပါ။",
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 14.sp
                    )
                } else {
                    state.appLogs.forEach { log ->
                        val color = when (log.type) {
                            LogType.INFO -> MaterialTheme.colorScheme.onSurface
                            LogType.CMD -> Color(0xFF64B5F6)
                            LogType.RES -> Color(0xFF81C784)
                        }
                        Text(
                            "[${log.time}] ${log.message}",
                            color = color,
                            fontSize = 13.sp,
                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            modifier = Modifier.padding(vertical = 3.dp)
                        )
                    }
                }
            }
        }
    }
}
