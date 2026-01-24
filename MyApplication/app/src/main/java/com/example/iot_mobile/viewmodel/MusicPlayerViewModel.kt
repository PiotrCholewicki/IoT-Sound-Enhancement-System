package com.example.iot_mobile.viewmodel


import android.app.Application
import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.iot_mobile.data.Track
import com.example.iot_mobile.data.loadTracksFromAssets
import com.example.iot_mobile.data.loadTracksFromLocalFiles
import com.example.iot_mobile.network.getCommandUrl
import com.example.iot_mobile.ui.screen.sendTrackToServer
import io.ktor.client.HttpClient
import io.ktor.client.engine.okhttp.OkHttp
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.content.TextContent
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File

class MusicPlayerViewModel(application: Application) : AndroidViewModel(application) {

    private val context = application.applicationContext
    private val assetManager = context.assets

    private val serverContentUrl: String
        get() = getCommandUrl(context)


    private val _currentFile = MutableStateFlow<String?>(null)
    val currentFile = _currentFile.asStateFlow()

    private val _isPlaying = MutableStateFlow(false)
    val isPlaying = _isPlaying.asStateFlow()

    private val _currentPosition = MutableStateFlow(0)
    val currentPosition = _currentPosition.asStateFlow()

    private val _totalDuration = MutableStateFlow(0)
    val totalDuration = _totalDuration.asStateFlow()
    private val _status = MutableStateFlow("IDLE")
    val status = _status.asStateFlow()

    private val _tracks = MutableStateFlow<List<Track>>(emptyList())
    val tracks: StateFlow<List<Track>> = _tracks

    fun loadAllTracks(context: Context) {
        _tracks.value =
            loadTracksFromAssets(context) +
                    loadTracksFromLocalFiles(context)
    }
    fun addSongFromUri(context: Context, uri: Uri) {
        val resolver = context.contentResolver

        val name = resolver.query(uri, null, null, null, null)
            ?.use { cursor ->
                val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                cursor.moveToFirst()
                cursor.getString(index)
            } ?: "song_${System.currentTimeMillis()}.mp3"

        val file = File(context.filesDir, name)

        resolver.openInputStream(uri)?.use { input ->
            file.outputStream().use { output ->
                input.copyTo(output)
            }
        }

        loadAllTracks(context)
    }
    fun playFile(track: Track) {
        viewModelScope.launch {
            try {

                _status.value = "Uploading..."
                sendTrackToServer(context, track)

                _status.value = "Playing"
                sendResumeRequest()

                _currentFile.value = track.path
                _isPlaying.value = true
            } catch (e: Exception) {
                _status.value = "Error"
            }
        }
    }

    fun togglePlayPause() {
        viewModelScope.launch {
            if (_isPlaying.value) {
                sendStopRequest()
                _isPlaying.value = false
                _status.value = "Paused"
            } else {
                sendResumeRequest()
                _isPlaying.value = true
                _status.value = "Playing"
            }
        }
    }

    fun stopPlayback() {
        viewModelScope.launch {
            sendTerminateRequest()
            _isPlaying.value = false
            _currentFile.value = null
            _status.value = "Stopped"
        }
    }



    //funkcja wstrzymująca odtwarzanie
    suspend fun sendTerminateRequest(){
        val client = HttpClient(OkHttp) {
            install(ContentNegotiation) { json() }
        }
        try{
            val response = client.post(serverContentUrl){
                setBody(TextContent("q", ContentType.Text.Plain))}
            Log.d("COMMAND", "Sukces, wysyłam prośbę o skonczenie ")
        }
        catch(e: Exception){
            Log.e("COMMAND", "Problem w wysyłaniu komunikatu o zatrzymanie")
        }
        finally {
            client.close()
        }

    }

    //funkcja zatrzymujaca odtwarzanie
    suspend fun sendStopRequest(){
        val client = HttpClient(OkHttp) {
            install(ContentNegotiation) { json() }
        }
        try{
            val response = client.post(serverContentUrl){
                setBody(TextContent("p", ContentType.Text.Plain))}
            Log.d("COMMAND", "Sukces, wysyłam prośbę o zatrzymanie")
        }
        catch(e: Exception){
            Log.e("COMMAND", "Problem w wysyłaniu komunikatu o zatrzymanie")
        }
        finally {
            client.close()
        }

    }
    //funkcja wznawiająca odtwarzanie
    suspend fun sendResumeRequest(){
        val client = HttpClient(OkHttp) {
            install(ContentNegotiation) { json() }
        }
        try{
            val response = client.post(serverContentUrl){
                setBody(TextContent("r", ContentType.Text.Plain))}
            Log.d("COMMAND", "Sukces, wysyłam prośbę o wznowienie")
        }
        catch(e: Exception){
            Log.e("COMMAND", "Problem w wysyłaniu komunikatu o wznowienie")
        }
        finally {
            client.close()
        }

    }
    //funkcja wstrzymująca odtwarzanie
    suspend fun sendCalibrateRequest() {
        val client = HttpClient(OkHttp) {
            install(ContentNegotiation) { json() }
        }
        try {
            val response = client.post(serverContentUrl) {
                setBody(TextContent("c", ContentType.Text.Plain))
            }
            Log.d("COMMAND", "Sukces, wysyłam prośbę o kalibrację mikrofonu")
        } catch (e: Exception) {
            Log.e("COMMAND", "Problem w wysyłaniu requesta o kalibrację mikrofonu")
        } finally {
            client.close()
        }
    }
    fun deleteTrack(context: Context, track: Track) {
        if (track.isAsset) return

        val file = File(track.path)
        if (file.exists()) {
            file.delete()
        }

        loadAllTracks(context)
    }


}