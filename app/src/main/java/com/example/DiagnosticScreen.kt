package com.example

import android.content.Context
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.tween
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.outlined.Build
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.geometry.Offset
import androidx.compose.foundation.Canvas
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch

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
                1 -> OtgFlashView(viewModel, uiState)
                2 -> StatusLogsView(viewModel, uiState)
                3 -> ConfigView(viewModel, uiState)
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
                            Triple(HardwareMode.I2C, "I2C", "🔎")
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
                
                // Real-Time Oscilloscope Graph
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
                        // Assume voltage range 0 to 3.3V for scaling
                        val maxValue = 3.3f
                        
                        history.forEachIndexed { index, value ->
                            val x = index * pointSpacing
                            // Invert y because canvas 0,0 is top-left
                            val y = size.height - ((value.coerceIn(0f, maxValue) / maxValue) * size.height)
                            if (index == 0) {
                                path.moveTo(x, y)
                            } else {
                                path.lineTo(x, y)
                            }
                        }
                        
                        // Draw outer glow (thicker, lower alpha)
                        drawPath(
                            path = path,
                            color = graphColor.copy(alpha = 0.3f),
                            style = Stroke(width = 6f)
                        )
                        // Draw core line
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
    LaunchedEffect(uiState.uartLogs.size) {
        if (uiState.uartLogs.isNotEmpty()) {
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
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("> UART_SERIAL_MONITOR", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = { viewModel.sendUartStart() },
                        shape = RoundedCornerShape(4.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
                        modifier = Modifier.height(28.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary, contentColor = MaterialTheme.colorScheme.onSecondary)
                    ) {
                        Text("START", fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                    }
                    Button(
                        onClick = { viewModel.sendUartStop() },
                        shape = RoundedCornerShape(4.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
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
            color = Color(0xFF0D1117), // Deep terminal background
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
                Text("ESP32 Diagnostic App - အသုံးပြုပုံလမ်းညွှန်", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 18.sp)
                Spacer(Modifier.height(12.dp))
                
                Text(
                    "၁။ ချိတ်ဆက်ခြင်း (Connection)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "Tools tab ရှိ 'Connection Mode' တွင် Wi-Fi သို့မဟုတ် Bluetooth ရွေးချယ်၍ ESP32 နှင့် ချိတ်ဆက်ပါ။ Wi-Fi ဖြင့် ချိတ်ဆက်ရန်အတွက် ESP32 မှ ထုတ်လွှင့်သော (ဥပမာ - 'ESP_Diag_Tool') Hotspot ကို ချိတ်ဆက်ပြီး IP နှင့် Port (Default: 192.168.4.1:80) အတိုင်းထား၍ ချိတ်ဆက်နိုင်ပါသည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "၂။ Hardware Modes (2 Probes စနစ်)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "• Diode Mode: ဖုန်းဘုတ်များရှိ လမ်းကြောင်းများကို တိုင်းတာရန်အတွက် ဖြစ်သည်။ Zero-Lag Live Probe ဖြင့် တိုက်ရိုက်တိုင်းတာနိုင်ပြီး၊ 'Read' ကိုနှိပ်၍ Reference Value နှင့် နှိုင်းယှဉ်စစ်ဆေးနိုင်ပါသည်။\n• UART Mode: Boot Logs များကို တိုက်ရိုက်ဖတ်ရှုရန် ဖြစ်သည်။ 'Start' ကိုနှိပ်၍ Log များကို ဖတ်ရှုနိုင်ပြီး ဖတ်ရှုပြီးပါက 'Stop' ကိုပြန်နှိပ်ပေးပါ။\n• I2C Mode: I2C လမ်းကြောင်းများ၏ အလုပ်လုပ်ပုံနှင့် ချိတ်ဆက်ထားသော IC များ (ဥပမာ 0x3C) ကို Scan ဖတ်ရှုနိုင်ပါသည်။ Probe 1 ကို SDA အဖြစ်နှင့် Probe 2 ကို SCL အဖြစ် အသုံးပြုပါ။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "၃။ မှတ်တမ်းများ (Logs) နှင့် OTG Flash",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "• Status Tab တွင် App ၏ လုပ်ဆောင်ချက် မှတ်တမ်းများနှင့် UART မှတ်တမ်းများကို သီးခြားစီ ဖတ်ရှုနိုင်ပါသည်။ လိုအပ်ပါက .txt ဖိုင်အနေဖြင့် Export ထုတ်ယူနိုင်ပါသည်။\n• Flash Tab တွင် ဖုန်းနှင့် ESP32 ကို OTG (USB) ဖြင့် ချိတ်ဆက်ပြီး Firmware (.bin) ဖိုင်ကို တိုက်ရိုက်တင်နိုင်ပါသည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
            }
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("ဆောင်ရန် နှင့် ရှောင်ရန်များ (Do's and Don'ts)", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.error, fontSize = 18.sp)
                Spacer(Modifier.height(12.dp))
                
                Text(
                    "ဆောင်ရန် (Do's)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
                Text(
                    "• တိုင်းတာမှုများ မပြုလုပ်မီ ESP32 နှင့် App ချိတ်ဆက်မှု (Connected) ဖြစ်/မဖြစ် အရင်သေချာစစ်ဆေးပါ။\n• I2C Scan ပြုလုပ်ရာတွင် Probe 1 (SDA) နှင့် Probe 2 (SCL) ကို မှန်ကန်စွာ ချိတ်ဆက်ပါ။\n• UART ဖတ်ရှုပြီးပါက အခြား Mode သို့ မပြောင်းမီ 'Stop' ကို အမြဲတမ်း နှိပ်ပေးပါ။\n• OTG Flash ပြုလုပ်ရာတွင် ဖုန်းဘက်မှ USB OTG ခွင့်ပြုချက် (Permission) တောင်းခံလာပါက Allow လုပ်ပေးပါ။",
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "ရှောင်ရန် (Don'ts)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
                Text(
                    "• Voltage များသော နေရာများကို တိုက်ရိုက်တိုင်းတာခြင်း (3.3V အထက်) ကို လုံးဝ ရှောင်ကြဉ်ပါ။ ESP32 ပျက်စီးနိုင်ပါသည်။\n• Firmware (OTG Flash) တင်နေစဉ်အတွင်း USB ကြိုးကို ဖြုတ်လိုက်ခြင်း လုံးဝ မပြုလုပ်ပါနှင့်။\n• UART Mode 'Start' လုပ်ထားစဉ် Diode သို့မဟုတ် I2C Mode သို့ ချက်ချင်း ပြောင်းလဲအသုံးပြုခြင်းမျိုး မပြုလုပ်ပါနှင့်။ 'Stop' အရင်နှိပ်ပါ။",
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    fontSize = 14.sp
                )
            }
        }
    }
}
