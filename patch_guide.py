import re

def patch_screen():
    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "r") as f:
        content = f.read()

    # Update Tabs
    old_tabs = """                val tabs = listOf(
                    Triple("Tools", Icons.Outlined.Build, Icons.Filled.Build),
                    Triple("Smart", Icons.Outlined.Info, Icons.Filled.Info),
                    Triple("Clock", Icons.Outlined.Refresh, Icons.Filled.Refresh),
                    Triple("Flash", Icons.Outlined.CheckCircle, Icons.Filled.CheckCircle),
                    Triple("Status", Icons.Outlined.Info, Icons.Filled.Info),
                    Triple("Settings", Icons.Outlined.Settings, Icons.Filled.Settings)
                )"""

    new_tabs = """                val tabs = listOf(
                    Triple("Tools", Icons.Outlined.Build, Icons.Filled.Build),
                    Triple("Smart", Icons.Outlined.CheckCircle, Icons.Filled.CheckCircle),
                    Triple("Guide", Icons.Outlined.Info, Icons.Filled.Info),
                    Triple("Clock", Icons.Outlined.Refresh, Icons.Filled.Refresh),
                    Triple("Flash", Icons.Outlined.Warning, Icons.Filled.Warning),
                    Triple("Status", Icons.Outlined.Info, Icons.Filled.Info),
                    Triple("Settings", Icons.Outlined.Settings, Icons.Filled.Settings)
                )"""

    if old_tabs in content:
        content = content.replace(old_tabs, new_tabs)
    else:
        print("Could not find old_tabs")
        return

    # Update View logic
    old_when = """            when (tab) {
                0 -> ToolsView(viewModel, uiState)
                1 -> SmartRecordView(viewModel, uiState)
                2 -> ClockCheckView(viewModel, uiState)
                3 -> OtgFlashView(viewModel, uiState)
                4 -> StatusLogsView(viewModel, uiState)
                5 -> ConfigView(viewModel, uiState)
            }"""
            
    new_when = """            when (tab) {
                0 -> ToolsView(viewModel, uiState)
                1 -> SmartRecordView(viewModel, uiState)
                2 -> GuideView()
                3 -> ClockCheckView(viewModel, uiState)
                4 -> OtgFlashView(viewModel, uiState)
                5 -> StatusLogsView(viewModel, uiState)
                6 -> ConfigView(viewModel, uiState)
            }"""

    if old_when in content:
        content = content.replace(old_when, new_when)
    else:
        print("Could not find old_when")
        return
        
    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "w") as f:
        f.write(content)

patch_screen()
