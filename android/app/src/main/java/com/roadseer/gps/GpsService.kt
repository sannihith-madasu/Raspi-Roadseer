package com.roadseer.gps

import android.app.*
import android.content.Intent
import android.content.pm.ServiceInfo
import android.location.Location
import android.os.Binder
import android.os.Build
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.core.app.NotificationCompat
import com.google.android.gms.location.*

/**
 * Foreground service that:
 * 1. Requests GPS updates every 2 seconds via FusedLocationProvider
 * 2. Runs the NanoHTTPD server on port 5000
 * 3. Keeps everything alive even when the screen is off
 *
 * This replaces the entire Termux + phone_gps_server.py workflow.
 */
class GpsService : Service() {

    companion object {
        const val TAG = "GpsService"
        const val NOTIFICATION_ID = 1001
        const val CHANNEL_ID = "gps_server_channel"
        const val SERVER_PORT = 5000
    }

    private lateinit var fusedClient: FusedLocationProviderClient
    private lateinit var locationCallback: LocationCallback
    private var gpsServer: GpsServer? = null

    // Binder so MainActivity can read live data
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): GpsService = this@GpsService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    // ── Expose live data to the UI ──
    var currentLocation: Location? = null
        private set
    var isServerRunning: Boolean = false
        private set
    var requestCount: Long = 0
        private set
    var lastPiPollTime: Long = 0
        private set

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        fusedClient = LocationServices.getFusedLocationProviderClient(this)

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                result.lastLocation?.let { loc ->
                    currentLocation = loc
                    gpsServer?.latestLocation = loc
                    gpsServer?.lastUpdateTime = System.currentTimeMillis()
                    Log.d(TAG, "GPS: ${loc.latitude}, ${loc.longitude} | acc: ${loc.accuracy}m")
                }
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Build the persistent notification (required for foreground services)
        val notification = buildNotification("Starting GPS server...")

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        startLocationUpdates()
        startHttpServer()

        return START_STICKY
    }

    @Suppress("MissingPermission") // Permission checked in MainActivity before starting
    private fun startLocationUpdates() {
        val request = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY,
            2000L  // Every 2 seconds (slightly faster than Termux's 3s)
        ).apply {
            setMinUpdateIntervalMillis(1000L)
            setMaxUpdateDelayMillis(3000L)
        }.build()

        fusedClient.requestLocationUpdates(request, locationCallback, Looper.getMainLooper())
        Log.d(TAG, "Location updates started (2s interval)")
    }

    private fun startHttpServer() {
        try {
            gpsServer = GpsServer(SERVER_PORT).also {
                it.start()
                isServerRunning = true
            }
            Log.d(TAG, "HTTP server started on port $SERVER_PORT")
            updateNotification("GPS server active on port $SERVER_PORT")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start HTTP server: ${e.message}")
            isServerRunning = false
            updateNotification("Server failed: ${e.message}")
        }
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "GPS Server",
            NotificationManager.IMPORTANCE_LOW  // Low = no sound, just persistent icon
        ).apply {
            description = "Keeps the GPS server running for the Raspberry Pi"
        }
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    private fun buildNotification(text: String): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Roadseer GPS")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .build()
    }

    private fun updateNotification(text: String) {
        val notification = buildNotification(text)
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification)
    }

    override fun onDestroy() {
        super.onDestroy()
        fusedClient.removeLocationUpdates(locationCallback)
        gpsServer?.stop()
        isServerRunning = false
        Log.d(TAG, "Service destroyed, server stopped")
    }
}