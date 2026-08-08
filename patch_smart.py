import re
import sys

def patch_view_model():
    with open("app/src/main/java/com/example/DiagnosticViewModel.kt", "r") as f:
        content = f.read()

    if "enum class PinStatus" not in content:
        insert_idx = content.find("enum class HardwareMode")
        if insert_idx == -1:
            return False
            
        enums = """enum class PinStatus { PENDING, PASS, FAIL, SHORT }
enum class SmartRecordMode { MANUAL, AUTO }

data class PinRecord(
    val pinNumber: Int,
    val name: String = "Pin",
    val referenceValue: Float = 0.400f,
    val measuredValue: Float? = null,
    val status: PinStatus = PinStatus.PENDING
)

"""
        content = content[:insert_idx] + enums + content[insert_idx:]

    if "val smartRecordMode:" not in content:
        insert_idx = content.find("val isDarkTheme: Boolean = true")
        if insert_idx != -1:
            state_additions = """,
    val smartRecordMode: SmartRecordMode = SmartRecordMode.MANUAL,
    val currentPinIndex: Int = 0,
    val pinRecords: List<PinRecord> = (1..10).map { PinRecord(pinNumber = it, name = "LCD_PIN_$it", referenceValue = 0.450f) },
    val isRecordingStarted: Boolean = false,
    val lastStableDiodeValue: Float? = null"""
            content = content[:insert_idx + len("val isDarkTheme: Boolean = true")] + state_additions + content[insert_idx + len("val isDarkTheme: Boolean = true"):]

    with open("app/src/main/java/com/example/DiagnosticViewModel.kt", "w") as f:
        f.write(content)

    return True

patch_view_model()
