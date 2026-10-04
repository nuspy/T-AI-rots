// Il parser SSE della lettura: lo stesso formato di `_sse()` (backend/tarot_core/api/routers/readings.py) e lo stesso
// comportamento di `flusso()` (frontend/lib/api.ts).

import 'dart:async';
import 'dart:convert';

import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/api/api.dart';
import 'package:tarots/api/client.dart';
import 'package:tarots/api/errori.dart';
import 'package:tarots/api/sse.dart';

import 'aiuti/finti.dart';

/// Un evento come lo scrive il server.
String sse(String evento, Object dati) => 'event: $evento\ndata: ${jsonEncode(dati)}\n\n';

Stream<List<int>> pezzi(List<List<int>> p) => Stream.fromIterable(p);

List<int> byte(String s) => utf8.encode(s);

Future<List<EventoSse>> leggi(List<List<int>> p) => leggiSse(pezzi(p)).toList();

const Map<String, Object?> cartaMinima = {
  'id': 'maj-17',
  'arcano': 'maggiore',
  'nome_thoth': 'The Star',
  'nome_it': 'La Stella',
  'elemento': 'aria',
  'astrologia': 'Aquarius',
};

void main() {
  group('leggiSse', () {
    test('legge eventi interi in un pezzo solo', () async {
      final eventi = await leggi([
        byte(sse('token', {'testo': 'Ciao'}) + sse('fine', {'posizione': 1})),
      ]);
      expect(eventi.map((e) => e.nome), ['token', 'fine']);
      expect(eventi.first.dati, {'testo': 'Ciao'});
    });

    test('ricompone un evento spezzato in più pacchetti, anche a metà della riga vuota', () async {
      final testo = sse('token', {'testo': 'uno'}) + sse('token', {'testo': 'due'});
      final tagli = [3, 10, 25, testo.indexOf('\n\n') + 1, testo.length - 1];
      final p = <List<int>>[];
      var da = 0;
      for (final a in tagli) {
        p.add(byte(testo.substring(da, a)));
        da = a;
      }
      p.add(byte(testo.substring(da)));
      final eventi = await leggi(p);
      expect(eventi.map((e) => e.dati['testo']), ['uno', 'due']);
    });

    test('un carattere accentato spezzato fra due pacchetti resta intero (UTF-8 a flusso)', () async {
      final b = byte(sse('token', {'testo': 'perché è così'}));
      final metaE = b.indexOf(0xC3) + 1; // dentro «é»
      final eventi = await leggi([b.sublist(0, metaE), b.sublist(metaE)]);
      expect(eventi.single.dati['testo'], 'perché è così');
    });

    test('accetta anche CRLF, ignora i commenti e le righe sconosciute', () async {
      final eventi = await leggi([byte(': tieni vivo\r\nevent: battito\r\ndata: {}\r\nid: 7\r\n\r\n')]);
      expect(eventi.single.nome, 'battito');
      expect(eventi.single.dati, isEmpty);
    });

    test('un evento senza dati ha dati vuoti; un blocco senza nome si salta', () async {
      final eventi = await leggi([byte('event: battito\n\ndata: {"x": 1}\n\n')]);
      expect(eventi.length, 1);
      expect(eventi.single.dati, isEmpty);
    });

    test('più righe data: si concatenano, come nel sito', () async {
      final eventi = await leggi([byte('event: token\ndata: {"testo":\ndata:  "a"}\n\n')]);
      expect(eventi.single.dati, {'testo': 'a'});
    });

    test('un blocco rimasto a metà alla fine del flusso si scarta', () async {
      final eventi = await leggi([
        byte('${sse('token', {'testo': 'a'})}event: token\ndata: {"testo": "b"}'),
      ]);
      expect(eventi.map((e) => e.dati['testo']), ['a']);
    });

    test('dati che non sono JSON fermano il flusso con un errore chiaro', () async {
      expect(leggi([byte('event: token\ndata: non json\n\n')]), throwsA(isA<ErroreSse>()));
      expect(leggi([byte('event: token\ndata: [1, 2]\n\n')]), throwsA(isA<ErroreSse>()));
    });
  });

  group('tipizza', () {
    test('rivelazione: carta, token, sostituisci, errore, fine', () {
      final carta = tipizza(
        const EventoSse('carta', {
          'posizione': 2,
          'carta': cartaMinima,
          'rovescio': true,
          'calcolata': false,
          'doppia_valenza': true,
          'dignita': {'elemento': 'aria', 'punteggio': 1, 'giudizio': 'buona', 'relazioni': <Object>[]},
        }),
        Flusso.rivelazione,
      );
      expect(carta, isA<EventoCarta>());
      carta as EventoCarta;
      expect((carta.posizione, carta.rovescio, carta.doppiaValenza, carta.carta.id), (2, true, true, 'maj-17'));
      expect(carta.dignita?.giudizio, 'buona');

      expect((tipizza(const EventoSse('token', {'testo': 'ab'}), Flusso.rivelazione) as EventoToken).testo, 'ab');
      expect(
        (tipizza(const EventoSse('sostituisci', {'testo': 'nuovo'}), Flusso.rivelazione) as EventoSostituisci).testo,
        'nuovo',
      );
      expect(
        (tipizza(const EventoSse('errore', {'messaggio': 'no'}), Flusso.rivelazione) as EventoErrore).messaggio,
        'no',
      );
      final fine = tipizza(
        const EventoSse('fine', {'posizione': 3, 'interpretazione': 'tutto', 'ultima': true}),
        Flusso.rivelazione,
      ) as EventoFineRivelazione;
      expect((fine.posizione, fine.interpretazione, fine.ultima), (3, 'tutto', true));
    });

    test('sintesi: fase, battito, fine con i dati della verifica', () {
      final fase =
          tipizza(const EventoSse('fase', {'fase': 'responso', 'guardia': 'ok'}), Flusso.sintesi) as EventoFase;
      expect((fase.fase, fase.guardia), ('responso', 'ok'));
      expect(tipizza(const EventoSse('battito', {}), Flusso.sintesi), isA<EventoBattito>());
      final fine = tipizza(
        const EventoSse('fine', {
          'disclaimer': 'd',
          'guardia': 'ok',
          'commitment': 'c',
          'deck_salt': 's',
          'saldo': 4,
          'anonimo': true,
        }),
        Flusso.sintesi,
      ) as EventoFineSintesi;
      expect((fine.deckSalt, fine.saldo, fine.anonimo), ('s', 4, true));
    });

    test('un evento sconosciuto non interrompe la lettura', () {
      expect(tipizza(const EventoSse('nuovo', {}), Flusso.sintesi), isA<EventoSconosciuto>());
    });
  });

  group('Api.rivela e Api.sintesi', () {
    Api api(AdattatoreFinto a) => Api(
      creaDio(
        base: 'http://api.prova',
        lingua: () => 'it',
        fonte: FonteFinta(attuale: 'tok'),
        cookie: CookieJar(),
        agente: 'prova',
        adattatore: a,
      ),
    );

    test('POST con Accept text/event-stream, eventi tipizzati nell\'ordine', () async {
      final a = AdattatoreFinto({
        'POST /readings/abc/reveal/1': (_) => RispostaFinta(
          200,
          pezzi: [
            byte(sse('carta', {'posizione': 1, 'carta': cartaMinima, 'rovescio': false, 'calcolata': false})),
            byte(sse('token', {'testo': 'La '})),
            byte(sse('token', {'testo': 'Stella'})),
            byte(sse('fine', {'posizione': 1, 'interpretazione': 'La Stella', 'ultima': false})),
          ],
          intestazioni: {
            Headers.contentTypeHeader: ['text/event-stream'],
          },
        ),
      });
      final eventi = await api(a).rivela('abc', 1).toList();
      expect(eventi.map((e) => e.runtimeType), [EventoCarta, EventoToken, EventoToken, EventoFineRivelazione]);
      final r = a.richieste.single;
      expect(r.method, 'POST');
      expect(r.headers['Accept'], 'text/event-stream');
      expect(r.headers['Authorization'], 'Bearer tok');
    });

    test('rivelaTutte: le carte, la fase «lettura», i testi con la loro posizione', () async {
      final a = AdattatoreFinto({
        'POST /readings/abc/reveal-all': (_) => RispostaFinta(
          200,
          pezzi: [
            byte(sse('carta', {'posizione': 1, 'carta': cartaMinima, 'rovescio': false, 'calcolata': false})),
            byte(sse('carta', {'posizione': 2, 'carta': cartaMinima, 'rovescio': true, 'calcolata': false})),
            byte(sse('fase', {'fase': 'lettura'})),
            byte(sse('battito', {})),
            byte(sse('token', {'posizione': 1, 'testo': 'Uno.'})),
            byte(sse('fine', {'posizione': 1, 'interpretazione': 'Uno.', 'ultima': false})),
            byte(sse('errore', {'posizione': 2, 'messaggio': 'non ora'})),
            byte(sse('fine', {'posizione': 2, 'interpretazione': '', 'ultima': true})),
          ],
        ),
      });
      final eventi = await api(a).rivelaTutte('abc').toList();
      expect(eventi.map((e) => e.runtimeType), [
        EventoCarta, EventoCarta, EventoFase, EventoBattito, EventoToken, EventoFineRivelazione, EventoErrore,
        EventoFineRivelazione,
      ]);
      expect((eventi[2] as EventoFase).fase, 'lettura');
      expect(((eventi[4] as EventoToken).posizione, (eventi[4] as EventoToken).testo), (1, 'Uno.'));
      expect((eventi[6] as EventoErrore).posizione, 2);
      expect((eventi[7] as EventoFineRivelazione).ultima, isTrue);
      // Lo svelamento di una carta sola non porta la posizione nei token: resta `null`.
      expect((tipizza(const EventoSse('token', {'testo': 'x'}), Flusso.rivelazione) as EventoToken).posizione, isNull);
    });

    test('un 409 diventa ErroreApi col motivo del server, senza riprovare', () async {
      final a = AdattatoreFinto({
        'POST /readings/abc/synthesis': (_) =>
            RispostaFinta.json({'detail': 'Le carte si rivelano in ordine'}, stato: 409),
      });
      await expectLater(
        api(a).sintesi('abc').toList(),
        throwsA(
          isA<ErroreApi>().having((e) => e.stato, 'stato', 409).having((e) => e.motivo, 'motivo', contains('ordine')),
        ),
      );
      expect(a.richieste.length, 1, reason: 'nessun riprova automatico');
    });

    test('chiudere l\'ascolto annulla la richiesta', () async {
      final a = AdattatoreFinto({
        'POST /readings/abc/synthesis': (_) => RispostaFinta(
          200,
          ritardo: const Duration(milliseconds: 20),
          pezzi: [for (var i = 0; i < 50; i++) byte(sse('battito', {}))],
        ),
      });
      final primo = await api(a).sintesi('abc').first;
      expect(primo, isA<EventoBattito>());
      await Future<void>.delayed(const Duration(milliseconds: 50));
      expect(a.annullata, isTrue);
      expect(a.richieste.length, 1);
    });
  });
}
