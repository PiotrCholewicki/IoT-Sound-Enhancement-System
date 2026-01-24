package com.example.iot_mobile.ui.screen
import com.example.iot_mobile.data.Track
import android.content.Context
import android.net.Uri
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.res.vectorResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.iot_mobile.R
import com.example.iot_mobile.data.BluetoothDeviceDto
import com.example.iot_mobile.network.*
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
import java.io.File

@Composable
fun MainScreen(
    modifier: Modifier = Modifier.fillMaxSize(),
    viewModel: MusicPlayerViewModel
) {
    val context = LocalContext.current

    // ===== FILE PICKER (+) =====
    val pickAudioLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        uri?.let {
            viewModel.addSongFromUri(context, it)
        }
    }

    // ===== BLUETOOTH / MIC STATE =====
    val showBtDialog = remember { mutableStateOf(false) }
    val btDevices = remember { mutableStateOf<List<BluetoothDeviceDto>>(emptyList()) }
    val loadingBt = remember { mutableStateOf(false) }
    val showCalibrationDialog = remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        fetchAndSavePiIp(context)
    }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(
                onClick = { pickAudioLauncher.launch(arrayOf("audio/*")) }
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = "Dodaj piosenkę"
                )
            }
        }
    ) { paddingValues ->

        Surface(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues),
            color = MaterialTheme.colorScheme.background
        ) {
            Column(
                modifier = Modifier
                    .padding(16.dp)
                    .fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {

                // ===== HEADER =====
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom=8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = stringResource(R.string.list_of_audio_tracks),
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f)
                    )

                    // ===== BLUETOOTH BUTTON =====
                    Card(
                        modifier = Modifier
                            .size(40.dp)
                            .clickable { showBtDialog.value = true },
                        elevation = CardDefaults.cardElevation(4.dp)
                    ) {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = ImageVector.vectorResource(R.drawable.bluetooth),
                                contentDescription = "Bluetooth"
                            )
                        }
                    }

                    Spacer(modifier = Modifier.width(8.dp))

                    // ===== MIC BUTTON =====
                    Card(
                        modifier = Modifier
                            .size(40.dp)
                            .clickable {
                                CoroutineScope(Dispatchers.IO).launch {
                                    showCalibrationDialog.value = true
                                    viewModel.sendCalibrateRequest()
                                }
                            },
                        elevation = CardDefaults.cardElevation(4.dp)
                    ) {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = ImageVector.vectorResource(R.drawable.mic),
                                contentDescription = "Kalibracja"
                            )
                        }
                    }
                }

                // ===== BLUETOOTH DIALOG =====
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

                // ===== MIC DIALOG =====
                if (showCalibrationDialog.value) {
                    AlertDialog(
                        onDismissRequest = { showCalibrationDialog.value = false },
                        title = { Text("Kalibracja mikrofonu") },
                        text = { Text("Czekaj...") },
                        confirmButton = {}
                    )

                    LaunchedEffect(Unit) {
                        kotlinx.coroutines.delay(3000)
                        showCalibrationDialog.value = false
                    }
                }

                // ===== FILE LIST =====
                FilesDisplay(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    musicPlayerViewModel = viewModel
                )
            }
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
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun FilesDisplay(
    modifier: Modifier = Modifier,
    musicPlayerViewModel: MusicPlayerViewModel
) {
    val context = LocalContext.current
    val currentFile by musicPlayerViewModel.currentFile.collectAsState()
    val tracks by musicPlayerViewModel.tracks.collectAsState()

    var trackToDelete by remember { mutableStateOf<Track?>(null) }

    LaunchedEffect(Unit) {
        musicPlayerViewModel.loadAllTracks(context)
    }

    LazyColumn(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(tracks) { track ->

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .combinedClickable(
                        onClick = {
                            if (currentFile != track.path) {
                                musicPlayerViewModel.playFile(track)
                                fetchAndSavePiIp(context)
                            }
                        },
                        onLongClick = {
                            if (!track.isAsset) {
                                trackToDelete = track
                            }
                        }
                    ),
                colors = CardDefaults.cardColors(
                    containerColor =
                        if (currentFile == track.path)
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


    trackToDelete?.let { track ->
        AlertDialog(
            onDismissRequest = { trackToDelete = null },
            title = { Text("Usuń piosenkę") },
            text = { Text("Czy na pewno chcesz usunąć „${track.name}”?") },
            confirmButton = {
                TextButton(
                    onClick = {
                        musicPlayerViewModel.deleteTrack(context, track)
                        trackToDelete = null
                    }
                ) {
                    Text("Usuń")
                }
            },
            dismissButton = {
                TextButton(onClick = { trackToDelete = null }) {
                    Text("Anuluj")
                }
            }
        )
    }

    if (currentFile != null) {
        Footer(musicPlayerViewModel)
    }
}


suspend fun sendTrackToServer(context: Context, track: Track) {
    val client = HttpClient(OkHttp) {
        install(ContentNegotiation) { json() }
    }

    try {
        val bytes: ByteArray
        val fileName: String

        if (track.isAsset) {
            context.assets.open(track.path).use { inputStream ->
                bytes = inputStream.readBytes()
            }
            fileName = track.name + ".mp3"
        } else {
            val file = File(track.path)
            bytes = file.readBytes()
            fileName = file.name
        }

        val response = client.submitFormWithBinaryData(
            url = getUploadUrl(context),
            formData = formData {
                append("file", bytes, Headers.build {
                    append(HttpHeaders.ContentType, "audio/mpeg")
                    append(
                        HttpHeaders.ContentDisposition,
                        "filename=\"$fileName\""
                    )
                })
            }
        )

        Log.d("UPLOAD", "Response: ${response.status}")

    } catch (e: Exception) {
        Log.e("UPLOAD", "Error: ${e.message}", e)
    } finally {
        client.close()
    }
}