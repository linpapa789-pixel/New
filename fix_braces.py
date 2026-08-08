with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

# I will find the `@Composable\nfun ToolsView` and insert `}` just before it.
import re
content = re.sub(r'(\s*)(@Composable\s*fun ToolsView)', r'\1}\1\2', content)

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
