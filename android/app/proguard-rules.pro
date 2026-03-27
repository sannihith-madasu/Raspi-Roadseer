# NanoHTTPD
-keep class fi.iki.elonen.** { *; }

# Google Play Services
-keep class com.google.android.gms.** { *; }

# Keep JSON serialization
-keepclassmembers class * {
    @org.json.* <fields>;
}