package com.roadseer.gps

import android.Manifest
import android.content.*
import android.net.wifi.WifiManager
import android.os.Bundle
import android.os.IBinder
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.roadseer.gps.ui.theme.*
import kotlinx.coroutines.delay
import java.util.Formatter
import java.util.Locale

class MainActivity : ComponentActivity() {

    private var gpsService: GpsService? = null
    private var isBound = false
    private var isRunning = mutableStateOf(false)

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            gpsService = (binder as GpsService.LocalBinder).getService()
            isBound = true
            isRunning.value = gpsService?.isServerRunning == true
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            gpsService = null
            isBound = false
            isRunning.value = false
        }
    }

    // Permission launcher
    private val locationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            startGpsService()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            RoadseerGPSTheme {
                GpsBeaconScreen(
                    isRunning = isRunning.value,
                    getService = { gpsService },
                    getPhoneIp = { getWifiIpAddress() },
                    onStartClick = { requestPermissionsAndStart() },
                    onStopClick = { stopGpsService() },
                )
            }
        }
    }

    override fun onStart() {
        super.onStart()
        // Bind to existing service if it's running
        Intent(this, GpsService::class.java).also {
            bindService(it, connection, Context.BIND_AUTO_CREATE)
        }
    }

    override fun onStop() {
        super.onStop()
        if (isBound) {
            unbindService(connection)
            isBound = false
        }
    }

    private fun requestPermissionsAndStart() {
        locationPermissionLauncher.launch(
            arrayOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION,
            )
        )
    }

    private fun startGpsService() {
        Intent(this, GpsService::class.java).also {
            startForegroundService(it)
            bindService(it, connection, Context.BIND_AUTO_CREATE)
        }
        isRunning.value = true
    }

    private fun stopGpsService() {
        Intent(this, GpsService::class.java).also {
            stopService(it)
        }
        isRunning.value = false
    }

    @Suppress("deprecation")
    private fun getWifiIpAddress(): String {
        val wifiManager = applicationContext.getSystemService(WIFI_SERVICE) as WifiManager
        val ip = wifiManager.connectionInfo.ipAddress
        if (ip == 0) return "Not connected to WiFi"
        return String.format(
            Locale.US, "%d.%d.%d.%d",
            ip and 0xff, ip shr 8 and 0xff,
            ip shr 16 and 0xff, ip shr 24 and 0xff
        )
    }
}

// ═══════════════════════════════════════════════════════════
//  COMPOSABLE UI — Single screen, matches your frontend's
//  slate-950 background + orange-500 accent + rounded-2xl cards
// ═══════════════════════════════════════════════════════════

@Composable
fun GpsBeaconScreen(
    isRunning: Boolean,
    getService: () -> GpsService?,
    getPhoneIp: () -> String,
    onStartClick: () -> Unit,
    onStopClick: () -> Unit,
) {
    // Poll service for live data every 500ms
    var lat by remember { mutableStateOf(0.0) }
    var lon by remember { mutableStateOf(0.0) }
    var altitude by remember { mutableStateOf(0.0) }
    var accuracy by remember { mutableStateOf(0f) }
    var speed by remember { mutableStateOf(0f) }
    var bearing by remember { mutableStateOf(0f) }
    var hasFix by remember { mutableStateOf(false) }
    var phoneIp by remember { mutableStateOf("...") }
    var serverActive by remember { mutableStateOf(false) }

    LaunchedEffect(isRunning) {
        while (true) {
            val svc = getService()
            val loc = svc?.currentLocation
            lat = loc?.latitude ?: 0.0
            lon = loc?.longitude ?: 0.0
            altitude = loc?.altitude ?: 0.0
            accuracy = loc?.accuracy ?: 0f
            speed = (loc?.speed ?: 0f) * 3.6f  // m/s → km/h for display
            bearing = loc?.bearing ?: 0f
            hasFix = loc != null
            serverActive = svc?.isServerRunning == true
            phoneIp = getPhoneIp()
            delay(500)
        }
    }

    Scaffold(
        containerColor = Slate950,
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(modifier = Modifier.height(24.dp))

            // ── App Header (like your Navbar logo) ──
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
            ) {
                // Orange icon box (matches bg-orange-500/20 + text-orange-400)
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(Orange500Alpha15),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        Icons.Default.CellTower,
                        contentDescription = null,
                        tint = Orange400,
                        modifier = Modifier.size(22.dp),
                    )
                }
                Spacer(modifier = Modifier.width(10.dp))
                Text(
                    "Raspi ",
                    style = MaterialTheme.typography.titleLarge,
                    color = Slate50,
                )
                Text(
                    "Roadseer",
                    style = MaterialTheme.typography.titleLarge,
                    color = Orange400,  // matches <span className="text-orange-400">
                )
            }

            Text(
                "GPS Beacon",
                style = MaterialTheme.typography.bodyMedium,
                color = Slate500,
                modifier = Modifier.padding(top = 4.dp),
            )

            Spacer(modifier = Modifier.height(32.dp))

            // ── Big Start/Stop Button ──
            val buttonColor = if (isRunning) Red500 else Orange500

            Button(
                onClick = { if (isRunning) onStopClick() else onStartClick() },
                modifier = Modifier
                    .size(160.dp)
                    .clip(CircleShape),
                shape = CircleShape,
                colors = ButtonDefaults.buttonColors(containerColor = buttonColor),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 8.dp),
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        if (isRunning) Icons.Default.Stop else Icons.Default.PlayArrow,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = Slate50,
                    )
                    Text(
                        if (isRunning) "STOP" else "START",
                        style = MaterialTheme.typography.labelLarge,
                        color = Slate50,
                        fontSize = 16.sp,
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // ── Status Badge (like your inline pill badges) ──
            val statusColor = if (isRunning && hasFix) Green500
                else if (isRunning) Amber500
                else Slate600
            val statusText = if (isRunning && hasFix) "● GPS Fix Active"
                else if (isRunning) "● Waiting for fix..."
                else "● Server Stopped"

            Surface(
                shape = RoundedCornerShape(50),
                color = statusColor.copy(alpha = 0.15f),
                modifier = Modifier.padding(vertical = 8.dp),
            ) {
                Text(
                    statusText,
                    color = statusColor,
                    style = MaterialTheme.typography.labelLarge,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp),
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // ── Server Info Card (matches rounded-2xl border border-slate-800 bg-slate-900/50) ──
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = Slate900.copy(alpha = 0.5f),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, Slate800, RoundedCornerShape(16.dp)),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Pi Connection",
                        style = MaterialTheme.typography.titleMedium,
                        color = Slate50,
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    InfoRow(
                        icon = Icons.Default.Wifi,
                        label = "Phone IP",
                        value = phoneIp,
                        valueColor = if (phoneIp.contains("Not")) Red500 else Orange400,
                    )
                    InfoRow(
                        icon = Icons.Default.Link,
                        label = "Pi fetches",
                        value = if (phoneIp.contains("Not")) "—"
                            else "http://$phoneIp:5000/gps",
                        valueColor = Orange400,
                    )
                    InfoRow(
                        icon = Icons.Default.CheckCircle,
                        label = "Server",
                        value = if (serverActive) "Running on :5000" else "Stopped",
                        valueColor = if (serverActive) Green500 else Slate500,
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // ── GPS Data Card ──
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = Slate900.copy(alpha = 0.5f),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, Slate800, RoundedCornerShape(16.dp)),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Live GPS Data",
                        style = MaterialTheme.typography.titleMedium,
                        color = Slate50,
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    // 2-column grid for GPS values
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            GpsValueTile("Latitude", String.format(Locale.US, "%.6f", lat))
                            GpsValueTile("Altitude", String.format(Locale.US, "%.1f m", altitude))
                            GpsValueTile("Speed", String.format(Locale.US, "%.1f km/h", speed))
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            GpsValueTile("Longitude", String.format(Locale.US, "%.6f", lon))
                            GpsValueTile("Accuracy", String.format(Locale.US, "%.1f m", accuracy))
                            GpsValueTile("Bearing", String.format(Locale.US, "%.0f°", bearing))
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            // ── Footer ──
            Text(
                "Raspi-RoadSeer • GPS Beacon for Pi 5",
                style = MaterialTheme.typography.labelSmall,
                color = Slate600,
                modifier = Modifier.padding(bottom = 8.dp),
            )
        }
    }
}

@Composable
fun InfoRow(icon: ImageVector, label: String, value: String, valueColor: androidx.compose.ui.graphics.Color) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = Slate500,
            modifier = Modifier.size(18.dp),
        )
        Spacer(modifier = Modifier.width(10.dp))
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            color = Slate400,
            modifier = Modifier.width(80.dp),
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium,
            color = valueColor,
            fontWeight = FontWeight.Medium,
        )
    }
}

@Composable
fun GpsValueTile(label: String, value: String) {
    Column(modifier = Modifier.padding(vertical = 6.dp)) {
        Text(
            label,
            style = MaterialTheme.typography.labelSmall,
            color = Slate500,
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyLarge,
            color = Orange400,
            fontWeight = FontWeight.SemiBold,
        )
    }
}