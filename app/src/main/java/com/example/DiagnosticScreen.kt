package com.example

import android.content.Context
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.outlined.Build
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiagnosticScreen(viewModel: DiagnosticViewModel, modifier: Modifier = Modifier) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        modifier = modifier.fillMaxSize(),
        topBar = {
            // Compact HUD
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        "SYS_DIAG_v1",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary,
                        fontSize = 14.sp
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "[${uiState.hardwareMode.name}]",
                        fontFamily = FontFamily.Monospace,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 12.sp
                    )
                }
                ConnectionBadge(uiState = uiState)
            }
        },
        bottomBar = {
            // Minimal Icon-only Tab Row
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.background)
                    .padding(vertical = 12.dp),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                val tabs = listOf(
                    Triple("Tools", Icons.Outlined.Build, Icons.Filled.Build),
                    Triple("Smart", Icons.Outlined.CheckCircle, Icons.Filled.CheckCircle),
                    Triple("Guide", Icons.Outlined.Info, Icons.Filled.Info),
                    Triple("Clock", Icons.Outlined.Refresh, Icons.Filled.Refresh),
                    Triple("Flash", Icons.Outlined.CheckCircle, Icons.Filled.CheckCircle),
                    Triple("Status", Icons.Outlined.Info, Icons.Filled.Info),
                    Triple("Settings", Icons.Outlined.Settings, Icons.Filled.Settings)
                )
                tabs.forEachIndexed { index, (title, unselectedIcon, selectedIcon) ->
                    val isSelected = uiState.activeTab == index
                    val iconColor = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant

                    Icon(
                        imageVector = if (isSelected) selectedIcon else unselectedIcon,
                        contentDescription = title,
                        tint = iconColor,
                        modifier = Modifier
                            .size(28.dp)
                            .clickable { viewModel.setActiveTab(index) }
                    )
                }
            }
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->
        Crossfade(
            targetState = uiState.activeTab,
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.background),
            animationSpec = tween(300)
        ) { tab ->
            when (tab) {
                0 -> ToolsView(viewModel, uiState)
                1 -> SmartRecordView(viewModel, uiState)
                2 -> GuideView()
                3 -> ClockCheckView(viewModel, uiState)
                4 -> OtgFlashView(viewModel, uiState)
                5 -> StatusLogsView(viewModel, uiState)
                6 -> ConfigView(viewModel, uiState)
            }
        }
    }
}

@Composable
fun ConnectionBadge(uiState: DiagnosticUiState) {
    val (statusColor, statusText) = when (uiState.connectionState) {
        ConnectionState.CONNECTED -> MaterialTheme.colorScheme.secondary to "LINK_ACT"
        ConnectionState.CONNECTING -> Color(0xFFFBBF24) to "SYNCING"
        ConnectionState.DISCONNECTED -> MaterialTheme.colorScheme.error to "OFFLINE"
    }

    Row(
        modifier = Modifier
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(6.dp)
                .clip(CircleShape)
                .background(statusColor)
        )
        Spacer(Modifier.width(6.dp))
        Text(
            text = statusText,
            fontSize = 10.sp,
            fontFamily = FontFamily.Monospace,
            color = statusColor
        )
    }
}

@Composable
fun ToolsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // --- 1. Mode Selection UI (Terminal Style) ---
        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(12.dp)
            ) {
                Column {
                    Text("SELECT_PROBE_MODE", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                    Spacer(Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        val modes = listOf(
                            Triple(HardwareMode.DIODE, "DIODE", "⚡"),
                            Triple(HardwareMode.UART, "UART", "📟"),
                            Triple(HardwareMode.I2C, "I2C", "🔎"),
                            Triple(HardwareMode.PWM, "PWM", "〰")
                        )

                        modes.forEach { (mode, label, icon) ->
                            val isSelected = uiState.hardwareMode == mode
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .padding(horizontal = 4.dp)
                                    .height(36.dp)
                                    .border(1.dp, if(isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
                                    .background(if (isSelected) MaterialTheme.colorScheme.primary.copy(alpha = 0.1f) else Color.Transparent)
                                    .clickable { viewModel.setHardwareMode(mode) },
                                contentAlignment = Alignment.Center
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(icon, fontSize = 12.sp)
                                    Spacer(Modifier.width(4.dp))
                                    Text(
                                        label,
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 12.sp,
                                        color = if(isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
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
            Crossfade(targetState = uiState.hardwareMode, animationSpec = tween(300)) { currentMode ->
                when (currentMode) {
                    HardwareMode.DIODE -> DiodeModeView(viewModel, uiState)
                    HardwareMode.UART -> UartModeView(viewModel, uiState)
                    HardwareMode.I2C -> I2cModeView(viewModel, uiState)
                    HardwareMode.CLOCK -> { /* Handled in Clock tab */ }
                    HardwareMode.PWM -> PwmModeView(viewModel, uiState)
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
        // Live Scan Card (Terminal Style + Oscilloscope)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.surface)
                .padding(16.dp)
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("> LIVE_PROBE_READING", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                        Spacer(Modifier.height(4.dp))
                        Text("ZERO_LAG_ADC | OSCILLOSCOPE_MODE", fontFamily = FontFamily.Monospace, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(
                            uiState.liveProbeValue,
                            fontSize = 42.sp,
                            fontFamily = FontFamily.Monospace,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        if (uiState.liveProbeValue != "--" && uiState.liveProbeValue != "0.00") {
                            Text("V", fontFamily = FontFamily.Monospace, fontSize = 20.sp, modifier = Modifier.padding(bottom = 6.dp, start = 4.dp), color = MaterialTheme.colorScheme.onSurface)
                        }
                    }
                }

                Spacer(Modifier.height(16.dp))

                // Real-Time Oscilloscope Graph (Optimized Canvas)
                val graphColor = MaterialTheme.colorScheme.secondary
                val gridColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.5f)
                val history = uiState.probeHistory

                Canvas(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(120.dp)
                        .background(MaterialTheme.colorScheme.background, RoundedCornerShape(4.dp))
                        .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
                ) {
                    // Draw terminal-style grid
                    val gridLines = 5
                    val stepX = size.width / gridLines
                    val stepY = size.height / gridLines
                    for (i in 1 until gridLines) {
                        drawLine(
                            color = gridColor,
                            start = Offset(x = stepX * i, y = 0f),
                            end = Offset(x = stepX * i, y = size.height),
                            strokeWidth = 1f
                        )
                        drawLine(
                            color = gridColor,
                            start = Offset(x = 0f, y = stepY * i),
                            end = Offset(x = size.width, y = stepY * i),
                            strokeWidth = 1f
                        )
                    }

                    // Draw glowing line graph
                    if (history.isNotEmpty()) {
                        val path = Path()
                        val maxPoints = 50
                        val pointSpacing = size.width / (maxPoints - 1)
                        val maxValue = 3.3f

                        history.forEachIndexed { index, value ->
                            val x = index * pointSpacing
                            val y = size.height - ((value.coerceIn(0f, maxValue) / maxValue) * size.height)
                            if (index == 0) {
                                path.moveTo(x, y)
                            } else {
                                path.lineTo(x, y)
                            }
                        }

                        // Outer glow
                        drawPath(
                            path = path,
                            color = graphColor.copy(alpha = 0.3f),
                            style = Stroke(width = 6f)
                        )
                        // Core line
                        drawPath(
                            path = path,
                            color = graphColor,
                            style = Stroke(width = 2f)
                        )
                    }
                }
            }
        }

        // Diode Smart Comparison
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.surface)
                .padding(16.dp)
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("> DIODE_REFERENCE_TEST", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                    Button(
                        onClick = { viewModel.sendDiode() },
                        shape = RoundedCornerShape(4.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary, contentColor = MaterialTheme.colorScheme.onPrimary),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
                        modifier = Modifier.height(28.dp)
                    ) {
                        Text("READ", fontFamily = FontFamily.Monospace, fontSize = 12.sp)
                    }
                }
                Spacer(Modifier.height(16.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Bottom
                ) {
                    // Smart Comparison Logic
                    val currentVal = uiState.diodeValue.toFloatOrNull()
                    val referenceVal = uiState.diodeReferenceValue
                    val isShort = currentVal != null && currentVal < 0.05f
                    val isBad = currentVal != null && kotlin.math.abs(currentVal - referenceVal) > 0.1f

                    val (displayColor, statusText) = when {
                        isShort -> MaterialTheme.colorScheme.error to "SHORT"
                        isBad -> MaterialTheme.colorScheme.error to "FAIL"
                        currentVal != null -> MaterialTheme.colorScheme.secondary to "PASS"
                        else -> MaterialTheme.colorScheme.onSurface to "WAIT"
                    }

                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(uiState.diodeValue, fontSize = 36.sp, fontFamily = FontFamily.Monospace, color = displayColor)
                        if (uiState.diodeValue != "--") {
                            Text("V", fontFamily = FontFamily.Monospace, fontSize = 18.sp, modifier = Modifier.padding(bottom = 4.dp, start = 4.dp), color = displayColor)
                        }
                    }

                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            statusText,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold,
                            color = displayColor,
                            fontSize = 18.sp
                        )
                        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(top=4.dp)) {
                            Text("REF:", fontFamily = FontFamily.Monospace, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(Modifier.width(4.dp))
                            Text("${String.format("%.3f", uiState.diodeReferenceValue)}V", fontFamily = FontFamily.Monospace, fontSize = 12.sp, color = MaterialTheme.colorScheme.primary)
                        }
                    }
                }

                Spacer(Modifier.height(16.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Text("Adjust Reference:", fontFamily = FontFamily.Monospace, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Slider(
                        value = uiState.diodeReferenceValue,
                        onValueChange = { viewModel.setDiodeReferenceValue(it) },
                        valueRange = 0.0f..3.3f,
                        steps = 33,
                        modifier = Modifier.weight(1f).padding(start = 12.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun UartModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    val listState = rememberLazyListState()

    // Controlled auto-scrolling that respects pause state
    LaunchedEffect(uiState.uartLogs.size, uiState.isUartPaused) {
        if (!uiState.isUartPaused && uiState.uartLogs.isNotEmpty()) {
            listState.animateScrollToItem(uiState.uartLogs.size - 1)
        }
    }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("> UART_SERIAL_MONITOR", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Button(
                        onClick = { viewModel.sendUartStart() },
                        shape = RoundedCornerShape(4.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 0.dp),
                        modifier = Modifier.height(28.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary, contentColor = MaterialTheme.colorScheme.onSecondary)
                    ) {
                        Text("START", fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                    }
                    Button(
                        onClick = { viewModel.toggleUartPause() },
                        shape = RoundedCornerShape(4.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 0.dp),
                        modifier = Modifier.height(28.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (uiState.isUartPaused) Color(0xFFFBBF24) else MaterialTheme.colorScheme.tertiary,
                            contentColor = if (uiState.isUartPaused) Color.Black else MaterialTheme.colorScheme.onTertiary
                        )
                    ) {
                        Text(
                            if (uiState.isUartPaused) "RESUME" else "PAUSE",
                            fontFamily = FontFamily.Monospace,
                            fontSize = 10.sp
                        )
                    }
                    Button(
                        onClick = { viewModel.sendUartStop() },
                        shape = RoundedCornerShape(4.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 0.dp),
                        modifier = Modifier.height(28.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error, contentColor = MaterialTheme.colorScheme.onError)
                    ) {
                        Text("STOP", fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text("BAUD RATE:", fontFamily = FontFamily.Monospace, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                val bauds = listOf(9600, 115200, 1500000)
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    bauds.forEach { baud ->
                        val isSelected = uiState.uartBaudRate == baud
                        Box(
                            modifier = Modifier
                                .border(1.dp, if(isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline, RoundedCornerShape(2.dp))
                                .background(if(isSelected) MaterialTheme.colorScheme.primary.copy(alpha=0.2f) else Color.Transparent)
                                .clickable { viewModel.setUartBaudRate(baud) }
                                .padding(horizontal = 6.dp, vertical = 2.dp)
                        ) {
                            Text(baud.toString(), fontFamily = FontFamily.Monospace, fontSize = 10.sp, color = if(isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Surface(
                modifier = Modifier.fillMaxWidth().height(300.dp),
                color = MaterialTheme.colorScheme.background,
                shape = RoundedCornerShape(4.dp),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline)
            ) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize().padding(8.dp)
                ) {
                    items(uiState.uartLogs) { log ->
                        Row(modifier = Modifier.padding(vertical = 2.dp)) {
                            Text(
                                "[${log.time}] ",
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace
                            )
                            val msgColor = when (log.type) {
                                LogType.INFO -> MaterialTheme.colorScheme.primary
                                LogType.CMD -> Color(0xFFD2A8FF)
                                LogType.RES -> MaterialTheme.colorScheme.secondary
                            }
                            Text(
                                log.message,
                                color = msgColor,
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun I2cModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    val icDictionary = mapOf(
        "0x3C" to "OLED Display",
        "0x27" to "LCD I2C Mod",
        "0x68" to "RTC DS3231/MPU6050",
        "0x76" to "BME280/BMP280",
        "0x77" to "BME280/BMP280",
        "0x57" to "EEPROM (AT24C32)"
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("> I2C_BUS_SCANNER", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                Button(
                    onClick = { viewModel.sendI2c() },
                    shape = RoundedCornerShape(4.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary, contentColor = MaterialTheme.colorScheme.onPrimary),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
                    modifier = Modifier.height(28.dp)
                ) {
                    Text("SCAN", fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                }
            }
            Spacer(Modifier.height(16.dp))

            if (uiState.i2cDevices.isEmpty()) {
                Text("BUS_IDLE / NO_ACK", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 12.sp, modifier = Modifier.padding(8.dp))
            } else {
                FlowRow(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    uiState.i2cDevices.forEach { device ->
                        val knownIc = icDictionary[device]
                        val displayStr = if (knownIc != null) "$device ($knownIc)" else device

                        Box(
                            modifier = Modifier
                                .border(1.dp, MaterialTheme.colorScheme.primary, RoundedCornerShape(4.dp))
                                .background(MaterialTheme.colorScheme.primary.copy(alpha=0.1f))
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text(
                                displayStr,
                                fontSize = 12.sp,
                                fontFamily = FontFamily.Monospace,
                                color = MaterialTheme.colorScheme.primary
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

@Composable
fun StatusLogsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    val listState = rememberLazyListState()
    val context = LocalContext.current
    val exportLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("text/plain")) { uri ->
        uri?.let { viewModel.saveLogsToFile(context, it) }
    }

    LaunchedEffect(uiState.appLogs.size) {
        if (uiState.appLogs.isNotEmpty()) {
            listState.animateScrollToItem(uiState.appLogs.size - 1)
        }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Diagnostic Logs", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Text(
                    "Clear",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.clickable { viewModel.clearLogs() },
                    fontWeight = FontWeight.Bold
                )
                Text(
                    "Export",
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.clickable { exportLauncher.launch("esp32_logs_${System.currentTimeMillis()}.txt") },
                    fontWeight = FontWeight.Bold
                )
            }
        }

        Surface(
            modifier = Modifier.fillMaxWidth().weight(1f),
            color = Color(0xFF0D1117),
            shape = RoundedCornerShape(12.dp),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
        ) {
            LazyColumn(
                state = listState,
                modifier = Modifier.fillMaxSize().padding(12.dp)
            ) {
                items(uiState.appLogs) { log ->
                    Row(modifier = Modifier.padding(vertical = 2.dp)) {
                        Text(
                            "[${log.time}] ",
                            color = Color(0xFF8B949E),
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace
                        )
                        val msgColor = when (log.type) {
                            LogType.INFO -> Color(0xFF58A6FF)
                            LogType.CMD -> Color(0xFFD2A8FF)
                            LogType.RES -> Color(0xFF3FB950)
                        }
                        Text(
                            log.message,
                            color = msgColor,
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun OtgFlashView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("OTG Firmware Flash", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.height(16.dp))

                OutlinedTextField(
                    value = uiState.usbDeviceName,
                    onValueChange = {},
                    readOnly = true,
                    label = { Text("USB Device") },
                    modifier = Modifier.fillMaxWidth(),
                    trailingIcon = {
                        TextButton(onClick = { viewModel.detectUsbDevice() }) {
                            Text("Detect")
                        }
                    }
                )

                Spacer(Modifier.height(12.dp))

                OutlinedTextField(
                    value = uiState.firmwareFileName,
                    onValueChange = {},
                    readOnly = true,
                    label = { Text("Firmware File") },
                    modifier = Modifier.fillMaxWidth(),
                    trailingIcon = {
                        TextButton(onClick = { viewModel.setFirmwareFile("esp32_firmware_v2.bin") }) {
                            Text("Select")
                        }
                    }
                )

                Spacer(Modifier.height(24.dp))

                if (uiState.isFlashing || uiState.flashProgress > 0) {
                    Column(modifier = Modifier.fillMaxWidth()) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Progress", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text("${(uiState.flashProgress * 100).toInt()}%", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                        Spacer(Modifier.height(8.dp))
                        LinearProgressIndicator(
                            progress = { uiState.flashProgress },
                            modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)),
                            color = MaterialTheme.colorScheme.primary,
                            trackColor = MaterialTheme.colorScheme.surfaceVariant
                        )
                    }
                    Spacer(Modifier.height(16.dp))
                }

                Button(
                    onClick = { viewModel.startFlashing() },
                    modifier = Modifier.fillMaxWidth().height(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    enabled = !uiState.isFlashing
                ) {
                    Text(if (uiState.isFlashing) "Flashing..." else "Start Flash")
                }
            }
        }
    }
}

@Composable
fun ConfigView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Appearance", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.height(16.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Dark Theme (Light/Dark)")
                    Switch(
                        checked = uiState.isDarkTheme,
                        onCheckedChange = { viewModel.toggleTheme() }
                    )
                }
            }
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("ESP32 + Pi Pico Diagnostic Tool လမ်းညွှန်", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 18.sp)
                Spacer(Modifier.height(12.dp))

                Text(
                    "၁။ စနစ်ဖွဲ့စည်းပုံ (System Architecture) နှင့် လိုအပ်သော ပစ္စည်းများ",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    """
                    ဤ Project သည် Phone Service သမားများအတွက် အထူးပြုလုပ်ထားသော Diagnostic Tool ဖြစ်ပြီး ESP32-S3 နှင့် Raspberry Pi Pico (RP2040) တို့ကို တွဲဖက်အသုံးပြုထားပါသည်။ အခြား မည်သည့် Module မှ ထပ်မံဝယ်ယူရန် မလိုအပ်ပါ။
                    
                    • ESP32-S3 Board: Wi-Fi/Bluetooth ဆက်သွယ်ရေး၊ WebSocket နှင့် App သို့ Data ပို့ဆောင်ခြင်းတို့ကို တာဝန်ယူသည်။
                    • Raspberry Pi Pico (RP2040): တိကျသော ADC (12-bit)၊ PWM ထုတ်လွှင့်ခြင်း နှင့် PIO အသုံးပြုကာ မြန်နှုန်းမြင့် တိုင်းတာမှုများကို ပြုလုပ်ပေးမည့် Precision Co-Processor အဖြစ် လုပ်ဆောင်သည်။
                    • Jumper Wires နှင့် Multimeter Probes များသာ လိုအပ်သည်။
                    """.trimIndent(),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                Text(
                    "၂။ ချိတ်ဆက်ခြင်း (Wiring Diagram)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    """
                    [ ESP32-S3 ] <--- UART ---> [ Pi Pico ]
                    • ESP32 TX (Pin 17) -> Pico RX (Pin 1)
                    • ESP32 RX (Pin 16) -> Pico TX (Pin 0)
                    • ESP32 GND -> Pico GND
                    • ESP32 3.3V -> Pico 3V3 (Power မျှသုံးရန်)
                    """.trimIndent(),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontFamily = FontFamily.Monospace,
                    fontSize = 12.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                Text(
                    "၃။ လက်တွေ့ အသုံးတည့်မည့် လုပ်ဆောင်ချက်များ (Practical Solutions)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    """
                    ၁။ Precision Diode & Short Circuit Detection (Pico ADC0 - Pin 26):
                    Pico ၏ 12-bit ADC ကို အသုံးပြု၍ ဖုန်းဘုတ်ပေါ်ရှိ လိုင်းများ၏ Diode တန်ဖိုးနှင့် Voltage ကို တိကျစွာတိုင်းတာမည်။ 0.05V အောက်ရောက်ပါက Short Circuit အဖြစ် Beep သံဖြင့် သတိပေးမည်။

                    ၂။ PWM Signal Injector (Pico PWM - Pin 15):
                    ပြင်ပ Module မလိုဘဲ Pico မှ တိုက်ရိုက် PWM လှိုင်းထုတ်ပေးကာ LCD Backlight နှင့် Charge Pump IC များကို လှုံ့ဆော် (Wake-up) စမ်းသပ်နိုင်ပါသည်။

                    ၃။ High-Speed Logic Analyzer (Pico PIO - Pin 2,3,4,5):
                    Pico ၏ PIO (Programmable I/O) ကို သုံး၍ ဖုန်း၏ I2C/SPI/UART Boot Log များကို အလွန်မြန်ဆန်သော နှုန်းဖြင့် ဖမ်းယူစစ်ဆေးနိုင်ပါသည်။

                    ၄။ Sleep Clock Monitor (Pico Pin 16):
                    ဖုန်းများ၏ 32.768kHz Sleep Clock နှင့် အခြား Oscillator Frequency များကို အတိအကျ တိုင်းတာပေးနိုင်ပါသည်။
                    """.trimIndent(),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "၄။ ချိတ်ဆက်အသုံးပြုနည်း (App Usage)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "Tools tab တွင် Wi-Fi သို့မဟုတ် BLE ရွေးချယ်ချိတ်ဆက်ပါ။ Wi-Fi အတွက် 'ESP_Pico_Diag' ကို ချိတ်ဆက်ပြီး Tools, Clock, PWM အစရှိသော Tab များမှတဆင့် လိုအပ်သော လုပ်ဆောင်ချက်များကို ရွေးချယ်အသုံးပြုနိုင်ပါသည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
            }
        }
    }
}

@Composable
fun ClockCheckView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Clock Frequency Monitor", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.height(16.dp))

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(120.dp)
                        .background(Color(0xFF0D1117), RoundedCornerShape(8.dp))
                        .border(1.dp, MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(8.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "${uiState.clockFreq}",
                            fontSize = 48.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace,
                            color = Color(0xFF3FB950)
                        )
                        Text(
                            text = "Hz",
                            fontSize = 18.sp,
                            fontFamily = FontFamily.Monospace,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Spacer(Modifier.height(16.dp))
                Text(
                    "Connect Pin 5 (ESP32-S3) to the signal source to measure its frequency.",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
fun PwmModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("PWM Generator (Pico)", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
            Spacer(Modifier.height(8.dp))
            Text("Inject PWM signal to test circuits (e.g., LCD backlight).", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(16.dp))

            Text("Frequency: ${uiState.pwmFreq} Hz", color = MaterialTheme.colorScheme.onSurface)
            Slider(
                value = uiState.pwmFreq.toFloat(),
                onValueChange = { viewModel.sendPwmConfig(it.toInt(), uiState.pwmDuty) },
                valueRange = 100f..10000f,
                colors = SliderDefaults.colors(thumbColor = MaterialTheme.colorScheme.primary, activeTrackColor = MaterialTheme.colorScheme.primary)
            )

            Spacer(Modifier.height(16.dp))

            Text("Duty Cycle: ${uiState.pwmDuty}%", color = MaterialTheme.colorScheme.onSurface)
            Slider(
                value = uiState.pwmDuty.toFloat(),
                onValueChange = { viewModel.sendPwmConfig(uiState.pwmFreq, it.toInt()) },
                valueRange = 0f..100f,
                colors = SliderDefaults.colors(thumbColor = MaterialTheme.colorScheme.secondary, activeTrackColor = MaterialTheme.colorScheme.secondary)
            )
        }
    }
}


@Composable
fun SmartRecordView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Header Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "Smart Diode Assistant",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary,
                    fontSize = 18.sp
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    "Memory scan for LCD sockets and multi-pin connectors",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(Modifier.height(16.dp))
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "Mode: " + if(uiState.smartRecordMode == SmartRecordMode.AUTO) "Auto-Advance" else "Manual Save",
                        fontFamily = FontFamily.Monospace,
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    Row {
                        FilterChip(
                            selected = uiState.smartRecordMode == SmartRecordMode.MANUAL,
                            onClick = { viewModel.setSmartRecordMode(SmartRecordMode.MANUAL) },
                            label = { Text("Manual") }
                        )
                        Spacer(Modifier.width(8.dp))
                        FilterChip(
                            selected = uiState.smartRecordMode == SmartRecordMode.AUTO,
                            onClick = { viewModel.setSmartRecordMode(SmartRecordMode.AUTO) },
                            label = { Text("Auto") }
                        )
                    }
                }
                
                Spacer(Modifier.height(16.dp))
                
                Button(
                    onClick = { viewModel.toggleSmartRecording() },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (uiState.isRecordingStarted) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                    )
                ) {
                    Text(if (uiState.isRecordingStarted) "STOP RECORDING" else "START RECORDING", fontFamily = FontFamily.Monospace)
                }
            }
        }
        
        // Live Value & Manual Action
        if (uiState.isRecordingStarted) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
                        .background(MaterialTheme.colorScheme.surface)
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        uiState.liveProbeValue + " V",
                        fontSize = 32.sp,
                        fontFamily = FontFamily.Monospace,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                
                if (uiState.smartRecordMode == SmartRecordMode.MANUAL) {
                    Spacer(Modifier.width(16.dp))
                    Button(
                        onClick = { 
                            uiState.liveProbeValue.toFloatOrNull()?.let { 
                                viewModel.recordCurrentPin(it) 
                            }
                        },
                        modifier = Modifier.height(72.dp)
                    ) {
                        Text("SAVE\nPIN", fontFamily = FontFamily.Monospace, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                    }
                }
            }
        }
        
        // Pin List
        LazyColumn(
            modifier = Modifier.fillMaxWidth().weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(uiState.pinRecords.size) { index ->
                val record = uiState.pinRecords[index]
                val isActive = uiState.isRecordingStarted && uiState.currentPinIndex == index
                
                val bgColor = when {
                    isActive -> MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f)
                    record.status == PinStatus.PASS -> Color(0xFF1B5E20).copy(alpha = 0.2f)
                    record.status == PinStatus.FAIL -> MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.5f)
                    record.status == PinStatus.SHORT -> MaterialTheme.colorScheme.error.copy(alpha = 0.5f)
                    else -> MaterialTheme.colorScheme.surface
                }
                
                val statusText = when (record.status) {
                    PinStatus.PENDING -> "--"
                    PinStatus.PASS -> "PASS"
                    PinStatus.FAIL -> "FAIL"
                    PinStatus.SHORT -> "SHORT"
                }
                
                val statusColor = when (record.status) {
                    PinStatus.PENDING -> MaterialTheme.colorScheme.onSurfaceVariant
                    PinStatus.PASS -> Color(0xFF4CAF50)
                    PinStatus.FAIL -> MaterialTheme.colorScheme.error
                    PinStatus.SHORT -> MaterialTheme.colorScheme.error
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(
                            if (isActive) 2.dp else 1.dp,
                            if (isActive) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline,
                            RoundedCornerShape(4.dp)
                        )
                        .background(bgColor)
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Pin ${record.pinNumber}: ${record.name}", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                        Text("Ref: ${record.referenceValue}V", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    
                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = if (record.measuredValue != null) String.format("%.3f V", record.measuredValue) else "--",
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(statusText, fontSize = 10.sp, color = statusColor, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
