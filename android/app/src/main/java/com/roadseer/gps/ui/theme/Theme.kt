package com.roadseer.gps.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Dark color scheme matching your frontend's slate-950 + orange-500 palette
private val RoadseerDarkScheme = darkColorScheme(
    primary = Orange500,
    onPrimary = Slate50,
    primaryContainer = Orange500Alpha15,
    onPrimaryContainer = Orange400,

    secondary = Slate700,
    onSecondary = Slate400,

    background = Slate950,
    onBackground = Slate50,

    surface = Slate900,
    onSurface = Slate50,
    surfaceVariant = Slate800,
    onSurfaceVariant = Slate400,

    error = Red500,
    onError = Slate50,

    outline = Slate800,
    outlineVariant = Slate700,
)

@Composable
fun RoadseerGPSTheme(content: @Composable () -> Unit) {
    val colorScheme = RoadseerDarkScheme
    val view = LocalView.current

    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // Status bar = slate-950 (your bg-slate-950)
            window.statusBarColor = Slate950.toArgb()
            // Navigation bar matches
            window.navigationBarColor = Slate950.toArgb()
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = false
                isAppearanceLightNavigationBars = false
            }
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = RoadseerTypography,
        content = content,
    )
}