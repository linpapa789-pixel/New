with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

old_disc = """    fun disconnect() {
        try {
            webSocket?.close(1000, "User disconnected")
        } catch (e: Exception) {}
        webSocket = null
        
        try {
            bluetoothGatt?.disconnect()
            bluetoothGatt?.close()
        } catch (e: Exception) {}
        bluetoothGatt = null
        
        _uiState.update { it.copy(connectionMode = ConnectionMode.NONE, connectionState = ConnectionState.DISCONNECTED) }
    }"""

new_disc = """    fun disconnect() {
        isAutoReconnectEnabled = false
        wifiReconnectJob?.cancel()
        disconnectInternal()
        _uiState.update { it.copy(connectionMode = ConnectionMode.NONE, connectionState = ConnectionState.DISCONNECTED) }
        addLog(LogType.INFO, "ချိတ်ဆက်မှု ဖြတ်တောက်လိုက်ပါပြီ")
    }"""

content = content.replace(old_disc, new_disc)

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)

