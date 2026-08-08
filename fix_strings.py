with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

bad_string = '''"• Diode: ဖုန်းဘုတ်များရှိ Short (သို့) Open လမ်းကြောင်းများကို တိုင်းတာရန်အတွက် ဖြစ်သည်။\\n" +
                    "• UART: Boot Logs များကို တိုက်ရိုက်ဖတ်ရှုရန်အတွက် ဖြစ်သည်။ Start/Stop ဖြင့် ထိန်းချုပ်နိုင်ပါသည်။\\n" +
                    "• I2C: I2C လမ်းကြောင်းများ၏ အလုပ်လုပ်ပုံနှင့် ချိတ်ဆက်ထားသော IC များကို (0x3C စသည်ဖြင့်) ရှာဖွေပေးမည် ဖြစ်သည်။"'''

good_string = '"""• Diode: ဖုန်းဘုတ်များရှိ Short (သို့) Open လမ်းကြောင်းများကို တိုင်းတာရန်အတွက် ဖြစ်သည်။\n• UART: Boot Logs များကို တိုက်ရိုက်ဖတ်ရှုရန်အတွက် ဖြစ်သည်။ Start/Stop ဖြင့် ထိန်းချုပ်နိုင်ပါသည်။\n• I2C: I2C လမ်းကြောင်းများ၏ အလုပ်လုပ်ပုံနှင့် ချိတ်ဆက်ထားသော IC များကို (0x3C စသည်ဖြင့်) ရှာဖွေပေးမည် ဖြစ်သည်။"""'

content = content.replace(bad_string, good_string)

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
