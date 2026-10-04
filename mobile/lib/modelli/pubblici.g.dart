// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pubblici.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CartaOggi _$CartaOggiFromJson(Map<String, dynamic> json) => _CartaOggi(
  giorno: json['giorno'] as String,
  carta: Carta.fromJson(json['carta'] as Map<String, dynamic>),
  testo: json['testo'] as String,
);

Map<String, dynamic> _$CartaOggiToJson(_CartaOggi instance) =>
    <String, dynamic>{
      'giorno': instance.giorno,
      'carta': instance.carta.toJson(),
      'testo': instance.testo,
    };

_CartaDelGiorno _$CartaDelGiornoFromJson(Map<String, dynamic> json) =>
    _CartaDelGiorno(
      giorno: json['giorno'] as String,
      carta: Carta.fromJson(json['carta'] as Map<String, dynamic>),
      rovescio: json['rovescio'] as bool,
      testo: json['testo'] as String,
      serie: (json['serie'] as num).toInt(),
    );

Map<String, dynamic> _$CartaDelGiornoToJson(_CartaDelGiorno instance) =>
    <String, dynamic>{
      'giorno': instance.giorno,
      'carta': instance.carta.toJson(),
      'rovescio': instance.rovescio,
      'testo': instance.testo,
      'serie': instance.serie,
    };

_ImpostazioniPubbliche _$ImpostazioniPubblicheFromJson(
  Map<String, dynamic> json,
) => _ImpostazioniPubbliche(
  creditiIscrizione: (json['crediti_iscrizione'] as num).toInt(),
  creditiInvito: (json['crediti_invito'] as num).toInt(),
  commissioneReferralPercentuale:
      json['commissione_referral_percentuale'] as num? ?? 0,
);

Map<String, dynamic> _$ImpostazioniPubblicheToJson(
  _ImpostazioniPubbliche instance,
) => <String, dynamic>{
  'crediti_iscrizione': instance.creditiIscrizione,
  'crediti_invito': instance.creditiInvito,
  'commissione_referral_percentuale': instance.commissioneReferralPercentuale,
};

_EtaMinima _$EtaMinimaFromJson(Map<String, dynamic> json) => _EtaMinima(
  anni: (json['anni'] as num).toInt(),
  paese: json['paese'] as String?,
);

Map<String, dynamic> _$EtaMinimaToJson(_EtaMinima instance) =>
    <String, dynamic>{'anni': instance.anni, 'paese': ?instance.paese};

_ImmagineArticolo _$ImmagineArticoloFromJson(Map<String, dynamic> json) =>
    _ImmagineArticolo(
      url: json['url'] as String?,
      mini: json['mini'] as String?,
      alt: json['alt'] as String?,
      larghezza: (json['larghezza'] as num?)?.toInt(),
      altezza: (json['altezza'] as num?)?.toInt(),
    );

Map<String, dynamic> _$ImmagineArticoloToJson(_ImmagineArticolo instance) =>
    <String, dynamic>{
      'url': ?instance.url,
      'mini': ?instance.mini,
      'alt': ?instance.alt,
      'larghezza': ?instance.larghezza,
      'altezza': ?instance.altezza,
    };

_Voce _$VoceFromJson(Map<String, dynamic> json) =>
    _Voce(slug: json['slug'] as String, nome: json['nome'] as String);

Map<String, dynamic> _$VoceToJson(_Voce instance) => <String, dynamic>{
  'slug': instance.slug,
  'nome': instance.nome,
};

_AutoreBlog _$AutoreBlogFromJson(Map<String, dynamic> json) => _AutoreBlog(
  id: (json['id'] as num?)?.toInt(),
  nome: json['nome'] as String,
  avatar: json['avatar'] as String?,
);

Map<String, dynamic> _$AutoreBlogToJson(_AutoreBlog instance) =>
    <String, dynamic>{
      'id': ?instance.id,
      'nome': instance.nome,
      'avatar': ?instance.avatar,
    };

_ArticoloBreve _$ArticoloBreveFromJson(Map<String, dynamic> json) =>
    _ArticoloBreve(
      slug: json['slug'] as String,
      titolo: json['titolo'] as String,
      sottotitolo: json['sottotitolo'] as String?,
      estratto: json['estratto'] as String?,
      immagine: json['immagine'] == null
          ? null
          : ImmagineArticolo.fromJson(json['immagine'] as Map<String, dynamic>),
      sezione: json['sezione'] == null
          ? null
          : Voce.fromJson(json['sezione'] as Map<String, dynamic>),
      tempoLettura: (json['tempo_lettura'] as num?)?.toInt() ?? 1,
      tags:
          (json['tags'] as List<dynamic>?)
              ?.map((e) => Voce.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <Voce>[],
      lang: json['lang'] as String?,
      autore: json['autore'] == null
          ? null
          : AutoreBlog.fromJson(json['autore'] as Map<String, dynamic>),
      pubblicatoIl: json['pubblicato_il'] as String?,
      aggiornatoIl: json['aggiornato_il'] as String?,
      inEvidenza: json['in_evidenza'] as bool? ?? false,
    );

Map<String, dynamic> _$ArticoloBreveToJson(_ArticoloBreve instance) =>
    <String, dynamic>{
      'slug': instance.slug,
      'titolo': instance.titolo,
      'sottotitolo': ?instance.sottotitolo,
      'estratto': ?instance.estratto,
      'immagine': ?instance.immagine?.toJson(),
      'sezione': ?instance.sezione?.toJson(),
      'tempo_lettura': instance.tempoLettura,
      'tags': instance.tags.map((e) => e.toJson()).toList(),
      'lang': ?instance.lang,
      'autore': ?instance.autore?.toJson(),
      'pubblicato_il': ?instance.pubblicatoIl,
      'aggiornato_il': ?instance.aggiornatoIl,
      'in_evidenza': instance.inEvidenza,
    };

_Nove _$NoveFromJson(Map<String, dynamic> json) => _Nove(
  recenti:
      (json['recenti'] as List<dynamic>?)
          ?.map((e) => ArticoloBreve.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <ArticoloBreve>[],
  scelti:
      (json['scelti'] as List<dynamic>?)
          ?.map((e) => ArticoloBreve.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <ArticoloBreve>[],
);

Map<String, dynamic> _$NoveToJson(_Nove instance) => <String, dynamic>{
  'recenti': instance.recenti.map((e) => e.toJson()).toList(),
  'scelti': instance.scelti.map((e) => e.toJson()).toList(),
};
