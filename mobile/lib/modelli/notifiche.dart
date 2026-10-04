/// Le notifiche (Fase 9, con l'API della Fase 5: `backend/tarot_core/api/routers/notifiche.py`): le preferenze di
/// `GET/PUT /me/preferenze-notifica` e i dispositivi registrati, come `PreferenzeNotifiche` di
/// `frontend/v2/lib/notifiche.ts`.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'notifiche.freezed.dart';
part 'notifiche.g.dart';

/// Un dispositivo che riceve le notifiche (un telefono con l'app, un browser).
@freezed
abstract class DispositivoNotifica with _$DispositivoNotifica {
  /// Un dispositivo.
  const factory DispositivoNotifica({
    required int id,

    /// `fcm` (le app) o `webpush` (il sito).
    required String canale,

    /// `android`, `ios` o `web`.
    required String piattaforma,
    @Default(true) bool attivo,
    String? lingua,
    String? versioneApp,
  }) = _DispositivoNotifica;

  /// Dal JSON dell'API.
  factory DispositivoNotifica.fromJson(Map<String, dynamic> json) => _$DispositivoNotificaFromJson(json);
}

/// Le preferenze delle notifiche di chi è entrato: le stesse del sito.
@freezed
abstract class PreferenzeNotifica with _$PreferenzeNotifica {
  /// Le preferenze.
  const factory PreferenzeNotifica({
    @Default(true) bool cartaGiorno,

    /// `HH:MM`, all'ora locale.
    String? oraCarta,
    @Default(false) bool silenzio,
    String? silenzioDal,
    String? silenzioAl,
    @Default(true) bool promemoria,
    @Default(2) int tettoPromozioniSettimana,
    @Default(2) int tettoMassimo,

    /// Il consenso `marketing` («Promozioni» nella privacy): lo stesso interruttore.
    @Default(false) bool promozioni,
    String? fusoOrario,
    @Default(<DispositivoNotifica>[]) List<DispositivoNotifica> dispositivi,
  }) = _PreferenzeNotifica;

  /// Dal JSON dell'API.
  factory PreferenzeNotifica.fromJson(Map<String, dynamic> json) => _$PreferenzeNotificaFromJson(json);
}
