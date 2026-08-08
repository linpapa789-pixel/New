import re

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

replacements = {
    'Color(0xFFF7F2FA)': 'theme.bg',
    'Color.White': 'theme.surface',
    'Color(0xFFCAC4D0)': 'theme.border',
    'Color(0xFF1C1B1F)': 'theme.textPrimary',
    'Color(0xFF49454F)': 'theme.textSecondary',
    'Color(0xFF6750A4)': 'theme.primary',
    'Color(0xFFE8DEF8)': 'theme.primaryContainer',
    'Color(0xFF1D192B)': 'theme.textPrimary',
    'Color(0xFFF3EDF7)': 'theme.secondaryContainer',
    'Color(0xFFE6E1E5)': 'theme.terminalText',
    'Color(0xFF1D1B20)': 'theme.textPrimary'
}

for old, new in replacements.items():
    content = content.replace(old, new)
    
# We also need to change signatures to pass theme.
# `fun DiagnosticScreen(viewModel: DiagnosticViewModel, modifier: Modifier = Modifier)` -> define theme inside, pass to views
# `fun ToolsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState)` -> `fun ToolsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState, theme: AppTheme)`

content = content.replace('fun ToolsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState)', 'fun ToolsView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState, theme: AppTheme)')
content = content.replace('ToolsView(viewModel, uiState)', 'ToolsView(viewModel, uiState, theme)')

content = content.replace('fun OtgFlashView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState)', 'fun OtgFlashView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState, theme: AppTheme)')
content = content.replace('OtgFlashView(viewModel, uiState)', 'OtgFlashView(viewModel, uiState, theme)')

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
