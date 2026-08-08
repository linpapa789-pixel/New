with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

old_uart = """@Composable
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
}"""

new_uart = """@Composable
fun UartModeView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    val listState = rememberLazyListState()

    LaunchedEffect(uiState.logs.size) {
        if (uiState.logs.isNotEmpty()) {
            listState.animateScrollToItem(uiState.logs.size - 1)
        }
    }

    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("UART Boot Logs", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = { viewModel.sendUartStart() },
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                        modifier = Modifier.height(32.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                    ) {
                        Text("Start", fontSize = 12.sp)
                    }
                    Button(
                        onClick = { viewModel.sendUartStop() },
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                        modifier = Modifier.height(32.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                    ) {
                        Text("Stop", fontSize = 12.sp)
                    }
                }
            }
            Spacer(Modifier.height(12.dp))
            
            Surface(
                modifier = Modifier.fillMaxWidth().height(300.dp),
                color = Color(0xFF0D1117), // Deep terminal background
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant)
            ) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize().padding(8.dp)
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
}"""

content = content.replace(old_uart, new_uart)
with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
