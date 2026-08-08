import re

def patch_vm():
    with open("app/src/main/java/com/example/DiagnosticViewModel.kt", "r") as f:
        content = f.read()

    # Find updateLiveDiode
    old_method = """    fun updateLiveDiode(value: String) {
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
    }"""
    
    new_method = """
    private var isProbeArmed = true
    private var consecutiveValidReadings = 0
    private var lastValidValue = 0f

    fun updateLiveDiode(value: String) {
        _uiState.update { it.copy(liveProbeValue = value) }
        val floatVal = value.toFloatOrNull()
        val isOL = value == "OL" || (floatVal != null && floatVal > 2.5f)
        
        if (isOL) {
            isProbeArmed = true // Probe lifted, re-arm for next pin
            consecutiveValidReadings = 0
        }
        
        val state = _uiState.value
        if (state.isRecordingStarted && state.smartRecordMode == SmartRecordMode.AUTO && floatVal != null && !isOL) {
            if (isProbeArmed) {
                if (Math.abs(floatVal - lastValidValue) < 0.02f) {
                    consecutiveValidReadings++
                } else {
                    consecutiveValidReadings = 1
                    lastValidValue = floatVal
                }
                
                // Wait for 3 consecutive stable readings
                if (consecutiveValidReadings >= 3) {
                    recordCurrentPin(lastValidValue)
                    isProbeArmed = false // Wait for OL to re-arm
                    consecutiveValidReadings = 0
                }
            }
        }
    }
"""
    if old_method in content:
        content = content.replace(old_method, new_method)
        with open("app/src/main/java/com/example/DiagnosticViewModel.kt", "w") as f:
            f.write(content)
        return True
    return False

patch_vm()
