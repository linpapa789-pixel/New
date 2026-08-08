with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "if (uiState.connectionMode == ConnectionMode.WIFI)" in line:
        if i > 350: # The second occurrence is around line 386
            skip = True
    
    if skip:
        if "}" in line and "Text(\"Connect\", color = theme.surface)" in lines[i-2]:
            # This is the end of the block
            skip = False
            continue
    
    if not skip:
        new_lines.append(line)

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.writelines(new_lines)

