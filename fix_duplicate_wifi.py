with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

# I will find the second occurrence of the wifi inputs block and remove it.
wifi_block = """                if (uiState.connectionMode == ConnectionMode.WIFI) {
                    Spacer(Modifier.height(12.dp))
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        androidx.compose.material3.OutlinedTextField(
                            value = uiState.wifiIp,
                            onValueChange = { viewModel.updateWifiIp(it) },
                            label = { Text("IP Address", fontSize = 12.sp) },
                            modifier = Modifier.weight(2f),
                            singleLine = true,
                            textStyle = androidx.compose.ui.text.TextStyle(fontSize = 12.sp, color = theme.textPrimary),
                            colors = androidx.compose.material3.OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = theme.primary,
                                unfocusedBorderColor = theme.border,
                                focusedLabelColor = theme.primary,
                                unfocusedLabelColor = theme.textSecondary
                            )
                        )
                        androidx.compose.material3.OutlinedTextField(
                            value = uiState.wifiPort,
                            onValueChange = { viewModel.updateWifiPort(it) },
                            label = { Text("Port", fontSize = 12.sp) },
                            modifier = Modifier.weight(1f),
                            singleLine = true,
                            textStyle = androidx.compose.ui.text.TextStyle(fontSize = 12.sp, color = theme.textPrimary),
                            colors = androidx.compose.material3.OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = theme.primary,
                                unfocusedBorderColor = theme.border,
                                focusedLabelColor = theme.primary,
                                unfocusedLabelColor = theme.textSecondary
                            )
                        )
                    }
                    Spacer(Modifier.height(8.dp))
                    Button(
                        onClick = { viewModel.connectWifi() },
                        modifier = Modifier.fillMaxWidth().height(48.dp),
                        shape = RoundedCornerShape(theme.cornerRadius),
                        colors = ButtonDefaults.buttonColors(containerColor = theme.primary)
                    ) {
                        Text("Connect", color = theme.surface)
                    }
                }
"""

first_idx = content.find(wifi_block)
if first_idx != -1:
    second_idx = content.find(wifi_block, first_idx + len(wifi_block))
    if second_idx != -1:
        # replace the second occurrence with just empty string
        content = content[:second_idx] + content[second_idx + len(wifi_block):]

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
