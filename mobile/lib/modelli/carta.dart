/// Carte e stese: i dati pubblici della conoscenza (`GET /cards`, `/cards/{id}`, `/spreads`, `/spreads/{id}`).
///
/// Scritti a mano come in `frontend/lib/api.ts` (`Carta`, `Stesa`, `Posizione`); il test di contratto
/// (`test/contratto_test.dart`) li confronta con le risposte vere dell'API salvate in `test/fixtures/`.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'carta.freezed.dart';
part 'carta.g.dart';

/// La lettera ebraica di un arcano maggiore.
@freezed
abstract class LetteraEbraica with _$LetteraEbraica {
  /// `{nome, glifo, valore}`.
  const factory LetteraEbraica({required String nome, required String glifo, required int valore}) = _LetteraEbraica;

  /// Dal JSON dell'API.
  factory LetteraEbraica.fromJson(Map<String, dynamic> json) => _$LetteraEbraicaFromJson(json);
}

/// Una carta del mazzo. I campi dopo `colori` ci sono solo nella scheda completa (`/cards/{id}`, carta del giorno).
@freezed
abstract class Carta with _$Carta {
  /// Una carta.
  const factory Carta({
    required String id,
    required String arcano,
    int? numero,
    String? numeroRomano,
    String? seme,
    String? rango,
    required String nomeThoth,
    String? titoloThoth,
    required String nomeIt,

    /// Il nome nelle altre lingue: `en` sempre, poi quelle con nomi propri.
    @Default(<String, String>{}) Map<String, String> nomi,

    /// La lingua dei testi chiesta con `?lang=` (`it` o `en`): `nome` e `slug` sono in quella lingua.
    String? lang,
    String? nome,
    String? slug,
    @Default(<String, String>{}) Map<String, String> slugs,
    String? elementoLabel,
    String? semeLabel,
    String? rangoLabel,
    String? arcanoLabel,
    LetteraEbraica? letteraEbraica,
    required String elemento,
    required String astrologia,
    @Default(<String>[]) List<String> paroleChiave,
    @Default(<String>[]) List<String> colori,
    int? percorso,
    List<String>? collega,
    String? sefira,
    Map<String, String>? significati,
    String? dritto,
    String? rovescio,
    Map<String, String>? ambiti,
    String? notaCrowley,
  }) = _Carta;

  const Carta._();

  /// Dal JSON dell'API.
  factory Carta.fromJson(Map<String, dynamic> json) => _$CartaFromJson(json);

  /// Il nome nella lingua dell'interfaccia, come `nomeDi()` del sito: quello della risposta se è nella lingua dei
  /// contenuti, altrimenti l'italiano, la traduzione, l'inglese, il nome di Thoth.
  String nomeIn(String lingua) {
    final contenuti = lingua == 'it' ? 'it' : 'en';
    if (lang == contenuti && (nome?.isNotEmpty ?? false)) return nome!;
    if (lingua == 'it') return nomeIt;
    return nomi[lingua] ?? nomi['en'] ?? nomeThoth;
  }
}

/// Una posizione di una stesa.
@freezed
abstract class Posizione with _$Posizione {
  /// Una posizione.
  const factory Posizione({
    required int n,
    required String nome,
    required String nomeEn,
    Map<String, String>? nomi,

    /// Solo nelle stese speciali: di chi parla (`tu`, `partner`, `coppia`, `strada-a`, `strada-b`).
    String? soggetto,
    required String significato,
    required String domanda,
    required double x,
    required double y,
    required double rotazione,
    required bool calcolata,
  }) = _Posizione;

  /// Dal JSON dell'API.
  factory Posizione.fromJson(Map<String, dynamic> json) => _$PosizioneFromJson(json);
}

/// Una stesa.
@freezed
abstract class Stesa with _$Stesa {
  /// Una stesa.
  const factory Stesa({
    required String id,
    required String nome,
    required String nomeEn,
    Map<String, String>? nomi,
    String? lang,
    String? slug,
    Map<String, String>? slugs,
    String? mazzoLabel,
    String? categoriaLabel,
    String? stileLabel,

    /// `standard`, `lavoro`, `compatibilita`, `coppia`.
    required String categoria,
    List<String>? temi,
    String? stile,
    double? larghezza,
    double? larghezzaStretto,
    required String forma,
    required String mazzo,
    required int carteDaScegliere,
    required String origine,
    required String descrizione,
    required List<Posizione> posizioni,
    @Default(<String>[]) List<String> regole,

    /// Le coppie di posizioni lette insieme: `[a, b, "perché"]`.
    @Default(<List<Object?>>[]) List<List<Object?>> coppie,
    @Default(false) bool sintesiWirth,
  }) = _Stesa;

  /// Dal JSON dell'API.
  factory Stesa.fromJson(Map<String, dynamic> json) => _$StesaFromJson(json);
}
