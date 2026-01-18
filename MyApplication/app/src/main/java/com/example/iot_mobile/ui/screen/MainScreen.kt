package com.example.iot_mobile.ui.screen


import android.content.Context
import android.util.Log
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.res.vectorResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.iot_mobile.data.loadTracksFromAssets
import com.example.iot_mobile.network.fetchAndSavePiIp
import com.example.iot_mobile.network.getSavedPiIp
import com.example.iot_mobile.network.getUploadUrl
import com.example.iot_mobile.R
import com.example.iot_mobile.data.BluetoothDeviceDto
import com.example.iot_mobile.network.connectBluetoothDevice
import com.example.iot_mobile.network.fetchBluetoothDevices

import com.example.iot_mobile.viewmodel.MusicPlayerViewModel

import io.ktor.client.HttpClient
import io.ktor.client.engine.okhttp.OkHttp
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.forms.formData
import io.ktor.client.request.forms.submitFormWithBinaryData

import io.ktor.http.Headers
import io.ktor.http.HttpHeaders

import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Composable
fun MainScreen(
    modifier: Modifier = Modifier.fillMaxSize(),
    viewModel: MusicPlayerViewModel,

) {
    val context = LocalContext.current
    Log.d("IP_RPI", "Próba uzyskania adresu RPI")
    LaunchedEffect(Unit) {
        fetchAndSavePiIp(context)
    }
    var showBtDialog = remember { mutableStateOf(false) }
    val btDevices = remember { mutableStateOf<List<BluetoothDeviceDto>>(emptyList()) }
    val loadingBt = remember { mutableStateOf(false) }
    val showCalibrationDialog = remember { mutableStateOf(false) }
    Surface(modifier = modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            modifier = modifier
                .padding(16.dp)
                .fillMaxSize(), // Increased overall padding
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Header
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = stringResource(R.string.list_of_audio_tracks),
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.weight(1f)
                )

                // BLUETOOTH
                Card(
                    modifier = Modifier
                        .size(40.dp)
                        .clickable { showBtDialog.value = true },
                    shape = MaterialTheme.shapes.medium,
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = ImageVector.vectorResource(R.drawable.bluetooth),
                            contentDescription = "Bluetooth",
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }
                }

                Spacer(modifier = Modifier.width(8.dp))

                // MICROPHONE
                Card(
                    modifier = Modifier
                        .size(40.dp)
                        .clickable {
                            CoroutineScope(Dispatchers.IO).launch {
                                showCalibrationDialog.value = true
                                viewModel.sendCalibrateRequest()

                            }
                        },
                    shape = MaterialTheme.shapes.medium,
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = ImageVector.vectorResource(R.drawable.mic),
                            contentDescription = "Kalibracja mikrofonu",
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }
                }

            }
            if (showBtDialog.value) {
                AlertDialog(
                    onDismissRequest = { showBtDialog.value = false },
                    title = { Text("Urządzenia Bluetooth") },
                    text = {
                        if (loadingBt.value) {
                            Text("Skanowanie...")
                        } else {
                            LazyColumn {
                                items(btDevices.value) { device ->
                                    Text(
                                        text = "${device.name} (${device.mac})",
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clickable {
                                                CoroutineScope(Dispatchers.IO).launch {
                                                    connectBluetoothDevice(context, device.mac)
                                                }
                                                showBtDialog.value = false
                                            }
                                            .padding(8.dp)
                                    )
                                }
                            }
                        }
                    },
                    confirmButton = {
                        Button(onClick = {
                            loadingBt.value = true
                            CoroutineScope(Dispatchers.IO).launch {
                                btDevices.value = fetchBluetoothDevices(context)
                                loadingBt.value = false
                            }
                        }) {
                            Text("Skanuj")
                        }
                    }
                )
            }
            if (showCalibrationDialog.value) {
                AlertDialog(
                    onDismissRequest = { showCalibrationDialog.value = false },
                    title = {
                        Text(
                            text = "Kalibracja mikrofonu",
                            fontWeight = FontWeight.Bold
                        )
                    },
                    text = {
                        Text("Czekaj...")
                    },
                    confirmButton = {}
                )

                // auto-zamykanie po 5 sekundach
                LaunchedEffect(Unit) {
                    kotlinx.coroutines.delay(3000)
                    showCalibrationDialog.value = false
                }
            }

            // MIDDLE BAR (LazyColumn for Files Display)
            FilesDisplay(
                modifier = Modifier
                    .weight(1f) // Takes remaining space
                    .fillMaxWidth(),
                musicPlayerViewModel = viewModel
            )
            val ip = getSavedPiIp(context)

            if (ip != null) {
                Log.d("IP_RPI", "Odczytane IP raspberryPi: $ip")
            }
            // Footer (Music Player Controls)
            // The footer will be placed here automatically after FilesDisplay due to weight
        }

    }
}

@Composable
fun Footer(viewModel: MusicPlayerViewModel) {

    val isPlaying by viewModel.isPlaying.collectAsState()

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.Center
    ) {
        Button(onClick = { viewModel.togglePlayPause() }) {
            Icon(
                imageVector = if (isPlaying)
                    ImageVector.vectorResource(R.drawable.pause_button)
                else
                    ImageVector.vectorResource(R.drawable.play_button),
                contentDescription = if (isPlaying) "Pause" else "Play",
                tint = MaterialTheme.colorScheme.onPrimary
            )
        }

        Spacer(modifier = Modifier.width(16.dp))

        Button(onClick = { viewModel.stopPlayback() }) {
            Icon(
                imageVector = ImageVector.vectorResource(R.drawable.stop_button),
                contentDescription = "Stop",
                tint = MaterialTheme.colorScheme.onPrimary
            )
        }
    }
}
@Composable
fun FilesDisplay(
    modifier: Modifier = Modifier,
    musicPlayerViewModel: MusicPlayerViewModel
) {
    val context = LocalContext.current
    val currentFile by musicPlayerViewModel.currentFile.collectAsState()

    val tracks = remember {
        loadTracksFromAssets(context)
    }

    LazyColumn(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(tracks) { track ->

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        if (currentFile != track.assetPath) {
                            musicPlayerViewModel.playFile(track.assetPath)
                            fetchAndSavePiIp(context)

                        }
                    },
                colors = CardDefaults.cardColors(
                    containerColor =
                        if (currentFile == track.assetPath)
                            MaterialTheme.colorScheme.primaryContainer
                        else
                            MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = track.name,
                        style = MaterialTheme.typography.titleMedium
                    )
                }

            }

        }
    }
    if (currentFile != null) {
        Footer(musicPlayerViewModel)
    }
}

//funkcja przesyłająca plik na serwer
suspend fun sendAssetToServer(context: Context, assetPath: String) {
    val client = HttpClient(OkHttp) {
        install(ContentNegotiation) { json() }
    }

    try {
        val inputStream = context.assets.open(assetPath)
        val bytes = inputStream.readBytes()
        inputStream.close()
        //wazne! wysyla dane jako multipart/form-data
        val response = client.submitFormWithBinaryData(
            //url = "http://10.83.205.237:8000/upload",
            url = getUploadUrl(context),
            formData = formData {
                //bitowe przesyłanie pliku
                append("file", bytes, Headers.build {
                    //deklaracja: to jest mp3
                    append(HttpHeaders.ContentType, "audio/mpeg")
                    append(HttpHeaders.ContentDisposition, "filename=$assetPath")
                })
            }
        )

        Log.d("UPLOAD", "Response: ${response.status}")
    } catch (e: Exception) {
        Log.e("UPLOAD", "Error: ${e.message}")
    } finally {
        client.close()
    }
}