package com.example.iot_mobile.data

import android.content.Context

data class Track(
    val name: String,
    val assetPath: String
)

fun loadTracksFromAssets(context: Context): List<Track> {
    val assetManager = context.assets
    val files = assetManager.list("audio_files") ?: emptyArray()

    return files
        .filter { it.endsWith(".mp3") }
        .map { fileName ->
            Track(
                name = fileName.removeSuffix(".mp3"),
                assetPath = "audio_files/$fileName"
            )
        }
}