import UserNotifications

// Fase 9: la Notification Service Extension «ImmagineNotifica» (scritta, NON ancora compilata né aggiunta al progetto:
// niente build iOS finché l'app non è definitiva; come aggiungerla è in mobile/LEGGIMI.md, «iOS: cosa resta»).
//
// Su iPhone una notifica con l'immagine grande arriva con `mutable-content: 1` (il backend lo mette quando c'è
// un'immagine, `notifiche/fcm.py`) e l'indirizzo dell'immagine in `fcm_options.image`. iOS dà a questa estensione
// qualche secondo per scaricarla e attaccarla alla notifica; se non ci riesce, la notifica esce senza immagine.
// Niente dipendenze (né Firebase né altro): solo URLSession.
class NotificationService: UNNotificationServiceExtension {
  private var consegna: ((UNNotificationContent) -> Void)?
  private var contenuto: UNMutableNotificationContent?

  override func didReceive(
    _ request: UNNotificationRequest,
    withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
  ) {
    consegna = contentHandler
    contenuto = request.content.mutableCopy() as? UNMutableNotificationContent
    guard let contenuto,
          let opzioni = request.content.userInfo["fcm_options"] as? [String: Any],
          let indirizzo = opzioni["image"] as? String,
          let url = URL(string: indirizzo),
          url.scheme == "https"
    else {
      contentHandler(request.content)
      return
    }
    URLSession.shared.downloadTask(with: url) { file, risposta, errore in
      defer { contentHandler(contenuto) }
      guard errore == nil, let file else { return }
      // L'allegato vuole un file con l'estensione giusta, in una cartella dell'estensione.
      let tipo = (risposta as? HTTPURLResponse)?.mimeType ?? "image/jpeg"
      let estensione = tipo.contains("png") ? "png" : tipo.contains("webp") ? "webp" : tipo.contains("gif") ? "gif" : "jpg"
      let destinazione = FileManager.default.temporaryDirectory
        .appendingPathComponent(UUID().uuidString)
        .appendingPathExtension(estensione)
      do {
        try FileManager.default.moveItem(at: file, to: destinazione)
        let allegato = try UNNotificationAttachment(identifier: "immagine", url: destinazione)
        contenuto.attachments = [allegato]
      } catch {
        // Senza immagine: la notifica esce lo stesso.
      }
    }.resume()
  }

  /// iOS sta per chiudere l'estensione: la notifica esce com'è.
  override func serviceExtensionTimeWillExpire() {
    if let consegna, let contenuto {
      consegna(contenuto)
    }
  }
}
