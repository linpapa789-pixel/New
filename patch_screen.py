import re

with open("app/src/main/java/com/example/DiagnosticScreen.kt", "r") as f:
    content = f.read()

# Replace DiagnosticScreen Scaffold
scaffold_regex = re.compile(r"@Composable\nfun DiagnosticScreen.*?\{ innerPadding ->", re.DOTALL)

new_scaffold = """@Composable
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
    ) { innerPadding ->"""

content = scaffold_regex.sub(new_scaffold, content)

# Update ConnectionBadge
connection_badge_regex = re.compile(r"@Composable\nfun ConnectionBadge.*?\}\n\}", re.DOTALL)
new_badge = """@Composable
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
}"""

content = connection_badge_regex.sub(new_badge, content)

# Update ToolsView
tools_view_regex = re.compile(r"@Composable\nfun ToolsView.*?fun DiodeModeView", re.DOTALL)
new_tools = """@Composable
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
fun DiodeModeView"""

content = tools_view_regex.sub(new_tools, content)

# Update DiodeModeView
diode_view_regex = re.compile(r"@Composable\nfun DiodeModeView.*?fun UartModeView", re.DOTALL)
new_diode = """@Composable
fun DiodeModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // Live Scan Card (Terminal Style)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.surface)
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("> LIVE_PROBE_READING", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                    Spacer(Modifier.height(4.dp))
                    Text("ZERO_LAG_ADC", fontFamily = FontFamily.Monospace, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
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
fun UartModeView"""

content = diode_view_regex.sub(new_diode, content)

# Update UartModeView
uart_view_regex = re.compile(r"@Composable\nfun UartModeView.*?fun I2cModeView", re.DOTALL)
new_uart = """@Composable
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
fun I2cModeView"""

content = uart_view_regex.sub(new_uart, content)

# Update I2cModeView
i2c_view_regex = re.compile(r"@Composable\nfun I2cModeView.*?fun ConnectionCard", re.DOTALL)
new_i2c = """@Composable
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
fun ConnectionCard"""

content = i2c_view_regex.sub(new_i2c, content)

with open("app/src/main/java/com/example/DiagnosticScreen.kt", "w") as f:
    f.write(content)

