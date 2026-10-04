/// Il diario (il blog): l'articolo intero, le sezioni, le etichette, gli elenchi a pagine. Come `frontend/lib/blog.ts`.
/// L'articolo negli elenchi ([ArticoloBreve]) e le sue parti stanno in `pubblici.dart` (li usano anche i nove articoli
/// di ogni pagina).
library;

import 'package:freezed_annotation/freezed_annotation.dart';

import 'pubblici.dart';

part 'blog.freezed.dart';
part 'blog.g.dart';

/// Una domanda frequente di un articolo.
@freezed
abstract class DomandaFaq with _$DomandaFaq {
  /// `{domanda, risposta}`.
  const factory DomandaFaq({required String domanda, required String risposta}) = _DomandaFaq;

  /// Dal JSON dell'API.
  factory DomandaFaq.fromJson(Map<String, dynamic> json) => _$DomandaFaqFromJson(json);
}

/// Una carta citata da un articolo.
@freezed
abstract class CartaCitata with _$CartaCitata {
  /// La carta.
  const factory CartaCitata({
    required String id,
    @Default('') String nomeIt,
    required String nome,
    required String slug,
    @Default(<String, String>{}) Map<String, String> slugs,
  }) = _CartaCitata;

  /// Dal JSON dell'API.
  factory CartaCitata.fromJson(Map<String, dynamic> json) => _$CartaCitataFromJson(json);
}

/// Una stesa citata da un articolo.
@freezed
abstract class StesaCitata with _$StesaCitata {
  /// La stesa.
  const factory StesaCitata({
    required String id,
    required String nome,
    required String slug,
    @Default(<String, String>{}) Map<String, String> slugs,
  }) = _StesaCitata;

  /// Dal JSON dell'API.
  factory StesaCitata.fromJson(Map<String, dynamic> json) => _$StesaCitataFromJson(json);
}

/// Carte, stese e articoli citati da un articolo.
@freezed
abstract class Collegamenti with _$Collegamenti {
  /// I collegamenti.
  const factory Collegamenti({
    @Default(<CartaCitata>[]) List<CartaCitata> carte,
    @Default(<StesaCitata>[]) List<StesaCitata> stese,
    @Default(<ArticoloBreve>[]) List<ArticoloBreve> articoli,
  }) = _Collegamenti;

  /// Dal JSON dell'API.
  factory Collegamenti.fromJson(Map<String, dynamic> json) => _$CollegamentiFromJson(json);
}

/// La metà di un articolo nell'altra lingua.
@freezed
abstract class Gemella with _$Gemella {
  /// `{lang, slug}`.
  const factory Gemella({required String lang, required String slug}) = _Gemella;

  /// Dal JSON dell'API.
  factory Gemella.fromJson(Map<String, dynamic> json) => _$GemellaFromJson(json);
}

/// `GET /blog/posts/{slug}`: l'articolo intero.
@freezed
abstract class ArticoloBlog with _$ArticoloBlog {
  /// L'articolo.
  const factory ArticoloBlog({
    required String slug,
    required String titolo,
    String? sottotitolo,
    @Default('') String estratto,
    ImmagineArticolo? immagine,
    Voce? sezione,
    AutoreBlog? autore,
    String? pubblicatoIl,
    String? aggiornatoIl,
    @Default(1) int tempoLettura,
    @Default(<Voce>[]) List<Voce> tags,
    @Default('en') String lang,
    @Default(false) bool inEvidenza,
    @Default('') String testo,
    String? seoTitolo,
    @Default('') String seoDescrizione,
    @Default(<DomandaFaq>[]) List<DomandaFaq> faq,
    @Default(false) bool commentiAperti,
    @Default(<Voce>[]) List<Voce> briciole,
    @Default(Collegamenti()) Collegamenti collegamenti,
    @Default(<ArticoloBreve>[]) List<ArticoloBreve> correlati,
    ArticoloBreve? precedente,
    ArticoloBreve? successivo,
    Gemella? gemellaLingua,
  }) = _ArticoloBlog;

  /// Dal JSON dell'API.
  factory ArticoloBlog.fromJson(Map<String, dynamic> json) => _$ArticoloBlogFromJson(json);
}

/// Una sezione del diario nell'albero (`GET /blog/sections`).
@freezed
abstract class NodoSezione with _$NodoSezione {
  /// Una sezione.
  const factory NodoSezione({
    required int id,
    required String slug,
    required String nome,
    String? descrizione,

    /// `articoli`, `carte`, `stese`, `contenitore`.
    @Default('articoli') String tipo,
    Map<String, String>? filtro,
    String? immagine,
    @Default(0) int nArticoli,
    int? nElementi,
    @Default(<NodoSezione>[]) List<NodoSezione> figli,
  }) = _NodoSezione;

  /// Dal JSON dell'API.
  factory NodoSezione.fromJson(Map<String, dynamic> json) => _$NodoSezioneFromJson(json);
}

/// `GET /blog/sections/{slug}`: una sezione con le briciole e, per le sezioni di carte o stese, gli elementi.
@freezed
abstract class DettaglioSezione with _$DettaglioSezione {
  /// La sezione.
  const factory DettaglioSezione({
    required int id,
    required String slug,
    required String nome,
    String? descrizione,
    @Default('articoli') String tipo,
    Map<String, String>? filtro,
    String? immagine,
    @Default(0) int nArticoli,
    int? nElementi,
    @Default(<NodoSezione>[]) List<NodoSezione> figli,
    String? seoTitolo,
    String? seoDescrizione,
    @Default(<Voce>[]) List<Voce> briciole,
    @Default(<Map<String, Object?>>[]) List<Map<String, Object?>> elementi,
  }) = _DettaglioSezione;

  /// Dal JSON dell'API.
  factory DettaglioSezione.fromJson(Map<String, dynamic> json) => _$DettaglioSezioneFromJson(json);
}

/// `GET /blog/posts`: una pagina dell'elenco.
@freezed
abstract class ElencoArticoli with _$ElencoArticoli {
  /// L'elenco.
  const factory ElencoArticoli({
    @Default(0) int totale,
    @Default(1) int pagina,
    @Default(6) int perPagina,
    @Default(1) int pagine,
    @Default(<ArticoloBreve>[]) List<ArticoloBreve> articoli,
  }) = _ElencoArticoli;

  /// Dal JSON dell'API.
  factory ElencoArticoli.fromJson(Map<String, dynamic> json) => _$ElencoArticoliFromJson(json);
}

/// `GET /blog/tags`: un'etichetta con quanti articoli ha.
@freezed
abstract class EtichettaConConteggio with _$EtichettaConConteggio {
  /// L'etichetta.
  const factory EtichettaConConteggio({required String slug, required String nome, @Default(0) int n}) =
      _EtichettaConConteggio;

  /// Dal JSON dell'API.
  factory EtichettaConConteggio.fromJson(Map<String, dynamic> json) => _$EtichettaConConteggioFromJson(json);
}
