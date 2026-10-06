/// v9.5: tradurre il markdown di un articolo senza romperlo. Il motore traduce frasi, non markdown: le parti che non
/// vanno toccate (immagini, scorciatoie `[[card:the-tower]]`, codice, indirizzi) si sostituiscono con segnaposto prima
/// di tradurre e si rimettono dopo; di un collegamento `[testo](indirizzo)` si traduce solo il testo, a parte. Se la
/// traduzione perde un segnaposto, la riga resta com'era: meglio l'originale che un collegamento rotto.
///
/// Si traduce riga per riga (negli articoli un paragrafo è una riga), tenendo il prefisso markdown (`## `, `- `,
/// `1. `, `> `); le righe di codice, le tabelle e le righe vuote restano com'erano.
library;

/// Una funzione che traduce una frase.
typedef TraduciFrase = Future<String> Function(String frase);

final RegExp _lettere = RegExp(r'\p{L}', unicode: true);
final RegExp _prefisso = RegExp(r'^(\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+|>\s*)*)');
final RegExp _protetti = RegExp(
  r'!\[[^\]]*\]\([^)]*\)' // un'immagine
  r'|\[\[[^\]]*\]\]' // una scorciatoia del sito
  r'|`[^`]*`' // codice in linea
  r'|<[^>]+>' // un'etichetta HTML
  r'|https?://\S+', // un indirizzo
);
// Non un'immagine (`![…](…)`, che resta intera): solo un collegamento.
final RegExp _collegamento = RegExp(r'(?<!!)\[([^\]]+)\]\(([^)]*)\)');

String _segnaposto(int n) => 'XQZ${n}ZQX';

/// Traduce una riga di testo semplice (o di markdown) con [traduci], proteggendone le parti fisse.
Future<String> traduciRiga(String riga, TraduciFrase traduci) async {
  if (!_lettere.hasMatch(riga)) return riga;
  final prefisso = _prefisso.firstMatch(riga)?.group(1) ?? '';
  var corpo = riga.substring(prefisso.length);
  final fissi = <String>[];
  // Prima i collegamenti: il loro testo si traduce a parte, l'indirizzo resta.
  final collegamenti = _collegamento.allMatches(corpo).toList();
  for (final m in collegamenti.reversed) {
    final testo = m.group(1)!;
    final tradotto = _lettere.hasMatch(testo) && !testo.startsWith('[') ? await traduci(testo) : testo;
    fissi.add('[$tradotto](${m.group(2)})');
    corpo = corpo.replaceRange(m.start, m.end, _segnaposto(fissi.length - 1));
  }
  corpo = corpo.replaceAllMapped(_protetti, (m) {
    fissi.add(m.group(0)!);
    return _segnaposto(fissi.length - 1);
  });
  if (!_lettere.hasMatch(corpo.replaceAll(RegExp(r'XQZ\d+ZQX'), ''))) return riga;
  var tradotto = await traduci(corpo);
  for (var i = 0; i < fissi.length; i++) {
    final segno = _segnaposto(i);
    if (!tradotto.contains(segno)) return riga;
    tradotto = tradotto.replaceFirst(segno, fissi[i]);
  }
  return '$prefisso$tradotto';
}

/// Traduce un testo markdown riga per riga (vedi sopra).
Future<String> traduciMarkdown(String testo, TraduciFrase traduci) async {
  final righe = testo.split('\n');
  final fuori = <String>[];
  var inCodice = false;
  for (final riga in righe) {
    final pulita = riga.trimLeft();
    if (pulita.startsWith('```') || pulita.startsWith('~~~')) {
      inCodice = !inCodice;
      fuori.add(riga);
    } else if (inCodice || pulita.startsWith('|') || pulita.isEmpty) {
      fuori.add(riga);
    } else {
      fuori.add(await traduciRiga(riga, traduci));
    }
  }
  return fuori.join('\n');
}
