# 📡 Roadseer GPS Beacon — Android App

**Replaces the Termux + `phone_gps_server.py` workflow with a one-tap Android app.**

Your Raspberry Pi's `gps_reader.py` fetches `http://<phone-ip>:5000/gps` — this app serves that exact same endpoint natively, with no terminal required.

## What It Does

- 📍 Gets GPS via Android's FusedLocationProvider (better than Termux's `termux-location`)
- 🌐 Runs an HTTP server on port 5000 with the same `/gps` and `/health` endpoints
- 🔒 Runs as a foreground service — won't get killed when screen is off
- 🎨 Matches the Roadseer dashboard color scheme (slate-950 + orange-500)

## Pi-Side Changes Required

**None.** Zero. The app serves the exact same JSON format:

```json
{
  "latitude": 17.385044,
  "longitude": 78.486702,
  "altitude": 0.0,
  "speed": 0.0,
  "accuracy": 12.3,
  "bearing": 0.0,
  "timestamp": 1710000000.0,
  "provider": "fused",
  "fix": true
}
```

## Setup

1. Open this folder in **Android Studio**
2. Plug in your Android phone (USB debugging enabled)
3. Click ▶ **Run**
4. App installs → tap **START** → done

## Build APK for Sharing

```bash
./gradlew assembleDebug
# APK at: app/build/outputs/apk/debug/app-debug.apk
```

## Color Scheme

Matches the web frontend exactly:

| Color | Hex | Usage |
|-------|-----|-------|
| `orange-500` | `#F97316` | Primary accent, buttons |
| `orange-400` | `#FB923C` | GPS values, highlights |
| `slate-950` | `#020617` | Background |
| `slate-900` | `#0F172A` | Cards |
| `slate-800` | `#1E293B` | Card borders |
| `red-500` | `#EF4444` | Stop button, errors |
| `green-500` | `#22C55E` | Active/success status |
| `amber-500` | `#F59E0B` | Warning/waiting |