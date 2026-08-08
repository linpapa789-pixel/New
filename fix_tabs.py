with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

config_tab_code = """
                3 -> ConfigView(viewModel, uiState, theme)
                else -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("Coming Soon", color = Color.Gray)
                }
"""

content = content.replace("""                else -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("Coming Soon", color = Color.Gray)
                }""", config_tab_code)

config_view = """
@Composable
fun ConfigView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState, theme: AppTheme) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(theme.surface, RoundedCornerShape(24.dp))
                .border(1.dp, theme.border, RoundedCornerShape(24.dp))
                .padding(16.dp)
        ) {
            Text("အပြင်အဆင် (Theme)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = theme.textPrimary, modifier = Modifier.padding(bottom = 16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("စက်ရုပ် အပြင်အဆင် (Robot Theme)", fontSize = 14.sp, color = theme.textSecondary)
                Switch(
                    checked = uiState.isRobotTheme,
                    onCheckedChange = { viewModel.toggleTheme() },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = theme.primary,
                        checkedTrackColor = theme.primaryContainer
                    )
                )
            }
        }
    }
}
"""

content += "\n" + config_view

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
