/// Le rotte dell'app: gli stessi percorsi del sito (`frontend/v2/lib/percorsi.ts`), coi nomi delle cartelle.
///
/// Un collegamento del sito (`https://tarots.chat/cards/maj-17`) apre la stessa pagina nell'app, e le statistiche
/// di app e sito si sommano pagina per pagina.
abstract final class R {
  static const String home = '/';
  static const String leggi = '/read';
  static const String fisica = '/physical-reading';
  static const String storia = '/my-story';
  static String lettura(String id) => '/my-story/${Uri.encodeComponent(id)}';
  static const String condivise = '/shared';
  static String condivisa(String token) => '/shared/${Uri.encodeComponent(token)}';
  static const String giorno = '/daily-card';
  static const String carte = '/cards';
  static String carta(String id) => '/cards/${Uri.encodeComponent(id)}';
  static const String stese = '/spreads';
  static String stesa(String id) => '/spreads/${Uri.encodeComponent(id)}';
  static const String mazzi = '/decks';
  static String mazzo(String slug) => '/decks/${Uri.encodeComponent(slug)}';
  static const String voto = '/vote';
  static const String negozio = '/shop';
  static const String carrello = '/cart';
  static const String prezzi = '/pricing';
  static const String esplora = '/explore';

  /// La prova gratuita (v9, Fase 2b): stesso nome in tutte le lingue.
  static const String prova = '/trial';
  static const String blog = '/blog';
  static String articolo(String slug) => '/blog/${Uri.encodeComponent(slug)}';
  static String blogSezione(String slug) => '/blog/sezione/${Uri.encodeComponent(slug)}';
  static String blogTag(String slug) => '/blog/tag/${Uri.encodeComponent(slug)}';
  static const String profilo = '/profile';
  static const String privacy = '/privacy';

  /// La cancellazione dell'account (GDPR, Fase 1).
  static const String elimina = '/account/elimina';
}
