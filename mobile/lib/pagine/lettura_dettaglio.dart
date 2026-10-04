/// Una lettura conclusa, dentro la mia storia (`frontend/v2/pagine/lettura-dettaglio.tsx`): la domanda, il tavolo, il
/// quadro, l'interpretazione, e il ritorno sulla lettura («si è avverato?»), che il lettore terrà presente nelle
/// prossime. Da qui si condivide (`apriCondivisione`), si stampa in PDF (`stampaLettura`), si cancella.
///
/// Qui stanno anche i pezzi che la lettura condivisa riusa (come nel sito, che li prende da `lettura.module.css`): la
/// scena (`.scena`), le due colonne (`.read-layout`), il riquadro del responso (`.responso`) col suo Markdown minimo
/// (`lib/markdown.tsx`).
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lettura/comuni.dart';
import '../lettura/condivisione.dart';
import '../lettura/immagine_condivisione.dart';
import '../lettura/stampa.dart';
import '../lettura/tavolo.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../modelli/carta.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/* ---- i pezzi comuni alle pagine di una lettura ---------------------------------------------------------------------- */

/// `.scena`: l'etichetta (la stesa, la data) in verderame maiuscolo e la domanda grande in corsivo.
class ScenaLettura extends StatelessWidget {
  /// La scena.
  const ScenaLettura({super.key, required this.etichetta, required this.domanda, this.sotto, this.lingua = 'en'});

  /// `<small>`.
  final String etichetta;

  /// `<q>`.
  final String domanda;

  /// Fra l'etichetta e la domanda (la frase dell'altra persona nella lettura condivisa).
  final Widget? sotto;

  /// La lingua della lettura (le virgolette).
  final String lingua;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return Padding(
      padding: const EdgeInsets.only(bottom: 22.4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            etichetta.toUpperCase(),
            style: Stile.sans(11.84, peso: FontWeight.w700, em: .1, colore: Token.verdigris, altezza: 1.6),
          ),
          if (sotto != null) ...[const SizedBox(height: 4.8), sotto!],
          const SizedBox(height: 4.8),
          Paragrafo(
            '${virgolette(lingua).$1}$domanda${virgolette(lingua).$2}',
            style: Stile.serif(w.clampVw(20, 2.6, 27.2), stile: FontStyle.italic, altezza: 1.35, colore: Token.ink),
          ),
        ],
      ),
    );
  }
}

/// `.read-panel` (chiaro) e `.read-panel.dark` (prugna): `padding: clamp(.75rem, 2vw, 1.5rem) clamp(1.25rem, 4vw, 3rem)`.
class PannelloLettura extends StatelessWidget {
  /// Un pannello.
  const PannelloLettura({super.key, required this.child, this.scuro = false});

  /// Il contenuto.
  final Widget child;

  /// `.dark`.
  final bool scuro;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return Container(
      color: scuro ? Token.plum : const Color(0xFFFFFAF1),
      padding: EdgeInsets.symmetric(horizontal: w.clampVw(20, 4, 48), vertical: w.clampVw(12, 2, 24)),
      child: DefaultTextStyle.merge(
        style: TextStyle(color: scuro ? const Color(0xFFF6ECDD) : Token.ink),
        child: child,
      ),
    );
  }
}

/// L'occhiello di un pannello: verderame, o il verderame chiaro sul prugna (`.read-panel.dark .eyebrow`).
class EyebrowPannello extends StatelessWidget {
  /// L'occhiello.
  const EyebrowPannello(this.testo, {super.key, this.scuro = false, this.sotto});

  /// Il testo.
  final String testo;

  /// Sul prugna.
  final bool scuro;

  /// Lo spazio sotto.
  final double? sotto;

  @override
  Widget build(BuildContext context) =>
      Eyebrow(testo, colore: scuro ? Colori.eyebrowScuro : Token.verdigris, sotto: sotto);
}

/// `.read-panel h2`: `font: 400 1.6rem var(--serif); margin: 0 0 1rem`.
class TitoloPannelloLettura extends StatelessWidget {
  /// Il titolo.
  const TitoloPannelloLettura(this.testo, {super.key, this.colore});

  /// Il testo.
  final String testo;

  /// Il colore (sul prugna, chiaro).
  final Color? colore;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 16),
    child: Semantics(
      header: true,
      child: TestoBilanciato(testo, stile: Stile.serif(25.6, colore: colore)),
    ),
  );
}

/// Il Markdown minimo del responso (`lib/markdown.tsx`): titoli `##` e `#`, paragrafi, elenchi, grassetto e corsivo;
/// con lo stile di `.testo` (`font: 1.04rem/1.75 var(--serif)`, i titoli `h3` prugna).
class MarkdownResponso extends StatelessWidget {
  /// Il testo del modello.
  const MarkdownResponso(this.testo, {super.key});

  /// Il Markdown.
  final String testo;

  static List<InlineSpan> _inline(String testo) {
    final spans = <InlineSpan>[];
    final re = RegExp(r'(\*\*[^*]+\*\*|\*[^*]+\*)');
    var da = 0;
    for (final m in re.allMatches(testo)) {
      if (m.start > da) spans.add(TextSpan(text: testo.substring(da, m.start)));
      final p = m[0]!;
      if (p.startsWith('**')) {
        spans.add(
          TextSpan(
            text: p.substring(2, p.length - 2),
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        );
      } else if (p.length > 2) {
        spans.add(
          TextSpan(
            text: p.substring(1, p.length - 1),
            style: const TextStyle(fontStyle: FontStyle.italic),
          ),
        );
      } else {
        spans.add(TextSpan(text: p));
      }
      da = m.end;
    }
    if (da < testo.length) spans.add(TextSpan(text: testo.substring(da)));
    return spans;
  }

  @override
  Widget build(BuildContext context) {
    final corpo = Stile.serif(16.64, altezza: 1.75, colore: Token.ink);
    final titolo = Stile.serif(20, colore: Token.plum);
    Widget h3(String t, {bool primo = false}) => Padding(
      padding: EdgeInsets.only(top: primo ? 0 : 25.6, bottom: 8),
      child: Semantics(header: true, child: TestoBilanciato(t, stile: titolo)),
    );
    Widget p(String t) => Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Text.rich(TextSpan(children: _inline(t), style: corpo)),
    );
    final blocchi = <Widget>[];
    for (final b in testo.split(RegExp(r'\n{2,}'))) {
      final righe = b.trim();
      if (righe.isEmpty) continue;
      final primo = blocchi.isEmpty;
      if (righe.startsWith('## ')) {
        final parti = righe.split('\n');
        blocchi.add(h3(parti.first.substring(3), primo: primo));
        if (parti.length > 1) blocchi.add(p(parti.skip(1).join(' ')));
      } else if (righe.startsWith('# ')) {
        blocchi.add(h3(righe.substring(2), primo: primo));
      } else if (RegExp(r'^[-*] ').hasMatch(righe)) {
        blocchi.add(
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final r in righe.split('\n'))
                  Padding(
                    padding: const EdgeInsets.only(left: 19.2),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('• ', style: corpo),
                        Expanded(
                          child: Text.rich(
                            TextSpan(children: _inline(r.replaceFirst(RegExp(r'^[-*] '), '')), style: corpo),
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        );
      } else {
        blocchi.add(p(righe.replaceAll('\n', ' ')));
      }
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: blocchi);
  }
}

/// `.responso`: il riquadro chiaro dell'interpretazione, col filo d'ottone in alto (largo al più 860 px).
class RiquadroResponso extends StatelessWidget {
  /// Il riquadro.
  const RiquadroResponso({super.key, required this.titolo, required this.testo, required this.avvertenza, this.dopo});

  /// `<h2>`.
  final String titolo;

  /// Il responso (Markdown).
  final String testo;

  /// `.avvertenza`.
  final String avvertenza;

  /// Ciò che segue l'avvertenza (la verifica del sorteggio).
  final Widget? dopo;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 860),
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.all(w.clampVw(22.4, 5, 48)),
          decoration: const BoxDecoration(
            color: Token.paperLight,
            border: Border(
              top: BorderSide(color: Token.brass, width: 3),
              left: BorderSide(color: Token.line),
              right: BorderSide(color: Token.line),
              bottom: BorderSide(color: Token.line),
            ),
            boxShadow: [BoxShadow(color: Color(0x1A3C1846), offset: Offset(0, 24), blurRadius: 50)],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.only(bottom: 19.2),
                child: Semantics(
                  header: true,
                  child: TestoBilanciato(
                    titolo,
                    stile: Stile.serif(w.clampVw(28.8, 3.4, 41.6), altezza: 1.15, em: -.03),
                  ),
                ),
              ),
              MarkdownResponso(testo),
              Container(
                margin: const EdgeInsets.only(top: 22.4),
                padding: const EdgeInsets.only(top: 16),
                decoration: const BoxDecoration(
                  border: Border(top: BorderSide(color: Token.line)),
                ),
                child: Text(avvertenza, style: Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6)),
              ),
              ?dopo,
            ],
          ),
        ),
      ),
    );
  }
}

/// `<details class="verifica">`: la verifica del sorteggio, chiusa finché non la si apre.
class VerificaSorteggio extends StatefulWidget {
  /// La verifica.
  const VerificaSorteggio({super.key, required this.commitment, this.sale});

  /// L'impronta del mazzo sigillato.
  final String commitment;

  /// Il sale rivelato a lettura conclusa.
  final String? sale;

  @override
  State<VerificaSorteggio> createState() => _VerificaSorteggioState();
}

class _VerificaSorteggioState extends State<VerificaSorteggio> {
  bool _aperta = false;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final piccolo = Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6);
    Widget codice(String c) => Container(
      width: double.infinity,
      padding: const EdgeInsets.all(9.6),
      color: Token.paper,
      child: Text(c, style: Stile.sans(12.16, colore: Token.inkSoft, altezza: 1.5)),
    );
    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Premibile(
            alTocco: () => setState(() => _aperta = !_aperta),
            selezionato: _aperta,
            costruisci: (context, premuto) => ConstrainedBox(
              constraints: const BoxConstraints(minHeight: 44),
              child: Row(
                children: [
                  Text(_aperta ? '▾ ' : '▸ ', style: Stile.sans(13.44, colore: Token.plum)),
                  Flexible(
                    child: Text(t.lettura_verifica, style: Stile.sans(13.44, colore: Token.plum, altezza: 1.6)),
                  ),
                ],
              ),
            ),
          ),
          if (_aperta) ...[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 13.44),
              child: Text(t.lettura_verifica_testo, style: piccolo),
            ),
            codice(widget.commitment),
            if (widget.sale != null)
              Padding(
                padding: const EdgeInsets.only(top: 13.44),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('salt: ', style: piccolo),
                    Expanded(child: codice(widget.sale!)),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
  }
}

/// Le carte di una lettura salvata come carte sul tavolo, con le dignità.
List<Posata> posateDi(Lettura lt) => [for (final c in lt.cards) Posata.da(c, dignita: lt.dignita['${c.posizione}'])];

/* ---- la pagina -------------------------------------------------------------------------------------------------- */

/// La lettura [id], per chi è dentro.
final letturaSalvataProvider = FutureProvider.autoDispose.family<Lettura, String>((ref, id) {
  ref.watch(sessioneProvider.select((s) => s.autenticata));
  return ref.read(apiProvider).lettura(id);
});

/// Le persone di una lettura speciale e la compatibilità zodiacale (`Persone` del sito).
class _Persone extends StatelessWidget {
  const _Persone({required this.persone, required this.compat, required this.lingua});

  final PersoneLettura persone;
  final Compatibilita? compat;
  final String lingua;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final segni = t.storiaSegni;
    final generi = t.storiaGeneri;
    String segno(String? c) => c == null ? '' : segni[c] ?? c;
    String cuspide(SegnoCalcolato? x) =>
        x != null && x.cuspide && x.vicino != null ? t.storia_cuspide(segno(x.vicino)) : '';
    String riga(String? genere, String? altro, bool trans, String nascita, String sg, String cu) => [
      if (genere != null)
        '${genere == 'altro' && altro != null && altro.isNotEmpty ? altro : generi[genere] ?? genere}'
            '${trans ? ', ${t.storia_persona_trans}' : ''}',
      dataLunga(nascita, lingua),
      sg + (cu.isNotEmpty ? ' ($cu)' : ''),
    ].where((s) => s.isNotEmpty).join(' · ');
    final piccolo = Stile.sans(13.44, colore: Token.ink, altezza: 1.6);
    final tenue = Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6);
    Widget voce(String forte, String resto) => Padding(
      padding: const EdgeInsets.only(bottom: 13.44),
      child: Text.rich(
        TextSpan(
          children: [
            TextSpan(
              text: forte,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            TextSpan(text: ' — $resto'),
          ],
        ),
        style: piccolo,
      ),
    );
    Widget riga2(String etichetta, String valore, [String dopo = '']) => Padding(
      padding: const EdgeInsets.only(bottom: 13.44),
      child: Text.rich(
        TextSpan(
          children: [
            TextSpan(text: '$etichetta: '),
            TextSpan(
              text: valore,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            TextSpan(text: dopo),
          ],
        ),
        style: piccolo,
      ),
    );
    final p = persone.partner;
    final c = compat;
    final elementi = t.storiaNomiElementi;
    return Pannello(
      titolo: t.storia_le_persone,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          voce(
            t.storia_tu,
            riga(
              persone.tu.genere,
              persone.tu.genereAltro,
              persone.tu.trans,
              persone.tu.nascita,
              segno(c?.segni.tu.codice),
              cuspide(c?.segni.tu),
            ),
          ),
          voce(
            [p.nome, p.cognome].whereType<String>().where((s) => s.isNotEmpty).join(' '),
            riga(
              p.genere,
              p.genereAltro,
              p.trans,
              p.nascita,
              segno(c?.segni.partner.codice),
              cuspide(c?.segni.partner),
            ),
          ),
          if (c != null) ...[
            Padding(
              padding: const EdgeInsets.only(top: 8, bottom: 9.6),
              child: Semantics(header: true, child: Text(t.storia_compat_titolo, style: Stile.serif(21.6))),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 13.44),
              child: Text.rich(
                TextSpan(
                  children: [
                    TextSpan(text: '${t.storia_aspetto}: '),
                    TextSpan(
                      text: t.storiaAspetti[c.aspetto] ?? c.aspetto,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    TextSpan(text: ' · ${t.storia_armonia}: '),
                    TextSpan(
                      text: t.storiaArmonie[c.armonia] ?? c.armonia,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
                style: piccolo,
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 13.44),
              child: Text(
                '${t.storia_elementi}: ${elementi[c.segni.tu.elemento] ?? c.segni.tu.elemento} / '
                '${elementi[c.segni.partner.elemento] ?? c.segni.partner.elemento} · '
                '${t.storiaRelazioniElementi[c.relazioneElementi] ?? c.relazioneElementi}',
                style: piccolo,
              ),
            ),
            riga2(t.storia_carta_coppia, nomeCartaIn(c.cartaCoppia, lingua)),
            Text(t.storia_compat_avviso, style: tenue),
          ],
        ],
      ),
    );
  }
}

/// La pagina di una lettura della storia.
class DettaglioLettura extends ConsumerStatefulWidget {
  /// La lettura [id].
  const DettaglioLettura({super.key, required this.id});

  /// L'identificativo.
  final String id;

  @override
  ConsumerState<DettaglioLettura> createState() => _DettaglioLetturaState();
}

class _DettaglioLetturaState extends ConsumerState<DettaglioLettura> {
  bool _annotato = false;
  String? _errore;

  Future<void> _annota(String esito) async {
    try {
      await ref.read(apiProvider).annotaLettura(widget.id, esito);
      if (!mounted) return;
      setState(() {
        _annotato = true;
        _errore = null;
      });
      ref.invalidate(letturaSalvataProvider(widget.id));
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _errore = e.messaggio(context.t));
    }
  }

  Future<void> _cancella() async {
    final t = context.t;
    final conferma = await apriModale<bool>(
      context,
      titolo: t.storia_cancella_conferma_titolo,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Paragrafo(t.storia_cancella_conferma_testo, style: Stile.sans(15.2, colore: Token.inkSoft)),
          ),
          FilaBottoni(
            children: [
              Bottone(t.storia_cancella, variante: Variante.pericolo, alTocco: () => Navigator.of(context).pop(true)),
              Bottone(t.comune_annulla, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop(false)),
            ],
          ),
        ],
      ),
    );
    if (conferma != true || !mounted) return;
    try {
      await ref.read(apiProvider).cancellaLettura(widget.id);
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _errore = e.messaggio(context.t));
      return;
    }
    if (mounted) GoRouter.of(context).go(R.storia);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    if (sessione.pronta && !sessione.autenticata) {
      return Pagina(
        sezioni: [
          Fascia(
            compatta: true,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(padding: const EdgeInsets.only(bottom: 16), child: Paragrafo(t.storia_fuori_testo)),
                Bottone(t.storia_fuori_entra, alTocco: () => unawaited(entraDa(ref))),
              ],
            ),
          ),
        ],
      );
    }
    final lettura = ref.watch(letturaSalvataProvider(widget.id));
    final lt = lettura.value;
    if (lt == null) return Pagina(sezioni: [StatoFascia(errore: lettura.error)]);
    return Pagina(sezioni: [_corpo(context, lt)]);
  }

  Widget _corpo(BuildContext context, Lettura lt) {
    final t = context.t;
    final interfaccia = ref.watch(linguaProvider);
    final ll = linguaLettura(lt.lang, interfaccia);
    final stesa = lt.stesaDati;
    final posate = posateDi(lt);
    final finita = lt.status == 'completata';
    final esiti = t.storiaEsiti;
    final piccolo = Stile.sans(13.44, altezza: 1.6, colore: Token.ink);

    final destra = PannelloLettura(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          EyebrowPannello(t.storia_esito),
          Padding(
            padding: const EdgeInsets.only(bottom: 13.44),
            child: Paragrafo(t.storia_esito_testo, style: piccolo),
          ),
          Semantics(
            container: true,
            label: t.storia_esito,
            child: FilaBottoni(
              children: [
                for (final e in const ['si', 'in_parte', 'no'])
                  Bottone(
                    esiti[e] ?? e,
                    piccolo: true,
                    variante: lt.feedback == e ? Variante.prugna : Variante.quieto,
                    alTocco: () => unawaited(_annota(e)),
                  ),
              ],
            ),
          ),
          if (_annotato) Successo(t.storia_esito_salvato),
          if (_errore != null) Errore(_errore!),
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: FilaBottoni(
              children: [
                if (finita)
                  Bottone(
                    t.storia_condividi,
                    piccolo: true,
                    an: 'share_started',
                    alTocco: () async {
                      await apriCondivisione(context, id: widget.id);
                      ref.invalidate(letturaSalvataProvider(widget.id));
                    },
                  ),
                Bottone(
                  t.storia_riprendi_tema,
                  piccolo: true,
                  variante: Variante.quieto,
                  an: 'followup_started',
                  href: '${R.leggi}?question=${Uri.encodeComponent(lt.question)}&source=story',
                ),
                if (finita)
                  Bottone(
                    '⎙ ${t.storia_stampa_pdf}',
                    piccolo: true,
                    variante: Variante.quieto,
                    an: 'stampa_pdf',
                    alTocco: () => unawaited(stampaLettura(ref, lt, interfaccia: interfaccia)),
                  ),
                Bottone(
                  t.storia_cancella,
                  piccolo: true,
                  variante: Variante.pericolo,
                  alTocco: () => unawaited(_cancella()),
                ),
              ],
            ),
          ),
          if (lt.shareToken != null)
            Padding(
              padding: const EdgeInsets.only(top: 13.44),
              child: Wrap(
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Text('${t.storia_link_attivo}: ', style: piccolo),
                  Collegamento(
                    urlCondivisione(lt.shareToken!),
                    href: R.condivisa(lt.shareToken!),
                    stile: Stile.sans(13.44, altezza: 1.6),
                  ),
                ],
              ),
            ),
          if (lt.contextSummary != null && lt.contextSummary!.isNotEmpty) ...[
            const SizedBox(height: 8),
            EyebrowPannello(t.storia_il_quadro),
            Paragrafo(lt.contextSummary!, style: Stile.serif(16, altezza: 1.6, colore: Token.ink)),
          ],
        ],
      ),
    );

    final sinistra = PannelloLettura(
      scuro: true,
      child: stesa == null
          ? const SizedBox.shrink()
          : Semantics(
              container: true,
              label: nomeStesaIn(stesa, ll),
              child: Tavolo(stesa: stesa, posate: posate, nomePartner: lt.persone?.partner.nome, manuale: lt.manuale),
            ),
    );

    final etichetta = [
      if (stesa != null) nomeStesaIn(stesa, ll) else nomeStesaDaNomi(lt.stesa, lt.stesaNomi, ll),
      t.storia_dettaglio_quando(dataLunga(lt.createdAt, interfaccia)),
    ].join(' · ');

    return MazzoAttivo(
      slug: lt.mazzo,
      child: LinguaNomi(
        lingua: ll,
        child: Fascia(
          compatta: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: Bottone('← ${t.storia_indietro}', href: R.storia, piccolo: true, variante: Variante.quieto),
              ),
              const SizedBox(height: 8),
              ScenaLettura(etichetta: etichetta, domanda: lt.question, lingua: ll),
              PannelliLettura(sinistra: sinistra, destra: destra),
              if (lt.persone != null)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: _Persone(persone: lt.persone!, compat: lt.compatibilita, lingua: interfaccia),
                ),
              if (lt.synthesis != null && lt.synthesis!.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 11.2),
                  child: RiquadroResponso(
                    titolo: t.storia_l_interpretazione,
                    testo: lt.synthesis!,
                    avvertenza: lt.disclaimer,
                    dopo: lt.commitment == null
                        ? null
                        : VerificaSorteggio(commitment: lt.commitment!, sale: lt.deckSalt),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Va alla pagina di una lettura (per chi la apre dallo storico).
void apriLettura(BuildContext context, String id) => vai(context, R.lettura(id));

/// Il nome della carta di una posizione, nella lingua della lettura (per i test e per la stampa).
String nomeCartaPosata(CartaPosata c, String lingua) => c.carta == null ? '' : nomeCartaIn(c.carta!, lingua);

/// La stesa di una lettura salvata (o `null` per una lettura vecchia senza i dati della stesa).
Stesa? stesaDi(Lettura lt) => lt.stesaDati;
