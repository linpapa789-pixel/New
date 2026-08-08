with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

content = content.replace('fun NavItem(icon: String, label: String, selected: Boolean, onClick: () -> Unit)', 'fun NavItem(icon: String, label: String, selected: Boolean, theme: AppTheme, onClick: () -> Unit)')
content = content.replace('NavItem("🛠️", "ကိရိယာများ", uiState.activeTab == 0)', 'NavItem("🛠️", "ကိရိယာများ", uiState.activeTab == 0, theme)')
content = content.replace('NavItem("💾", "ဖန်းဝဲတင်ရန်", uiState.activeTab == 1)', 'NavItem("💾", "ဖန်းဝဲတင်ရန်", uiState.activeTab == 1, theme)')
content = content.replace('NavItem("📡", "အခြေအနေ", uiState.activeTab == 2)', 'NavItem("📡", "အခြေအနေ", uiState.activeTab == 2, theme)')
content = content.replace('NavItem("⚙️", "ဆက်တင်များ", uiState.activeTab == 3)', 'NavItem("⚙️", "ဆက်တင်များ", uiState.activeTab == 3, theme)')

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
