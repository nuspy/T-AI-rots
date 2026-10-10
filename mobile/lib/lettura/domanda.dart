/// Quando una domanda basta per partire (10/10/2026): almeno due parole, prima i pulsanti d'invio restano spenti. Le
/// scritture che non separano le parole (cinese, giapponese) contano i caratteri: ne bastano quattro. La stessa regola
/// del sito (`frontend/v2/lettura/domanda.ts`).
library;

final RegExp _senzaSpazi = RegExp(r'[぀-ヿ㐀-鿿]');
final RegExp _lettera = RegExp(r'\p{L}', unicode: true);

/// Se la domanda ha almeno due parole (con almeno una lettera ciascuna), o quattro caratteri in cinese o giapponese.
bool domandaBasta(String testo) {
  final pulito = testo.trim();
  if (_senzaSpazi.hasMatch(pulito)) return pulito.replaceAll(RegExp(r'\s'), '').runes.length >= 4;
  return pulito.split(RegExp(r'\s+')).where(_lettera.hasMatch).length >= 2;
}
