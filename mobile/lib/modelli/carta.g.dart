// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'carta.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_LetteraEbraica _$LetteraEbraicaFromJson(Map<String, dynamic> json) =>
    _LetteraEbraica(
      nome: json['nome'] as String,
      glifo: json['glifo'] as String,
      valore: (json['valore'] as num).toInt(),
    );

Map<String, dynamic> _$LetteraEbraicaToJson(_LetteraEbraica instance) =>
    <String, dynamic>{
      'nome': instance.nome,
      'glifo': instance.glifo,
      'valore': instance.valore,
    };

_Carta _$CartaFromJson(Map<String, dynamic> json) => _Carta(
  id: json['id'] as String,
  arcano: json['arcano'] as String,
  numero: (json['numero'] as num?)?.toInt(),
  numeroRomano: json['numero_romano'] as String?,
  seme: json['seme'] as String?,
  rango: json['rango'] as String?,
  nomeThoth: json['nome_thoth'] as String,
  titoloThoth: json['titolo_thoth'] as String?,
  nomeIt: json['nome_it'] as String,
  nomi:
      (json['nomi'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ) ??
      const <String, String>{},
  lang: json['lang'] as String?,
  nome: json['nome'] as String?,
  slug: json['slug'] as String?,
  slugs:
      (json['slugs'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ) ??
      const <String, String>{},
  elementoLabel: json['elemento_label'] as String?,
  semeLabel: json['seme_label'] as String?,
  rangoLabel: json['rango_label'] as String?,
  arcanoLabel: json['arcano_label'] as String?,
  letteraEbraica: json['lettera_ebraica'] == null
      ? null
      : LetteraEbraica.fromJson(
          json['lettera_ebraica'] as Map<String, dynamic>,
        ),
  elemento: json['elemento'] as String,
  astrologia: json['astrologia'] as String,
  paroleChiave:
      (json['parole_chiave'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const <String>[],
  colori:
      (json['colori'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const <String>[],
  percorso: (json['percorso'] as num?)?.toInt(),
  collega: (json['collega'] as List<dynamic>?)
      ?.map((e) => e as String)
      .toList(),
  sefira: json['sefira'] as String?,
  significati: (json['significati'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  dritto: json['dritto'] as String?,
  rovescio: json['rovescio'] as String?,
  ambiti: (json['ambiti'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  notaCrowley: json['nota_crowley'] as String?,
);

Map<String, dynamic> _$CartaToJson(_Carta instance) => <String, dynamic>{
  'id': instance.id,
  'arcano': instance.arcano,
  'numero': ?instance.numero,
  'numero_romano': ?instance.numeroRomano,
  'seme': ?instance.seme,
  'rango': ?instance.rango,
  'nome_thoth': instance.nomeThoth,
  'titolo_thoth': ?instance.titoloThoth,
  'nome_it': instance.nomeIt,
  'nomi': instance.nomi,
  'lang': ?instance.lang,
  'nome': ?instance.nome,
  'slug': ?instance.slug,
  'slugs': instance.slugs,
  'elemento_label': ?instance.elementoLabel,
  'seme_label': ?instance.semeLabel,
  'rango_label': ?instance.rangoLabel,
  'arcano_label': ?instance.arcanoLabel,
  'lettera_ebraica': ?instance.letteraEbraica?.toJson(),
  'elemento': instance.elemento,
  'astrologia': instance.astrologia,
  'parole_chiave': instance.paroleChiave,
  'colori': instance.colori,
  'percorso': ?instance.percorso,
  'collega': ?instance.collega,
  'sefira': ?instance.sefira,
  'significati': ?instance.significati,
  'dritto': ?instance.dritto,
  'rovescio': ?instance.rovescio,
  'ambiti': ?instance.ambiti,
  'nota_crowley': ?instance.notaCrowley,
};

_Posizione _$PosizioneFromJson(Map<String, dynamic> json) => _Posizione(
  n: (json['n'] as num).toInt(),
  nome: json['nome'] as String,
  nomeEn: json['nome_en'] as String,
  nomi: (json['nomi'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  soggetto: json['soggetto'] as String?,
  significato: json['significato'] as String,
  domanda: json['domanda'] as String,
  x: (json['x'] as num).toDouble(),
  y: (json['y'] as num).toDouble(),
  rotazione: (json['rotazione'] as num).toDouble(),
  calcolata: json['calcolata'] as bool,
);

Map<String, dynamic> _$PosizioneToJson(_Posizione instance) =>
    <String, dynamic>{
      'n': instance.n,
      'nome': instance.nome,
      'nome_en': instance.nomeEn,
      'nomi': ?instance.nomi,
      'soggetto': ?instance.soggetto,
      'significato': instance.significato,
      'domanda': instance.domanda,
      'x': instance.x,
      'y': instance.y,
      'rotazione': instance.rotazione,
      'calcolata': instance.calcolata,
    };

_Stesa _$StesaFromJson(Map<String, dynamic> json) => _Stesa(
  id: json['id'] as String,
  nome: json['nome'] as String,
  nomeEn: json['nome_en'] as String,
  nomi: (json['nomi'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  lang: json['lang'] as String?,
  slug: json['slug'] as String?,
  slugs: (json['slugs'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  mazzoLabel: json['mazzo_label'] as String?,
  categoriaLabel: json['categoria_label'] as String?,
  stileLabel: json['stile_label'] as String?,
  categoria: json['categoria'] as String,
  temi: (json['temi'] as List<dynamic>?)?.map((e) => e as String).toList(),
  stile: json['stile'] as String?,
  larghezza: (json['larghezza'] as num?)?.toDouble(),
  larghezzaStretto: (json['larghezza_stretto'] as num?)?.toDouble(),
  forma: json['forma'] as String,
  mazzo: json['mazzo'] as String,
  carteDaScegliere: (json['carte_da_scegliere'] as num).toInt(),
  origine: json['origine'] as String,
  descrizione: json['descrizione'] as String,
  posizioni: (json['posizioni'] as List<dynamic>)
      .map((e) => Posizione.fromJson(e as Map<String, dynamic>))
      .toList(),
  regole:
      (json['regole'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const <String>[],
  coppie:
      (json['coppie'] as List<dynamic>?)
          ?.map((e) => e as List<dynamic>)
          .toList() ??
      const <List<Object?>>[],
  sintesiWirth: json['sintesi_wirth'] as bool? ?? false,
);

Map<String, dynamic> _$StesaToJson(_Stesa instance) => <String, dynamic>{
  'id': instance.id,
  'nome': instance.nome,
  'nome_en': instance.nomeEn,
  'nomi': ?instance.nomi,
  'lang': ?instance.lang,
  'slug': ?instance.slug,
  'slugs': ?instance.slugs,
  'mazzo_label': ?instance.mazzoLabel,
  'categoria_label': ?instance.categoriaLabel,
  'stile_label': ?instance.stileLabel,
  'categoria': instance.categoria,
  'temi': ?instance.temi,
  'stile': ?instance.stile,
  'larghezza': ?instance.larghezza,
  'larghezza_stretto': ?instance.larghezzaStretto,
  'forma': instance.forma,
  'mazzo': instance.mazzo,
  'carte_da_scegliere': instance.carteDaScegliere,
  'origine': instance.origine,
  'descrizione': instance.descrizione,
  'posizioni': instance.posizioni.map((e) => e.toJson()).toList(),
  'regole': instance.regole,
  'coppie': instance.coppie,
  'sintesi_wirth': instance.sintesiWirth,
};
