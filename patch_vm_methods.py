import re

def patch_methods():
    with open("app/src/main/java/com/example/DiagnosticViewModel.kt", "r") as f:
        content = f.read()

    methods = """
    fun setSmartRecordMode(mode: SmartRecordMode) {
        _uiState.update { it.copy(smartRecordMode = mode) }
    }
    
    fun toggleSmartRecording() {
        _uiState.update { 
            if (it.isRecordingStarted) {
                it.copy(isRecordingStarted = false)
            } else {
                // reset if starting fresh
                it.copy(
                    isRecordingStarted = true, 
                    currentPinIndex = 0,
                    pinRecords = it.pinRecords.map { p -> p.copy(measuredValue = null, status = PinStatus.PENDING) }
                )
            }
        }
    }
    
    fun recordCurrentPin(measured: Float) {
        val state = _uiState.value
        if (!state.isRecordingStarted || state.currentPinIndex >= state.pinRecords.size) return
        
        val record = state.pinRecords[state.currentPinIndex]
        val diff = Math.abs(record.referenceValue - measured)
        val status = when {
            measured < 0.05f -> PinStatus.SHORT
            diff <= 0.05f -> PinStatus.PASS
            else -> PinStatus.FAIL
        }
        
        val newList = state.pinRecords.toMutableList()
        newList[state.currentPinIndex] = record.copy(measuredValue = measured, status = status)
        
        _uiState.update { 
            it.copy(
                pinRecords = newList,
                currentPinIndex = if (it.currentPinIndex < it.pinRecords.size - 1) it.currentPinIndex + 1 else it.currentPinIndex,
                isRecordingStarted = it.currentPinIndex < it.pinRecords.size - 1
            )
        }
    }
    
    fun updateLiveDiode(value: String) {
        _uiState.update { it.copy(liveProbeValue = value) }
        val floatVal = value.toFloatOrNull() ?: return
        
        val state = _uiState.value
        if (state.isRecordingStarted && state.smartRecordMode == SmartRecordMode.AUTO) {
             // Basic Auto save logic: if stable for a moment (simulated here by just checking if it's > 0.1 and not floating)
             // In a real app we'd want debouncing, but for now let's just trigger if we see a valid reading drop from OL
             if (floatVal > 0.05f && floatVal < 2.5f) {
                 recordCurrentPin(floatVal)
             }
        }
    }
"""

    if "fun setSmartRecordMode" not in content:
        insert_idx = content.find("fun setHardwareMode")
        if insert_idx != -1:
            content = content[:insert_idx] + methods + "\n" + content[insert_idx:]
            with open("app/src/main/java/com/example/DiagnosticViewModel.kt", "w") as f:
                f.write(content)

patch_methods()
