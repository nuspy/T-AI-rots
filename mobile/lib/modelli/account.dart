/// Ciò che appartiene a un account: il profilo (`GET /me/profile`), le letture (`GET /me/readings`,
/// `GET /me/readings/{id}`), le persone e la compatibilità delle letture speciali, le memorie, la chat proattiva.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

import 'carta.dart';

part 'account.freezed.dart';
part 'account.g.dart';

/// Una persona ricordata (il partner): il cognome si mostra solo al proprietario e all'AI non arriva mai.
@freezed
abstract class PersonaSalvata with _$PersonaSalvata {
  /// Una persona.
  const factory PersonaSalvata({
    required String nome,
    String? cognome,

    /// `donna`, `uomo`, `non_binario`, `altro`, `non_dice`.
    required String genere,
    String? genereAltro,
    @Default(false) bool trans,
    required String nascita,
  }) = _PersonaSalvata;

  /// Dal JSON dell'API.
  factory PersonaSalvata.fromJson(Map<String, dynamic> json) => _$PersonaSalvataFromJson(json);
}

/// Il contatore delle condivisioni verificate.
@freezed
abstract class Condivisioni with _$Condivisioni {
  /// Il contatore.
  const factory Condivisioni({
    @Default(0) int verificate,
    @Default(0) int premi,
    @Default(0) int prossimoTra,
    @Default(0) int iscrizioni,
    @Default(5) int soglia,
    @Default(5) int creditiIscrizione,
  }) = _Condivisioni;

  /// Dal JSON dell'API.
  factory Condivisioni.fromJson(Map<String, dynamic> json) => _$CondivisioniFromJson(json);
}

/// Dove si trova adesso chi usa l'app (dal social o dall'IP all'accesso; `fonte` `utente` se l'ha corretta).
@freezed
abstract class PosizioneAttuale with _$PosizioneAttuale {
  /// La posizione.
  const factory PosizioneAttuale({String? paese, String? citta, String? fonte, String? il}) = _PosizioneAttuale;

  /// Dal JSON dell'API.
  factory PosizioneAttuale.fromJson(Map<String, dynamic> json) => _$PosizioneAttualeFromJson(json);
}

/// Se il profilo ha ciò che serve alle letture di coppia (genere e nascita).
@freezed
abstract class Relazioni with _$Relazioni {
  /// `{completo, mancanti}`.
  const factory Relazioni({@Default(true) bool completo, @Default(<String>[]) List<String> mancanti}) = _Relazioni;

  /// Dal JSON dell'API.
  factory Relazioni.fromJson(Map<String, dynamic> json) => _$RelazioniFromJson(json);
}

/// Da dove viene un campo preso dai social.
@freezed
abstract class OrigineDato with _$OrigineDato {
  /// `{da, il}`.
  const factory OrigineDato({required String da, required String il}) = _OrigineDato;

  /// Dal JSON dell'API.
  factory OrigineDato.fromJson(Map<String, dynamic> json) => _$OrigineDatoFromJson(json);
}

/// Il profilo (`GET /me/profile`).
@freezed
abstract class Profilo with _$Profilo {
  /// Il profilo.
  const factory Profilo({
    required int id,
    String? email,
    String? displayName,
    @Default('it') String locale,

    /// v9.5: la versione della lettura di questa persona (`chat` o `classica`), fissata alla sua prima lettura e
    /// uguale su tutti i dispositivi; `null` = ancora nessuna.
    String? varianteLettura,

    /// Fase 2d: quando la lingua è stata scelta dal sito o dall'app; `null` = mai.
    String? localeSceltaIl,
    String? birthDate,

    /// `donna`, `uomo`, `non_binario`, `altro`, `non_dice`.
    String? gender,
    String? genderCustom,
    @Default(false) bool isTrans,
    @JsonKey(name: 'promemoria_2fa') @Default(true) bool promemoria2fa,
    String? nomePubblico,

    /// `esoterico` o `quotidiano`.
    @Default('esoterico') String registroLinguistico,
    int? mazzoPredefinitoId,
    @Default('') String nomeMostrato,

    /// Percorso relativo dell'API.
    String? avatar,
    PersonaSalvata? partnerRicordato,
    @Default(Relazioni()) Relazioni relazioni,
    String? referralCode,
    @Default(false) bool invitato,
    @Default(Condivisioni()) Condivisioni condivisioni,
    Carta? cartaAnima,
    Carta? cartaAnno,
    String? nome,
    String? cognome,
    PosizioneAttuale? posizione,
    @Default(<String, OrigineDato>{}) Map<String, OrigineDato> datiSocial,
    bool? importaSocial,
    bool? rilevaPosizione,
  }) = _Profilo;

  /// Dal JSON dell'API.
  factory Profilo.fromJson(Map<String, dynamic> json) => _$ProfiloFromJson(json);
}

/// Le dignità elementali di una posizione.
@freezed
abstract class Dignita with _$Dignita {
  /// Le dignità.
  const factory Dignita({
    required String elemento,
    required num punteggio,
    required String giudizio,
    @Default(<RelazioneDignita>[]) List<RelazioneDignita> relazioni,
  }) = _Dignita;

  /// Dal JSON dell'API.
  factory Dignita.fromJson(Map<String, dynamic> json) => _$DignitaFromJson(json);
}

/// Il rapporto con una carta vicina.
@freezed
abstract class RelazioneDignita with _$RelazioneDignita {
  /// `{posizione, elemento, relazione}`.
  const factory RelazioneDignita({required int posizione, required String elemento, required String relazione}) =
      _RelazioneDignita;

  /// Dal JSON dell'API.
  factory RelazioneDignita.fromJson(Map<String, dynamic> json) => _$RelazioneDignitaFromJson(json);
}

/// Una carta posata sul tavolo di una lettura.
@freezed
abstract class CartaPosata with _$CartaPosata {
  /// Una carta posata.
  const factory CartaPosata({
    required int posizione,
    required bool calcolata,
    required bool rivelata,
    Carta? carta,
    bool? rovescio,
    String? interpretazione,
  }) = _CartaPosata;

  /// Dal JSON dell'API.
  factory CartaPosata.fromJson(Map<String, dynamic> json) => _$CartaPosataFromJson(json);
}

/// Un turno dell'intervista prima delle carte.
@freezed
abstract class TurnoIntervista with _$TurnoIntervista {
  /// `ruolo` è `oracolo` o `utente`.
  const factory TurnoIntervista({required String ruolo, required String testo, required int ordine}) = _TurnoIntervista;

  /// Dal JSON dell'API.
  factory TurnoIntervista.fromJson(Map<String, dynamic> json) => _$TurnoIntervistaFromJson(json);
}

/// Chi consulta, nelle letture speciali.
@freezed
abstract class PersonaTu with _$PersonaTu {
  /// `{genere, genere_altro, trans, nascita}`.
  const factory PersonaTu({String? genere, String? genereAltro, @Default(false) bool trans, required String nascita}) =
      _PersonaTu;

  /// Dal JSON dell'API.
  factory PersonaTu.fromJson(Map<String, dynamic> json) => _$PersonaTuFromJson(json);
}

/// Le persone di una lettura speciale (compatibilità, coppia).
@freezed
abstract class PersoneLettura with _$PersoneLettura {
  /// Le persone.
  const factory PersoneLettura({@Default(1) int v, required PersonaTu tu, required PersonaSalvata partner}) =
      _PersoneLettura;

  /// Dal JSON dell'API.
  factory PersoneLettura.fromJson(Map<String, dynamic> json) => _$PersoneLetturaFromJson(json);
}

/// Un segno calcolato dalla data di nascita (codici: l'interfaccia li traduce).
@freezed
abstract class SegnoCalcolato with _$SegnoCalcolato {
  /// Il segno.
  const factory SegnoCalcolato({
    required String codice,
    required String elemento,
    required String modalita,
    @Default(false) bool cuspide,
    String? vicino,
  }) = _SegnoCalcolato;

  /// Dal JSON dell'API.
  factory SegnoCalcolato.fromJson(Map<String, dynamic> json) => _$SegnoCalcolatoFromJson(json);
}

/// I segni delle due persone.
@freezed
abstract class SegniCoppia with _$SegniCoppia {
  /// `{tu, partner}`.
  const factory SegniCoppia({required SegnoCalcolato tu, required SegnoCalcolato partner}) = _SegniCoppia;

  /// Dal JSON dell'API.
  factory SegniCoppia.fromJson(Map<String, dynamic> json) => _$SegniCoppiaFromJson(json);
}

/// La compatibilità zodiacale (codici: l'interfaccia li traduce).
@freezed
abstract class Compatibilita with _$Compatibilita {
  /// La compatibilità.
  const factory Compatibilita({
    required SegniCoppia segni,
    required int distanza,
    required String aspetto,
    required String relazioneElementi,
    @Default(false) bool stessaModalita,
    required String armonia,
    required Carta cartaCoppia,
    required Carta cartaAnimaTu,
    required Carta cartaAnimaPartner,
  }) = _Compatibilita;

  /// Dal JSON dell'API.
  factory Compatibilita.fromJson(Map<String, dynamic> json) => _$CompatibilitaFromJson(json);
}

/// Una lettura intera (`GET /me/readings/{id}`).
@freezed
abstract class Lettura with _$Lettura {
  /// Una lettura.
  const factory Lettura({
    required String id,

    /// La cartella delle immagini del mazzo; `null` = il predefinito.
    String? mazzo,
    required String spreadId,
    required String stesa,
    @Default(<String, String>{}) Map<String, String> stesaNomi,
    required String categoria,
    String? stile,
    PersoneLettura? persone,
    Compatibilita? compatibilita,
    required String question,

    /// `intervista`, `ventaglio`, `scelta`, `rivelazione`, `sintesi`, `completata`, `annullata`.
    required String status,
    required String lang,
    @Default('') String consumo,
    required String createdAt,
    String? completedAt,

    /// `si`, `in_parte`, `no`.
    String? feedback,
    @Default(false) bool shared,
    @Default(false) bool manuale,
    String? contextSummary,
    @Default(<TurnoIntervista>[]) List<TurnoIntervista> interview,
    @Default(<CartaPosata>[]) List<CartaPosata> cards,
    int? slotCount,
    @Default(<int>[]) List<int> pickedSlots,
    String? commitment,
    String? deckSalt,
    String? synthesis,
    String? guardOutcome,
    String? shareToken,
    String? shareText,
    String? feedbackNote,
    @Default('') String disclaimer,
    @Default(<String, Dignita>{}) Map<String, Dignita> dignita,
    Stesa? stesaDati,
  }) = _Lettura;

  /// Dal JSON dell'API.
  factory Lettura.fromJson(Map<String, dynamic> json) => _$LetturaFromJson(json);
}

/// Una lettura nello storico (`GET /me/readings`).
@freezed
abstract class LetturaBreve with _$LetturaBreve {
  /// Una lettura nello storico.
  const factory LetturaBreve({
    required String id,
    String? mazzo,
    required String spreadId,
    required String stesa,
    @Default(<String, String>{}) Map<String, String> stesaNomi,
    required String categoria,
    String? stile,
    String? partnerNome,
    required String question,
    required String status,
    required String createdAt,
    String? completedAt,
    String? feedback,
    @Default(false) bool shared,
    @Default(<String>[]) List<String> carte,
  }) = _LetturaBreve;

  /// Dal JSON dell'API.
  factory LetturaBreve.fromJson(Map<String, dynamic> json) => _$LetturaBreveFromJson(json);
}

/// `GET /me/readings`: il totale e l'elenco.
@freezed
abstract class ElencoLetture with _$ElencoLetture {
  /// L'elenco.
  const factory ElencoLetture({required int totale, @Default(<LetturaBreve>[]) List<LetturaBreve> letture}) =
      _ElencoLetture;

  /// Dal JSON dell'API.
  factory ElencoLetture.fromJson(Map<String, dynamic> json) => _$ElencoLettureFromJson(json);
}

/* ---- il rito: le risposte dei passi ------------------------------------------------------------------------------ */

/// `POST /readings` e `POST /readings/anonime`: la lettura aperta (o il messaggio di crisi).
@freezed
abstract class Apertura with _$Apertura {
  /// L'apertura.
  const factory Apertura({
    String? id,
    String? status,
    String? categoria,

    /// La lingua del quesito, ricavata dal server: quella di domande e responso.
    String? lang,
    String? consumo,
    String? disclaimer,
    Stesa? stesa,
    int? saldo,
    @Default(false) bool crisi,
    String? messaggio,
  }) = _Apertura;

  /// Dal JSON dell'API.
  factory Apertura.fromJson(Map<String, dynamic> json) => _$AperturaFromJson(json);
}

/// `POST /readings/{id}/interview`: la domanda successiva o la fine dell'intervista.
@freezed
abstract class PassoIntervista with _$PassoIntervista {
  /// Un passo.
  const factory PassoIntervista({
    @Default(false) bool completa,
    String? domanda,
    int? ordine,
    String? riassunto,
    @Default(false) bool crisi,
    String? messaggio,

    /// Il minimo di domande è raggiunto: ci si può fermare («Basta con le domande»).
    @Default(false) bool facoltativa,

    /// v9.5: dopo una risposta il server non chiede subito un'altra domanda: tocca a chi legge scegliere (i tre
    /// pulsanti).
    @Default(false) bool scelta,

    /// v9.5: le domande poste finora, e il minimo e il massimo della console.
    int? poste,
    int? minDomande,
    int? maxDomande,
  }) = _PassoIntervista;

  /// Dal JSON dell'API.
  factory PassoIntervista.fromJson(Map<String, dynamic> json) => _$PassoIntervistaFromJson(json);
}

/// `POST /readings/{id}/fan`: il ventaglio sigillato.
@freezed
abstract class Ventaglio with _$Ventaglio {
  /// Il ventaglio.
  const factory Ventaglio({
    required int slotCount,
    required String commitment,
    required int daScegliere,
    @Default(<int>[]) List<int> pickedSlots,
  }) = _Ventaglio;

  /// Dal JSON dell'API.
  factory Ventaglio.fromJson(Map<String, dynamic> json) => _$VentaglioFromJson(json);
}

/// `POST /readings/{id}/pick`: la carta scelta.
@freezed
abstract class Scelta with _$Scelta {
  /// La scelta.
  const factory Scelta({
    required int posizione,
    required int slot,
    @Default(false) bool tutteScelte,
    @Default(<int>[]) List<int> posizioniCalcolate,
  }) = _Scelta;

  /// Dal JSON dell'API.
  factory Scelta.fromJson(Map<String, dynamic> json) => _$SceltaFromJson(json);
}

/// `POST /me/readings/{id}/share`: il collegamento pubblico e il testo del post.
@freezed
abstract class StatoCondivisione with _$StatoCondivisione {
  /// `{share_token, share_text}`.
  const factory StatoCondivisione({String? shareToken, String? shareText}) = _StatoCondivisione;

  /// Dal JSON dell'API.
  factory StatoCondivisione.fromJson(Map<String, dynamic> json) => _$StatoCondivisioneFromJson(json);
}

/// `GET /shared/{token}`: ciò che chiunque vede di una lettura condivisa.
@freezed
abstract class LetturaCondivisa with _$LetturaCondivisa {
  /// La lettura condivisa.
  const factory LetturaCondivisa({
    required String question,
    String? mazzo,
    required String lang,
    Stesa? stesa,
    required String categoria,
    @Default(false) bool speciale,

    /// `venere`, `marte`, `mercurio`, `stella`.
    String? partnerSimbolo,
    String? partnerFrase,
    @Default(<CartaPosata>[]) List<CartaPosata> cards,
    String? synthesis,
    String? shareText,
    @Default(false) bool immagine,
    required String createdAt,
    @Default('') String disclaimer,
  }) = _LetturaCondivisa;

  /// Dal JSON dell'API.
  factory LetturaCondivisa.fromJson(Map<String, dynamic> json) => _$LetturaCondivisaFromJson(json);
}

/* ---- memoria e chat proattiva ------------------------------------------------------------------------------------- */

/// Una memoria del lettore.
@freezed
abstract class Memoria with _$Memoria {
  /// Una memoria.
  const factory Memoria({
    required String id,
    required String contenuto,

    /// `stabile` o `variabile`.
    required String tipo,
    required String campoAttinenza,

    /// `lettura` o `chat`.
    required String fonte,
    String? aggiornata,
  }) = _Memoria;

  /// Dal JSON dell'API.
  factory Memoria.fromJson(Map<String, dynamic> json) => _$MemoriaFromJson(json);
}

/// Una lettura proposta dall'oracolo nella chat.
@freezed
abstract class PropostaLettura with _$PropostaLettura {
  /// `{argomento, categoria}`.
  const factory PropostaLettura({required String argomento, required String categoria}) = _PropostaLettura;

  /// Dal JSON dell'API.
  factory PropostaLettura.fromJson(Map<String, dynamic> json) => _$PropostaLetturaFromJson(json);
}

/// Un turno della chat proattiva.
@freezed
abstract class TurnoChat with _$TurnoChat {
  /// Un turno.
  const factory TurnoChat({
    required String id,

    /// `ai` o `utente`.
    required String ruolo,
    required String testo,
    PropostaLettura? proposta,
    String? creato,
  }) = _TurnoChat;

  /// Dal JSON dell'API.
  factory TurnoChat.fromJson(Map<String, dynamic> json) => _$TurnoChatFromJson(json);
}

/// `GET /impostazioni-chat`: il silenzio prima dell'apertura proattiva e il tetto per visita.
@freezed
abstract class ImpostazioniChat with _$ImpostazioniChat {
  /// Le impostazioni.
  const factory ImpostazioniChat({
    @Default(30) int proattivaMinutiInattivita,
    @Default(3) int proattivaMaxPerVisita,
  }) = _ImpostazioniChat;

  /// Dal JSON dell'API.
  factory ImpostazioniChat.fromJson(Map<String, dynamic> json) => _$ImpostazioniChatFromJson(json);
}
