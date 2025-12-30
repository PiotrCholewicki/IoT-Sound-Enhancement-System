package com.example.iot_mobile.ui.screen


import android.content.Context
import android.content.res.AssetFileDescriptor
import android.os.Environment
import android.util.Log
import android.util.Log.e
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.runtime.livedata.observeAsState
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
import com.example.iot_mobile.loadTracksFromAssets
import com.example.iot_mobile.network.fetchAndSavePiIp
import com.example.iot_mobile.network.getSavedPiIp
import com.example.iot_mobile.network.getUploadUrl
import com.example.iot_mobile.R

import com.example.iot_mobile.viewmodel.MusicPlayerViewModel

import io.ktor.client.HttpClient
import io.ktor.client.engine.okhttp.OkHttp
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.forms.formData
import io.ktor.client.request.forms.submitForm
import io.ktor.client.request.forms.submitFormWithBinaryData
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.Headers
import io.ktor.http.HttpHeaders
import io.ktor.http.content.TextContent
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.w3c.dom.Text
import java.io.File
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import org.json.JSONObject
import java.net.URL

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
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Text(
                    text = stringResource(R.string.list_of_audio_tracks),
                    fontSize = 24.sp, // Larger font for title
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary // Theme primary color for title
                )
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
fun Footer(musicPlayerViewModel: MusicPlayerViewModel) {
    val context = LocalContext.current
    val isPlaying by musicPlayerViewModel.isPlaying.collectAsState()
    val currentPosition by musicPlayerViewModel.currentPosition.collectAsState()
    val totalDuration by musicPlayerViewModel.totalDuration.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 16.dp, bottom = 8.dp), // Added top padding to separate from list
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Slider(
            value = if (totalDuration > 0) currentPosition.toFloat() / totalDuration else 0f,
            onValueChange = {
                val newPos = (it * totalDuration).toInt()
                musicPlayerViewModel.seekTo(newPos)
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp),
            colors = androidx.compose.material3.SliderDefaults.colors(
                thumbColor = MaterialTheme.colorScheme.primary,
                activeTrackColor = MaterialTheme.colorScheme.primary,
                inactiveTrackColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
        )
        Spacer(modifier = Modifier.height(8.dp)) // Spacer between slider and buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center, // Center buttons
            verticalAlignment = Alignment.CenterVertically
        ) {
            Button(

                onClick = {CoroutineScope(Dispatchers.IO).launch {
                    musicPlayerViewModel.togglePlayPause()}
                    //fetchAndSavePiIp(context)
                  },
                modifier = Modifier.padding(horizontal = 4.dp)
            ) {
                Icon(
                    imageVector = if (isPlaying) ImageVector.vectorResource(R.drawable.pause_button) else ImageVector.vectorResource(R.drawable.play_button),
                    contentDescription = if (isPlaying) "Pause" else "Play",
                    tint = MaterialTheme.colorScheme.onPrimary // Icon color
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Button(
                onClick = {
                    musicPlayerViewModel.stopPlayback()
                    //fetchAndSavePiIp(context)

                },
                modifier = Modifier.padding(horizontal = 4.dp)
            ) {
                Icon(
                    imageVector = ImageVector.vectorResource(R.drawable.stop_button),
                    contentDescription = "Stop",
                    tint = MaterialTheme.colorScheme.onPrimary // Icon color
                )
            }
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

                            CoroutineScope(Dispatchers.IO).launch {
                                sendAssetToServer(context, track.assetPath)
                            }
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