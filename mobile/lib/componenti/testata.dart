/// La testata del sito (`frontend/v2/componenti/testata.tsx`), nelle due forme del CSS:
///
/// - **telefono** (fino a 760 px, il blocco «la testata sul telefono» di v2.css): **una riga sola** con il simbolo,
///   le sei voci del menu (icona + etichetta corta a 8 px con gli a capo scritti nei dizionari, `nav_breve_*`;
///   «Read» sparisce perché c'è già «Start reading»), carrello, crediti, profilo (o «Sign in») e «Start reading» su
///   due righe, largo quanto la sua parola più lunga. Un'unica fila di icone equidistanti (4/10): menu e azioni
///   larghi uguale (`flex: 1 1 0`), mai meno della loro parola più lunga (`min-width: min-content`). Bordo 4 px,
///   voci alte 44 px. Sotto i 340 px le
///   etichette scendono a 7 px. Fra 561 e 760 px c'è anche il nome del marchio e la lingua;
/// - **tablet e computer** (oltre 760 px): marchio e azioni in alto, il menu con le etichette lunghe sotto (fino a
///   1100 px) o in mezzo (oltre).
library;

import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/tracciato.dart';
import '../auth/sessione.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../rotte/percorso.dart';
import '../tema/tema.dart';
import 'icone.dart';
import 'marchio.dart';
import 'premibile.dart';
import 'selettore_lingua.dart';

/// Quale voce del menu accendere: ogni sezione possiede alcune pagine (come `SEZIONI` del sito).
const List<({Voce voce, String href, List<String> pagine})> sezioni = [
  (voce: Voce.leggi, href: R.leggi, pagine: [R.leggi]),
  (voce: Voce.fisica, href: R.fisica, pagine: [R.fisica]),
  (voce: Voce.giorno, href: R.giorno, pagine: [R.giorno]),
  (voce: Voce.diario, href: R.blog, pagine: [R.blog]),
  (voce: Voce.esplora, href: R.esplora, pagine: [R.esplora, R.stese, R.carte, R.mazzi, R.voto]),
  (voce: Voce.storia, href: R.storia, pagine: [R.storia, R.profilo]),
  (voce: Voce.negozio, href: R.negozio, pagine: [R.negozio, R.carrello]),
];

/// La voce accesa per il percorso [p].
Voce? voceAttiva(String p) {
  for (final s in sezioni) {
    if (s.pagine.any((x) => p == x || p.startsWith('$x/'))) return s.voce;
  }
  return null;
}

/// L'etichetta lunga di una voce (`nav_*`, con gli a capo per il computer).
String nomeVoce(AppLocalizations t, Voce v) => switch (v) {
  Voce.leggi => t.comune_nav_leggi,
  Voce.fisica => t.comune_nav_fisica,
  Voce.giorno => t.comune_nav_giorno,
  Voce.diario => t.comune_nav_diario,
  Voce.esplora => t.comune_nav_esplora,
  Voce.storia => t.comune_nav_storia,
  Voce.negozio => t.comune_nav_negozio,
};

/// L'etichetta corta di una voce (`nav_breve_*`, con gli a capo per il telefono).
String nomeBreve(AppLocalizations t, Voce v) => switch (v) {
  Voce.leggi => t.comune_nav_breve_leggi,
  Voce.fisica => t.comune_nav_breve_fisica,
  Voce.giorno => t.comune_nav_breve_giorno,
  Voce.diario => t.comune_nav_breve_diario,
  Voce.esplora => t.comune_nav_breve_esplora,
  Voce.storia => t.comune_nav_breve_storia,
  Voce.negozio => t.comune_nav_breve_negozio,
};

/// La testata.
class Testata extends ConsumerWidget {
  /// La testata della pagina.
  const Testata({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final w = MediaQuery.sizeOf(context).width;
    return Semantics(
      container: true,
      explicitChildNodes: true,
      child: DecoratedBox(
        decoration: const BoxDecoration(
          color: Colori.testataFondo,
          border: Border(bottom: BorderSide(color: Colori.testataBordo)),
        ),
        child: w.telefono ? const _TestataTelefono() : const _TestataLarga(),
      ),
    );
  }
}

/* ---- i dati comuni alle due forme ------------------------------------------------------------------------------- */

typedef _Azioni = ({bool autenticata, bool pronta, int? saldo, int pezzi, Voce? attiva, String percorso});

_Azioni _azioni(WidgetRef ref) {
  final sessione = ref.watch(sessioneProvider);
  final percorso = ref.watch(percorsoProvider).path;
  return (
    autenticata: sessione.autenticata,
    pronta: sessione.pronta,
    saldo: sessione.autenticata ? ref.watch(saldoProvider).value : null,
    pezzi: ref.watch(pezziCarrelloProvider),
    attiva: voceAttiva(percorso),
    percorso: percorso,
  );
}

TextPainter _misura(String testo, TextStyle stile, TextScaler scala, {double maxWidth = double.infinity}) =>
    TextPainter(
      text: TextSpan(text: testo, style: stile),
      textDirection: TextDirection.ltr,
      textScaler: scala,
    )..layout(maxWidth: maxWidth);

/// La parola più lunga (`min-content`).
double _parolaPiuLunga(String testo, TextStyle stile, TextScaler scala) =>
    testo.split(RegExp(r'\s+')).where((p) => p.isNotEmpty).map((p) => _misura(p, stile, scala).width).fold(0, math.max);

/* ---- il telefono: una riga sola ---------------------------------------------------------------------------------- */

class _TestataTelefono extends ConsumerWidget {
  const _TestataTelefono();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final media = MediaQuery.of(context);
    final scala = media.textScaler;
    final w = media.size.width;
    final a = _azioni(ref);
    final minima = w <= Rottura.minima;

    // Le misure del blocco «la testata sul telefono» di v2.css.
    final etichetta = Stile.sans(
      minima ? Token.etichettaTestataStretta : Token.etichettaTestataTelefono,
      peso: FontWeight.w600,
      altezza: 1.15,
    );
    final etichettaAzione = etichetta.copyWith(height: 1.1);
    final crediti = Stile.sans(11.2, peso: FontWeight.w700, altezza: 1.1, colore: Token.brassPale);
    final bottone = Stile.sans(minima ? 9.6 : 10.24, peso: FontWeight.w700, altezza: 1.08, em: .01);
    final nomeMarchio = w > Rottura.piccola;
    final lingua = w > Rottura.piccola;
    final pl = math.max(4.0, media.padding.left);
    final pr = math.max(4.0, media.padding.right);

    // Il marchio: segno 22×27, poi il nome (oltre 560 px), margine destro 2 px.
    final pxNome = w.stretto ? 14.4 : 16.0;
    final larghezzaNome = nomeMarchio ? _misura('TAROTS chat', Stile.serif(pxNome, em: .04), scala).width + 6.4 : 0.0;
    final larghezzaMarchio = 22 + larghezzaNome;

    // «Start reading»: largo quanto la parola più lunga, imbottitura 3 px, bordo 1 px, margine sinistro 2 px.
    final testoBottone = t.comune_inizia_lettura;
    final internoBottone = _parolaPiuLunga(testoBottone, bottone, scala).ceilToDouble();
    final larghezzaBottone = internoBottone + 6 + 2;

    // Le voci: il minimo di ciascuna è la sua parola più lunga (o l'icona, 20 px).
    final voci = [
      for (final s in sezioni.where((s) => s.voce != Voce.leggi))
        (s: s, testo: nomeBreve(t, s.voce), stile: etichetta, menu: true),
    ];
    final testoProfilo = a.autenticata ? t.comune_testata_profilo : t.comune_testata_entra;
    final mostraProfilo = a.autenticata || a.pronta;
    final azioni = [
      (testo: t.comune_testata_carrello, stile: etichettaAzione),
      (
        testo: a.saldo == null ? t.comune_testata_crediti : '${a.saldo}',
        stile: a.saldo == null ? etichettaAzione : crediti,
      ),
      if (mostraProfilo) (testo: testoProfilo, stile: etichettaAzione),
    ];
    // Misure esatte, senza arrotondare: come il browser, che a 320 px fa stare la riga per un pixel. Il testo poi si
    // dispone con lo stesso motore che l'ha misurato, quindi la riga più lunga ci sta (+.01 per gli arrotondamenti).
    double minimo(String testo, TextStyle s) => math.max(20.0, _parolaPiuLunga(testo, s, scala)) + 2.01;
    final minimiMenu = [for (final v in voci) minimo(v.testo, v.stile)];
    final minimiAzioni = [for (final v in azioni) minimo(v.testo, v.stile)];
    final larghezzaLingua = lingua ? 100.0 : 0.0;

    // Un'unica fila di icone equidistanti, come il sito (4/10): menu e azioni larghi uguale (`flex: 1 1 0`), mai meno
    // della loro parola più lunga (`min-width: min-content`); chi ha bisogno di più spazio lo prende, gli altri si
    // dividono il resto in parti uguali.
    final fisso = pl + pr + larghezzaMarchio + 2 + larghezzaBottone + 2 + larghezzaLingua;
    final larghe = _parti([...minimiMenu, ...minimiAzioni], w - fisso - .1);
    final menu = larghe.sublist(0, minimiMenu.length);
    final az = larghe.sublist(minimiMenu.length);

    final contenuto = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Il marchio.
        Padding(
          padding: const EdgeInsets.only(right: 2),
          child: _Marchio(nome: nomeMarchio, pxNome: pxNome, piccolo: true),
        ),
        // Il menu.
        Semantics(
          label: t.comune_aria_nav,
          container: true,
          explicitChildNodes: true,
          child: Row(
            children: [
              for (var i = 0; i < voci.length; i++)
                SizedBox(
                  width: menu[i],
                  child: _VoceIcona(
                    icona: iconeMenu[voci[i].s.voce]!,
                    etichetta: voci[i].testo,
                    stile: voci[i].stile,
                    colore: Colori.voceMenu,
                    distanza: 2.4,
                    attiva: a.attiva == voci[i].s.voce,
                    lungo: nomeVoce(t, voci[i].s.voce).replaceAll('\n', ' '),
                    alTocco: () => vai(context, voci[i].s.href),
                  ),
                ),
            ],
          ),
        ),
        // Le azioni.
        SizedBox(
          width: az[0],
          child: _VoceIcona(
            icona: Icone.carrello,
            etichetta: azioni[0].testo,
            stile: azioni[0].stile,
            colore: Colori.iconaTestata,
            distanza: 1.6,
            attiva: a.percorso == R.carrello,
            lungo: a.pezzi > 0 ? t.comune_testata_carrello_tip_n(a.pezzi) : t.comune_testata_carrello_tip,
            distintivo: a.pezzi > 0 ? (a.pezzi > 99 ? '99+' : '${a.pezzi}') : null,
            alTocco: () => vai(context, R.carrello),
          ),
        ),
        if (lingua) SizedBox(width: larghezzaLingua, child: const SelettoreLingua(larghezzaMassima: 100)),
        SizedBox(
          width: az[1],
          child: _VoceIcona(
            icona: Icone.crediti,
            etichetta: azioni[1].testo,
            stile: azioni[1].stile,
            colore: Colori.iconaTestata,
            distanza: 1.6,
            attiva: a.percorso == R.prezzi,
            lungo: a.saldo == null
                ? t.comune_testata_crediti_tip
                : t.comune_testata_crediti_tip_n(t.comune_testata_crediti_n(a.saldo!)),
            alTocco: () => vai(context, R.prezzi),
          ),
        ),
        if (mostraProfilo)
          SizedBox(
            width: az[2],
            child: _VoceIcona(
              icona: a.autenticata ? Icone.profilo : Icone.entra,
              etichetta: azioni[2].testo,
              stile: azioni[2].stile,
              colore: Colori.iconaTestata,
              distanza: 1.6,
              attiva: a.percorso == R.profilo,
              lungo: a.autenticata ? t.comune_profilo : t.comune_entra,
              alTocco: () => a.autenticata ? vai(context, R.profilo) : _entra(ref),
            ),
          ),
        Padding(
          padding: const EdgeInsets.only(left: 2),
          child: _BottoneInizia(
            testo: testoBottone,
            stile: bottone,
            larghezzaTesto: internoBottone,
            imbottitura: const EdgeInsets.symmetric(horizontal: 3, vertical: 2),
          ),
        ),
      ],
    );

    return Padding(
      padding: EdgeInsets.fromLTRB(pl, math.max(4, media.padding.top), pr, 4),
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: Token.altezzaTestataTelefono - 8),
        // Se le parole più lunghe non ci stanno, la riga esce a destra come nel browser: si taglia, non si avvisa.
        child: Align(
          alignment: Alignment.centerLeft,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            physics: const NeverScrollableScrollPhysics(),
            child: contenuto,
          ),
        ),
      ),
    );
  }
}

/// Divide [spazio] in parti uguali fra le voci (`flex: 1 1 0`), senza scendere sotto il minimo di ciascuna: chi ha
/// il minimo più grande della parte lo tiene, e le altre si dividono il resto. Se nemmeno i minimi ci stanno, ognuna
/// resta al suo minimo (la riga esce a destra, come nel browser).
List<double> _parti(List<double> minimi, double spazio) {
  final w = List<double>.filled(minimi.length, 0);
  final fisse = <int>{};
  for (var giro = 0; giro <= minimi.length; giro++) {
    final libere = [
      for (var i = 0; i < minimi.length; i++)
        if (!fisse.contains(i)) i,
    ];
    if (libere.isEmpty) break;
    final occupato = fisse.fold(0.0, (s, i) => s + minimi[i]);
    final parte = (spazio - occupato) / libere.length;
    final nuove = [for (final i in libere) if (minimi[i] > parte) i];
    if (nuove.isEmpty) {
      for (final i in libere) {
        w[i] = parte;
      }
      break;
    }
    fisse.addAll(nuove);
  }
  for (final i in fisse) {
    w[i] = minimi[i];
  }
  return w;
}

Future<void> _entra(WidgetRef ref) async {
  try {
    await ref.read(sessioneProvider.notifier).entra();
  } on Object catch (e) {
    debugPrint('Accesso non riuscito: $e');
  }
}

/// Un'icona con l'etichetta sotto (`.nav-voce` e `.hdr-icon` sul telefono): alta almeno 44 px, la voce accesa in
/// ottone chiaro con la linea sotto (`box-shadow: inset 0 -2px 0`).
class _VoceIcona extends StatelessWidget {
  const _VoceIcona({
    required this.icona,
    required this.etichetta,
    required this.stile,
    required this.colore,
    required this.distanza,
    required this.attiva,
    required this.lungo,
    required this.alTocco,
    this.distintivo,
  });

  final String icona;
  final String etichetta;
  final TextStyle stile;
  final Color colore;
  final double distanza;
  final bool attiva;
  final String lungo;
  final VoidCallback alTocco;
  final String? distintivo;

  @override
  Widget build(BuildContext context) {
    final c = attiva ? Token.brassPale : colore;
    return Premibile(
      alTocco: alTocco,
      collegamento: true,
      selezionato: attiva,
      etichetta: lungo,
      costruisci: (context, premuto) => Container(
        constraints: const BoxConstraints(minHeight: 44),
        padding: const EdgeInsets.symmetric(horizontal: 1, vertical: 2),
        decoration: attiva
            ? const BoxDecoration(
                border: Border(bottom: BorderSide(color: Token.brassPale, width: 2)),
              )
            : null,
        child: Stack(
          clipBehavior: Clip.none,
          alignment: Alignment.center,
          children: [
            Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconaTratto(icona, misura: 20, colore: premuto ? Token.brassPale : c),
                SizedBox(height: distanza),
                Text(
                  etichetta,
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.clip,
                  style: stile.copyWith(color: stile.color == Token.brassPale ? Token.brassPale : c),
                ),
              ],
            ),
            if (distintivo != null)
              Positioned(
                top: -2,
                right: -3,
                child: Container(
                  constraints: const BoxConstraints(minWidth: 15),
                  height: 15,
                  padding: const EdgeInsets.symmetric(horizontal: 3),
                  decoration: BoxDecoration(color: Token.brassPale, borderRadius: BorderRadius.circular(999)),
                  alignment: Alignment.center,
                  child: Text(
                    distintivo!,
                    style: Stile.sans(9.28, peso: FontWeight.w800, colore: Colori.testoOttone, altezza: 1),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// «Start reading» (`.button.button-brass.button-small` con `data-an="cta_testata"`).
class _BottoneInizia extends StatelessWidget {
  const _BottoneInizia({required this.testo, required this.stile, required this.imbottitura, this.larghezzaTesto});

  final String testo;
  final TextStyle stile;
  final EdgeInsets imbottitura;
  final double? larghezzaTesto;

  @override
  Widget build(BuildContext context) {
    return Tracciato(
      an: 'cta_testata',
      child: Premibile(
        alTocco: () => vai(context, R.leggi),
        collegamento: true,
        raggioFuoco: Token.raggio,
        costruisci: (context, premuto) => Container(
          constraints: const BoxConstraints(minHeight: 44),
          padding: imbottitura,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: premuto ? const Color(0xFFC69543) : Token.brass,
            border: Border.all(color: Colori.bordoOttone),
            borderRadius: BorderRadius.circular(Token.raggio),
          ),
          child: SizedBox(
            width: larghezzaTesto,
            child: Text(
              testo,
              textAlign: TextAlign.center,
              softWrap: larghezzaTesto != null,
              style: stile.copyWith(color: Colori.testoOttone),
            ),
          ),
        ),
      ),
    );
  }
}

/// Il marchio come collegamento alla home.
class _Marchio extends StatelessWidget {
  const _Marchio({required this.nome, required this.pxNome, required this.piccolo});

  final bool nome;
  final double pxNome;
  final bool piccolo;

  @override
  Widget build(BuildContext context) {
    return Premibile(
      alTocco: () => vai(context, R.home),
      collegamento: true,
      etichetta: context.t.comune_aria_home,
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 44),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            piccolo
                ? const SegnoMarchio(larghezza: 22, altezza: 27, px: 12.8)
                : const SegnoMarchio(larghezza: 33, altezza: 40, px: 16),
            if (nome) ...[SizedBox(width: piccolo ? 6.4 : 9.6), NomeMarchio(px: pxNome)],
          ],
        ),
      ),
    );
  }
}

/* ---- tablet e computer ----------------------------------------------------------------------------------------- */

class _TestataLarga extends ConsumerWidget {
  const _TestataLarga();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final a = _azioni(ref);
    final gutter = w.gutter;
    final dueRighe = w.largoMedio;

    final menu = Wrap(
      spacing: w.clampVw(4, 1.4, 20),
      alignment: dueRighe ? WrapAlignment.start : WrapAlignment.center,
      children: [
        for (final s in sezioni)
          Premibile(
            alTocco: () => vai(context, s.href),
            collegamento: true,
            selezionato: a.attiva == s.voce,
            etichetta: nomeVoce(t, s.voce).replaceAll('\n', ' '),
            costruisci: (context, premuto) {
              final accesa = a.attiva == s.voce || premuto;
              return Container(
                constraints: const BoxConstraints(minHeight: 44),
                padding: const EdgeInsets.symmetric(horizontal: 7.2),
                decoration: a.attiva == s.voce
                    ? const BoxDecoration(
                        border: Border(bottom: BorderSide(color: Token.brassPale, width: 2)),
                      )
                    : null,
                // Centrata ma larga quanto la scritta (un `alignment` del Container la allargherebbe a tutta riga).
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      nomeVoce(t, s.voce),
                      textAlign: TextAlign.center,
                      style: Stile.sans(
                        12.8,
                        peso: FontWeight.w600,
                        altezza: 1.12,
                        colore: accesa ? Token.brassPale : Colori.voceMenu,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
      ],
    );

    final etichetta = Stile.sans(9.92, peso: FontWeight.w600, altezza: 1.1, em: .02);
    Widget icona(String d, String testo, String lungo, bool attiva, VoidCallback azione, {TextStyle? stile}) =>
        ConstrainedBox(
          constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
          child: _VoceIcona(
            icona: d,
            etichetta: testo.replaceAll('\n', ' '),
            stile: stile ?? etichetta,
            colore: Colori.iconaTestata,
            distanza: 1.6,
            attiva: attiva,
            lungo: lungo,
            alTocco: azione,
          ),
        );

    final azioni = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        icona(
          Icone.carrello,
          t.comune_testata_carrello,
          t.comune_testata_carrello_tip,
          a.percorso == R.carrello,
          () => vai(context, R.carrello),
        ),
        const SizedBox(width: 9.6),
        const SelettoreLingua(),
        const SizedBox(width: 9.6),
        icona(
          Icone.crediti,
          a.saldo == null ? t.comune_testata_crediti : '${a.saldo}',
          a.saldo == null
              ? t.comune_testata_crediti_tip
              : t.comune_testata_crediti_tip_n(t.comune_testata_crediti_n(a.saldo!)),
          a.percorso == R.prezzi,
          () => vai(context, R.prezzi),
          stile: a.saldo == null
              ? null
              : Stile.sans(11.2, peso: FontWeight.w700, altezza: 1.1, colore: Token.brassPale),
        ),
        if (a.autenticata || a.pronta) ...[
          const SizedBox(width: 9.6),
          icona(
            a.autenticata ? Icone.profilo : Icone.entra,
            a.autenticata ? t.comune_testata_profilo : t.comune_testata_entra,
            a.autenticata ? t.comune_profilo : t.comune_entra,
            a.percorso == R.profilo,
            () => a.autenticata ? vai(context, R.profilo) : _entra(ref),
          ),
        ],
        const SizedBox(width: 9.6),
        _BottoneInizia(
          testo: t.comune_inizia_lettura,
          stile: Stile.sans(12.8, peso: FontWeight.w700, altezza: 1.2, em: .01),
          imbottitura: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 8),
        ),
      ],
    );

    const marchio = _Marchio(nome: true, pxNome: 16, piccolo: false);
    final contenuto = dueRighe
        ? Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(children: [marchio, const Spacer(), azioni]),
              const SizedBox(height: 11.2),
              Transform.translate(offset: const Offset(-7.2, 0), child: menu),
            ],
          )
        : Row(
            children: [
              marchio,
              const SizedBox(width: 32),
              Expanded(child: menu),
              const SizedBox(width: 32),
              azioni,
            ],
          );
    return Padding(
      padding: EdgeInsets.fromLTRB(
        math.max(gutter, media.padding.left),
        math.max(12.8, media.padding.top),
        math.max(gutter, media.padding.right),
        12.8,
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: Token.altezzaTestata - 25.6),
        child: Center(child: contenuto),
      ),
    );
  }
}
