/// Ciò che si legge senza account: la carta di oggi, i numeri del regalo d'iscrizione, l'età minima, i nove
/// articoli del diario di ogni pagina.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

import 'carta.dart';

part 'pubblici.freezed.dart';
part 'pubblici.g.dart';

/// `GET /daily-card/today`: la carta di oggi per tutti, uguale per chiunque fino a mezzanotte UTC.
@freezed
abstract class CartaOggi with _$CartaOggi {
  /// La carta di oggi.
  const factory CartaOggi({required String giorno, required Carta carta, required String testo}) = _CartaOggi;

  /// Dal JSON dell'API.
  factory CartaOggi.fromJson(Map<String, dynamic> json) => _$CartaOggiFromJson(json);
}

/// `GET /me/daily-card`: la carta personale di oggi, da girare, con i giorni di fila.
@freezed
abstract class CartaDelGiorno with _$CartaDelGiorno {
  /// La carta personale.
  const factory CartaDelGiorno({
    required String giorno,
    required Carta carta,
    required bool rovescio,
    required String testo,
    required int serie,
  }) = _CartaDelGiorno;

  /// Dal JSON dell'API.
  factory CartaDelGiorno.fromJson(Map<String, dynamic> json) => _$CartaDelGiornoFromJson(json);
}

/// `GET /impostazioni-pubbliche`: i numeri veri del regalo d'iscrizione e dell'invito.
@freezed
abstract class ImpostazioniPubbliche with _$ImpostazioniPubbliche {
  /// Le impostazioni pubbliche.
  const factory ImpostazioniPubbliche({
    required int creditiIscrizione,
    required int creditiInvito,
    @Default(0) num commissioneReferralPercentuale,

    /// v9.5: quante persone su cento ricevono la lettura in chat (prova 90/10, dalla console).
    @Default(90) int letturaChatPercentuale,
  }) = _ImpostazioniPubbliche;

  /// Dal JSON dell'API.
  factory ImpostazioniPubbliche.fromJson(Map<String, dynamic> json) => _$ImpostazioniPubblicheFromJson(json);
}

/// `GET /eta-minima`: l'età minima per il paese stimato (GDPR, Fase 1).
@freezed
abstract class EtaMinima with _$EtaMinima {
  /// L'età minima.
  const factory EtaMinima({required int anni, String? paese}) = _EtaMinima;

  /// Dal JSON dell'API.
  factory EtaMinima.fromJson(Map<String, dynamic> json) => _$EtaMinimaFromJson(json);
}

/// L'immagine di un articolo: l'originale e la miniatura (percorsi relativi dell'API).
@freezed
abstract class ImmagineArticolo with _$ImmagineArticolo {
  /// L'immagine.
  const factory ImmagineArticolo({String? url, String? mini, String? alt, int? larghezza, int? altezza}) =
      _ImmagineArticolo;

  /// Dal JSON dell'API.
  factory ImmagineArticolo.fromJson(Map<String, dynamic> json) => _$ImmagineArticoloFromJson(json);
}

/// Un nome con il suo indirizzo: la sezione o un'etichetta di un articolo.
@freezed
abstract class Voce with _$Voce {
  /// `{slug, nome}`.
  const factory Voce({required String slug, required String nome}) = _Voce;

  /// Dal JSON dell'API.
  factory Voce.fromJson(Map<String, dynamic> json) => _$VoceFromJson(json);
}

/// Chi ha scritto un articolo.
@freezed
abstract class AutoreBlog with _$AutoreBlog {
  /// `{id, nome, avatar}`.
  const factory AutoreBlog({int? id, required String nome, String? avatar}) = _AutoreBlog;

  /// Dal JSON dell'API.
  factory AutoreBlog.fromJson(Map<String, dynamic> json) => _$AutoreBlogFromJson(json);
}

/// Di che cosa parla un articolo (v9.4): una carta o una stesa, coi nomi e l'indirizzo nella lingua dell'articolo.
@freezed
abstract class SoggettoArticolo with _$SoggettoArticolo {
  /// `{tipo, ref, nome, slug}`: `tipo` è `carta` o `stesa`, `ref` l'id canonico (`maj-10`, `croce-celtica`).
  const factory SoggettoArticolo({required String tipo, required String ref, String? nome, String? slug}) =
      _SoggettoArticolo;

  /// Dal JSON dell'API.
  factory SoggettoArticolo.fromJson(Map<String, dynamic> json) => _$SoggettoArticoloFromJson(json);
}

/// Un articolo del diario negli elenchi.
@freezed
abstract class ArticoloBreve with _$ArticoloBreve {
  /// Un articolo.
  const factory ArticoloBreve({
    required String slug,
    required String titolo,
    String? sottotitolo,
    String? estratto,
    ImmagineArticolo? immagine,
    Voce? sezione,
    @Default(1) int tempoLettura,
    @Default(<Voce>[]) List<Voce> tags,
    String? lang,
    AutoreBlog? autore,
    String? pubblicatoIl,
    String? aggiornatoIl,
    @Default(false) bool inEvidenza,

    /// La carta o la stesa di cui parla (v9.4), o null.
    SoggettoArticolo? soggetto,
  }) = _ArticoloBreve;

  /// Dal JSON dell'API.
  factory ArticoloBreve.fromJson(Map<String, dynamic> json) => _$ArticoloBreveFromJson(json);
}

/// `GET /blog/nove`: i 3 articoli più recenti e 6 attinenti alla pagina.
@freezed
abstract class Nove with _$Nove {
  /// I nove articoli.
  const factory Nove({
    @Default(<ArticoloBreve>[]) List<ArticoloBreve> recenti,
    @Default(<ArticoloBreve>[]) List<ArticoloBreve> scelti,
  }) = _Nove;

  /// Dal JSON dell'API.
  factory Nove.fromJson(Map<String, dynamic> json) => _$NoveFromJson(json);
}
