package com.example.iot_mobile.network

import android.content.Context
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.net.URL

//funkcja fetchująca adres IP raspberrki z FastAPI z endpointa /status
fun fetchAndSavePiIp(context: Context) {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val url = URL("http://192.168.4.1:8000/status")
            val connection = url.openConnection()

            val data = connection.getInputStream().bufferedReader().readText()
            val json = JSONObject(data)
            val ip = json.getString("ip")
            Log.d("IP_RPI","Zapisano IP Raspberry Pi: $ip")

            // zapis w SharedPreferences
            val prefs = context.getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE)
            prefs.edit().putString("raspberry_ip", ip).apply()
            Log.d("IP_RPI", "Zapisano ip do shared preferences")

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}

// odczyt później
fun getSavedPiIp(context: Context): String? {
    val prefs = context.getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE)
    return prefs.getString("raspberry_ip", null)
}

fun getUploadUrl(context: Context): String{
    val ip = getSavedPiIp(context)
    return "http://"+ip+":8002/upload"
}
fun getCommandUrl(context: Context): String{
    val ip = getSavedPiIp(context)
    return "http://"+ip+":8002/command"
}
