import os

code = """package com.example

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
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
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
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Filled.Build,
                            contentDescription = "Logo",
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(Modifier.width(12.dp))
                        Text(
                            "Hardware Diagnostics",
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                },
                actions = {
                    ConnectionBadge(uiState = uiState)
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface
                )
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                tonalElevation = 8.dp
            ) {
                val tabs = listOf(
                    Triple("Tools", Icons.Outlined.Build, Icons.Filled.Build),
                    Triple("Flash", Icons.Outlined.CheckCircle, Icons.Filled.CheckCircle),
                    Triple("Status", Icons.Outlined.Info, Icons.Filled.Info),
                    Triple("Settings", Icons.Outlined.Settings, Icons.Filled.Settings)
                )
                tabs.forEachIndexed { index, (title, unselectedIcon, selectedIcon) ->
                    val isSelected = uiState.activeTab == index
                    NavigationBarItem(
                        selected = isSelected,
                        onClick = { viewModel.setActiveTab(index) },
                        icon = { 
                            Icon(
                                imageVector = if (isSelected) selectedIcon else unselectedIcon,
                                contentDescription = title
                            )
                        },
                        label = { Text(title) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = MaterialTheme.colorScheme.onPrimaryContainer,
                            selectedTextColor = MaterialTheme.colorScheme.onSurface,
                            indicatorColor = MaterialTheme.colorScheme.primaryContainer,
                            unselectedIconColor = MaterialTheme.colorScheme.onSurfaceVariant,
                            unselectedTextColor = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    )
                }
            }
        }
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
        ConnectionState.CONNECTED -> Color(0xFF4ADE80) to "Connected"
        ConnectionState.CONNECTING -> Color(0xFFFBBF24) to "Connecting"
        ConnectionState.DISCONNECTED -> MaterialTheme.colorScheme.error to "Disconnected"
    }

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.padding(end = 16.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(statusColor)
            )
            Spacer(Modifier.width(8.dp))
            Text(
                text = statusText,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
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
        item {
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
        
        item {
            Row(modifier = Modifier.fillMaxWidth().height(IntrinsicSize.Max), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                // Diode Card
                Card(
                    modifier = Modifier.weight(1f).fillMaxHeight(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp).fillMaxSize(),
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Diode Mode", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        Spacer(Modifier.height(16.dp))
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(uiState.diodeValue, fontSize = 28.sp, fontWeight = FontWeight.Medium, fontFamily = FontFamily.Monospace)
                            if (uiState.diodeValue != "--") {
                                Text("V", fontSize = 16.sp, modifier = Modifier.padding(bottom = 4.dp))
                            }
                        }
                        Spacer(Modifier.height(16.dp))
                        Button(
                            onClick = { viewModel.sendDiode() },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("Read")
                        }
                    }
                }
                
                // I2C Card
                Card(
                    modifier = Modifier.weight(1f).fillMaxHeight(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp).fillMaxSize(),
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("I2C Scanner", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        Spacer(Modifier.height(12.dp))
                        
                        Row(
                            modifier = Modifier.fillMaxWidth().weight(1f), 
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            uiState.i2cDevices.take(3).forEach { device ->
                                Surface(
                                    color = MaterialTheme.colorScheme.primaryContainer,
                                    shape = RoundedCornerShape(4.dp)
                                ) {
                                    Text(
                                        device, 
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                        fontSize = 12.sp, 
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }
                            if (uiState.i2cDevices.size > 3) {
                                Surface(
                                    border = border.BorderStroke(1.dp, MaterialTheme.colorScheme.primary),
                                    shape = RoundedCornerShape(4.dp),
                                    color = Color.Transparent
                                ) {
                                    Text(
                                        "...", 
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                        fontSize = 12.sp, 
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }
                        }
                        Spacer(Modifier.height(12.dp))
                        OutlinedButton(
                            onClick = { viewModel.sendI2c() },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("Scan")
                        }
                    }
                }
            }
        }
        
        item {
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

    LaunchedEffect(uiState.logs.size) {
        if (uiState.logs.isNotEmpty()) {
            listState.animateScrollToItem(uiState.logs.size - 1)
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
            border = border.BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
        ) {
            LazyColumn(
                state = listState,
                modifier = Modifier.fillMaxSize().padding(12.dp)
            ) {
                items(uiState.logs) { log ->
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
                Text("Appearance", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.height(16.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Robot Theme / Legacy Dark Mode")
                    Switch(
                        checked = uiState.isRobotTheme,
                        onCheckedChange = { viewModel.toggleTheme() }
                    )
                }
            }
        }
    }
}
"""

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(code)

