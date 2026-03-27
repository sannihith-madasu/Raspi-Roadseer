package com.roadseer.gps

import android.location.Location
import fi.iki.elonen.NanoHTTPD
import org.json.JSONObject

/**
 * Embedded HTTP server that serves the EXACT same JSON endpoints
 * as src/phone_gps_server.py — so your Pi's gps_reader.py needs
 * ZERO changes.
 *
 * Endpoints:
 *   GET /gps    → { latitude, longitude, altitude, speed, accuracy, bearing, timestamp, provider, fix }
 *   GET /health → { status, gps_fix, uptime_seconds }
 */
class GpsServer(private val port: Int = 5000) : NanoHTTPD(port) {

    @Volatile
    var latestLocation: Location? = null

    @Volatile
    var lastUpdateTime: Long = 0L

    private val startTime = System.currentTimeMillis()

    override fun serve(session: IHTTPSession): Response {
        return when (session.uri) {
            "/gps" -> serveGps()
            "/health" -> serveHealth()
            else -> newFixedLengthResponse(
                Response.Status.NOT_FOUND,
                "text/plain",
                "Not found. Use /gps or /health"
            )
        }
    }

    /**
     * Matches phone_gps_server.py's /gps endpoint exactly:
     * {
     *   "latitude": 17.385044,
     *   "longitude": 78.486702,
     *   "altitude": 0.0,
     *   "speed": 0.0,        ← m/s (Pi converts to km/h)
     *   "accuracy": 12.3,
     *   "bearing": 0.0,
     *   "timestamp": 1710000000.0,
     *   "provider": "fused",
     *   "fix": true
     * }
     */
    private fun serveGps(): Response {
        val loc = latestLocation
        val timeSinceUpdate = (System.currentTimeMillis() - lastUpdateTime) / 1000.0
        val hasFix = loc != null && timeSinceUpdate < 10.0

        val json = JSONObject().apply {
            put("latitude", loc?.latitude ?: 0.0)
            put("longitude", loc?.longitude ?: 0.0)
            put("altitude", loc?.altitude ?: 0.0)
            put("speed", loc?.speed?.toDouble() ?: 0.0)
            put("accuracy", loc?.accuracy?.toDouble() ?: 0.0)
            put("bearing", loc?.bearing?.toDouble() ?: 0.0)
            put("timestamp", if (loc != null) lastUpdateTime / 1000.0 else 0.0)
            put("provider", loc?.provider ?: "none")
            put("fix", hasFix)
        }

        return newFixedLengthResponse(
            Response.Status.OK,
            "application/json",
            json.toString()
        ).apply {
            addHeader("Access-Control-Allow-Origin", "*")
        }
    }

    /**
     * Matches phone_gps_server.py's /health endpoint:
     * { "status": "ok", "gps_fix": true }
     */
    private fun serveHealth(): Response {
        val loc = latestLocation
        val timeSinceUpdate = (System.currentTimeMillis() - lastUpdateTime) / 1000.0
        val hasFix = loc != null && timeSinceUpdate < 10.0
        val uptimeSeconds = (System.currentTimeMillis() - startTime) / 1000

        val json = JSONObject().apply {
            put("status", "ok")
            put("gps_fix", hasFix)
            put("uptime_seconds", uptimeSeconds)
        }

        return newFixedLengthResponse(
            Response.Status.OK,
            "application/json",
            json.toString()
        ).apply {
            addHeader("Access-Control-Allow-Origin", "*")
        }
    }
}