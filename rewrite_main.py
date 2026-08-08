with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

content = content.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier\nimport androidx.compose.runtime.collectAsState\nimport androidx.compose.runtime.getValue")
content = content.replace("setContent {\n            MyApplicationTheme {", "setContent {\n            val uiState by viewModel.uiState.collectAsState()\n            MyApplicationTheme(darkTheme = uiState.isDarkTheme) {")

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content)

