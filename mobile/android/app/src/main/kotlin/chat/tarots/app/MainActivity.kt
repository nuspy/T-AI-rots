package chat.tarots.app

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

/**
 * L'attività dell'app. Fase 9: il canale `chat.tarots.app/impostazioni` apre le impostazioni delle notifiche
 * dell'app (quando la persona le ha negate e vuole riaccenderle dal profilo): Android non ha un indirizzo per farlo.
 */
class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "chat.tarots.app/impostazioni")
            .setMethodCallHandler { chiamata, risposta ->
                if (chiamata.method != "notifiche") {
                    risposta.notImplemented()
                    return@setMethodCallHandler
                }
                val intento = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE, packageName)
                } else {
                    Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.fromParts("package", packageName, null))
                }
                try {
                    startActivity(intento)
                    risposta.success(true)
                } catch (e: Exception) {
                    risposta.success(false)
                }
            }
    }
}
