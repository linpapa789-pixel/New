import re

def patch():
    # Fix GuideView
    with open("app/src/main/java/com/example/GuideView.kt", "r") as f:
        content = f.read()
    
    if "import androidx.compose.foundation.BorderStroke" not in content:
        content = content.replace("import androidx.compose.foundation.layout.*", "import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.BorderStroke")
        
    with open("app/src/main/java/com/example/GuideView.kt", "w") as f:
        f.write(content)
        
    # Fix DiagnosticScreen
    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "r") as f:
        content = f.read()
        
    content = content.replace("Icons.Outlined.Warning", "Icons.Outlined.PlayArrow")
    content = content.replace("Icons.Filled.Warning", "Icons.Filled.PlayArrow")
    
    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "w") as f:
        f.write(content)

patch()
