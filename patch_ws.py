import re

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

# Add liveProbeValue to state
content = content.replace('val diodeValue: String = "--",', 'val diodeValue: String = "--",\n    val liveProbeValue: String = "0.00",')

# Modify ViewModel imports
import_block = "import kotlinx.coroutines.delay\nimport kotlinx.coroutines.Job\n"
if "import kotlinx.coroutines.delay" not in content:
    content = content.replace('import kotlinx.coroutines.withContext', 'import kotlinx.coroutines.withContext\n' + import_block)

# Add class variables
if "private var wifiReconnectJob: Job? = null" not in content:
    content = content.replace('private val client = OkHttpClient()', 'private val client = OkHttpClient()\n    private var wifiReconnectJob: Job? = null\n    private var isAutoReconnectEnabled = false')

# Replace connectWifi method
old_connect_wifi = """    fun connectWifi() {
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
            }
            override fun onMessage(webSocket: WebSocket, text: String) {
                handleIncomingMessage(text)
            }
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                addLog(LogType.INFO, "Wi-Fi ချိတ်ဆက်မှု ပြတ်တောက်သွားပါပြီ")
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                addLog(LogType.INFO, "Wi-Fi အမှားအယွင်း: ${t.message}")
            }
        })
    }"""

new_connect_wifi = """    fun connectWifi() {
        isAutoReconnectEnabled = true
        wifiReconnectJob?.cancel()
        
        disconnectInternal() // disconnect without clearing auto-reconnect flag
        _uiState.update { it.copy(connectionMode = ConnectionMode.WIFI, connectionState = ConnectionState.CONNECTING) }
        
        val ip = _uiState.value.wifiIp
        val port = _uiState.value.wifiPort
        val url = "ws://$ip:$port"
        
        val request = Request.Builder().url(url).build()
        
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _uiState.update { it.copy(connectionState = ConnectionState.CONNECTED) }
                addLog(LogType.INFO, "$url သို့ ချိတ်ဆက်ပြီးပါပြီ")
            }
            override fun onMessage(webSocket: WebSocket, text: String) {
                handleIncomingMessage(text)
            }
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                addLog(LogType.INFO, "Wi-Fi ချိတ်ဆက်မှု ပြတ်တောက်သွားပါပြီ")
                handleReconnect()
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                addLog(LogType.INFO, "Wi-Fi အမှားအယွင်း: ${t.message}")
                handleReconnect()
            }
        })
    }
    
    private fun handleReconnect() {
        if (isAutoReconnectEnabled) {
            wifiReconnectJob?.cancel()
            wifiReconnectJob = viewModelScope.launch(Dispatchers.IO) {
                addLog(LogType.INFO, "၃ စက္ကန့်အတွင်း ပြန်လည်ချိတ်ဆက်ပါမည်...")
                delay(3000)
                if (isAutoReconnectEnabled) {
                    withContext(Dispatchers.Main) {
                        connectWifi()
                    }
                }
            }
        }
    }
    
    private fun disconnectInternal() {
        webSocket?.cancel()
        webSocket = null
        if (bluetoothGatt != null) {
            if (ActivityCompat.checkSelfPermission(getApplication(), Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
                bluetoothGatt?.disconnect()
                bluetoothGatt?.close()
            }
            bluetoothGatt = null
        }
        usbSerialPort?.close()
        usbSerialPort = null
    }"""

content = content.replace(old_connect_wifi, new_connect_wifi)

# Replace disconnect method to turn off auto-reconnect
old_disconnect = """    fun disconnect() {
        webSocket?.cancel()
        webSocket = null
        if (bluetoothGatt != null) {
            if (ActivityCompat.checkSelfPermission(getApplication(), Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
                bluetoothGatt?.disconnect()
                bluetoothGatt?.close()
            }
            bluetoothGatt = null
        }
        usbSerialPort?.close()
        usbSerialPort = null
        _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
        addLog(LogType.INFO, "ချိတ်ဆက်မှု ဖြတ်တောက်လိုက်ပါပြီ")
    }"""

new_disconnect = """    fun disconnect() {
        isAutoReconnectEnabled = false
        wifiReconnectJob?.cancel()
        disconnectInternal()
        _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
        addLog(LogType.INFO, "ချိတ်ဆက်မှု ဖြတ်တောက်လိုက်ပါပြီ")
    }"""

content = content.replace(old_disconnect, new_disconnect)

# Replace handleIncomingMessage to parse live_probe without spamming logs
old_handle = """    private fun handleIncomingMessage(text: String) {
        addLog(LogType.RES, text)
        try {
            val json = JSONObject(text)
            val type = json.optString("type")
            if (type == "diode") {
                _uiState.update { it.copy(diodeValue = json.optString("value", "--")) }
            } else if (type == "i2c") {
                val devicesArray = json.optJSONArray("devices")
                val devices = mutableListOf<String>()
                if (devicesArray != null) {
                    for (i in 0 until devicesArray.length()) {
                        devices.add(devicesArray.getString(i))
                    }
                }
                _uiState.update { it.copy(i2cDevices = devices) }
            }
        } catch (e: Exception) {
            Log.e("DiagnosticViewModel", "JSON Parse Error", e)
        }
    }"""

new_handle = """    private fun handleIncomingMessage(text: String) {
        try {
            val json = JSONObject(text)
            val type = json.optString("type")
            
            // Only log non-live messages to prevent log spam & UI lag
            if (type != "live_probe") {
                addLog(LogType.RES, text)
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
            addLog(LogType.RES, text)
        }
    }"""

content = content.replace(old_handle, new_handle)

# Fix imports in case of missing PackageManager / ActivityCompat for disconnectInternal
if "android.content.pm.PackageManager" not in content:
    content = "import android.content.pm.PackageManager\n" + content
if "androidx.core.app.ActivityCompat" not in content:
    content = "import androidx.core.app.ActivityCompat\n" + content
if "android.Manifest" not in content:
    content = "import android.Manifest\n" + content

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)

