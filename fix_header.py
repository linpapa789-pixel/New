with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

content = content.replace('.background(theme.primaryContainer, CircleShape)', '.background(theme.primaryContainer, RoundedCornerShape(theme.cornerRadius))')
content = content.replace('Text("ESP32 စစ်ဆေးခြင်း", fontSize = 18.sp', 'Text(if (theme.isRobot) "[ ESP32_DIAGNOSTICS_SYS_V2.0 ]" else "ESP32 စစ်ဆေးခြင်း", fontSize = if (theme.isRobot) 12.sp else 18.sp')

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)

