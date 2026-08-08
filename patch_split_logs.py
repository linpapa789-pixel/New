import re

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

# Replace logs with appLogs and uartLogs in state
content = content.replace('val logs: List<LogMessage> = emptyList(),', 'val appLogs: List<LogMessage> = emptyList(),\n    val uartLogs: List<LogMessage> = emptyList(),')

# Replace addLog with addAppLog and addUartLog
old_add_log = """    private fun addLog(type: LogType, message: String) {
        _uiState.update { state -> 
            val newLogs = (state.logs + LogMessage(currentTime(), type, message)).takeLast(1000)
            state.copy(logs = newLogs) 
        }
    }"""

new_add_log = """    private fun addAppLog(type: LogType, message: String) {
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

content = content.replace(old_add_log, new_add_log)

# Replace addLog with addAppLog everywhere else
content = content.replace('addLog(', 'addAppLog(')

# Update handleIncomingMessage to route UART logs correctly
old_handle = """    private fun handleIncomingMessage(text: String) {
        try {
            val json = JSONObject(text)
            val type = json.optString("type")
            
            // Only log non-live messages to prevent log spam & UI lag
            if (type != "live_probe") {
                addAppLog(LogType.RES, text)
            }
            
            when (type) {
                "live_probe" -> {
                    _uiState.update { it.copy(liveProbeValue = json.optString("value", "0.00")) }
                }
                "diode" -> {
                    _uiState.update { it.copy(diodeValue = json.optString("value", "--")) }
                }
                "i2c" -> {
                    val devicesArray = json.optJSONArray("devices")
                    val devices = mutableListOf<String>()
                    if (devicesArray != null) {
                        for (i in 0 until devicesArray.length()) {
                            devices.add(devicesArray.getString(i))
                        }
                    }
                    _uiState.update { it.copy(i2cDevices = devices) }
                }
            }
        } catch (e: Exception) {
            // Not JSON, just log it
            addAppLog(LogType.RES, text)
        }
    }"""

new_handle = """    private fun handleIncomingMessage(text: String) {
        try {
            val json = JSONObject(text)
            val type = json.optString("type")
            
            if (type == "uart" || type == "uart_log") {
                addUartLog(json.optString("log", text))
                return
            }
            
            // Only log non-live messages to prevent log spam & UI lag
            if (type != "live_probe") {
                addAppLog(LogType.RES, text)
            }
            
            when (type) {
                "live_probe" -> {
                    _uiState.update { it.copy(liveProbeValue = json.optString("value", "0.00")) }
                }
                "diode" -> {
                    _uiState.update { it.copy(diodeValue = json.optString("value", "--")) }
                }
                "i2c" -> {
                    val devicesArray = json.optJSONArray("devices")
                    val devices = mutableListOf<String>()
                    if (devicesArray != null) {
                        for (i in 0 until devicesArray.length()) {
                            devices.add(devicesArray.getString(i))
                        }
                    }
                    _uiState.update { it.copy(i2cDevices = devices) }
                }
            }
        } catch (e: Exception) {
            // Not JSON, assume it's raw UART data
            addUartLog(text)
        }
    }"""

content = content.replace(old_handle, new_handle)

# Update saveLogsToFile and clearLogs
old_save = """    fun saveLogsToFile(context: Context, uri: android.net.Uri) {
        try {
            context.contentResolver.openOutputStream(uri)?.use { outputStream ->
                val sb = StringBuilder()
                _uiState.value.logs.forEach { log ->
                    sb.append("[${log.time}] [${log.type}] ${log.message}\\n")
                }
                outputStream.write(sb.toString().toByteArray())
            }
            addAppLog(LogType.INFO, "Log များကို သိမ်းဆည်းပြီးပါပြီ")
        } catch (e: Exception) {
            addAppLog(LogType.INFO, "Log သိမ်းဆည်းခြင်း မအောင်မြင်ပါ: ${e.message}")
        }
    }

    fun clearLogs() {
        _uiState.update { it.copy(logs = emptyList()) }
    }"""

new_save = """    fun saveLogsToFile(context: Context, uri: android.net.Uri) {
        try {
            context.contentResolver.openOutputStream(uri)?.use { outputStream ->
                val sb = StringBuilder()
                sb.append("--- APP LOGS ---\\n")
                _uiState.value.appLogs.forEach { log ->
                    sb.append("[${log.time}] [${log.type}] ${log.message}\\n")
                }
                sb.append("\\n--- UART LOGS ---\\n")
                _uiState.value.uartLogs.forEach { log ->
                    sb.append("[${log.time}] ${log.message}\\n")
                }
                outputStream.write(sb.toString().toByteArray())
            }
            addAppLog(LogType.INFO, "Log များကို သိမ်းဆည်းပြီးပါပြီ")
        } catch (e: Exception) {
            addAppLog(LogType.INFO, "Log သိမ်းဆည်းခြင်း မအောင်မြင်ပါ: ${e.message}")
        }
    }

    fun clearLogs() {
        _uiState.update { it.copy(appLogs = emptyList(), uartLogs = emptyList()) }
    }"""

content = content.replace(old_save, new_save)

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)
