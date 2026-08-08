import re

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'r') as f:
    content = f.read()

# Add HardwareMode enum
content = content.replace('enum class LogType { INFO, CMD, RES }', 'enum class LogType { INFO, CMD, RES }\nenum class HardwareMode { DIODE, UART, I2C }')

# Add hardwareMode to state
content = content.replace('val connectionState: ConnectionState = ConnectionState.DISCONNECTED,', 'val connectionState: ConnectionState = ConnectionState.DISCONNECTED,\n    val hardwareMode: HardwareMode = HardwareMode.DIODE,')

# Add method to set mode
set_mode_func = """    fun setHardwareMode(mode: HardwareMode) {
        _uiState.update { it.copy(hardwareMode = mode) }
        val modeStr = when (mode) {
            HardwareMode.DIODE -> "diode"
            HardwareMode.UART -> "uart"
            HardwareMode.I2C -> "i2c_scanner"
        }
        sendMessage("{\\"command\\": \\"set_mode\\", \\"mode\\": \\"$modeStr\\"}")
    }"""

if "fun setHardwareMode" not in content:
    content = content.replace('fun setActiveTab(index: Int) {', set_mode_func + '\n\n    fun setActiveTab(index: Int) {')

with open('app/src/main/java/com/example/DiagnosticViewModel.kt', 'w') as f:
    f.write(content)

