/// I termini di servizio (10/10/2026, `frontend/v2/i18n/en/termini.ts`): l'accordo fra chi usa TAROTS chat e noi.
///
/// Sono scritti solo in inglese, l'originale che vale: la pagina prende sempre i testi inglesi e il telefono li traduce
/// nella lingua di lettura (ML Kit, come articoli, carte e stese), col riquadro della traduzione e la nota che
/// l'originale è l'inglese. Chi siamo viene dalla console come nella privacy (`GET /privacy/titolare`); senza un dato
/// restano le frasi neutre del dizionario. Stesso aspetto della privacy: pannelli uno sotto l'altro.
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/bottoni.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../profilo/comuni.dart';
import '../profilo/dati_account.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import '../traduzione/con_traduzione.dart';
import 'privacy.dart' show CollegamentoEsterno, NotaOriginale, testiInglesi;

/// Le sezioni dei termini (`termini.sezioni`): un elenco di elenchi, che `liste.g.dart` non ricompone, quindi le voci
/// dell'ARB si leggono qui una per una. Se il dizionario cambia, `termini_test.dart` se ne accorge.
List<({String titolo, List<String> testi})> sezioniTermini(AppLocalizations en) => [
  (
    titolo: en.termini_sezioni_0_titolo,
    testi: [en.termini_sezioni_0_testi_0, en.termini_sezioni_0_testi_1, en.termini_sezioni_0_testi_2],
  ),
  (titolo: en.termini_sezioni_1_titolo, testi: [en.termini_sezioni_1_testi_0, en.termini_sezioni_1_testi_1]),
  (titolo: en.termini_sezioni_2_titolo, testi: [en.termini_sezioni_2_testi_0, en.termini_sezioni_2_testi_1]),
  (
    titolo: en.termini_sezioni_3_titolo,
    testi: [en.termini_sezioni_3_testi_0, en.termini_sezioni_3_testi_1, en.termini_sezioni_3_testi_2],
  ),
  (
    titolo: en.termini_sezioni_4_titolo,
    testi: [
      en.termini_sezioni_4_testi_0,
      en.termini_sezioni_4_testi_1,
      en.termini_sezioni_4_testi_2,
      en.termini_sezioni_4_testi_3,
      en.termini_sezioni_4_testi_4,
      en.termini_sezioni_4_testi_5,
    ],
  ),
  (
    titolo: en.termini_sezioni_5_titolo,
    testi: [
      en.termini_sezioni_5_testi_0,
      en.termini_sezioni_5_testi_1,
      en.termini_sezioni_5_testi_2,
      en.termini_sezioni_5_testi_3,
      en.termini_sezioni_5_testi_4,
    ],
  ),
  (titolo: en.termini_sezioni_6_titolo, testi: [en.termini_sezioni_6_testi_0]),
  (titolo: en.termini_sezioni_7_titolo, testi: [en.termini_sezioni_7_testi_0, en.termini_sezioni_7_testi_1]),
  (titolo: en.termini_sezioni_8_titolo, testi: [en.termini_sezioni_8_testi_0, en.termini_sezioni_8_testi_1]),
  (titolo: en.termini_sezioni_9_titolo, testi: [en.termini_sezioni_9_testi_0]),
  (titolo: en.termini_sezioni_10_titolo, testi: [en.termini_sezioni_10_testi_0]),
  (titolo: en.termini_sezioni_11_titolo, testi: [en.termini_sezioni_11_testi_0, en.termini_sezioni_11_testi_1]),
  (titolo: en.termini_sezioni_12_titolo, testi: [en.termini_sezioni_12_testi_0]),
  (titolo: en.termini_sezioni_13_titolo, testi: [en.termini_sezioni_13_testi_0, en.termini_sezioni_13_testi_1]),
];

/// La pagina dei termini di servizio.
class PaginaTermini extends ConsumerWidget {
  /// La pagina.
  const PaginaTermini({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final en = testiInglesi;
    final titolare = ref.watch(titolareProvider).value;
    final piccolo = Stile.sans(13.44, colore: Token.ink, altezza: 1.6);
    final collegamento = Stile.sans(13.44, altezza: 1.6);
    final email = titolare?.emailPrivacy;

    return conTestiRaccolti(
      da: 'en',
      pagina: (tr, avviso) {
        // Chi siamo: il nome, l'indirizzo e il codice solo se la console li sa; il contatto, o il rimando alla privacy.
        final chi = Sezione(
          titolo: tr(en.termini_chi_titolo),
          children: [
            TestoPiccolo(
              tr(titolare?.nome == null ? en.termini_chi_testo_senza_nome : en.termini_chi_testo(titolare!.nome!)),
            ),
            if (titolare?.indirizzo != null) TestoPiccolo(tr(en.termini_chi_indirizzo(titolare!.indirizzo!))),
            if (titolare?.codiceFiscale != null) TestoPiccolo(tr(en.termini_chi_codice(titolare!.codiceFiscale!))),
            if (email == null)
              TestoPiccolo(tr(en.termini_chi_email_vuoto), sotto: 0)
            else
              Wrap(
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  // Lo spazio fuori dalla traduzione: ML Kit lo perderebbe.
                  Text('${tr(en.termini_chi_email('').trim())} ', style: piccolo),
                  CollegamentoEsterno(testo: email, url: 'mailto:$email', stile: collegamento),
                ],
              ),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Collegamento(tr(en.termini_privacy_link), href: R.privacy, stile: collegamento),
            ),
          ],
        );
        final celle = <CellaProfilo>[
          (widget: chi, larga: true),
          for (final s in sezioniTermini(en))
            (
              widget: Sezione(
                titolo: tr(s.titolo),
                children: [
                  for (final (i, testo) in s.testi.indexed)
                    TestoPiccolo(tr(testo), sotto: i == s.testi.length - 1 ? 0 : 13.44),
                ],
              ),
              larga: true,
            ),
          (widget: TestoPiccolo(tr(en.termini_versione), tenue: true, sotto: 0), larga: true),
        ];
        return Pagina(
          sezioni: [
            Sottotitolo(
              eyebrow: tr(en.termini_eyebrow),
              titolo: tr(en.termini_titolo),
              intro: tr(en.termini_intro),
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
