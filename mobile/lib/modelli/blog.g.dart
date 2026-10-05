// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'blog.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DomandaFaq _$DomandaFaqFromJson(Map<String, dynamic> json) => _DomandaFaq(
  domanda: json['domanda'] as String,
  risposta: json['risposta'] as String,
);

Map<String, dynamic> _$DomandaFaqToJson(_DomandaFaq instance) =>
    <String, dynamic>{
      'domanda': instance.domanda,
      'risposta': instance.risposta,
    };

_CartaCitata _$CartaCitataFromJson(Map<String, dynamic> json) => _CartaCitata(
  id: json['id'] as String,
  nomeIt: json['nome_it'] as String? ?? '',
  nome: json['nome'] as String,
  slug: json['slug'] as String,
  slugs:
      (json['slugs'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ) ??
      const <String, String>{},
);

Map<String, dynamic> _$CartaCitataToJson(_CartaCitata instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nome_it': instance.nomeIt,
      'nome': instance.nome,
      'slug': instance.slug,
      'slugs': instance.slugs,
    };

_StesaCitata _$StesaCitataFromJson(Map<String, dynamic> json) => _StesaCitata(
  id: json['id'] as String,
  nome: json['nome'] as String,
  slug: json['slug'] as String,
  slugs:
      (json['slugs'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ) ??
      const <String, String>{},
);

Map<String, dynamic> _$StesaCitataToJson(_StesaCitata instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nome': instance.nome,
      'slug': instance.slug,
      'slugs': instance.slugs,
    };

_Collegamenti _$CollegamentiFromJson(Map<String, dynamic> json) =>
    _Collegamenti(
      carte:
          (json['carte'] as List<dynamic>?)
              ?.map((e) => CartaCitata.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <CartaCitata>[],
      stese:
          (json['stese'] as List<dynamic>?)
              ?.map((e) => StesaCitata.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <StesaCitata>[],
      articoli:
          (json['articoli'] as List<dynamic>?)
              ?.map((e) => ArticoloBreve.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <ArticoloBreve>[],
    );

Map<String, dynamic> _$CollegamentiToJson(_Collegamenti instance) =>
    <String, dynamic>{
      'carte': instance.carte.map((e) => e.toJson()).toList(),
      'stese': instance.stese.map((e) => e.toJson()).toList(),
      'articoli': instance.articoli.map((e) => e.toJson()).toList(),
    };

_Gemella _$GemellaFromJson(Map<String, dynamic> json) =>
    _Gemella(lang: json['lang'] as String, slug: json['slug'] as String);

Map<String, dynamic> _$GemellaToJson(_Gemella instance) => <String, dynamic>{
  'lang': instance.lang,
  'slug': instance.slug,
};

_ArticoloBlog _$ArticoloBlogFromJson(Map<String, dynamic> json) =>
    _ArticoloBlog(
      slug: json['slug'] as String,
      titolo: json['titolo'] as String,
      sottotitolo: json['sottotitolo'] as String?,
      estratto: json['estratto'] as String? ?? '',
      immagine: json['immagine'] == null
          ? null
          : ImmagineArticolo.fromJson(json['immagine'] as Map<String, dynamic>),
      sezione: json['sezione'] == null
          ? null
          : Voce.fromJson(json['sezione'] as Map<String, dynamic>),
      autore: json['autore'] == null
          ? null
          : AutoreBlog.fromJson(json['autore'] as Map<String, dynamic>),
      pubblicatoIl: json['pubblicato_il'] as String?,
      aggiornatoIl: json['aggiornato_il'] as String?,
      tempoLettura: (json['tempo_lettura'] as num?)?.toInt() ?? 1,
      tags:
          (json['tags'] as List<dynamic>?)
              ?.map((e) => Voce.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <Voce>[],
      lang: json['lang'] as String? ?? 'en',
      inEvidenza: json['in_evidenza'] as bool? ?? false,
      testo: json['testo'] as String? ?? '',
      seoTitolo: json['seo_titolo'] as String?,
      seoDescrizione: json['seo_descrizione'] as String? ?? '',
      faq:
          (json['faq'] as List<dynamic>?)
              ?.map((e) => DomandaFaq.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <DomandaFaq>[],
      commentiAperti: json['commenti_aperti'] as bool? ?? false,
      briciole:
          (json['briciole'] as List<dynamic>?)
              ?.map((e) => Voce.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <Voce>[],
      collegamenti: json['collegamenti'] == null
          ? const Collegamenti()
          : Collegamenti.fromJson(json['collegamenti'] as Map<String, dynamic>),
      correlati:
          (json['correlati'] as List<dynamic>?)
              ?.map((e) => ArticoloBreve.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <ArticoloBreve>[],
      precedente: json['precedente'] == null
          ? null
          : ArticoloBreve.fromJson(json['precedente'] as Map<String, dynamic>),
      successivo: json['successivo'] == null
          ? null
          : ArticoloBreve.fromJson(json['successivo'] as Map<String, dynamic>),
      gemellaLingua: json['gemella_lingua'] == null
          ? null
          : Gemella.fromJson(json['gemella_lingua'] as Map<String, dynamic>),
      soggetto: json['soggetto'] == null
          ? null
          : SoggettoArticolo.fromJson(json['soggetto'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$ArticoloBlogToJson(_ArticoloBlog instance) =>
    <String, dynamic>{
      'slug': instance.slug,
      'titolo': instance.titolo,
      'sottotitolo': ?instance.sottotitolo,
      'estratto': instance.estratto,
      'immagine': ?instance.immagine?.toJson(),
      'sezione': ?instance.sezione?.toJson(),
      'autore': ?instance.autore?.toJson(),
      'pubblicato_il': ?instance.pubblicatoIl,
      'aggiornato_il': ?instance.aggiornatoIl,
      'tempo_lettura': instance.tempoLettura,
      'tags': instance.tags.map((e) => e.toJson()).toList(),
      'lang': instance.lang,
      'in_evidenza': instance.inEvidenza,
      'testo': instance.testo,
      'seo_titolo': ?instance.seoTitolo,
      'seo_descrizione': instance.seoDescrizione,
      'faq': instance.faq.map((e) => e.toJson()).toList(),
      'commenti_aperti': instance.commentiAperti,
      'briciole': instance.briciole.map((e) => e.toJson()).toList(),
      'collegamenti': instance.collegamenti.toJson(),
      'correlati': instance.correlati.map((e) => e.toJson()).toList(),
      'precedente': ?instance.precedente?.toJson(),
      'successivo': ?instance.successivo?.toJson(),
      'gemella_lingua': ?instance.gemellaLingua?.toJson(),
      'soggetto': ?instance.soggetto?.toJson(),
    };

_ImmagineBlog _$ImmagineBlogFromJson(Map<String, dynamic> json) =>
    _ImmagineBlog(
      url: json['url'] as String?,
      mini: json['mini'] as String?,
      alt: json['alt'] as String?,
    );

Map<String, dynamic> _$ImmagineBlogToJson(_ImmagineBlog instance) =>
    <String, dynamic>{
      'url': ?instance.url,
      'mini': ?instance.mini,
      'alt': ?instance.alt,
    };

_NodoSezione _$NodoSezioneFromJson(Map<String, dynamic> json) => _NodoSezione(
  id: (json['id'] as num).toInt(),
  slug: json['slug'] as String,
  nome: json['nome'] as String,
  descrizione: json['descrizione'] as String?,
  tipo: json['tipo'] as String? ?? 'articoli',
  filtro: (json['filtro'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  immagine: const ImmagineBlogJson().fromJson(json['immagine']),
  nArticoli: (json['n_articoli'] as num?)?.toInt() ?? 0,
  nArticoliDiretti: (json['n_articoli_diretti'] as num?)?.toInt(),
  nElementi: (json['n_elementi'] as num?)?.toInt(),
  nCarte: (json['n_carte'] as num?)?.toInt() ?? 0,
  nStese: (json['n_stese'] as num?)?.toInt() ?? 0,
  figli:
      (json['figli'] as List<dynamic>?)
          ?.map((e) => NodoSezione.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <NodoSezione>[],
  articoli:
      (json['articoli'] as List<dynamic>?)
          ?.map((e) => ArticoloBreve.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <ArticoloBreve>[],
);

Map<String, dynamic> _$NodoSezioneToJson(_NodoSezione instance) =>
    <String, dynamic>{
      'id': instance.id,
      'slug': instance.slug,
      'nome': instance.nome,
      'descrizione': ?instance.descrizione,
      'tipo': instance.tipo,
      'filtro': ?instance.filtro,
      'immagine': ?const ImmagineBlogJson().toJson(instance.immagine),
      'n_articoli': instance.nArticoli,
      'n_articoli_diretti': ?instance.nArticoliDiretti,
      'n_elementi': ?instance.nElementi,
      'n_carte': instance.nCarte,
      'n_stese': instance.nStese,
      'figli': instance.figli.map((e) => e.toJson()).toList(),
      'articoli': instance.articoli.map((e) => e.toJson()).toList(),
    };

_DettaglioSezione _$DettaglioSezioneFromJson(Map<String, dynamic> json) =>
    _DettaglioSezione(
      id: (json['id'] as num).toInt(),
      slug: json['slug'] as String,
      nome: json['nome'] as String,
      descrizione: json['descrizione'] as String?,
      tipo: json['tipo'] as String? ?? 'articoli',
      filtro: (json['filtro'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ),
      immagine: const ImmagineBlogJson().fromJson(json['immagine']),
      nArticoli: (json['n_articoli'] as num?)?.toInt() ?? 0,
      nArticoliDiretti: (json['n_articoli_diretti'] as num?)?.toInt(),
      nElementi: (json['n_elementi'] as num?)?.toInt(),
      nCarte: (json['n_carte'] as num?)?.toInt() ?? 0,
      nStese: (json['n_stese'] as num?)?.toInt() ?? 0,
      figli:
          (json['figli'] as List<dynamic>?)
              ?.map((e) => NodoSezione.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <NodoSezione>[],
      seoTitolo: json['seo_titolo'] as String?,
      seoDescrizione: json['seo_descrizione'] as String?,
      briciole:
          (json['briciole'] as List<dynamic>?)
              ?.map((e) => Voce.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <Voce>[],
      elementi:
          (json['elementi'] as List<dynamic>?)
              ?.map((e) => e as Map<String, dynamic>)
              .toList() ??
          const <Map<String, Object?>>[],
    );

Map<String, dynamic> _$DettaglioSezioneToJson(_DettaglioSezione instance) =>
    <String, dynamic>{
      'id': instance.id,
      'slug': instance.slug,
      'nome': instance.nome,
      'descrizione': ?instance.descrizione,
      'tipo': instance.tipo,
      'filtro': ?instance.filtro,
      'immagine': ?const ImmagineBlogJson().toJson(instance.immagine),
      'n_articoli': instance.nArticoli,
      'n_articoli_diretti': ?instance.nArticoliDiretti,
      'n_elementi': ?instance.nElementi,
      'n_carte': instance.nCarte,
      'n_stese': instance.nStese,
      'figli': instance.figli.map((e) => e.toJson()).toList(),
      'seo_titolo': ?instance.seoTitolo,
      'seo_descrizione': ?instance.seoDescrizione,
      'briciole': instance.briciole.map((e) => e.toJson()).toList(),
      'elementi': instance.elementi,
    };

_StesaSezione _$StesaSezioneFromJson(Map<String, dynamic> json) =>
    _StesaSezione(
      id: json['id'] as String,
      nome: json['nome'] as String,
      nomi: (json['nomi'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ),
      descrizione: json['descrizione'] as String? ?? '',
      descrizioneBreve: json['descrizione_breve'] as String? ?? '',
      categoria: json['categoria'] as String? ?? 'standard',
      stile: json['stile'] as String?,
      posizioni:
          (json['posizioni'] as List<dynamic>?)
              ?.map((e) => Posizione.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <Posizione>[],
      lang: json['lang'] as String?,
      slug: json['slug'] as String?,
      slugs: (json['slugs'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ),
      tradizione: json['tradizione'] as String?,
      tradizioni: (json['tradizioni'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ),
      forma: json['forma'] as String? ?? 'standard',
      larghezza: (json['larghezza'] as num?)?.toDouble(),
      larghezzaStretto: (json['larghezza_stretto'] as num?)?.toDouble(),
      carteDaScegliere: (json['carte_da_scegliere'] as num?)?.toInt(),
      mazzo: json['mazzo'] as String? ?? 'completo',
      nCarte: (json['n_carte'] as num?)?.toInt(),
      immagine: const ImmagineBlogJson().fromJson(json['immagine']),
    );

Map<String, dynamic> _$StesaSezioneToJson(_StesaSezione instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nome': instance.nome,
      'nomi': ?instance.nomi,
      'descrizione': instance.descrizione,
      'descrizione_breve': instance.descrizioneBreve,
      'categoria': instance.categoria,
      'stile': ?instance.stile,
      'posizioni': instance.posizioni.map((e) => e.toJson()).toList(),
      'lang': ?instance.lang,
      'slug': ?instance.slug,
      'slugs': ?instance.slugs,
      'tradizione': ?instance.tradizione,
      'tradizioni': ?instance.tradizioni,
      'forma': instance.forma,
      'larghezza': ?instance.larghezza,
      'larghezza_stretto': ?instance.larghezzaStretto,
      'carte_da_scegliere': ?instance.carteDaScegliere,
      'mazzo': instance.mazzo,
      'n_carte': ?instance.nCarte,
      'immagine': ?const ImmagineBlogJson().toJson(instance.immagine),
    };

_ElencoArticoli _$ElencoArticoliFromJson(Map<String, dynamic> json) =>
    _ElencoArticoli(
      totale: (json['totale'] as num?)?.toInt() ?? 0,
      pagina: (json['pagina'] as num?)?.toInt() ?? 1,
      perPagina: (json['per_pagina'] as num?)?.toInt() ?? 25,
      pagine: (json['pagine'] as num?)?.toInt() ?? 1,
      articoli:
          (json['articoli'] as List<dynamic>?)
              ?.map((e) => ArticoloBreve.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <ArticoloBreve>[],
    );

Map<String, dynamic> _$ElencoArticoliToJson(_ElencoArticoli instance) =>
    <String, dynamic>{
      'totale': instance.totale,
      'pagina': instance.pagina,
      'per_pagina': instance.perPagina,
      'pagine': instance.pagine,
      'articoli': instance.articoli.map((e) => e.toJson()).toList(),
    };

_EtichettaConConteggio _$EtichettaConConteggioFromJson(
  Map<String, dynamic> json,
) => _EtichettaConConteggio(
  slug: json['slug'] as String,
  nome: json['nome'] as String,
  n: (json['n'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$EtichettaConConteggioToJson(
  _EtichettaConConteggio instance,
) => <String, dynamic>{
  'slug': instance.slug,
  'nome': instance.nome,
  'n': instance.n,
};
