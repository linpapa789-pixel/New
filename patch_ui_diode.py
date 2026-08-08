with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

old_diode = """                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(uiState.diodeValue, fontSize = 28.sp, fontWeight = FontWeight.Medium, fontFamily = FontFamily.Monospace)
                            if (uiState.diodeValue != "--") {
                                Text("V", fontSize = 16.sp, modifier = Modifier.padding(bottom = 4.dp))
                            }
                        }"""

new_diode = """                        Column {
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
                        }"""

content = content.replace(old_diode, new_diode)

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)

