import re
import sys

def patch_ui():
    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "r") as f:
        content = f.read()

    new_view = """
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
"""
    content = content + "\n" + new_view
    
    # We need to add an import if it's not there, but most are there.
    # Text align import is in the string.
    
    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "w") as f:
        f.write(content)

patch_ui()
