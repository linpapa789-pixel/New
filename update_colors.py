with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

# Define new theme attributes
new_theme_class = """data class AppTheme(
    val bg: Color,
    val surface: Color,
    val border: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val primary: Color,
    val primaryContainer: Color,
    val secondaryContainer: Color,
    val terminalBg: Color,
    val terminalText: Color,
    val statusConnected: Color,
    val statusConnecting: Color,
    val statusDisconnected: Color,
    val logTime: Color,
    val logInfo: Color,
    val logCmd: Color,
    val logRes: Color,
    val terminalCursor: Color,
    val error: Color
)"""

modern_theme = """val ModernTheme = AppTheme(
    bg = Color(0xFFF7F2FA),
    surface = Color.White,
    border = Color(0xFFCAC4D0),
    textPrimary = Color(0xFF1C1B1F),
    textSecondary = Color(0xFF49454F),
    primary = Color(0xFF6750A4),
    primaryContainer = Color(0xFFE8DEF8),
    secondaryContainer = Color(0xFFF3EDF7),
    terminalBg = Color(0xFF1C1B1F),
    terminalText = Color(0xFFE6E1E5),
    statusConnected = Color(0xFF4ADE80),
    statusConnecting = Color(0xFFFBBF24),
    statusDisconnected = Color(0xFFF43F5E),
    logTime = Color(0xFF938F99),
    logInfo = Color(0xFFD0BCFF),
    logCmd = Color(0xFFB6C4FF),
    logRes = Color(0xFFC4EED0),
    terminalCursor = Color(0xFFD0BCFF),
    error = Color(0xFFB3261E)
)"""

robot_theme = """val RobotTheme = AppTheme(
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

import re

# replace data class
content = re.sub(r'data class AppTheme\(.*?\)', new_theme_class, content, flags=re.DOTALL)
content = re.sub(r'val ModernTheme = AppTheme\(.*?\)', modern_theme, content, flags=re.DOTALL)
content = re.sub(r'val RobotTheme = AppTheme\(.*?\)', robot_theme, content, flags=re.DOTALL)

# Now replace usages
content = content.replace('Color(0xFF4ADE80)', 'theme.statusConnected')
content = content.replace('Color(0xFFFBBF24)', 'theme.statusConnecting')
content = content.replace('Color(0xFFF43F5E)', 'theme.statusDisconnected')
content = content.replace('Color.Red', 'theme.statusDisconnected')
content = content.replace('Color(0xFFD0BCFF)', 'theme.logInfo')
content = content.replace('Color(0xFFF2B8B5)', 'theme.error')
content = content.replace('Color(0xFF938F99)', 'theme.logTime')
content = content.replace('Color(0xFFB6C4FF)', 'theme.logCmd')
content = content.replace('Color(0xFFC4EED0)', 'theme.logRes')
content = content.replace('Color(0xFFB3261E)', 'theme.error')

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)

