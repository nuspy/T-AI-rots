// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'voto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CampioneVoto _$CampioneVotoFromJson(Map<String, dynamic> json) =>
    _CampioneVoto(
      etichetta: json['etichetta'] as String?,
      url: json['url'] as String?,
      mini: json['mini'] as String?,
    );

Map<String, dynamic> _$CampioneVotoToJson(_CampioneVoto instance) =>
    <String, dynamic>{
      'etichetta': ?instance.etichetta,
      'url': ?instance.url,
      'mini': ?instance.mini,
    };

_CandidatoVoto _$CandidatoVotoFromJson(Map<String, dynamic> json) =>
    _CandidatoVoto(
      id: json['id'] as String,
      nome: json['nome'] as String,
      descrizione: json['descrizione'] as String?,
      campioni:
          (json['campioni'] as List<dynamic>?)
              ?.map((e) => CampioneVoto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <CampioneVoto>[],
      percentuale: json['percentuale'] as num?,
    );

Map<String, dynamic> _$CandidatoVotoToJson(_CandidatoVoto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nome': instance.nome,
      'descrizione': ?instance.descrizione,
      'campioni': instance.campioni.map((e) => e.toJson()).toList(),
      'percentuale': ?instance.percentuale,
    };

_VincitorePrecedente _$VincitorePrecedenteFromJson(Map<String, dynamic> json) =>
    _VincitorePrecedente(
      nome: json['nome'] as String,
      percentuale: json['percentuale'] as num,
    );

Map<String, dynamic> _$VincitorePrecedenteToJson(
  _VincitorePrecedente instance,
) => <String, dynamic>{
  'nome': instance.nome,
  'percentuale': instance.percentuale,
};

_Tornata _$TornataFromJson(Map<String, dynamic> json) =>
    _Tornata(id: json['id'] as String);

Map<String, dynamic> _$TornataToJson(_Tornata instance) => <String, dynamic>{
  'id': instance.id,
};

_StatoVoto _$StatoVotoFromJson(Map<String, dynamic> json) => _StatoVoto(
  tornata: json['tornata'] == null
      ? null
      : Tornata.fromJson(json['tornata'] as Map<String, dynamic>),
  mioVoto: json['mio_voto'] as String?,
  candidati:
      (json['candidati'] as List<dynamic>?)
          ?.map((e) => CandidatoVoto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <CandidatoVoto>[],
  vincitoriPrecedenti: (json['vincitori_precedenti'] as List<dynamic>?)
      ?.map((e) => VincitorePrecedente.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$StatoVotoToJson(_StatoVoto instance) =>
    <String, dynamic>{
      'tornata': ?instance.tornata?.toJson(),
      'mio_voto': ?instance.mioVoto,
      'candidati': instance.candidati.map((e) => e.toJson()).toList(),
      'vincitori_precedenti': ?instance.vincitoriPrecedenti
          ?.map((e) => e.toJson())
          .toList(),
    };

_CandidatoRisultato _$CandidatoRisultatoFromJson(Map<String, dynamic> json) =>
    _CandidatoRisultato(
      nome: json['nome'] as String,
      percentuale: json['percentuale'] as num,
      campioni:
          (json['campioni'] as List<dynamic>?)
              ?.map((e) => CampioneVoto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <CampioneVoto>[],
    );

Map<String, dynamic> _$CandidatoRisultatoToJson(_CandidatoRisultato instance) =>
    <String, dynamic>{
      'nome': instance.nome,
      'percentuale': instance.percentuale,
      'campioni': instance.campioni.map((e) => e.toJson()).toList(),
    };

_RisultatoRecente _$RisultatoRecenteFromJson(Map<String, dynamic> json) =>
    _RisultatoRecente(
      chiusaIl: json['chiusa_il'] as String?,
      candidati:
          (json['candidati'] as List<dynamic>?)
              ?.map(
                (e) => CandidatoRisultato.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const <CandidatoRisultato>[],
    );

Map<String, dynamic> _$RisultatoRecenteToJson(_RisultatoRecente instance) =>
    <String, dynamic>{
      'chiusa_il': ?instance.chiusaIl,
      'candidati': instance.candidati.map((e) => e.toJson()).toList(),
    };

_VotoHome _$VotoHomeFromJson(Map<String, dynamic> json) => _VotoHome(
  votoAperto: json['voto_aperto'] as bool? ?? false,
  risultatoRecente: json['risultato_recente'] == null
      ? null
      : RisultatoRecente.fromJson(
          json['risultato_recente'] as Map<String, dynamic>,
        ),
);

Map<String, dynamic> _$VotoHomeToJson(_VotoHome instance) => <String, dynamic>{
  'voto_aperto': instance.votoAperto,
  'risultato_recente': ?instance.risultatoRecente?.toJson(),
};
