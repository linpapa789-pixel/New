with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

# Cap the logs to 1000 to prevent OOM
old_add_log = """    private fun addLog(type: LogType, message: String) {
        _uiState.update { it.copy(logs = it.logs + LogMessage(currentTime(), type, message)) }
    }"""

new_add_log = """    private fun addLog(type: LogType, message: String) {
        _uiState.update { state -> 
            val newLogs = (state.logs + LogMessage(currentTime(), type, message)).takeLast(1000)
            state.copy(logs = newLogs) 
        }
    }"""

content = content.replace(old_add_log, new_add_log)

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)

