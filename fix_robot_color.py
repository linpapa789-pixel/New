with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

robot_theme_old = """val RobotTheme = AppTheme(
    bg = Color(0xFF0F172A),
    surface = Color(0xFF1E293B),
    border = Color(0xFF334155),
    textPrimary = Color(0xFFF8FAFC),
    textSecondary = Color(0xFF94A3B8),
    primary = Color(0xFF10B981),
    primaryContainer = Color(0xFF064E3B),
    secondaryContainer = Color(0xFF0F172A),
    terminalBg = Color(0xFF020617),
    terminalText = Color(0xFF10B981),
    statusConnected = Color(0xFF10B981),
    statusConnecting = Color(0xFFEAB308),
    statusDisconnected = Color(0xFFEF4444),
    logTime = Color(0xFF64748B),
    logInfo = Color(0xFF38BDF8),
    logCmd = Color(0xFFF472B6),
    logRes = Color(0xFF10B981),
    terminalCursor = Color(0xFF10B981),
    error = Color(0xFFEF4444)
)"""

robot_theme_new = """val RobotTheme = AppTheme(
    bg = Color(0xFF121212),
    surface = Color(0xFF1E1E1E),
    border = Color(0xFF333333),
    textPrimary = Color(0xFFE0E0E0),
    textSecondary = Color(0xFF9E9E9E),
    primary = Color(0xFFBDBDBD),
    primaryContainer = Color(0xFF424242),
    secondaryContainer = Color(0xFF121212),
    terminalBg = Color(0xFF000000),
    terminalText = Color(0xFFBDBDBD),
    statusConnected = Color(0xFFE0E0E0),
    statusConnecting = Color(0xFF9E9E9E),
    statusDisconnected = Color(0xFF757575),
    logTime = Color(0xFF757575),
    logInfo = Color(0xFFBDBDBD),
    logCmd = Color(0xFF9E9E9E),
    logRes = Color(0xFFE0E0E0),
    terminalCursor = Color(0xFFBDBDBD),
    error = Color(0xFFF44336)
)"""

content = content.replace(robot_theme_old, robot_theme_new)

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
