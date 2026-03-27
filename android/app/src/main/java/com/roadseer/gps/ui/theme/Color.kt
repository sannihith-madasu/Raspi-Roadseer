package com.roadseer.gps.ui.theme

import androidx.compose.ui.graphics.Color

// ── Matches frontend/src/index.css exactly ──
// --color-primary: #f97316   (orange-500)
// --color-danger:  #ef4444   (red-500)
// --color-warning: #f59e0b   (amber-500)
// --color-success: #22c55e   (green-500)
// --color-dark:    #0f172a   (slate-900)
// --color-darker:  #020617   (slate-950)

// Primary Orange (your accent color everywhere)
val Orange500 = Color(0xFFF97316)
val Orange400 = Color(0xFFFB923C)
val Orange600 = Color(0xFFEA580C)
val Orange500Alpha15 = Color(0x26F97316)  // bg-orange-500/15
val Orange500Alpha10 = Color(0x19F97316)  // bg-orange-500/10

// Status Colors
val Red500 = Color(0xFFEF4444)     // --color-danger / critical
val Amber500 = Color(0xFFF59E0B)   // --color-warning / moderate
val Green500 = Color(0xFF22C55E)   // --color-success / active

// Slate palette (your dark theme backbone)
val Slate950 = Color(0xFF020617)   // --color-darker / bg-slate-950
val Slate900 = Color(0xFF0F172A)   // --color-dark / bg-slate-900
val Slate800 = Color(0xFF1E293B)   // border-slate-800
val Slate700 = Color(0xFF334155)   // border-slate-700
val Slate600 = Color(0xFF475569)   // scrollbar-thumb
val Slate500 = Color(0xFF64748B)   // text-slate-500
val Slate400 = Color(0xFF94A3B8)   // text-slate-400
val Slate50  = Color(0xFFF8FAFC)   // text primary (white-ish)