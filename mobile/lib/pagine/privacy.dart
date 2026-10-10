/// Metodo e privacy (`frontend/v2/pagine/privacy.tsx`): l'informativa completa (GDPR, artt. 13-14) — il titolare e i
/// contatti, le scelte, le finalità con le basi giuridiche, letture e memoria, l'AI, i dati particolari, l'accesso coi
/// social, le statistiche, i responsabili e i trasferimenti, la conservazione, i diritti, l'età.
///
/// I dati del titolare e i fornitori dell'AI vengono dalla console (`GET /privacy/titolare`, Fase 2c); se l'API non li
/// sa dire la pagina usa i ripieghi del sito. «Le tue scelte» qui riguardano il telefono: i testi sono quelli dell'app
/// (`app_scelte_*`, `app_consenso_*`); la pubblicità non c'è nell'app, quindi nemmeno la sua scelta e il suo paragrafo.
///
/// 10/10/2026: l'informativa è scritta solo in inglese (l'originale, come i termini di servizio): il testo viene sempre
/// dall'inglese e il telefono lo traduce nella lingua di lettura, come articoli, carte e stese, con la nota che
/// l'originale è l'inglese. Restano nella lingua dell'app le parti da usare: le scelte del telefono e i bottoni.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../cassa/pagamento.dart' show apriFuori;
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../consensi/consensi.dart';
import '../l10n/testi.dart';
import '../modelli/privacy.dart';
import '../profilo/comuni.dart';
import '../profilo/dati_account.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import '../traduzione/con_traduzione.dart';

/// I nomi dei paesi dei fornitori dell'AI che si incontrano davvero (`Intl.DisplayNames` del sito, che Dart non ha),
/// in inglese e in italiano; altrove il codice.
const Map<String, Map<String, String>> _paesi = {
  'US': {'en': 'United States', 'it': 'Stati Uniti'},
  'CN': {'en': 'China', 'it': 'Cina'},
  'FR': {'en': 'France', 'it': 'Francia'},
  'DE': {'en': 'Germany', 'it': 'Germania'},
  'GB': {'en': 'United Kingdom', 'it': 'Regno Unito'},
  'IE': {'en': 'Ireland', 'it': 'Irlanda'},
  'IT': {'en': 'Italy', 'it': 'Italia'},
  'NL': {'en': 'Netherlands', 'it': 'Paesi Bassi'},
  'CA': {'en': 'Canada', 'it': 'Canada'},
  'JP': {'en': 'Japan', 'it': 'Giappone'},
};

/// «NVIDIA (Stati Uniti), DeepSeek (Cina), LM Studio (su un nostro server, nessun terzo)».
String elencoFornitori(List<FornitoreAi> fornitori, String lingua, String proprio, String vuoto) {
  if (fornitori.isEmpty) return vuoto;
  return fornitori
      .map((f) {
        final paese = f.paese == null
            ? ''
            : (_paesi[f.paese!.toUpperCase()]?[lingua == 'it' ? 'it' : 'en'] ?? f.paese!);
        final dove = f.proprio ? proprio : paese;
        return dove.isEmpty ? f.nome : '${f.nome} ($dove)';
      })
      .join(', ');
}

/// I testi di privacy e termini: sempre quelli inglesi (l'originale), qualunque sia la lingua dell'app.
AppLocalizations get testiInglesi => lookupAppLocalizations(const Locale('en'));

/// La pagina della privacy.
class PaginaPrivacy extends ConsumerStatefulWidget {
  /// La pagina.
  const PaginaPrivacy({super.key});

  @override
  ConsumerState<PaginaPrivacy> createState() => _PaginaPrivacyState();
}

class _PaginaPrivacyState extends ConsumerState<PaginaPrivacy> {
  bool _salvando = false;
  bool _errore = false;

  Future<void> _cambia(String tipo, bool acceso) async {
    setState(() {
      _salvando = true;
      _errore = false;
    });
    await ref.read(consensiProvider.notifier).scegli({tipo: acceso ? 'accettato' : 'rifiutato'});
    if (!mounted) return;
    setState(() {
      _salvando = false;
      // La scelta vale sul telefono; se il server non l'ha ricevuta, si riprova al prossimo avvio (come il primo avvio).
      _errore = ref.read(consensiProvider).daSincronizzare;
    });
  }

  @override
  Widget build(BuildContext context) {
    // `t` è la lingua dell'app (le scelte e i bottoni), `en` l'informativa, che passa da `tr`.
    final t = context.t;
    final en = testiInglesi;
    final titolare = ref.watch(titolareProvider).value;
    final consensi = ref.watch(consensiProvider);
    final piccolo = Stile.sans(13.44, colore: Token.ink, altezza: 1.6);
    final collegamento = Stile.sans(13.44, altezza: 1.6);
    final valori = (
      hosting: (titolare?.hosting?.isNotEmpty ?? false) ? titolare!.hosting! : en.privacy_hosting_vuoto,
      fornitori: titolare == null
          ? '…'
          : elencoFornitori(titolare.fornitoriAi, 'en', en.privacy_fornitori_ai_proprio, en.privacy_fornitori_ai_vuoto),
    );

    Widget bottone(String testo, String href) => Bottone(testo, href: href, variante: Variante.quieto, piccolo: true);

    return conTestiRaccolti(
      da: 'en',
      pagina: (tr, avviso) {
        final celle = <CellaProfilo>[
          (
            widget: Sezione(
              titolo: tr(en.privacy_custode_titolo),
              children: titolare == null
                  ? [TestoPiccolo(tr(en.privacy_custode_testo_senza_nome), tenue: true, sotto: 0)]
                  : [
                      TestoPiccolo(
                        tr(
                          titolare.nome == null
                              ? en.privacy_custode_testo_senza_nome
                              : en.privacy_custode_testo(titolare.nome!),
                        ),
                      ),
                      TestoPiccolo(
                        tr(
                          titolare.indirizzo == null
                              ? en.privacy_custode_indirizzo_vuoto
                              : en.privacy_custode_indirizzo(titolare.indirizzo!),
                        ),
                      ),
                      if (titolare.codiceFiscale != null)
                        TestoPiccolo(tr(en.privacy_custode_codice(titolare.codiceFiscale!))),
                      if (titolare.emailPrivacy == null)
                        TestoPiccolo(tr(en.privacy_custode_email_vuoto))
                      else
                        Padding(
                          padding: const EdgeInsets.only(bottom: 13.44),
                          child: Wrap(
                            crossAxisAlignment: WrapCrossAlignment.center,
                            children: [
                              // Lo spazio fuori dalla traduzione: ML Kit lo perderebbe.
                              Text('${tr(en.privacy_custode_email('').trim())} ', style: piccolo),
                              CollegamentoEsterno(
                                testo: titolare.emailPrivacy!,
                                url: 'mailto:${titolare.emailPrivacy}',
                                stile: collegamento,
                              ),
                            ],
                          ),
                        ),
                      TestoPiccolo(
                        tr(
                          titolare.dpo.nominato && titolare.dpo.contatto != null
                              ? en.privacy_custode_dpo(titolare.dpo.contatto!)
                              : en.privacy_custode_dpo_no,
                        ),
                        sotto: 0,
                      ),
                    ],
            ),
            larga: true,
          ),
          // Le scelte del telefono: nella lingua dell'app, fuori dalla traduzione.
          (
            widget: Sezione(
              titolo: t.app_scelte_titolo,
              children: [
                TestoPiccolo(t.app_scelte_testo),
                Padding(
                  padding: const EdgeInsets.only(top: 3.2, bottom: 12.8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      for (final (i, s) in [
                        ('statistiche', t.app_consenso_statistiche, t.app_consenso_statistiche_testo),
                        ('google_analytics', t.app_consenso_google, t.app_consenso_google_testo),
                      ].indexed)
                        Container(
                          decoration: i == 0
                              ? null
                              : const BoxDecoration(
                                  border: Border(top: BorderSide(color: Token.line)),
                                ),
                          child: _Scelta(
                            valore: consensi.accettato(s.$1),
                            attiva: !_salvando,
                            titolo: s.$2,
                            testo: s.$3,
                            alCambio: (v) => unawaited(_cambia(s.$1, v)),
                          ),
                        ),
                    ],
                  ),
                ),
                if (_errore) Errore(t.comune_err_operazione, sopra: 0),
                TestoPiccolo(
                  t.privacy_scelte_account,
                  sotto: 0,
                  figlio: Collegamento('${t.privacy_scelte_account_cta}.', href: R.profilo, stile: collegamento),
                ),
              ],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_finalita_titolo),
              children: [
                TestoPiccolo(tr(en.privacy_finalita_intro)),
                // `.privacy-finalita`: una voce per uso, con la base giuridica tenue.
                for (final v in en.privacyFinalita)
                  Container(
                    margin: const EdgeInsets.only(bottom: 11.2),
                    padding: const EdgeInsets.only(bottom: 9.6),
                    decoration: const BoxDecoration(
                      border: Border(bottom: BorderSide(color: Token.line)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          tr(v.cosa),
                          style: Stile.sans(14.4, peso: FontWeight.w700, colore: Token.ink),
                        ),
                        const SizedBox(height: 3.2),
                        Text.rich(
                          TextSpan(
                            style: piccolo,
                            children: [
                              TextSpan(text: '${tr(v.perche)} '),
                              TextSpan(
                                text: tr(v.base),
                                style: const TextStyle(color: Token.inkSoft),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_letture_titolo),
              children: [
                TestoPiccolo(tr(en.privacy_letture_testo)),
                Align(alignment: AlignmentDirectional.centerStart, child: bottone(t.privacy_letture_cta, R.storia)),
              ],
            ),
            larga: false,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_ai_titolo),
              children: [TestoPiccolo(tr(en.privacy_ai_testo), sotto: 0)],
            ),
            larga: false,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_art9_titolo),
              children: [TestoPiccolo(tr(en.privacy_art9_testo)), TestoPiccolo(tr(en.privacy_art9_crisi), sotto: 0)],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_social_titolo),
              children: [
                TestoPiccolo(tr(en.privacy_social_account)),
                TestoPiccolo(tr(en.privacy_social_cosa)),
                TestoPiccolo(tr(en.privacy_social_perche)),
                TestoPiccolo(tr(en.privacy_social_posizione)),
                TestoPiccolo(tr(en.privacy_social_controllo)),
                Align(alignment: AlignmentDirectional.centerStart, child: bottone(t.privacy_social_cta, R.profilo)),
              ],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_stat_titolo),
              children: [
                TestoPiccolo(tr(en.privacy_stat_anonime)),
                TestoPiccolo(tr(en.privacy_stat_account)),
                TestoPiccolo(tr(en.privacy_stat_esteso)),
                TestoPiccolo(tr(en.privacy_stat_google)),
                TestoPiccolo(tr(en.privacy_stat_conservazione)),
                Wrap(
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Text('${tr(en.privacy_stat_geo)} ', style: piccolo),
                    CollegamentoEsterno(
                      testo: 'IP Geolocation by DB-IP',
                      url: 'https://db-ip.com',
                      stile: collegamento,
                    ),
                    Text(' (CC BY 4.0)', style: piccolo),
                  ],
                ),
              ],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_responsabili_titolo),
              children: [
                TestoPiccolo(tr(en.privacy_responsabili_intro)),
                Padding(
                  padding: const EdgeInsets.only(top: 6.4, bottom: 12.8),
                  child: ElencoPuntato(
                    voci: [
                      for (final r in en.privacyResponsabili(hosting: valori.hosting, fornitori_ai: valori.fornitori))
                        TestoConGrassetto(grassetto: tr(r.chi), resto: ' — ${tr(r.cosa)}'),
                    ],
                  ),
                ),
                TestoPiccolo(tr(en.privacy_trasferimenti), sotto: 0),
              ],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_conservazione_titolo),
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 6.4, bottom: 12.8),
                  child: ElencoPuntato(voci: [for (final v in en.privacyConservazione) Text(tr(v), style: piccolo)]),
                ),
              ],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              titolo: tr(en.privacy_diritti_titolo),
              children: [
                TestoPiccolo(tr(en.privacy_diritti_testo)),
                TestoPiccolo(tr(en.privacy_diritti_come)),
                FilaBottoni(
                  children: [
                    bottone(t.privacy_diritti_cta_dati, R.profilo),
                    bottone(t.privacy_diritti_cta_elimina, R.elimina),
                  ],
                ),
                TitoloPannello(tr(en.privacy_garante_titolo)),
                TestoPiccolo(tr(en.privacy_garante_testo), sotto: 0),
              ],
            ),
            larga: true,
          ),
          (
            widget: Sezione(
              id: 'pv-eta',
              titolo: tr(en.privacy_eta_titolo),
              children: [TestoPiccolo(tr(en.privacy_eta_testo), sotto: 0)],
            ),
            larga: true,
          ),
          (widget: TestoPiccolo(tr(en.privacy_versione), tenue: true, sotto: 0), larga: true),
        ];
        return Pagina(
          sezioni: [
            Sottotitolo(
              eyebrow: tr(en.privacy_eyebrow),
              titolo: tr(en.privacy_titolo),
              intro: tr(en.privacy_intro),
              compatta: true,
            ),
            Fascia(
              compatta: true,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  avviso,
                  NotaOriginale(tr(en.termini_originale)),
                  GrigliaProfilo(celle: celle),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

/// «L'originale è l'inglese» (`termini.originale`, generico): sopra il testo di privacy e termini.
class NotaOriginale extends StatelessWidget {
  /// La nota, già tradotta.
  const NotaOriginale(this.testo, {super.key});

  /// Il testo.
  final String testo;

  @override
  Widget build(BuildContext context) => TestoPiccolo(testo, tenue: true);
}

/// Una scelta del telefono: come le caselle del profilo, senza la riga dello stato (come la pagina del sito).
class _Scelta extends StatelessWidget {
  const _Scelta({
    required this.valore,
    required this.attiva,
    required this.titolo,
    required this.testo,
    required this.alCambio,
  });

  final bool valore;
  final bool attiva;
  final String titolo;
  final String testo;
  final ValueChanged<bool> alCambio;

  @override
  Widget build(BuildContext context) =>
      Casella(valore: valore, attiva: attiva, titolo: titolo, testo: testo, alCambio: alCambio);
}

/// Un collegamento fuori dall'app (la posta, un sito), sottolineato d'ottone come `a.inline`.
class CollegamentoEsterno extends StatelessWidget {
  /// Un collegamento a [url].
  const CollegamentoEsterno({super.key, required this.testo, required this.url, required this.stile});

  /// Il testo.
  final String testo;

  /// Dove porta (`mailto:`, `https:`).
  final String url;

  /// Lo stile del testo.
  final TextStyle stile;

  @override
  Widget build(BuildContext context) => Premibile(
    alTocco: () => unawaited(apriFuori(url)),
    collegamento: true,
    costruisci: (context, premuto) => ConstrainedBox(
      constraints: const BoxConstraints(minHeight: 44),
      child: Align(
        alignment: AlignmentDirectional.centerStart,
        widthFactor: 1,
        heightFactor: 1,
        child: TestoSottolineato(testo, stile: stile, colore: premuto ? Token.verdigris : Token.plum),
      ),
    ),
  );
}
