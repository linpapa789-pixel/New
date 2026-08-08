import re
with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

# Add to DiagnosticUiState
content = content.replace("    val connectionState: ConnectionState = ConnectionState.DISCONNECTED,", "    val connectionState: ConnectionState = ConnectionState.DISCONNECTED,\n    val wifiIp: String = \"192.168.4.1\",\n    val wifiPort: String = \"81\",")

# Add setters in ViewModel
setters = """
    fun updateWifiIp(ip: String) {
        _uiState.update { it.copy(wifiIp = ip) }
    }

    fun updateWifiPort(port: String) {
        _uiState.update { it.copy(wifiPort = port) }
    }

    fun connectWifi() {"""

content = content.replace("    fun connectWifi() {", setters)

# Update connectWifi
connect_wifi_old = """    fun connectWifi() {
        disconnect()
        _uiState.update { it.copy(connectionMode = ConnectionMode.WIFI, connectionState = ConnectionState.CONNECTING) }
        val request = Request.Builder().url("ws://192.168.4.1:81").build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _uiState.update { it.copy(connectionState = ConnectionState.CONNECTED) }
                addLog(LogType.INFO, "ws://192.168.4.1:81 သို့ ချိတ်ဆက်ပြီးပါပြီ")
            }"""

connect_wifi_new = """    fun connectWifi() {
        disconnect()
        _uiState.update { it.copy(connectionMode = ConnectionMode.WIFI, connectionState = ConnectionState.CONNECTING) }
        val ip = _uiState.value.wifiIp
        val port = _uiState.value.wifiPort
        val url = "ws://$ip:$port"
        val request = Request.Builder().url(url).build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _uiState.update { it.copy(connectionState = ConnectionState.CONNECTED) }
                addLog(LogType.INFO, "$url သို့ ချိတ်ဆက်ပြီးပါပြီ")
            }"""

content = content.replace(connect_wifi_old, connect_wifi_new)

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)
