with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

# Adding Live Probe Card before Diode Card (in ToolsView)
old_cards = """            Row(modifier = Modifier.fillMaxWidth().height(IntrinsicSize.Max), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                // Diode Card
                Card("""

new_cards = """            // Live Scan Card
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp).fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Live Probe (Zero-Lag)", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        Spacer(Modifier.height(4.dp))
                        Text("Real-time voltage/resistance", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(uiState.liveProbeValue, fontSize = 36.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace, color = MaterialTheme.colorScheme.onSurface)
                        if (uiState.liveProbeValue != "--" && uiState.liveProbeValue != "0.00") {
                            Text("V", fontSize = 18.sp, modifier = Modifier.padding(bottom = 6.dp, start = 4.dp), color = MaterialTheme.colorScheme.onSurface)
                        }
                    }
                }
            }
            
            Row(modifier = Modifier.fillMaxWidth().height(IntrinsicSize.Max), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                // Diode Card
                Card("""

content = content.replace(old_cards, new_cards)

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)

