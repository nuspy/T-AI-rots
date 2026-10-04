/// Gli indirizzi del sito, da cartella dell'app a indirizzo che si vede e ritorno: lo stesso codice di
/// `frontend/lib/indirizzi.ts`, riscritto in Dart.
///
/// L'app usa internamente i percorsi delle cartelle del sito (`/cards/maj-17`, `/daily-card`), cioè le rotte di
/// go_router. Serve tradurli in due casi:
/// - un **collegamento** che arriva da fuori (`https://tarots.chat/it/carta-del-giorno`, un vecchio `/carte/x`):
///   [interno] lo porta alla rotta giusta;
/// - le **statistiche**: lanterna riceve dal sito l'indirizzo che si vede (`/card-of-the-day`,
///   `/it/carta-del-giorno`), e l'app manda lo stesso ([pubblico]), così le visite si sommano pagina per pagina.
library;

/// La lingua degli indirizzi: l'inglese alla radice, l'italiano sotto `/it`.
enum LinguaPubblica { en, it }

/// La lingua pubblica di una lingua dell'interfaccia: `it` è italiano, tutto il resto ricade sull'inglese.
LinguaPubblica linguaPubblica(String? lingua) => lingua == 'it' ? LinguaPubblica.it : LinguaPubblica.en;

/// Cartella (primo segmento) → segmento visibile per lingua.
const Map<String, Map<LinguaPubblica, String>> _segmenti = {
  'cards': {LinguaPubblica.en: 'cards', LinguaPubblica.it: 'carte'},
  'spreads': {LinguaPubblica.en: 'spreads', LinguaPubblica.it: 'stese'},
  'pricing': {LinguaPubblica.en: 'pricing', LinguaPubblica.it: 'piano'},
  'daily-card': {LinguaPubblica.en: 'card-of-the-day', LinguaPubblica.it: 'carta-del-giorno'},
};

/// Segmento visibile → cartella, per lingua.
final Map<LinguaPubblica, Map<String, String>> _inCartella = {
  for (final l in LinguaPubblica.values) l: {for (final e in _segmenti.entries) e.value[l]!: e.key},
};

/// I nomi della v1 → la cartella della v2 che ne fa le veci.
const Map<String, String> _dallaV1 = {
  'carte': 'cards',
  'stese': 'spreads',
  'piano': 'pricing',
  'carta-del-giorno': 'daily-card',
  'mazzo': 'decks',
  'deck': 'decks',
  'leggi': 'read',
  'letture': 'my-story',
  'profilo': 'profile',
  's': 'shared',
  'interpreta': 'physical-reading',
  'vota-mazzo': 'vote',
};

/// Le pagine personali o di servizio: non si indicizzano.
const Set<String> _private = {'read', 'my-story', 'profile', 'shared', 'cart'};

/// Vero per le pagine da indicizzare.
bool indicizzabile(String interno) {
  final parti = interno.split(RegExp(r'[/?#]'));
  return !_private.contains(parti.length > 1 ? parti[1] : '');
}

({String percorso, String coda}) _separa(String indirizzo) {
  final fine = indirizzo.indexOf(RegExp(r'[?#]'));
  return fine == -1
      ? (percorso: indirizzo, coda: '')
      : (percorso: indirizzo.substring(0, fine), coda: indirizzo.substring(fine));
}

bool _esterno(String indirizzo) => !indirizzo.startsWith('/') || indirizzo.startsWith('//');

/// Un indirizzo scritto coi nomi della v1 (`/carte/maj-17`, `/blog/section/x`) → quello interno della v2.
String normalizza(String interno) {
  if (_esterno(interno)) return interno;
  final (:percorso, :coda) = _separa(interno);
  final parti = percorso.split('/');
  final v2 = parti.length > 1 ? _dallaV1[parti[1]] : null;
  if (v2 != null) parti[1] = v2;
  if (parti.length > 2 && parti[1] == 'blog' && parti[2] == 'section') parti[2] = 'sezione';
  return parti.join('/') + coda;
}

/// Un indirizzo interno → quello che si vede nella lingua: `/cards/maj-17` o `/it/carte/maj-17`.
String pubblico(LinguaPubblica lingua, String interno) {
  if (_esterno(interno)) return interno;
  final (:percorso, :coda) = _separa(normalizza(interno));
  final parti = percorso.split('/');
  final segmento = parti.length > 1 ? _segmenti[parti[1]] : null;
  if (segmento != null) parti[1] = segmento[lingua]!;
  final unito = parti.join('/');
  final visibile = unito.isEmpty ? '/' : unito;
  if (lingua == LinguaPubblica.it) return '/it${visibile == '/' ? '' : visibile}$coda';
  return visibile + coda;
}

/// Il risultato di [risolvi]: la lingua dell'indirizzo, la rotta interna e, se l'indirizzo è vecchio o nell'altra
/// lingua, dove andrebbe reindirizzato.
typedef Risolto = ({LinguaPubblica lingua, String interno, bool pubblica, String? reindirizza});

/// Dall'indirizzo che si vede (senza query) a quello interno, con la lingua. È ciò che fa il proxy del sito.
Risolto risolvi(String percorso) {
  var lingua = LinguaPubblica.en;
  var p = percorso;
  if (p == '/it' || p.startsWith('/it/')) {
    lingua = LinguaPubblica.it;
    p = p.substring(3).isEmpty ? '/' : p.substring(3);
  }
  final parti = p.split('/');
  final primo = parti.length > 1 ? parti[1] : '';
  Risolto verso(String interno, [LinguaPubblica? l]) {
    final ll = l ?? lingua;
    return (lingua: ll, interno: interno, pubblica: indicizzabile(interno), reindirizza: pubblico(ll, interno));
  }

  // L'anteprima: `/v2/cards/x` → `/cards/x`.
  if (primo == 'v2') return verso(normalizza('/${parti.skip(2).join('/')}'));

  // Il segmento visibile della lingua: la pagina.
  final cartella = _inCartella[lingua]![primo];
  if (cartella != null) {
    parti[1] = cartella;
    return (lingua: lingua, interno: parti.join('/'), pubblica: true, reindirizza: null);
  }

  // Un vecchio indirizzo italiano senza `/it`: era la versione italiana.
  if (lingua == LinguaPubblica.en && _inCartella[LinguaPubblica.it]!.containsKey(primo)) {
    parti[1] = _inCartella[LinguaPubblica.it]![primo]!;
    return verso(parti.join('/'), LinguaPubblica.it);
  }

  // Il segmento dell'altra lingua o il nome della cartella dove si vede un nome diverso.
  final altraLingua = lingua == LinguaPubblica.en ? LinguaPubblica.it : LinguaPubblica.en;
  final altra = _inCartella[altraLingua]![primo] ?? (_segmenti.containsKey(primo) ? primo : null);
  if (altra != null) {
    parti[1] = altra;
    return verso(parti.join('/'));
  }

  // I nomi della v1 e `/blog/section/…`. Il vecchio `/mazzo` senza `/it` era la pagina italiana.
  if (lingua == LinguaPubblica.en && primo == 'mazzo') return verso(normalizza(p), LinguaPubblica.it);
  if (_dallaV1.containsKey(primo) || (primo == 'blog' && parti.length > 2 && parti[2] == 'section')) {
    return verso(normalizza(p));
  }

  return (lingua: lingua, interno: p, pubblica: indicizzabile(p), reindirizza: null);
}

/// Il percorso interno di un indirizzo visibile (`/it/carte/la-stella` → `/cards/la-stella`).
String interno(String percorso) {
  final r = risolvi(percorso);
  final verso = r.reindirizza;
  return verso != null ? risolvi(verso).interno : r.interno;
}
