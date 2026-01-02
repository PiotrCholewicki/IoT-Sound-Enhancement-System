package com.example.iot_mobile.network

import android.content.Context
import android.util.Log
import com.example.iot_mobile.data.BluetoothDeviceDto
import com.example.iot_mobile.data.BtConnectRequest
import com.example.iot_mobile.data.BtScanResponse
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.okhttp.OkHttp
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json

suspend fun fetchBluetoothDevices(context: Context): List<BluetoothDeviceDto> {
    val ip = getSavedPiIp(context) ?: return emptyList()

    val client = HttpClient(OkHttp) {
        install(HttpTimeout) {
            connectTimeoutMillis = 15_000
            requestTimeoutMillis = 30_000
            socketTimeoutMillis = 30_000
        }
        install(ContentNegotiation) {
            json(
                Json {
                    ignoreUnknownKeys = true
                }
            )
        }
    }

    return try {
        val response: BtScanResponse = client.post("http://$ip:8002/bt/scan").body()

        // Mapujemy Map<String, String> na List<BluetoothDeviceDto>
        response.devices.map { (mac, name) ->
            BluetoothDeviceDto(
                name = name,
                mac = mac
            )
        }
    } catch (e: Exception) {
        Log.e("BT", "Scan error", e)
        emptyList()
    } finally {
        client.close()
    }
}



suspend fun connectBluetoothDevice(context: Context, mac: String): Boolean {
    val ip = getSavedPiIp(context) ?: return false

    val client = HttpClient(OkHttp) {
        install(HttpTimeout) {
            connectTimeoutMillis = 15_000
            requestTimeoutMillis = 30_000
            socketTimeoutMillis = 30_000
        }
        install(ContentNegotiation) {
            json()
        }
    }

    return try {
        client.post("http://$ip:8002/bt/connect") {
            contentType(io.ktor.http.ContentType.Application.Json)
            setBody(BtConnectRequest(mac))
        }
        true
    } catch (e: Exception) {
        Log.e("BT", "Connect error", e)
        false
    } finally {
        client.close()
    }
}

