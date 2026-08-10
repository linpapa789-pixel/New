package com.example

import android.Manifest
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.ui.Modifier
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import com.example.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {
    private val viewModel: DiagnosticViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        val requestPermissionLauncher = registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            val allGranted = permissions.entries.all { it.value }
            if (!allGranted) {
                Toast.makeText(
                    this,
                    "Hardware များနှင့် ချိတ်ဆက်ရန် Bluetooth နှင့် Location ခွင့်ပြုချက်များ လိုအပ်ပါသည်။",
                    Toast.LENGTH_LONG
                ).show()
            }
        }

        val requiredPermissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
            )
        } else {
            arrayOf(
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN,
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
            )
        }

        // ✅ DiagnosticScreen လိုအပ်တဲ့ onRequestBluetoothPermission ထည့်ပေးလိုက်ပြီ
        setContent {
            val uiState by viewModel.uiState.collectAsState()
            MyApplicationTheme(darkTheme = uiState.isDarkTheme) {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    DiagnosticScreen(
                        viewModel = viewModel,
                        modifier = Modifier.padding(innerPadding),
                        onRequestBluetoothPermission = {
                            requestPermissionLauncher.launch(requiredPermissions)
                        }
                    )
                }
            }
        }
    }
}
