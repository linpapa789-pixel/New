import re

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

idx = content.find("fun ConfigView")
if idx != -1:
    content = content[:idx] + """fun ConfigView(viewModel: DiagnosticViewModel, uiState: DiagnosticUiState) {
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
                    "Tools tab ရှိ 'Connection Mode' တွင် Wi-Fi သို့မဟုတ် Bluetooth ရွေးချယ်၍ ESP32 နှင့် ချိတ်ဆက်ပါ။ Wi-Fi ဖြင့် ချိတ်ဆက်ရန်အတွက် ESP32 မှ ထုတ်လွှင့်သော (ဥပမာ - 'ESP_Diag_Tool') Hotspot ကို ချိတ်ဆက်ပြီး IP နှင့် Port (Default: 192.168.4.1:80) အတိုင်းထား၍ ချိတ်ဆက်နိုင်ပါသည်။",
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
                    "• Diode Mode: ဖုန်းဘုတ်များရှိ လမ်းကြောင်းများကို တိုင်းတာရန်အတွက် ဖြစ်သည်။ Zero-Lag Live Probe ဖြင့် တိုက်ရိုက်တိုင်းတာနိုင်ပြီး၊ 'Read' ကိုနှိပ်၍ Reference Value နှင့် နှိုင်းယှဉ်စစ်ဆေးနိုင်ပါသည်။\\n• UART Mode: Boot Logs များကို တိုက်ရိုက်ဖတ်ရှုရန် ဖြစ်သည်။ 'Start' ကိုနှိပ်၍ Log များကို ဖတ်ရှုနိုင်ပြီး ဖတ်ရှုပြီးပါက 'Stop' ကိုပြန်နှိပ်ပေးပါ။\\n• I2C Mode: I2C လမ်းကြောင်းများ၏ အလုပ်လုပ်ပုံနှင့် ချိတ်ဆက်ထားသော IC များ (ဥပမာ 0x3C) ကို Scan ဖတ်ရှုနိုင်ပါသည်။ Probe 1 ကို SDA အဖြစ်နှင့် Probe 2 ကို SCL အဖြစ် အသုံးပြုပါ။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "၃။ မှတ်တမ်းများ (Logs) နှင့် OTG Flash",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "• Status Tab တွင် App ၏ လုပ်ဆောင်ချက် မှတ်တမ်းများနှင့် UART မှတ်တမ်းများကို သီးခြားစီ ဖတ်ရှုနိုင်ပါသည်။ လိုအပ်ပါက .txt ဖိုင်အနေဖြင့် Export ထုတ်ယူနိုင်ပါသည်။\\n• Flash Tab တွင် ဖုန်းနှင့် ESP32 ကို OTG (USB) ဖြင့် ချိတ်ဆက်ပြီး Firmware (.bin) ဖိုင်ကို တိုက်ရိုက်တင်နိုင်ပါသည်။",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
            }
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("ဆောင်ရန် နှင့် ရှောင်ရန်များ (Do's and Don'ts)", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.error, fontSize = 18.sp)
                Spacer(Modifier.height(12.dp))
                
                Text(
                    "ဆောင်ရန် (Do's)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
                Text(
                    "• တိုင်းတာမှုများ မပြုလုပ်မီ ESP32 နှင့် App ချိတ်ဆက်မှု (Connected) ဖြစ်/မဖြစ် အရင်သေချာစစ်ဆေးပါ။\\n• I2C Scan ပြုလုပ်ရာတွင် Probe 1 (SDA) နှင့် Probe 2 (SCL) ကို မှန်ကန်စွာ ချိတ်ဆက်ပါ။\\n• UART ဖတ်ရှုပြီးပါက အခြား Mode သို့ မပြောင်းမီ 'Stop' ကို အမြဲတမ်း နှိပ်ပေးပါ။\\n• OTG Flash ပြုလုပ်ရာတွင် ဖုန်းဘက်မှ USB OTG ခွင့်ပြုချက် (Permission) တောင်းခံလာပါက Allow လုပ်ပေးပါ။",
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Text(
                    "ရှောင်ရန် (Don'ts)",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
                Text(
                    "• Voltage များသော နေရာများကို တိုက်ရိုက်တိုင်းတာခြင်း (3.3V အထက်) ကို လုံးဝ ရှောင်ကြဉ်ပါ။ ESP32 ပျက်စီးနိုင်ပါသည်။\\n• Firmware (OTG Flash) တင်နေစဉ်အတွင်း USB ကြိုးကို ဖြုတ်လိုက်ခြင်း လုံးဝ မပြုလုပ်ပါနှင့်။\\n• UART Mode 'Start' လုပ်ထားစဉ် Diode သို့မဟုတ် I2C Mode သို့ ချက်ချင်း ပြောင်းလဲအသုံးပြုခြင်းမျိုး မပြုလုပ်ပါနှင့်။ 'Stop' အရင်နှိပ်ပါ။",
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    fontSize = 14.sp
                )
            }
        }
    }
}
"""

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)

