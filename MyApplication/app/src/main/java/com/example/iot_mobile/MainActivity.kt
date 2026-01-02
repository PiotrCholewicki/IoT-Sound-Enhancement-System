package com.example.iot_mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.example.iot_mobile.ui.screen.MainScreen
import com.example.iot_mobile.ui.theme.Iot_mobileTheme
import com.example.iot_mobile.viewmodel.MusicPlayerViewModel
import androidx.activity.viewModels

class MainActivity : ComponentActivity() {

    private val musicPlayerViewModel: MusicPlayerViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        enableEdgeToEdge()

        setContent {
            Iot_mobileTheme {
                MainScreen(viewModel = musicPlayerViewModel)
            }
        }
    }
}

