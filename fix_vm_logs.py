import re

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

old_add_app_log = """    private fun addAppLog(type: LogType, message: String) {
        _uiState.update { state ->
            val newLogs = state.logs.toMutableList()
            newLogs.add(LogMessage(currentTime(), type, message))
            if (newLogs.size > 200) newLogs.removeAt(0)
            state.copy(logs = newLogs)
        }
    }"""

new_add_app_log = """    private fun addAppLog(type: LogType, message: String) {
        _uiState.update { state -> 
            val newLogs = (state.appLogs + LogMessage(currentTime(), type, message)).takeLast(1000)
            state.copy(appLogs = newLogs) 
        }
    }

    private fun addUartLog(message: String) {
        _uiState.update { state -> 
            val newLogs = (state.uartLogs + LogMessage(currentTime(), LogType.RES, message)).takeLast(1000)
            state.copy(uartLogs = newLogs) 
        }
    }"""

if old_add_app_log in content:
    content = content.replace(old_add_app_log, new_add_app_log)
else:
    print("Could not find old_add_app_log")

old_clear_logs = """    fun clearLogs() {
        _uiState.update { state ->
            state.copy(logs = emptyList())
        }
        addAppLog(LogType.INFO, "မှတ်တမ်းများကို ရှင်းလင်းလိုက်ပါပြီ")
    }"""

new_clear_logs = """    fun clearLogs() {
        _uiState.update { state ->
            state.copy(appLogs = emptyList(), uartLogs = emptyList())
        }
        addAppLog(LogType.INFO, "မှတ်တမ်းများကို ရှင်းလင်းလိုက်ပါပြီ")
    }"""

if old_clear_logs in content:
    content = content.replace(old_clear_logs, new_clear_logs)

old_save_logs = """                    val logsText = _uiState.value.logs.joinToString("\\n") { log ->
                        "[${log.time}] ${log.type}: ${log.message}"
                    }"""

new_save_logs = """                    val appLogsText = _uiState.value.appLogs.joinToString("\\n") { log ->
                        "[${log.time}] ${log.type}: ${log.message}"
                    }
                    val uartLogsText = _uiState.value.uartLogs.joinToString("\\n") { log ->
                        "[${log.time}] ${log.message}"
                    }
                    val logsText = "--- APP LOGS ---\\n$appLogsText\\n\\n--- UART LOGS ---\\n$uartLogsText" """

if old_save_logs in content:
    content = content.replace(old_save_logs, new_save_logs)
else:
    print("Could not find old_save_logs")

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)
