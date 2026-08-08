with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

theme_defs = """
data class AppTheme(
    val bg: Color,
    val surface: Color,
    val border: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val primary: Color,
    val primaryContainer: Color,
    val secondaryContainer: Color,
    val terminalBg: Color,
    val terminalText: Color
)

val ModernTheme = AppTheme(
    bg = Color(0xFFF7F2FA),
    surface = Color.White,
    border = Color(0xFFCAC4D0),
    textPrimary = Color(0xFF1C1B1F),
    textSecondary = Color(0xFF49454F),
    primary = Color(0xFF6750A4),
    primaryContainer = Color(0xFFE8DEF8),
    secondaryContainer = Color(0xFFF3EDF7),
    terminalBg = Color(0xFF1C1B1F),
    terminalText = Color(0xFFE6E1E5)
)

val RobotTheme = AppTheme(
    bg = Color(0xFF0F172A),
    surface = Color(0xFF1E293B),
    border = Color(0xFF334155),
    textPrimary = Color(0xFFF8FAFC),
    textSecondary = Color(0xFF94A3B8),
    primary = Color(0xFF10B981),
    primaryContainer = Color(0xFF064E3B),
    secondaryContainer = Color(0xFF0F172A),
    terminalBg = Color(0xFF020617),
    terminalText = Color(0xFF10B981)
)

@Composable
fun DiagnosticScreen(viewModel: DiagnosticViewModel, modifier: Modifier = Modifier) {
    val uiState by viewModel.uiState.collectAsState()
    val theme = if (uiState.isRobotTheme) RobotTheme else ModernTheme

    Column(modifier = modifier.fillMaxSize().background(theme.bg)) {
"""

# Replace the beginning of DiagnosticScreen
old_screen_start = """@Composable
fun DiagnosticScreen(viewModel: DiagnosticViewModel, modifier: Modifier = Modifier) {
    val uiState by viewModel.uiState.collectAsState()

    val bgColor = theme.bg
    val primaryText = theme.textPrimary

    Column(modifier = modifier.fillMaxSize().background(bgColor)) {"""

if old_screen_start in content:
    content = content.replace(old_screen_start, theme_defs)
else:
    # Try another pattern just in case
    old2 = """@Composable
fun DiagnosticScreen(viewModel: DiagnosticViewModel, modifier: Modifier = Modifier) {
    val uiState by viewModel.uiState.collectAsState()

    val bgColor = theme.bg
    val primaryText = theme.textPrimary

    Column(modifier = modifier.fillMaxSize().background(theme.bg)) {"""
    if old2 in content:
        content = content.replace(old2, theme_defs)
    else:
        print("Could not find insertion point for AppTheme.")

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
