package com.example

import android.Manifest
import android.annotation.SuppressLint
import android.app.Application
import android.app.PendingIntent
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbDeviceConnection
import android.hardware.usb.UsbManager
import android.media.AudioManager
import android.media.ToneGenerator
import android.net.Uri
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.hoho.android.usbserial.driver.UsbSerialPort
import com.hoho.android.usbserial.driver.UsbSerialProber
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import okhttp3.*
import org.json.JSONObject
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.TimeUnit

enum class ConnectionMode { NONE, WIFI, BLE }
enum class ConnectionState { DISCONNECTED, CONNECTING, CONNECTED }
enum class LogType { INFO, CMD, RES }
enum class HardwareMode { DIODE, UART, I2C }
data class LogMessage(val time: String, val type: LogType, val message: String)

data class DiagnosticUiState(
    val connectionMode: ConnectionMode = ConnectionMode.NONE,
    val connectionState: ConnectionState = ConnectionState.DISCONNECTED,
    val hardwareMode: HardwareMode = HardwareMode.DIODE,
    val wifiIp: String = "192.168.4.1",
    val wifiPort: String = "80",
    val diodeValue: String = "--",
    val liveProbeValue: String = "0.00",
    val probeHistory: List<Float> = emptyList(),
    val diodeReferenceValue: Float = 0.450f,
    val i2cDevices: List<String> = emptyList(),
    val appLogs: List<LogMessage> = emptyList(),
    val uartLogs: List<LogMessage> = emptyList(),
    val isUartPaused: Boolean = false,
    val uartBaudRate: Int = 115200,

    // OTG Features
    val activeTab: Int = 0, // 0 = Tools, 1 = Flash, 2 = Status, 3 = Config
    val usbDeviceName: String = "စက်မတွေ့ရှိပါ",
    val firmwareFileName: String = ".bin ဖိုင်ကို ရွေးချယ်ပါ",
    val flashProgress: Float = 0f,
    val isFlashing: Boolean = false,
    val isDarkTheme: Boolean = true
)

class DiagnosticViewModel(application: Application) : AndroidViewModel(application) {
    private val _uiState = MutableStateFlow(DiagnosticUiState())
    val uiState: StateFlow<DiagnosticUiState> = _uiState.asStateFlow()

    private val client = OkHttpClient.Builder()
        .pingInterval(3, TimeUnit.SECONDS)
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.SECONDS)
        .build()

    private var wifiReconnectJob: Job? = null
    private var isAutoReconnectEnabled = false
    private var webSocket: WebSocket? = null

    private var bluetoothAdapter: BluetoothAdapter? = null
    private var bluetoothGatt: BluetoothGatt? = null
    private var writeCharacteristic: BluetoothGattCharacteristic? = null
    private var bleScanner: android.bluetooth.le.BluetoothLeScanner? = null
    private var bleScanCallback: ScanCallback? = null

    private val timeFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
    private val usbManager = application.getSystemService(Context.USB_SERVICE) as UsbManager

    // --- Audio Continuity Beep for Short-Circuit Detection ---
    private var toneGenerator: ToneGenerator? = null
    private var beepJob: Job? = null
    @Volatile
    private var isBeeping = false

    // --- UART Log Buffer for Pause State ---
    private val bufferedUartLogs = Collections.synchronizedList(mutableListOf<LogMessage>())

    init {
        try {
            toneGenerator = ToneGenerator(AudioManager.STREAM_MUSIC, 80)
        } catch (e: Exception) {
            Log.e("DiagnosticViewModel", "Failed to initialize ToneGenerator", e)
        }
        addAppLog(LogType.INFO, "ESP32 Diagnostic Kernel v1.0.5")
    }

    private fun currentTime(): String = timeFormat.format(Date())

    private fun addAppLog(type: LogType, message: String) {
        _uiState.update { state ->
            val newLogs = (state.appLogs + LogMessage(currentTime(), type, message)).takeLast(1000)
            state.copy(appLogs = newLogs)
        }
    }

    private fun addUartLog(message: String) {
        val newLog = LogMessage(currentTime(), LogType.RES, message)
        if (_uiState.value.isUartPaused) {
            bufferedUartLogs.add(newLog)
            if (bufferedUartLogs.size > 1000) {
                bufferedUartLogs.removeAt(0)
            }
        } else {
            _uiState.update { state ->
                val newLogs = (state.uartLogs + newLog).takeLast(1000)
                state.copy(uartLogs = newLogs)
            }
        }
    }

    fun toggleUartPause() {
        _uiState.update { state ->
            val nextPausedState = !state.isUartPaused
            if (!nextPausedState) {
                // Unpaused: Flush buffered logs into UI state
                val flushedLogs: List<LogMessage>
                synchronized(bufferedUartLogs) {
                    flushedLogs = ArrayList(bufferedUartLogs)
                    bufferedUartLogs.clear()
                }
                val combinedLogs = (state.uartLogs + flushedLogs).takeLast(1000)
                state.copy(isUartPaused = false, uartLogs = combinedLogs)
            } else {
                state.copy(isUartPaused = true)
            }
        }
    }

    fun clearLogs() {
        bufferedUartLogs.clear()
        _uiState.update { state ->
            state.copy(appLogs = emptyList(), uartLogs = emptyList())
        }
        addAppLog(LogType.INFO, "မှတ်တမ်းများကို ရှင်းလင်းလိုက်ပါပြီ")
    }

    fun saveLogsToFile(context: Context, uri: Uri) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                context.contentResolver.openOutputStream(uri)?.use { outputStream ->
                    val appLogsText = _uiState.value.appLogs.joinToString("\n") { log ->
                        "[${log.time}] ${log.type}: ${log.message}"
                    }
                    val uartLogsText = _uiState.value.uartLogs.joinToString("\n") { log ->
                        "[${log.time}] ${log.message}"
                    }
                    val logsText = "--- APP LOGS ---\n$appLogsText\n\n--- UART LOGS ---\n$uartLogsText"
                    outputStream.write(logsText.toByteArray())
                }
                withContext(Dispatchers.Main) {
                    addAppLog(LogType.INFO, "မှတ်တမ်းများကို သိမ်းဆည်းပြီးပါပြီ")
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    addAppLog(LogType.INFO, "မှတ်တမ်း သိမ်းဆည်းခြင်း မအောင်မြင်ပါ: ${e.message}")
                }
            }
        }
    }

    fun updateWifiIp(ip: String) {
        _uiState.update { it.copy(wifiIp = ip) }
    }

    fun updateWifiPort(port: String) {
        _uiState.update { it.copy(wifiPort = port) }
    }

    fun connectWifi() {
        isAutoReconnectEnabled = true
        wifiReconnectJob?.cancel()

        disconnectInternal()
        _uiState.update { it.copy(connectionMode = ConnectionMode.WIFI, connectionState = ConnectionState.CONNECTING) }

        val ip = _uiState.value.wifiIp
        val port = _uiState.value.wifiPort
        val url = "ws://$ip:$port/ws"

        try {
            val request = Request.Builder().url(url).build()
            webSocket = client.newWebSocket(request, object : WebSocketListener() {
                override fun onOpen(webSocket: WebSocket, response: Response) {
                    _uiState.update { it.copy(connectionState = ConnectionState.CONNECTED) }
                    addAppLog(LogType.INFO, "$url သို့ ချိတ်ဆက်ပြီးပါပြီ")
                }
                override fun onMessage(webSocket: WebSocket, text: String) {
                    handleIncomingMessage(text)
                }
                override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                    _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                    stopShortCircuitBeep()
                    addAppLog(LogType.INFO, "Wi-Fi ချိတ်ဆက်မှု ပြတ်တောက်သွားပါပြီ")
                    handleReconnect()
                }
                override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                    _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                    stopShortCircuitBeep()
                    addAppLog(LogType.INFO, "Wi-Fi အမှားအယွင်း: ${t.message}")
                    handleReconnect()
                }
            })
        } catch (e: Exception) {
            _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
            addAppLog(LogType.INFO, "URL မှားယွင်းနေပါသည်: ${e.message}")
            isAutoReconnectEnabled = false
        }
    }

    private fun handleReconnect() {
        if (isAutoReconnectEnabled) {
            wifiReconnectJob?.cancel()
            wifiReconnectJob = viewModelScope.launch(Dispatchers.IO) {
                addAppLog(LogType.INFO, "၃ စက္ကန့်အတွင်း ပြန်လည်ချိတ်ဆက်ပါမည်...")
                delay(3000)
                if (isAutoReconnectEnabled) {
                    withContext(Dispatchers.Main) {
                        connectWifi()
                    }
                }
            }
        }
    }

    @SuppressLint("MissingPermission")
    private fun disconnectInternal() {
        stopShortCircuitBeep()
        webSocket?.cancel()
        webSocket = null

        try {
            bleScanCallback?.let { bleScanner?.stopScan(it) }
        } catch (e: Exception) {}

        if (bluetoothGatt != null) {
            try {
                bluetoothGatt?.disconnect()
                bluetoothGatt?.close()
            } catch (e: Exception) {}
            bluetoothGatt = null
        }
    }

    @SuppressLint("MissingPermission")
    fun connectBle() {
        disconnect()
        _uiState.update { it.copy(connectionMode = ConnectionMode.BLE, connectionState = ConnectionState.CONNECTING) }
        val bluetoothManager = getApplication<Application>().getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothAdapter = bluetoothManager.adapter

        if (bluetoothAdapter == null || !bluetoothAdapter!!.isEnabled) {
            addAppLog(LogType.INFO, "ဘလူးတုသ် ပိတ်ထားသည် (သို့) အသုံးပြု၍မရပါ")
            _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
            return
        }

        bleScanner = bluetoothAdapter!!.bluetoothLeScanner
        if (bleScanner == null) {
            addAppLog(LogType.INFO, "BLE စကန်ဖတ်၍မရပါ")
            _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
            return
        }

        addAppLog(LogType.INFO, "Mobile_Tool_ESP32 ကို ရှာဖွေနေသည်...")

        bleScanCallback = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                val name = result.device.name ?: result.scanRecord?.deviceName
                if (name == "Mobile_Tool_ESP32") {
                    try { bleScanCallback?.let { bleScanner?.stopScan(it) } } catch (e: Exception) {}
                    addAppLog(LogType.INFO, "ESP32 ကိုတွေ့ရှိပါသည်၊ ချိတ်ဆက်နေပါသည်...")
                    bluetoothGatt = result.device.connectGatt(getApplication(), false, gattCallback)
                }
            }
            override fun onScanFailed(errorCode: Int) {
                addAppLog(LogType.INFO, "ရှာဖွေမှု မအောင်မြင်ပါ: $errorCode")
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
            }
        }

        try {
            bleScanCallback?.let { bleScanner?.startScan(it) }
        } catch (e: Exception) {
            addAppLog(LogType.INFO, "ရှာဖွေမှု စတင်၍မရပါ")
            _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
        }

        viewModelScope.launch {
            delay(10000)
            if (_uiState.value.connectionState != ConnectionState.CONNECTED && bluetoothGatt == null) {
                try { bleScanCallback?.let { bleScanner?.stopScan(it) } } catch (e: Exception) {}
                addAppLog(LogType.INFO, "ရှာဖွေချိန် ကုန်ဆုံးသွားပါပြီ")
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
            }
        }
    }

    private val gattCallback = object : BluetoothGattCallback() {
        @SuppressLint("MissingPermission")
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                gatt.requestMtu(512)
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                _uiState.update { it.copy(connectionState = ConnectionState.DISCONNECTED) }
                stopShortCircuitBeep()
                addAppLog(LogType.INFO, "BLE ချိတ်ဆက်မှု ပြတ်တောက်သွားပါပြီ")
            }
        }

        @SuppressLint("MissingPermission")
        override fun onMtuChanged(gatt: BluetoothGatt, mtu: Int, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                addAppLog(LogType.INFO, "MTU ညှိနှိုင်းမှု ပြီးစီးပါပြီ ($mtu)")
                gatt.discoverServices()
            }
        }

        @SuppressLint("MissingPermission")
        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt.getService(UUID.fromString("4fafc201-1fb5-459e-8fcc-c5c9c331914b"))
                if (service != null) {
                    writeCharacteristic = service.getCharacteristic(UUID.fromString("beb5483e-36e1-4688-b7f5-ea07361b26a8"))
                    val readChar = service.getCharacteristic(UUID.fromString("beb5483f-36e1-4688-b7f5-ea07361b26a8"))
                    if (readChar != null) {
                        gatt.setCharacteristicNotification(readChar, true)
                        val descriptor = readChar.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))
                        if (descriptor != null) {
                            @Suppress("DEPRECATION")
                            descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                            gatt.writeDescriptor(descriptor)
                        }
                    }
                    _uiState.update { it.copy(connectionState = ConnectionState.CONNECTED) }
                    addAppLog(LogType.INFO, "Mobile_Tool_ESP32 သို့ ချိတ်ဆက်ပြီးပါပြီ")
                } else {
                    addAppLog(LogType.INFO, "BLE ဝန်ဆောင်မှု မတွေ့ရှိပါ")
                }
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
            val value = String(characteristic.value)
            handleIncomingMessage(value)
        }
    }

    private fun handleIncomingMessage(text: String) {
        try {
            val json = JSONObject(text)
            val type = json.optString("type")

            if (type == "uart" || type == "uart_log") {
                addUartLog(json.optString("log", text))
                return
            }

            if (type != "live_probe") {
                addAppLog(LogType.RES, text)
            }

            when (type) {
                "live_probe" -> {
                    val valueStr = json.optString("value", "0.00")
                    val valueFloat = valueStr.toFloatOrNull() ?: 0f
                    
                    // Check for short circuit beep trigger (< 0.05V)
                    checkShortCircuitBeep(valueFloat)

                    _uiState.update { state ->
                        val newHistory = (state.probeHistory + valueFloat).takeLast(50)
                        state.copy(liveProbeValue = valueStr, probeHistory = newHistory)
                    }
                }
                "diode" -> {
                    val valueStr = json.optString("value", "--")
                    val valueFloat = valueStr.toFloatOrNull()
                    if (valueFloat != null) {
                        checkShortCircuitBeep(valueFloat)
                    }
                    _uiState.update { it.copy(diodeValue = valueStr) }
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
            // Raw text log
            addUartLog(text)
        }
    }

    // Trigger audio beep when diode/live_probe voltage drops below 0.05V (SHORT circuit)
    private fun checkShortCircuitBeep(voltage: Float) {
        if (_uiState.value.hardwareMode == HardwareMode.DIODE && voltage in 0.0001f..0.0499f) {
            if (!isBeeping) {
                isBeeping = true
                beepJob?.cancel()
                beepJob = viewModelScope.launch(Dispatchers.Default) {
                    while (isBeeping && _uiState.value.hardwareMode == HardwareMode.DIODE) {
                        toneGenerator?.startTone(ToneGenerator.TONE_PROP_BEEP, 100)
                        delay(150)
                    }
                }
            }
        } else {
            stopShortCircuitBeep()
        }
    }

    private fun stopShortCircuitBeep() {
        isBeeping = false
        beepJob?.cancel()
        beepJob = null
    }

    @SuppressLint("MissingPermission")
    fun sendMessage(cmd: String) {
        val state = _uiState.value
        if (state.connectionState != ConnectionState.CONNECTED) {
            addAppLog(LogType.INFO, "ချိတ်ဆက်မထားပါ။ ကွန်မန်း ပို့၍မရပါ။")
            return
        }

        addAppLog(LogType.CMD, cmd)
        if (state.connectionMode == ConnectionMode.WIFI) {
            webSocket?.send(cmd)
        } else if (state.connectionMode == ConnectionMode.BLE) {
            writeCharacteristic?.let {
                @Suppress("DEPRECATION")
                it.value = cmd.toByteArray()
                bluetoothGatt?.writeCharacteristic(it)
            }
        }
    }

    fun sendDiode() = sendMessage("{\"cmd\": \"diode\"}")
    fun sendI2c() = sendMessage("{\"cmd\": \"i2c\"}")

    fun setUartBaudRate(baud: Int) {
        _uiState.update { it.copy(uartBaudRate = baud) }
    }

    fun setDiodeReferenceValue(ref: Float) {
        _uiState.update { it.copy(diodeReferenceValue = ref) }
    }

    fun sendUartStart() = sendMessage("{\"cmd\": \"uart_start\", \"baud\": ${_uiState.value.uartBaudRate}}")
    fun sendUartStop() = sendMessage("{\"cmd\": \"uart_stop\"}")

    fun setHardwareMode(mode: HardwareMode) {
        stopShortCircuitBeep()
        _uiState.update { it.copy(hardwareMode = mode) }
        val modeStr = when (mode) {
            HardwareMode.DIODE -> "diode"
            HardwareMode.UART -> "uart"
            HardwareMode.I2C -> "i2c_scanner"
        }
        sendMessage("{\"command\": \"set_mode\", \"mode\": \"$modeStr\"}")
    }

    fun setActiveTab(index: Int) {
        _uiState.update { it.copy(activeTab = index) }
    }

    fun toggleTheme() {
        _uiState.update { it.copy(isDarkTheme = !it.isDarkTheme) }
    }

    fun detectUsbDevice() {
        val deviceList = usbManager.deviceList
        if (deviceList.isNotEmpty()) {
            val device = deviceList.values.first()
            val name = device.productName ?: "ESP32-S3 (ID: ${device.deviceId})"
            _uiState.update { it.copy(usbDeviceName = name) }
            addAppLog(LogType.INFO, "USB စက်တွေ့ရှိပါသည်: $name")

            if (!usbManager.hasPermission(device)) {
                addAppLog(LogType.INFO, "USB ခွင့်ပြုချက် တောင်းခံနေပါသည်...")
                val intent = Intent("com.example.USB_PERMISSION")
                val pendingIntent = PendingIntent.getBroadcast(
                    getApplication(),
                    0,
                    intent,
                    PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
                )
                usbManager.requestPermission(device, pendingIntent)
            }
        } else {
            _uiState.update { it.copy(usbDeviceName = "စက်မတွေ့ရှိပါ") }
            addAppLog(LogType.INFO, "မည်သည့် USB စက်မှ မတွေ့ရှိပါ။")
        }
    }

    fun setFirmwareFile(name: String) {
        _uiState.update { it.copy(firmwareFileName = name) }
    }

    fun startFlashing() {
        if (_uiState.value.firmwareFileName == ".bin ဖိုင်ကို ရွေးချယ်ပါ") {
            addAppLog(LogType.INFO, "ကျေးဇူးပြု၍ ဖန်းဝဲဖိုင်ကို အရင်ရွေးချယ်ပါ။")
            return
        }
        if (_uiState.value.usbDeviceName == "စက်မတွေ့ရှိပါ") {
            addAppLog(LogType.INFO, "ကျေးဇူးပြု၍ USB စက်ကို အရင်ရှာဖွေ/ချိတ်ဆက်ပါ။")
            return
        }

        _uiState.update { it.copy(isFlashing = true, flashProgress = 0f) }
        addAppLog(LogType.INFO, "ESP32-S3 OTG ချိတ်ဆက်မှုကို စမ်းသပ်နေပါသည်...")

        viewModelScope.launch(Dispatchers.IO) {
            try {
                val availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(usbManager)
                if (availableDrivers.isEmpty()) {
                    withContext(Dispatchers.Main) {
                        addAppLog(LogType.INFO, "ပံ့ပိုးပေးထားသော USB Serial ဒရိုက်ဘာ မတွေ့ပါ။")
                        _uiState.update { it.copy(isFlashing = false) }
                    }
                    return@launch
                }

                val driver = availableDrivers[0]
                val connection = usbManager.openDevice(driver.device)
                if (connection == null) {
                    withContext(Dispatchers.Main) {
                        addAppLog(LogType.INFO, "USB ခွင့်ပြုချက် မရှိပါ။ \"USB စက်ကို ရှာဖွေရန်\" ကို ထပ်နှိပ်ပြီး ခွင့်ပြုချက်ပေးပါ။")
                        _uiState.update { it.copy(isFlashing = false) }
                    }
                    return@launch
                }

                val port = driver.ports[0]
                port.open(connection)
                port.setParameters(115200, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE)

                withContext(Dispatchers.Main) {
                    addAppLog(LogType.INFO, "USB ချိတ်ဆက်မှု အောင်မြင်ပါသည်။")
                    addAppLog(LogType.INFO, "ESP32 ကို Bootloader Mode သို့ ပြောင်းနေပါသည် (RTS/DTR)...")
                }

                port.dtr = false
                port.rts = true
                Thread.sleep(100)
                port.dtr = true
                port.rts = false
                Thread.sleep(100)
                port.dtr = false
                port.rts = false

                withContext(Dispatchers.Main) {
                    addAppLog(LogType.INFO, "Bootloader သို့ ဝင်ရောက်သွားပါပြီ။")
                    addAppLog(LogType.INFO, "မှတ်ချက် - အပြည့်အစုံ ဖန်းဝဲတင်ရန်အတွက် esptool protocol အပြည့်အစုံရေးသားရန် လိုအပ်ပါသည်။")

                    port.close()
                    _uiState.update { it.copy(isFlashing = false, flashProgress = 1.0f) }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    addAppLog(LogType.INFO, "OTG အမှားအယွင်း: ${e.message}")
                    _uiState.update { it.copy(isFlashing = false) }
                }
            }
        }
    }

    @SuppressLint("MissingPermission")
    fun disconnect() {
        isAutoReconnectEnabled = false
        wifiReconnectJob?.cancel()
        disconnectInternal()
        _uiState.update { it.copy(connectionMode = ConnectionMode.NONE, connectionState = ConnectionState.DISCONNECTED) }
        addAppLog(LogType.INFO, "ချိတ်ဆက်မှု ဖြတ်တောက်လိုက်ပါပြီ")
    }

    @SuppressLint("MissingPermission")
    override fun onCleared() {
        super.onCleared()
        stopShortCircuitBeep()
        try {
            toneGenerator?.release()
            toneGenerator = null
        } catch (e: Exception) {}
        disconnect()
        try {
            bleScanCallback?.let { bleScanner?.stopScan(it) }
        } catch (e: Exception) {}
        client.dispatcher.executorService.shutdown()
        client.connectionPool.evictAll()
        client.cache?.close()
    }
}
