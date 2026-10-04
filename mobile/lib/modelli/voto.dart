/// «Vota il prossimo mazzo» (`GET /voto/mazzi`, `GET /voto/home`), come `StatoVoto` e `VotoHome` di
/// `frontend/lib/api.ts`.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'voto.freezed.dart';
part 'voto.g.dart';

/// Un'immagine d'esempio di un candidato (percorsi relativi dell'API).
@freezed
abstract class CampioneVoto with _$CampioneVoto {
  /// `{etichetta, url, mini}`.
  const factory CampioneVoto({String? etichetta, String? url, String? mini}) = _CampioneVoto;

  /// Dal JSON dell'API.
  factory CampioneVoto.fromJson(Map<String, dynamic> json) => _$CampioneVotoFromJson(json);
}

/// Un mazzo candidato.
@freezed
abstract class CandidatoVoto with _$CandidatoVoto {
  /// Un candidato.
  const factory CandidatoVoto({
    required String id,
    required String nome,
    String? descrizione,
    @Default(<CampioneVoto>[]) List<CampioneVoto> campioni,

    /// `null` finché non si è votato in questa tornata: le percentuali non si mostrano prima.
    num? percentuale,
  }) = _CandidatoVoto;

  /// Dal JSON dell'API.
  factory CandidatoVoto.fromJson(Map<String, dynamic> json) => _$CandidatoVotoFromJson(json);
}

/// Il vincitore di una tornata passata.
@freezed
abstract class VincitorePrecedente with _$VincitorePrecedente {
  /// `{nome, percentuale}`.
  const factory VincitorePrecedente({required String nome, required num percentuale}) = _VincitorePrecedente;

  /// Dal JSON dell'API.
  factory VincitorePrecedente.fromJson(Map<String, dynamic> json) => _$VincitorePrecedenteFromJson(json);
}

/// L'identificativo di una tornata.
@freezed
abstract class Tornata with _$Tornata {
  /// `{id}`.
  const factory Tornata({required String id}) = _Tornata;

  /// Dal JSON dell'API.
  factory Tornata.fromJson(Map<String, dynamic> json) => _$TornataFromJson(json);
}

/// `GET /voto/mazzi`.
@freezed
abstract class StatoVoto with _$StatoVoto {
  /// Lo stato del voto.
  const factory StatoVoto({
    Tornata? tornata,
    String? mioVoto,
    @Default(<CandidatoVoto>[]) List<CandidatoVoto> candidati,
    List<VincitorePrecedente>? vincitoriPrecedenti,
  }) = _StatoVoto;

  /// Dal JSON dell'API.
  factory StatoVoto.fromJson(Map<String, dynamic> json) => _$StatoVotoFromJson(json);
}

/// Un candidato dell'ultima tornata chiusa.
@freezed
abstract class CandidatoRisultato with _$CandidatoRisultato {
  /// Un candidato.
  const factory CandidatoRisultato({
    required String nome,
    required num percentuale,
    @Default(<CampioneVoto>[]) List<CampioneVoto> campioni,
  }) = _CandidatoRisultato;

  /// Dal JSON dell'API.
  factory CandidatoRisultato.fromJson(Map<String, dynamic> json) => _$CandidatoRisultatoFromJson(json);
}

/// L'ultima tornata chiusa.
@freezed
abstract class RisultatoRecente with _$RisultatoRecente {
  /// Il risultato.
  const factory RisultatoRecente({String? chiusaIl, @Default(<CandidatoRisultato>[]) List<CandidatoRisultato> candidati}) =
      _RisultatoRecente;

  /// Dal JSON dell'API.
  factory RisultatoRecente.fromJson(Map<String, dynamic> json) => _$RisultatoRecenteFromJson(json);
}

/// `GET /voto/home`.
@freezed
abstract class VotoHome with _$VotoHome {
  /// Il riepilogo.
  const factory VotoHome({@Default(false) bool votoAperto, RisultatoRecente? risultatoRecente}) = _VotoHome;

  /// Dal JSON dell'API.
  factory VotoHome.fromJson(Map<String, dynamic> json) => _$VotoHomeFromJson(json);
}
