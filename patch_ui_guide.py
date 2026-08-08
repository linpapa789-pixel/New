with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

old_config = """fun ConfigView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Appearance", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.height(16.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Dark Theme (Light/Dark)")
                    Switch(
                        checked = uiState.isDarkTheme,
                        onCheckedChange = { viewModel.toggleTheme() }
                    )
                }
            }
        }
    }
}"""

new_config = """fun ConfigView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
    val scrollState = rememberScrollState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Appearance", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.height(16.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Dark Theme (Light/Dark)")
                    Switch(
                        checked = uiState.isDarkTheme,
                        onCheckedChange = { viewModel.toggleTheme() }
                    )
                }
            }
        }
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("ESP32 Diagnostic App - အသုံးပြုပုံလမ်းညွှန်", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 18.sp)
                Spacer(Modifier.height(12.dp))
                
                Text(
                    "၁။ ချိတ်ဆက်ခြင်း (Connection)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "Tools tab အောက်ခြေရှိ 'Connection Mode' တွင် Wi-Fi သို့မဟုတ် Bluetooth ရွေးချယ်၍ ESP32 နှင့် ချိတ်ဆက်ပါ။ Wi-Fi အတွက် IP နှင့် Port ကို မှန်ကန်စွာ ထည့်သွင်းပေးရန် လိုအပ်ပါသည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "၂။ Hardware Modes (2 Probes စနစ်)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "• Diode: ဖုန်းဘုတ်များရှိ Short (သို့) Open လမ်းကြောင်းများကို တိုင်းတာရန်အတွက် ဖြစ်သည်။\n" +
                    "• UART: Boot Logs များကို တိုက်ရိုက်ဖတ်ရှုရန်အတွက် ဖြစ်သည်။ Start/Stop ဖြင့် ထိန်းချုပ်နိုင်ပါသည်။\n" +
                    "• I2C: I2C လမ်းကြောင်းများ၏ အလုပ်လုပ်ပုံနှင့် ချိတ်ဆက်ထားသော IC များကို (0x3C စသည်ဖြင့်) ရှာဖွေပေးမည် ဖြစ်သည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "၃။ မှတ်တမ်းများ (Logs)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "Status tab တွင် App မှတ်တမ်းများနှင့် UART မှတ်တမ်းများကို သီးခြားစီ ဖတ်ရှုနိုင်ပါသည်။ လိုအပ်ပါက .txt ဖိုင်အနေဖြင့် Export ထုတ်ယူနိုင်ပါသည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "၄။ Firmware တင်ခြင်း (OTG Flash)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "Flash tab သို့သွား၍ ဖုန်းနှင့် ESP32 ကို OTG (USB) ဖြင့် ချိတ်ဆက်ပါ။ 'USB စက်ကို ရှာဖွေရန်' ကို နှိပ်ပြီး .bin ဖိုင်ရွေးချယ်ကာ Firmware တိုက်ရိုက်တင်နိုင်ပါသည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp
                )
            }
        }
    }
}"""

content = content.replace(old_config, new_config)

if "import androidx.compose.foundation.rememberScrollState" not in content:
    content = content.replace("import androidx.compose.foundation.layout.*", "import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.rememberScrollState\nimport androidx.compose.foundation.verticalScroll")

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
