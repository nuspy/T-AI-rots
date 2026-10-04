import Flutter
import StoreKit
import UIKit
import UserNotifications

// Fase 9 (scritto, non ancora compilato: niente build iOS finché l'app non è definitiva).
// - Le notifiche: il centro notifiche passa a FlutterAppDelegate, che le gira ai plugin (firebase_messaging per i
//   tocchi, flutter_local_notifications); il permesso NON si chiede qui ma dall'app, dopo un sì della persona.
// - Il canale `chat.tarots.app/store`: «Gestisci l'abbonamento» apre il foglio di Apple (`showManageSubscriptions`,
//   StoreKit 2), che il plugin in_app_purchase non espone. Se non riesce, l'app apre la pagina degli abbonamenti.
@main
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    UNUserNotificationCenter.current().delegate = self as UNUserNotificationCenterDelegate
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
    guard let registrar = engineBridge.pluginRegistry.registrar(forPlugin: "TarotsStore") else { return }
    let canale = FlutterMethodChannel(name: "chat.tarots.app/store", binaryMessenger: registrar.messenger())
    canale.setMethodCallHandler { chiamata, risposta in
      guard chiamata.method == "gestisciAbbonamenti" else {
        risposta(FlutterMethodNotImplemented)
        return
      }
      Task { @MainActor in
        let scene = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
        guard let scena = scene.first(where: { $0.activationState == .foregroundActive }) ?? scene.first else {
          risposta(false)
          return
        }
        do {
          try await AppStore.showManageSubscriptions(in: scena)
          risposta(true)
        } catch {
          risposta(false)
        }
      }
    }
  }
}
