/// La privacy dell'account (GDPR, Fase 1) e i dati del titolare per l'informativa (Fase 2c), come `StatoPrivacy` di
/// `frontend/lib/privacy.ts` e `TitolarePubblico` di `frontend/v2/pagine/privacy.tsx`.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'privacy.freezed.dart';
part 'privacy.g.dart';

/// L'età minima e la conferma.
@freezed
abstract class StatoEtaAccount with _$StatoEtaAccount {
  /// Lo stato.
  const factory StatoEtaAccount({
    @Default(16) int anni,
    String? paese,
    String? confermataIl,
    @Default(false) bool daConfermare,
    @Default(false) bool sottoEta,
  }) = _StatoEtaAccount;

  /// Dal JSON dell'API.
  factory StatoEtaAccount.fromJson(Map<String, dynamic> json) => _$StatoEtaAccountFromJson(json);
}

/// La cancellazione dell'account (30 giorni di ripensamento).
@freezed
abstract class StatoCancellazione with _$StatoCancellazione {
  /// Lo stato.
  const factory StatoCancellazione({
    String? richiestaIl,
    String? definitivaIl,
    String? eseguitaIl,
    @Default(false) bool annullabile,
    @Default(30) int giorniRipensamento,
    bool? sessioniChiuse,
  }) = _StatoCancellazione;

  /// Dal JSON dell'API.
  factory StatoCancellazione.fromJson(Map<String, dynamic> json) => _$StatoCancellazioneFromJson(json);
}

/// L'ultima esportazione e quando se ne può chiedere un'altra.
@freezed
abstract class StatoEsportazione with _$StatoEsportazione {
  /// `{ultima_il, prossima_dal}`.
  const factory StatoEsportazione({String? ultimaIl, String? prossimaDal}) = _StatoEsportazione;

  /// Dal JSON dell'API.
  factory StatoEsportazione.fromJson(Map<String, dynamic> json) => _$StatoEsportazioneFromJson(json);
}

/// Una scelta registrata.
@freezed
abstract class SceltaRegistrata with _$SceltaRegistrata {
  /// `{valore, versione, il}`.
  const factory SceltaRegistrata({required String valore, @Default('') String versione, String? il}) =
      _SceltaRegistrata;

  /// Dal JSON dell'API.
  factory SceltaRegistrata.fromJson(Map<String, dynamic> json) => _$SceltaRegistrataFromJson(json);
}

/// `GET /me/privacy`.
@freezed
abstract class StatoPrivacy with _$StatoPrivacy {
  /// Lo stato.
  const factory StatoPrivacy({
    @Default(StatoEtaAccount()) StatoEtaAccount eta,
    @Default(StatoEsportazione()) StatoEsportazione esportazione,
    @Default(<String, SceltaRegistrata>{}) Map<String, SceltaRegistrata> consensi,
    @Default(StatoCancellazione()) StatoCancellazione cancellazione,
  }) = _StatoPrivacy;

  /// Dal JSON dell'API.
  factory StatoPrivacy.fromJson(Map<String, dynamic> json) => _$StatoPrivacyFromJson(json);
}

/// Il responsabile della protezione dei dati.
@freezed
abstract class Dpo with _$Dpo {
  /// `{nominato, contatto}`.
  const factory Dpo({@Default(false) bool nominato, String? contatto}) = _Dpo;

  /// Dal JSON dell'API.
  factory Dpo.fromJson(Map<String, dynamic> json) => _$DpoFromJson(json);
}

/// Un fornitore dell'AI.
@freezed
abstract class FornitoreAi with _$FornitoreAi {
  /// `{nome, paese, proprio}`.
  const factory FornitoreAi({required String nome, String? paese, @Default(false) bool proprio}) = _FornitoreAi;

  /// Dal JSON dell'API.
  factory FornitoreAi.fromJson(Map<String, dynamic> json) => _$FornitoreAiFromJson(json);
}

/// `GET /privacy/titolare`: un campo vuoto è `null`.
@freezed
abstract class Titolare with _$Titolare {
  /// Il titolare.
  const factory Titolare({
    String? nome,
    String? indirizzo,
    String? codiceFiscale,
    String? emailPrivacy,
    @Default(Dpo()) Dpo dpo,
    String? hosting,
    @Default(<FornitoreAi>[]) List<FornitoreAi> fornitoriAi,
  }) = _Titolare;

  /// Dal JSON dell'API.
  factory Titolare.fromJson(Map<String, dynamic> json) => _$TitolareFromJson(json);
}
