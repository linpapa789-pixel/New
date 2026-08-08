package com.example.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val HackerColorScheme = darkColorScheme(
    primary = ElectricCyan,
    secondary = CyberpunkGreen,
    tertiary = AlertRed,
    background = HackerBackground,
    surface = HackerSurface,
    surfaceVariant = HackerSurfaceVariant,
    onPrimary = HackerBackground,
    onSecondary = HackerBackground,
    onBackground = TerminalText,
    onSurface = TerminalText,
    onSurfaceVariant = Color.Gray,
    error = AlertRed,
    primaryContainer = HackerSurfaceVariant,
    onPrimaryContainer = ElectricCyan,
    outline = DimmedGray
)

@Composable
fun MyApplicationTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = HackerColorScheme
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            window.navigationBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
            WindowCompat.getInsetsController(window, view).isAppearanceLightNavigationBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
