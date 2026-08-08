import re

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'r') as f:
    content = f.read()

# 1. Update AppTheme
new_theme_props = """    val error: Color,
    val cornerRadius: androidx.compose.ui.unit.Dp,
    val fontFamily: androidx.compose.ui.text.font.FontFamily,
    val isRobot: Boolean
)"""
content = content.replace("    val error: Color\n)", new_theme_props)

# 2. Update ModernTheme
modern_theme_props = """    error = Color(0xFFB3261E),
    cornerRadius = 24.dp,
    fontFamily = androidx.compose.ui.text.font.FontFamily.SansSerif,
    isRobot = false
)"""
content = content.replace("    error = Color(0xFFB3261E)\n)", modern_theme_props)

# 3. Update RobotTheme
robot_theme_props = """    error = Color(0xFFF44336),
    cornerRadius = 0.dp,
    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
    isRobot = true
)"""
content = content.replace("    error = Color(0xFFF44336)\n)", robot_theme_props)

# 4. Use cornerRadius instead of 24.dp
content = content.replace("RoundedCornerShape(24.dp)", "RoundedCornerShape(theme.cornerRadius)")
content = content.replace("RoundedCornerShape(16.dp)", "RoundedCornerShape(theme.cornerRadius)")
content = content.replace("RoundedCornerShape(12.dp)", "RoundedCornerShape(theme.cornerRadius)")
content = content.replace("RoundedCornerShape(8.dp)", "RoundedCornerShape(theme.cornerRadius)")

# 5. Use cornerRadius for CircleShapes in the UI
content = content.replace("clip(CircleShape)", "clip(if (theme.isRobot) androidx.compose.foundation.shape.CutCornerShape(4.dp) else CircleShape)")
content = content.replace("background(theme.secondaryContainer, CircleShape)", "background(theme.secondaryContainer, if (theme.isRobot) androidx.compose.foundation.shape.CutCornerShape(4.dp) else CircleShape)")

# 6. Apply ProvideTextStyle for global font family
provide_text_style = """
    androidx.compose.material3.ProvideTextStyle(androidx.compose.ui.text.TextStyle(fontFamily = theme.fontFamily)) {
        Column(modifier = modifier.fillMaxSize().background(theme.bg)) {"""
content = content.replace("    Column(modifier = modifier.fillMaxSize().background(theme.bg)) {", provide_text_style)

# close the ProvideTextStyle block at the end of DiagnosticScreen
end_of_screen = """                    else -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("Coming Soon", color = Color.Gray)
                    }
                }
            }
        }
    }
}
"""

content = content.replace("""                    else -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("Coming Soon", color = Color.Gray)
                    }
                }
            }
        }
    }
}""", """                    else -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("Coming Soon", color = Color.Gray)
                    }
                }
            }
        }
    }
    }
}""")

with open('app/src/main/java/com/example/DiagnosticScreen.kt', 'w') as f:
    f.write(content)
