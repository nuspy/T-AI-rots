// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notifiche.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DispositivoNotifica _$DispositivoNotificaFromJson(Map<String, dynamic> json) =>
    _DispositivoNotifica(
      id: (json['id'] as num).toInt(),
      canale: json['canale'] as String,
      piattaforma: json['piattaforma'] as String,
      attivo: json['attivo'] as bool? ?? true,
      lingua: json['lingua'] as String?,
      versioneApp: json['versione_app'] as String?,
    );

Map<String, dynamic> _$DispositivoNotificaToJson(
  _DispositivoNotifica instance,
) => <String, dynamic>{
  'id': instance.id,
  'canale': instance.canale,
  'piattaforma': instance.piattaforma,
  'attivo': instance.attivo,
  'lingua': ?instance.lingua,
  'versione_app': ?instance.versioneApp,
};

_PreferenzeNotifica _$PreferenzeNotificaFromJson(Map<String, dynamic> json) =>
    _PreferenzeNotifica(
      cartaGiorno: json['carta_giorno'] as bool? ?? true,
      oraCarta: json['ora_carta'] as String?,
      silenzio: json['silenzio'] as bool? ?? false,
      silenzioDal: json['silenzio_dal'] as String?,
      silenzioAl: json['silenzio_al'] as String?,
      promemoria: json['promemoria'] as bool? ?? true,
      tettoPromozioniSettimana:
          (json['tetto_promozioni_settimana'] as num?)?.toInt() ?? 2,
      tettoMassimo: (json['tetto_massimo'] as num?)?.toInt() ?? 2,
      promozioni: json['promozioni'] as bool? ?? false,
      fusoOrario: json['fuso_orario'] as String?,
      dispositivi:
          (json['dispositivi'] as List<dynamic>?)
              ?.map(
                (e) => DispositivoNotifica.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const <DispositivoNotifica>[],
    );

Map<String, dynamic> _$PreferenzeNotificaToJson(_PreferenzeNotifica instance) =>
    <String, dynamic>{
      'carta_giorno': instance.cartaGiorno,
      'ora_carta': ?instance.oraCarta,
      'silenzio': instance.silenzio,
      'silenzio_dal': ?instance.silenzioDal,
      'silenzio_al': ?instance.silenzioAl,
      'promemoria': instance.promemoria,
      'tetto_promozioni_settimana': instance.tettoPromozioniSettimana,
      'tetto_massimo': instance.tettoMassimo,
      'promozioni': instance.promozioni,
      'fuso_orario': ?instance.fusoOrario,
      'dispositivi': instance.dispositivi.map((e) => e.toJson()).toList(),
    };
