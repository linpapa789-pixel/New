with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

# Update UartModeView to use uartLogs
content = content.replace('uiState.logs.size', 'uiState.uartLogs.size')
content = content.replace('uiState.logs.isNotEmpty()', 'uiState.uartLogs.isNotEmpty()')
content = content.replace('items(uiState.logs)', 'items(uiState.uartLogs)')

# The above replacements will change BOTH UartModeView and StatusLogsView since both had `uiState.logs`.
# Let's verify how we can fix StatusLogsView to use appLogs explicitly.

# Fix StatusLogsView to use appLogs
status_view_start = content.find("fun StatusLogsView")
if status_view_start != -1:
    before = content[:status_view_start]
    after = content[status_view_start:]
    # in the 'after' portion, which is StatusLogsView, we want to replace uartLogs back to appLogs
    after = after.replace('uiState.uartLogs.size', 'uiState.appLogs.size')
    after = after.replace('uiState.uartLogs.isNotEmpty()', 'uiState.appLogs.isNotEmpty()')
    after = after.replace('items(uiState.uartLogs)', 'items(uiState.appLogs)')
    content = before + after

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
