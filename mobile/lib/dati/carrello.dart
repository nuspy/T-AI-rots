/// Il carrello (`frontend/v2/lib/carrello.tsx`): quali mazzi, in quale formato, quante copie. Vive sul telefono (la
/// stessa chiave e lo stesso formato del sito, `tarots.v2.carrello`), così resta fra un avvio e l'altro e prima
/// dell'accesso: chi compone il carrello senza account lo ritrova dopo essere entrato. Solo gli identificativi: prezzi,
/// sconti e totale li dice sempre il server (`POST /shop/quote`), mai l'app.
library;

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../archivio.dart';

/// I formati di un mazzo.
const List<String> tipiVoce = ['digitale', 'pdf', 'fisico'];

/// Le copie al massimo per riga.
const int maxQuantita = 20;

/// La chiave dell'archivio: la stessa del sito.
const String chiaveCarrello = 'tarots.v2.carrello';

/// Una riga del carrello.
@immutable
class VoceCarrello {
  /// Una riga.
  const VoceCarrello({required this.deckId, required this.tipo, required this.quantita});

  /// Il mazzo.
  final int deckId;

  /// `digitale`, `pdf`, `fisico`.
  final String tipo;

  /// Le copie (un mazzo digitale: sempre una).
  final int quantita;

  /// In JSON, come il sito.
  Map<String, Object?> inJson() => {'deckId': deckId, 'tipo': tipo, 'quantita': quantita};

  /// Per l'API (`POST /shop/quote`, `POST /orders`).
  ({int deckId, String tipo, int quantita}) get perApi => (deckId: deckId, tipo: tipo, quantita: quantita);

  VoceCarrello _con(int q) => VoceCarrello(deckId: deckId, tipo: tipo, quantita: q);

  @override
  bool operator ==(Object other) =>
      other is VoceCarrello && other.deckId == deckId && other.tipo == tipo && other.quantita == quantita;

  @override
  int get hashCode => Object.hash(deckId, tipo, quantita);
}

/// Le righe salvate, ripulite come fa il sito (`leggi()`): formati noti, copie fra 1 e 20, un digitale una volta sola.
List<VoceCarrello> leggiCarrello(String? testo) {
  if (testo == null) return const [];
  try {
    final grezzo = jsonDecode(testo);
    if (grezzo is! List) return const [];
    return [
      for (final v in grezzo)
        if (v is Map && v['deckId'] is num && tipiVoce.contains(v['tipo']))
          VoceCarrello(
            deckId: (v['deckId'] as num).toInt(),
            tipo: v['tipo'] as String,
            quantita: v['tipo'] == 'digitale'
                ? 1
                : ((v['quantita'] is num ? (v['quantita'] as num).floor() : 1).clamp(1, maxQuantita)),
          ),
    ];
  } on FormatException {
    return const [];
  }
}

/// Il carrello.
class Carrello extends Notifier<List<VoceCarrello>> {
  @override
  List<VoceCarrello> build() => leggiCarrello(ref.read(archivioProvider).leggi(chiaveCarrello));

  void _scrivi(List<VoceCarrello> dopo) {
    state = List.unmodifiable(dopo);
    unawaited(ref.read(archivioProvider).scrivi(chiaveCarrello, jsonEncode([for (final v in dopo) v.inJson()])));
  }

  /// Aggiunge una copia (un mazzo digitale si possiede una volta sola: una seconda copia non ha senso).
  void aggiungi(int deckId, String tipo) {
    final c = state.where((v) => v.deckId == deckId && v.tipo == tipo).firstOrNull;
    if (c == null) {
      _scrivi([...state, VoceCarrello(deckId: deckId, tipo: tipo, quantita: 1)]);
      return;
    }
    final q = tipo == 'digitale' ? 1 : (c.quantita + 1).clamp(1, maxQuantita);
    _scrivi([for (final v in state) v == c ? v._con(q) : v]);
  }

  /// Cambia le copie di una riga; sotto 1 la riga si toglie.
  void quantita(int deckId, String tipo, int n) {
    _scrivi([
      for (final v in state)
        if (v.deckId != deckId || v.tipo != tipo)
          v
        else if (n >= 1)
          v._con(n.clamp(1, tipo == 'digitale' ? 1 : maxQuantita)),
    ]);
  }

  /// Toglie una riga.
  void togli(int deckId, String tipo) => _scrivi([
    for (final v in state)
      if (v.deckId != deckId || v.tipo != tipo) v,
  ]);

  /// Svuota il carrello (dopo l'ordine).
  void svuota() => _scrivi(const []);
}

/// Il carrello dell'app.
final carrelloProvider = NotifierProvider<Carrello, List<VoceCarrello>>(Carrello.new);
