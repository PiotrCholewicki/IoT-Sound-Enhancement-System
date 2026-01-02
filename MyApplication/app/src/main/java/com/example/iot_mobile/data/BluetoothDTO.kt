package com.example.iot_mobile.data;
import kotlinx.serialization.Serializable
data class BluetoothDeviceDto(
    val name: String,
    val mac: String
)


@Serializable
data class BtScanResponse(
    val count: Int,
    val devices: Map<String, String>
)

@Serializable
data class BtConnectRequest(
    val mac: String
)
