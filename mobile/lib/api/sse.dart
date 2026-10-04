/// Lo streaming della lettura: `POST /readings/{id}/reveal/{posizione}` e `POST /readings/{id}/synthesis` rispondono
/// con eventi SSE (`text/event-stream`), scritti dal server con `_sse()` di `backend/tarot_core/api/routers/readings.py`:
///
///     event: token
///     data: {"testo": "…"}
///     (riga vuota)
///
/// Il parser è lo stesso di `flusso()` in `frontend/lib/api.ts`: blocchi separati da una riga vuota, `event:` dà il
/// nome, le righe `data:` si concatenano e sono JSON. La decodifica UTF-8 è a flusso, perché un carattere accentato
/// può arrivare spezzato fra due pacchetti. Un blocco rimasto a metà alla fine del flusso si scarta (come nel sito e
/// come vuole la specifica SSE). **Nessun riprova automatico**: se il flusso si interrompe, decide chi lo mostra.
library;

import 'dart:async';
import 'dart:convert';

import '../modelli/account.dart';
import '../modelli/carta.dart';

/// Un evento grezzo: il nome e i dati JSON.
class EventoSse {
  /// `event:` e `data:` di un blocco.
  const EventoSse(this.nome, this.dati);

  /// Il nome (`carta`, `token`, `fine`…).
  final String nome;

  /// I dati, già letti dal JSON; vuoti se il blocco non ne aveva.
  final Map<String, Object?> dati;

  @override
  String toString() => 'EventoSse($nome, $dati)';
}

/// Un flusso SSE che non si può leggere (dati che non sono JSON).
class ErroreSse implements FormatException {
  /// Con il blocco che non si è potuto leggere.
  const ErroreSse(this.message, [this.source]);

  @override
  final String message;

  @override
  final Object? source;

  @override
  int? get offset => null;

  @override
  String toString() => 'ErroreSse: $message';
}

/// I byte di una risposta → gli eventi, nell'ordine in cui arrivano.
Stream<EventoSse> leggiSse(Stream<List<int>> byte) async* {
  var avanzo = '';
  // `bind` e non `transform`: il corpo di dio è uno `Stream<Uint8List>`, che `transform` non accetterebbe.
  await for (final testo in utf8.decoder.bind(byte)) {
    avanzo = (avanzo + testo).replaceAll('\r\n', '\n');
    final blocchi = avanzo.split('\n\n');
    avanzo = blocchi.removeLast();
    for (final blocco in blocchi) {
      final evento = _blocco(blocco);
      if (evento != null) yield evento;
    }
  }
}

EventoSse? _blocco(String blocco) {
  var nome = '';
  final dati = StringBuffer();
  for (final riga in blocco.split('\n')) {
    if (riga.startsWith('event:')) {
      nome = riga.substring(6).trim();
    } else if (riga.startsWith('data:')) {
      dati.write(riga.substring(5).trim());
    }
  }
  if (nome.isEmpty) return null;
  if (dati.isEmpty) return EventoSse(nome, const {});
  try {
    final letto = jsonDecode(dati.toString());
    if (letto is Map<String, Object?>) return EventoSse(nome, letto);
    throw ErroreSse('i dati dell\'evento «$nome» non sono un oggetto JSON', blocco);
  } on FormatException catch (e) {
    if (e is ErroreSse) rethrow;
    throw ErroreSse('i dati dell\'evento «$nome» non sono JSON: ${e.message}', blocco);
  }
}

/// Un evento della lettura, già tipizzato. Gli stessi tipi di `EventoRivelazione` ed `EventoSintesi` del sito.
sealed class EventoLettura {
  const EventoLettura();
}

/// `carta`: la carta della posizione appena rivelata.
class EventoCarta extends EventoLettura {
  /// La carta rivelata.
  const EventoCarta({
    required this.posizione,
    required this.carta,
    required this.rovescio,
    required this.calcolata,
    required this.doppiaValenza,
    this.dignita,
  });

  /// La posizione nella stesa.
  final int posizione;

  /// La carta.
  final Carta carta;

  /// Rovesciata.
  final bool rovescio;

  /// Una posizione calcolata (la carta non si sceglie).
  final bool calcolata;

  /// La carta vale in due modi in questa posizione.
  final bool doppiaValenza;

  /// Le dignità elementali.
  final Dignita? dignita;
}

/// `token`: un pezzo di testo da aggiungere.
class EventoToken extends EventoLettura {
  /// Un pezzo di testo.
  const EventoToken(this.testo, {this.posizione});

  /// Il testo da aggiungere.
  final String testo;

  /// A quale carta va: c'è solo nello svelamento di tutte le carte (`POST /readings/{id}/reveal-all`).
  final int? posizione;
}

/// `sostituisci`: il testo scritto finora va sostituito (la guardia l'ha riscritto).
class EventoSostituisci extends EventoLettura {
  /// Il testo nuovo.
  const EventoSostituisci(this.testo, {this.posizione});

  /// Il testo che prende il posto di quello mostrato.
  final String testo;

  /// A quale carta va (solo nello svelamento di tutte le carte).
  final int? posizione;
}

/// `errore`: il modello non ha risposto; il messaggio è già nella lingua della lettura.
class EventoErrore extends EventoLettura {
  /// Un errore.
  const EventoErrore(this.messaggio, {this.posizione});

  /// Il messaggio del server.
  final String messaggio;

  /// La carta rimasta senza spiegazione (solo nello svelamento di tutte le carte).
  final int? posizione;
}

/// `fase`: la sintesi è passata a un'altra fase (`unione`, `guardia`, `revisione`, `responso`).
class EventoFase extends EventoLettura {
  /// Una fase.
  const EventoFase(this.fase, {this.guardia});

  /// Il nome della fase.
  final String fase;

  /// L'esito della guardia, nella fase `responso`.
  final String? guardia;
}

/// `battito`: il server è vivo, il responso è in preparazione.
class EventoBattito extends EventoLettura {
  /// Un battito.
  const EventoBattito();
}

/// `fine` di una rivelazione: l'interpretazione completa della posizione.
class EventoFineRivelazione extends EventoLettura {
  /// La fine di una rivelazione.
  const EventoFineRivelazione({required this.posizione, required this.interpretazione, required this.ultima});

  /// La posizione.
  final int posizione;

  /// Il testo completo.
  final String interpretazione;

  /// Era l'ultima posizione da rivelare.
  final bool ultima;
}

/// `fine` della sintesi: il responso è completo, con i dati per verificare il sorteggio.
class EventoFineSintesi extends EventoLettura {
  /// La fine della sintesi.
  const EventoFineSintesi({
    required this.disclaimer,
    required this.guardia,
    required this.commitment,
    required this.deckSalt,
    this.saldo,
    this.anonimo = false,
  });

  /// L'avvertenza da mostrare sotto il responso.
  final String disclaimer;

  /// L'esito della guardia.
  final String guardia;

  /// L'impronta del mazzo sigillato prima della scelta.
  final String commitment;

  /// Il sale rivelato a lettura conclusa.
  final String deckSalt;

  /// Il saldo dei crediti dopo la lettura.
  final int? saldo;

  /// Un visitatore senza account: il testo ricevuto è l'anteprima, non il responso.
  final bool anonimo;
}

/// Un evento che questa versione dell'app non conosce: si ignora, non si interrompe la lettura.
class EventoSconosciuto extends EventoLettura {
  /// Un evento sconosciuto.
  const EventoSconosciuto(this.grezzo);

  /// L'evento così com'è arrivato.
  final EventoSse grezzo;
}

/// Da quale flusso viene un evento: cambia il significato di `fine`.
enum Flusso {
  /// `POST /readings/{id}/reveal/{posizione}` e `POST /readings/{id}/reveal-all` (una `fine` per carta).
  rivelazione,

  /// `POST /readings/{id}/synthesis`.
  sintesi,
}

String _testo(Map<String, Object?> d, String chiave) => d[chiave] is String ? d[chiave] as String : '';
int _intero(Map<String, Object?> d, String chiave) => d[chiave] is num ? (d[chiave] as num).toInt() : 0;
bool _vero(Map<String, Object?> d, String chiave) => d[chiave] == true;
int? _posizione(Map<String, Object?> d) => d['posizione'] is num ? (d['posizione']! as num).toInt() : null;

/// Un evento grezzo → il suo tipo.
EventoLettura tipizza(EventoSse e, Flusso flusso) {
  final d = e.dati;
  switch (e.nome) {
    case 'carta':
      final dignita = d['dignita'];
      return EventoCarta(
        posizione: _intero(d, 'posizione'),
        carta: Carta.fromJson(d['carta']! as Map<String, Object?>),
        rovescio: _vero(d, 'rovescio'),
        calcolata: _vero(d, 'calcolata'),
        doppiaValenza: _vero(d, 'doppia_valenza'),
        dignita: dignita is Map<String, Object?> ? Dignita.fromJson(dignita) : null,
      );
    case 'token':
      return EventoToken(_testo(d, 'testo'), posizione: _posizione(d));
    case 'sostituisci':
      return EventoSostituisci(_testo(d, 'testo'), posizione: _posizione(d));
    case 'errore':
      return EventoErrore(_testo(d, 'messaggio'), posizione: _posizione(d));
    case 'fase':
      return EventoFase(_testo(d, 'fase'), guardia: d['guardia'] as String?);
    case 'battito':
      return const EventoBattito();
    case 'fine' when flusso == Flusso.rivelazione:
      return EventoFineRivelazione(
        posizione: _intero(d, 'posizione'),
        interpretazione: _testo(d, 'interpretazione'),
        ultima: _vero(d, 'ultima'),
      );
    case 'fine':
      return EventoFineSintesi(
        disclaimer: _testo(d, 'disclaimer'),
        guardia: _testo(d, 'guardia'),
        commitment: _testo(d, 'commitment'),
        deckSalt: _testo(d, 'deck_salt'),
        saldo: d['saldo'] is num ? (d['saldo']! as num).toInt() : null,
        anonimo: _vero(d, 'anonimo'),
      );
    default:
      return EventoSconosciuto(e);
  }
}
