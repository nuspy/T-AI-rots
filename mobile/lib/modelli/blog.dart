/// Il diario (il blog): l'articolo intero, le sezioni, le etichette, gli elenchi a pagine. Come `frontend/lib/blog.ts`.
/// L'articolo negli elenchi ([ArticoloBreve]) e le sue parti stanno in `pubblici.dart` (li usano anche i nove articoli
/// di ogni pagina).
library;

import 'package:flutter/foundation.dart' show debugPrint;
import 'package:freezed_annotation/freezed_annotation.dart';

import 'carta.dart';
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

    /// La carta o la stesa di cui parla (v9.4), o null.
    SoggettoArticolo? soggetto,
  }) = _ArticoloBlog;

  /// Dal JSON dell'API.
  factory ArticoloBlog.fromJson(Map<String, dynamic> json) => _$ArticoloBlogFromJson(json);
}

/// L'immagine di una sezione, di una stesa del catalogo o di un elemento (v9.4): l'originale, la miniatura e il testo
/// alternativo (percorsi relativi dell'API). Prima della v9.4 una sezione aveva solo l'indirizzo: [ImmagineBlogJson]
/// legge anche quella forma.
@freezed
abstract class ImmagineBlog with _$ImmagineBlog {
  /// `{url, mini, alt}`.
  const factory ImmagineBlog({String? url, String? mini, String? alt}) = _ImmagineBlog;

  const ImmagineBlog._();

  /// Dal JSON dell'API.
  factory ImmagineBlog.fromJson(Map<String, dynamic> json) => _$ImmagineBlogFromJson(json);

  /// Il percorso da mostrare in una tessera: la miniatura se c'è, altrimenti l'originale.
  String? get perTessera => (mini ?? '').isNotEmpty ? mini : ((url ?? '').isNotEmpty ? url : null);
}

/// Legge `immagine` sia come oggetto `{url, mini, alt}` (v9.4) sia come la stringa di prima (solo l'indirizzo).
class ImmagineBlogJson implements JsonConverter<ImmagineBlog?, Object?> {
  /// Il convertitore.
  const ImmagineBlogJson();

  @override
  ImmagineBlog? fromJson(Object? json) => switch (json) {
    final String s when s.isNotEmpty => ImmagineBlog(url: s),
    final Map<String, dynamic> m => ImmagineBlog.fromJson(m),
    final Map<Object?, Object?> m => ImmagineBlog.fromJson(m.cast<String, dynamic>()),
    _ => null,
  };

  @override
  Object? toJson(ImmagineBlog? immagine) => immagine?.toJson();
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
    @ImmagineBlogJson() ImmagineBlog? immagine,

    /// Gli articoli di tutto il ramo (la sezione e le sotto-sezioni).
    @Default(0) int nArticoli,

    /// Solo quelli della sezione.
    int? nArticoliDiretti,
    int? nElementi,

    /// Le carte e le stese diverse di tutto il ramo.
    @Default(0) int nCarte,
    @Default(0) int nStese,
    @Default(<NodoSezione>[]) List<NodoSezione> figli,

    /// Solo nei figli di `GET /blog/sections/{slug}` (v9.4): 3 articoli del ramo scelti per la giornata.
    @Default(<ArticoloBreve>[]) List<ArticoloBreve> articoli,
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
    @ImmagineBlogJson() ImmagineBlog? immagine,
    @Default(0) int nArticoli,
    int? nArticoliDiretti,
    int? nElementi,
    @Default(0) int nCarte,
    @Default(0) int nStese,

    /// Le sotto-sezioni dirette, ognuna coi suoi 3 `articoli` (v9.4).
    @Default(<NodoSezione>[]) List<NodoSezione> figli,
    String? seoTitolo,
    String? seoDescrizione,
    @Default(<Voce>[]) List<Voce> briciole,

    /// Le carte (sezioni `carte`: la forma di `GET /cards`) o le stese (sezioni `stese`: vedi [StesaSezione]).
    @Default(<Map<String, Object?>>[]) List<Map<String, Object?>> elementi,
  }) = _DettaglioSezione;

  const DettaglioSezione._();

  /// Dal JSON dell'API.
  factory DettaglioSezione.fromJson(Map<String, dynamic> json) => _$DettaglioSezioneFromJson(json);

  /// Le stese di una sezione `stese`; un elemento che non si legge si salta (non rompe la pagina).
  List<StesaSezione> get stese {
    if (tipo != 'stese') return const [];
    final esito = <StesaSezione>[];
    for (final e in elementi) {
      try {
        esito.add(StesaSezione.fromJson(Map<String, dynamic>.from(e)));
      } on Object catch (errore) {
        debugPrint('Stesa della sezione $slug non letta: $errore');
      }
    }
    return esito;
  }
}

/// Una stesa fra gli `elementi` di una sezione `stese` (v9.4): ciò che serve alla scheda ricca del diario
/// (illustrazione, schema, titolo, intro breve, tradizione, numero di carte).
@freezed
abstract class StesaSezione with _$StesaSezione {
  /// La stesa.
  const factory StesaSezione({
    required String id,
    required String nome,
    Map<String, String>? nomi,
    @Default('') String descrizione,

    /// La descrizione accorciata (al più 160 caratteri).
    @Default('') String descrizioneBreve,
    @Default('standard') String categoria,
    String? stile,
    @Default(<Posizione>[]) List<Posizione> posizioni,
    String? lang,
    String? slug,
    Map<String, String>? slugs,

    /// La tradizione in poche parole («love», «Celtic tradition»), nella lingua dei testi.
    String? tradizione,

    /// La tradizione in ogni lingua che ce l'ha.
    Map<String, String>? tradizioni,
    @Default('standard') String forma,
    double? larghezza,
    double? larghezzaStretto,
    int? carteDaScegliere,
    @Default('completo') String mazzo,
    int? nCarte,
    @ImmagineBlogJson() ImmagineBlog? immagine,
  }) = _StesaSezione;

  const StesaSezione._();

  /// Dal JSON dell'API.
  factory StesaSezione.fromJson(Map<String, dynamic> json) => _$StesaSezioneFromJson(json);

  /// Quante carte ha.
  int get carte => nCarte ?? posizioni.length;

  /// La tradizione nella lingua [lingua] dell'interfaccia, se c'è; altrimenti quella dei testi.
  String? tradizioneIn(String lingua) {
    final t = tradizioni?[lingua] ?? tradizione;
    return (t ?? '').trim().isEmpty ? null : t!.trim();
  }

  /// La stessa stesa come [Stesa] del catalogo, per disegnarne lo schema (`MiniaturaStesa`) e per i nomi.
  Stesa comeStesa() => Stesa(
    id: id,
    nome: nome,
    nomeEn: nomi?['en'] ?? nome,
    nomi: nomi,
    lang: lang,
    slug: slug,
    slugs: slugs,
    categoria: categoria,
    stile: stile,
    larghezza: larghezza,
    larghezzaStretto: larghezzaStretto,
    forma: forma,
    mazzo: mazzo,
    carteDaScegliere: carteDaScegliere ?? posizioni.length,
    origine: '',
    descrizione: descrizione,
    posizioni: posizioni,
  );
}

/// `GET /blog/posts`: una pagina dell'elenco.
@freezed
abstract class ElencoArticoli with _$ElencoArticoli {
  /// L'elenco.
  const factory ElencoArticoli({
    @Default(0) int totale,
    @Default(1) int pagina,
    @Default(25) int perPagina,
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
