/// Gli errori dell'API, come `ErroreApi` e `leggi()` di `frontend/lib/api.ts`: il motivo che il server manda, quando
/// c'è (per 402 e 409 è proprio ciò che serve a chi usa l'app: «non hai crediti», «le carte si rivelano in ordine»),
/// altrimenti un messaggio generico. Un 401 è sempre «la sessione è finita».
library;

import '../l10n/generato/app_localizations.dart';

/// Un errore dell'API, o della rete (stato 0).
class ErroreApi implements Exception {
  /// Uno stato HTTP con il motivo del server (`detail` o `detail.messaggio`) e il dettaglio intero.
  const ErroreApi(this.stato, {this.motivo, this.dettaglio});

  /// Dal corpo JSON di una risposta d'errore.
  factory ErroreApi.daCorpo(int stato, Object? corpo) {
    final dettaglio = corpo is Map ? corpo['detail'] : null;
    String? motivo;
    if (dettaglio is String) {
      motivo = dettaglio;
    } else if (dettaglio is Map && dettaglio['messaggio'] is String) {
      motivo = dettaglio['messaggio'] as String;
    }
    return ErroreApi(stato, motivo: motivo, dettaglio: dettaglio);
  }

  /// Lo stato HTTP; 0 se la richiesta non è arrivata (rete assente, server spento).
  final int stato;

  /// Il motivo scritto dal server, già nella lingua della richiesta.
  final String? motivo;

  /// `detail` della risposta (stringa o oggetto con `motivo`, `anni`, …).
  final Object? dettaglio;

  /// Il codice del motivo, quando il dettaglio è un oggetto (`eta_da_confermare`, `account_in_cancellazione`…).
  String? get codice {
    final d = dettaglio;
    return d is Map && d['motivo'] is String ? d['motivo'] as String : null;
  }

  /// Il messaggio da mostrare.
  String messaggio(AppLocalizations t) {
    if (stato == 401) return t.comune_err_sessione;
    return motivo ?? (stato == 0 ? t.comune_err_generico : t.comune_err_richiesta);
  }

  @override
  String toString() => 'ErroreApi($stato${motivo == null ? '' : ': $motivo'})';
}
