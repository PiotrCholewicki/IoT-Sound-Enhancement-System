    package com.example.iot_mobile.data

    import android.content.Context

    data class Track(
        val name: String,
        val path: String,
        val isAsset: Boolean
    )

    fun loadTracksFromAssets(context: Context): List<Track> {
        val files = context.assets.list("audio_files") ?: emptyArray()

        return files
            .filter { it.endsWith(".mp3") || it.endsWith(".wav") }
            .map { fileName ->
                Track(
                    name = fileName.substringBeforeLast("."),
                    path = "audio_files/$fileName",
                    isAsset = true
                )
            }
    }
    fun loadTracksFromLocalFiles(context: Context): List<Track> {
        return context.filesDir
            .listFiles { file -> file.extension.lowercase() in listOf("mp3", "wav") }
            ?.map { file ->
                Track(
                    name = file.nameWithoutExtension,
                    path = file.absolutePath,
                    isAsset = false
                )
            } ?: emptyList()
    }

