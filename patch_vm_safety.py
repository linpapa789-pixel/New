import re

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

# Fix connectWifi to prevent crash on invalid URL
old_connect_wifi = """    fun connectWifi() {
        isAutoReconnectEnabled = true
        wifiReconnectJob?.cancel()
        
        disconnectInternal() // disconnect without clearing auto-reconnect flag
        _uiState.update { it.copy(connectionMode = ConnectionMode.WIFI, connectionState = ConnectionState.CONNECTING) }
        
        val ip = _uiState.value.wifiIp
        val port = _uiState.value.wifiPort
        val url = "ws://$ip:$port"
        
        val request = Request.Builder().url(url).build()
        
        webSocket = client.newWebSocket(request, object : WebSocketListener() {"""

new_connect_wifi = """    fun connectWifi() {
        isAutoReconnectEnabled = true
        wifiReconnectJob?.cancel()
        
        disconnectInternal() // disconnect without clearing auto-reconnect flag
        _uiState.update { it.copy(connectionMode = ConnectionMode.WIFI, connectionState = ConnectionState.CONNECTING) }
        
        val ip = _uiState.value.wifiIp
        val port = _uiState.value.wifiPort
        val url = "ws://$ip:$port"
        
        try {
            val request = Request.Builder().url(url).build()
            webSocket = client.newWebSocket(request, object : WebSocketListener() {"""

content = content.replace(old_connect_wifi, new_connect_wifi)

# Fix the end of connectWifi to close the try block
old_connect_wifi_end = """            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                addAppLog(LogType.INFO, "Wi-Fi အမှားအယွင်း: ${t.message}")
                handleReconnect()
            }
        })
    }"""

new_connect_wifi_end = """            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                addAppLog(LogType.INFO, "Wi-Fi အမှားအယွင်း: ${t.message}")
                handleReconnect()
            }
        })
        } catch (e: Exception) {
            _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
            addAppLog(LogType.INFO, "URL မှားယွင်းနေပါသည်: ${e.message}")
            isAutoReconnectEnabled = false // stop auto reconnect for invalid URL
        }
    }"""

content = content.replace(old_connect_wifi_end, new_connect_wifi_end)


with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)

