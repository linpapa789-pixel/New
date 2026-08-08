import re
import sys

def patch_ui():
    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "r") as f:
        content = f.read()

    # Add Smart Tab in BottomBar
    if 'Triple("Smart"' not in content:
        content = content.replace(
            'Triple("Tools", Icons.Outlined.Build, Icons.Filled.Build),',
            'Triple("Tools", Icons.Outlined.Build, Icons.Filled.Build),\n                    Triple("Smart", Icons.Outlined.CheckCircle, Icons.Filled.CheckCircle),'
        )
        content = content.replace(
            '3 -> StatusLogsView(viewModel, uiState)',
            '3 -> StatusLogsView(viewModel, uiState)\n                4 -> ConfigView(viewModel, uiState)'
        )
        content = content.replace(
            '1 -> ClockCheckView(viewModel, uiState)',
            '1 -> SmartRecordView(viewModel, uiState)\n                2 -> ClockCheckView(viewModel, uiState)'
        )
        content = content.replace(
            '2 -> OtgFlashView(viewModel, uiState)',
            '3 -> OtgFlashView(viewModel, uiState)'
        )
        content = content.replace(
            '4 -> ConfigView(viewModel, uiState)',
            '5 -> ConfigView(viewModel, uiState)'
        )
        # We need to change the count of tabs to 6, wait, the original was 5 tabs. Now it's 6.
        content = content.replace(
            'Triple("Flash", Icons.Outlined.CheckCircle, Icons.Filled.CheckCircle),',
            'Triple("Flash", Icons.Outlined.Info, Icons.Filled.Info),'
        )

    with open("app/src/main/java/com/example/DiagnosticScreen.kt", "w") as f:
        f.write(content)

patch_ui()
