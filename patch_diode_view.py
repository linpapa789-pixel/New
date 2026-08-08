import re

with open("app/src/main/java/com/example/DiagnosticScreen.kt", "r") as f:
    content = f.read()

# Add necessary Canvas imports if missing
imports = [
    "import androidx.compose.foundation.Canvas",
    "import androidx.compose.ui.geometry.Offset",
    "import androidx.compose.ui.graphics.Path",
    "import androidx.compose.ui.graphics.drawscope.Stroke",
]
for imp in imports:
    if imp not in content:
        content = content.replace("import androidx.compose.runtime.*", f"import androidx.compose.runtime.*\n{imp}")

diode_view_regex = re.compile(r"@Composable\nfun DiodeModeView.*?// Diode Smart Comparison", re.DOTALL)

new_diode = """@Composable
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
        
        // Diode Smart Comparison"""

content = diode_view_regex.sub(new_diode, content)

with open("app/src/main/java/com/example/DiagnosticScreen.kt", "w") as f:
    f.write(content)

