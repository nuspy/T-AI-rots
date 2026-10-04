// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'privacy.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_StatoEtaAccount _$StatoEtaAccountFromJson(Map<String, dynamic> json) =>
    _StatoEtaAccount(
      anni: (json['anni'] as num?)?.toInt() ?? 16,
      paese: json['paese'] as String?,
      confermataIl: json['confermata_il'] as String?,
      daConfermare: json['da_confermare'] as bool? ?? false,
      sottoEta: json['sotto_eta'] as bool? ?? false,
    );

Map<String, dynamic> _$StatoEtaAccountToJson(_StatoEtaAccount instance) =>
    <String, dynamic>{
      'anni': instance.anni,
      'paese': ?instance.paese,
      'confermata_il': ?instance.confermataIl,
      'da_confermare': instance.daConfermare,
      'sotto_eta': instance.sottoEta,
    };

_StatoCancellazione _$StatoCancellazioneFromJson(Map<String, dynamic> json) =>
    _StatoCancellazione(
      richiestaIl: json['richiesta_il'] as String?,
      definitivaIl: json['definitiva_il'] as String?,
      eseguitaIl: json['eseguita_il'] as String?,
      annullabile: json['annullabile'] as bool? ?? false,
      giorniRipensamento: (json['giorni_ripensamento'] as num?)?.toInt() ?? 30,
      sessioniChiuse: json['sessioni_chiuse'] as bool?,
    );

Map<String, dynamic> _$StatoCancellazioneToJson(_StatoCancellazione instance) =>
    <String, dynamic>{
      'richiesta_il': ?instance.richiestaIl,
      'definitiva_il': ?instance.definitivaIl,
      'eseguita_il': ?instance.eseguitaIl,
      'annullabile': instance.annullabile,
      'giorni_ripensamento': instance.giorniRipensamento,
      'sessioni_chiuse': ?instance.sessioniChiuse,
    };

_StatoEsportazione _$StatoEsportazioneFromJson(Map<String, dynamic> json) =>
    _StatoEsportazione(
      ultimaIl: json['ultima_il'] as String?,
      prossimaDal: json['prossima_dal'] as String?,
    );

Map<String, dynamic> _$StatoEsportazioneToJson(_StatoEsportazione instance) =>
    <String, dynamic>{
      'ultima_il': ?instance.ultimaIl,
      'prossima_dal': ?instance.prossimaDal,
    };

_SceltaRegistrata _$SceltaRegistrataFromJson(Map<String, dynamic> json) =>
    _SceltaRegistrata(
      valore: json['valore'] as String,
      versione: json['versione'] as String? ?? '',
      il: json['il'] as String?,
    );

Map<String, dynamic> _$SceltaRegistrataToJson(_SceltaRegistrata instance) =>
    <String, dynamic>{
      'valore': instance.valore,
      'versione': instance.versione,
      'il': ?instance.il,
    };

_StatoPrivacy _$StatoPrivacyFromJson(Map<String, dynamic> json) =>
    _StatoPrivacy(
      eta: json['eta'] == null
          ? const StatoEtaAccount()
          : StatoEtaAccount.fromJson(json['eta'] as Map<String, dynamic>),
      esportazione: json['esportazione'] == null
          ? const StatoEsportazione()
          : StatoEsportazione.fromJson(
              json['esportazione'] as Map<String, dynamic>,
            ),
      consensi:
          (json['consensi'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(
              k,
              SceltaRegistrata.fromJson(e as Map<String, dynamic>),
            ),
          ) ??
          const <String, SceltaRegistrata>{},
      cancellazione: json['cancellazione'] == null
          ? const StatoCancellazione()
          : StatoCancellazione.fromJson(
              json['cancellazione'] as Map<String, dynamic>,
            ),
    );

Map<String, dynamic> _$StatoPrivacyToJson(_StatoPrivacy instance) =>
    <String, dynamic>{
      'eta': instance.eta.toJson(),
      'esportazione': instance.esportazione.toJson(),
      'consensi': instance.consensi.map((k, e) => MapEntry(k, e.toJson())),
      'cancellazione': instance.cancellazione.toJson(),
    };

_Dpo _$DpoFromJson(Map<String, dynamic> json) => _Dpo(
  nominato: json['nominato'] as bool? ?? false,
  contatto: json['contatto'] as String?,
);

Map<String, dynamic> _$DpoToJson(_Dpo instance) => <String, dynamic>{
  'nominato': instance.nominato,
  'contatto': ?instance.contatto,
};

_FornitoreAi _$FornitoreAiFromJson(Map<String, dynamic> json) => _FornitoreAi(
  nome: json['nome'] as String,
  paese: json['paese'] as String?,
  proprio: json['proprio'] as bool? ?? false,
);

Map<String, dynamic> _$FornitoreAiToJson(_FornitoreAi instance) =>
    <String, dynamic>{
      'nome': instance.nome,
      'paese': ?instance.paese,
      'proprio': instance.proprio,
    };

_Titolare _$TitolareFromJson(Map<String, dynamic> json) => _Titolare(
  nome: json['nome'] as String?,
  indirizzo: json['indirizzo'] as String?,
  codiceFiscale: json['codice_fiscale'] as String?,
  emailPrivacy: json['email_privacy'] as String?,
  dpo: json['dpo'] == null
      ? const Dpo()
      : Dpo.fromJson(json['dpo'] as Map<String, dynamic>),
  hosting: json['hosting'] as String?,
  fornitoriAi:
      (json['fornitori_ai'] as List<dynamic>?)
          ?.map((e) => FornitoreAi.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <FornitoreAi>[],
);

Map<String, dynamic> _$TitolareToJson(_Titolare instance) => <String, dynamic>{
  'nome': ?instance.nome,
  'indirizzo': ?instance.indirizzo,
  'codice_fiscale': ?instance.codiceFiscale,
  'email_privacy': ?instance.emailPrivacy,
  'dpo': instance.dpo.toJson(),
  'hosting': ?instance.hosting,
  'fornitori_ai': instance.fornitoriAi.map((e) => e.toJson()).toList(),
};
