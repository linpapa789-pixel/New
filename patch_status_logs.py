import re

with open("app/src/main/java/com/example/DiagnosticScreen.kt", "r") as f:
    content = f.read()

status_logs_regex = re.compile(r"@Composable\nfun StatusLogsView.*?\}\n\}\n\}\n", re.DOTALL)

new_status_logs = """@Composable
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
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
            .background(MaterialTheme.colorScheme.surface)
    ) {
        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("> SYSTEM_EVENT_LOGS", fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = { viewModel.clearLogs() },
                        shape = RoundedCornerShape(4.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
                        modifier = Modifier.height(28.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error, contentColor = MaterialTheme.colorScheme.onError)
                    ) {
                        Text("CLEAR", fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                    }
                    Button(
                        onClick = { exportLauncher.launch("esp32_logs_${System.currentTimeMillis()}.txt") },
                        shape = RoundedCornerShape(4.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
                        modifier = Modifier.height(28.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary, contentColor = MaterialTheme.colorScheme.onPrimary)
                    ) {
                        Text("EXPORT", fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                    }
                }
            }
            
            Surface(
                modifier = Modifier.fillMaxWidth().weight(1f),
                color = MaterialTheme.colorScheme.background,
                shape = RoundedCornerShape(4.dp),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline)
            ) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize().padding(8.dp)
                ) {
                    items(uiState.appLogs) { log ->
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
"""

# Let's replace the StatusLogsView method.
content = status_logs_regex.sub(new_status_logs, content)

with open("app/src/main/java/com/example/DiagnosticScreen.kt", "w") as f:
    f.write(content)

