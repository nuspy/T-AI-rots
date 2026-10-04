/// «Vota il prossimo mazzo» (`frontend/v2/pagine/voto.tsx` e `v2/componenti/campioni-voto.tsx`): un voto per persona
/// e per tornata, sostituibile finché la tornata è aperta; le percentuali solo dopo aver votato (come sul server). Chi
/// non è entrato vede l'invito ad accedere e l'ultimo risultato. In fondo, il suggerimento di un tema.
library;

import 'dart:async';

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../catalogo/comuni.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/diario.dart' show immagineMediaProvider;
import '../componenti/galleria_mazzo.dart' show ImmagineNoveSedici, ZoomCarte;
import '../componenti/griglia.dart';
import '../componenti/modale.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../modelli/voto.dart';
import '../tema/tema.dart';
import 'mazzi.dart' show RiepilogoVoto;

/// Lo stato del voto (con un account).
final statoVotoProvider = FutureProvider<StatoVoto>((ref) {
  ref.watch(sessioneProvider.select((s) => s.autenticata));
  return ref.read(apiProvider).statoVoto();
});

/// La pagina del voto.
class Voto extends ConsumerWidget {
  /// Il voto.
  const Voto({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    final Widget corpo;
    if (!sessione.pronta) {
      corpo = const SizedBox.shrink();
    } else if (sessione.autenticata) {
      corpo = const _Votazione();
    } else {
      corpo = GrigliaStoria(
        sinistra: Pannello(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(padding: const EdgeInsets.only(bottom: 16), child: Paragrafo(t.mazzi_voto_fuori)),
              Bottone(t.mazzi_voto_entra, alTocco: () => unawaited(entraDa(ref))),
            ],
          ),
        ),
        destra: const RiepilogoVoto(),
      );
    }
    return Pagina(
      sezioni: [
        Sottotitolo(
          eyebrow: t.mazzi_voto_eyebrow,
          titolo: t.mazzi_voto_titolo_pagina,
          intro: t.mazzi_voto_intro,
          compatta: true,
        ),
        Fascia(compatta: true, child: corpo),
      ],
    );
  }
}

class _Votazione extends ConsumerStatefulWidget {
  const _Votazione();

  @override
  ConsumerState<_Votazione> createState() => _VotazioneState();
}

class _VotazioneState extends ConsumerState<_Votazione> {
  String? _votatoOra;
  bool _inCorso = false;
  String? _errore;

  Future<void> _vota(String id) async {
    setState(() {
      _inCorso = true;
      _errore = null;
    });
    try {
      await ref.read(apiProvider).votaMazzo(id);
      _votatoOra = id;
      ref.invalidate(statoVotoProvider);
    } on ErroreApi catch (e) {
      if (mounted) _errore = e.messaggio(context.t);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final stato = ref.watch(statoVotoProvider);
    if (stato.hasError && !stato.hasValue) return Errore(messaggioErrore(stato.error!, t), sopra: 0);
    final s = stato.value;
    if (s == null) return Text(t.comune_carica, style: Stile.sans(16, colore: Token.inkSoft));
    final mio = _votatoOra ?? s.mioVoto;
    final w = larghezza(context);
    final vincitori = s.vincitoriPrecedenti ?? const <VincitorePrecedente>[];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (s.tornata != null) ...[
          if (mio != null) Successo(t.mazzi_voto_grazie, sopra: 0),
          Padding(
            padding: const EdgeInsets.only(top: 8),
            // `.pricing-grid`: tre colonne, una sul telefono; le tessere alte uguali.
            child: Griglia(
              colonne: w.telefono ? 1 : 3,
              spazioColonne: 16,
              spazioRighe: 8,
              children: [
                for (final c in s.candidati)
                  _Candidato(c: c, mio: mio, inCorso: _inCorso, alVoto: () => unawaited(_vota(c.id))),
              ],
            ),
          ),
          if (mio != null)
            Padding(
              padding: const EdgeInsets.only(top: 13.44),
              child: Text(t.mazzi_voto_cambia, style: stilePiccolo()),
            ),
          if (_errore != null) Errore(_errore!),
        ] else
          Avviso(t.mazzi_voto_nessuna, sopra: 0),
        if (vincitori.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 11.2),
            child: Pannello(
              titolo: t.mazzi_voto_vincitori,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (final v in vincitori)
                    VoceMemoria(
                      titolo: v.nome,
                      figli: [Text(t.mazzi_voto_percentuale(v.percentuale), style: Stile.sans(13.44))],
                    ),
                ],
              ),
            ),
          ),
        const Padding(padding: EdgeInsets.only(top: 11.2), child: _Suggerisci()),
      ],
    );
  }
}

/// `.plan` (`.featured` per il proprio voto): il candidato, i campioni, la percentuale dopo il voto, il bottone.
class _Candidato extends StatelessWidget {
  const _Candidato({required this.c, required this.mio, required this.inCorso, required this.alVoto});

  final CandidatoVoto c;
  final String? mio;
  final bool inCorso;
  final VoidCallback alVoto;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final qui = mio == c.id;
    final testo = qui ? const Color(0xFFD9CADE) : Token.inkSoft;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 27.2, vertical: 13.6),
      decoration: BoxDecoration(
        color: qui ? Token.plum : Colori.carta,
        border: Border.all(color: qui ? Token.plum : Token.line),
        boxShadow: qui ? const [BoxShadow(color: Token.brassPale, offset: Offset(10, 10))] : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Semantics(
            header: true,
            child: Text(c.nome, style: Stile.serif(23.2, colore: qui ? const Color(0xFFFFF7E8) : Token.ink)),
          ),
          if (c.descrizione != null)
            Padding(
              padding: const EdgeInsets.only(top: 14.08),
              child: Paragrafo(c.descrizione!, style: Stile.sans(14.08, colore: testo)),
            ),
          CampioniVoto(nome: c.nome, campioni: c.campioni),
          if (c.percentuale != null) ...[
            BarraPercentuale(percentuale: c.percentuale!, etichetta: '', chiara: qui),
            Text(t.mazzi_voto_percentuale(c.percentuale!), style: Stile.sans(13.44, colore: qui ? testo : Token.ink)),
          ],
          // `.plan .button { margin-top: auto }`: in fondo alla tessera quando le tessere stanno in riga.
          if (!larghezza(context).telefono) const Spacer(),
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Bottone(
              qui ? t.mazzi_voto_votato : t.mazzi_voto_bottone,
              variante: qui ? Variante.ottone : Variante.quieto,
              pieno: true,
              alTocco: inCorso || qui ? null : alVoto,
            ),
          ),
        ],
      ),
    );
  }
}

/// `.stat-bar`: la barra della percentuale (ottone; chiara sul fondo prugna).
class BarraPercentuale extends StatelessWidget {
  /// La barra.
  const BarraPercentuale({super.key, required this.percentuale, required this.etichetta, this.chiara = false});

  /// La percentuale (0–100).
  final num percentuale;

  /// L'etichetta per i lettori di schermo (vuota: decorativa, il numero è scritto accanto).
  final String etichetta;

  /// Dentro `.plan.featured`.
  final bool chiara;

  @override
  Widget build(BuildContext context) {
    final barra = Container(
      height: 6,
      margin: const EdgeInsets.only(top: 8, bottom: 4.8),
      color: chiara ? const Color(0x26FFFFFF) : const Color(0x1F3C1846),
      alignment: AlignmentDirectional.centerStart,
      child: FractionallySizedBox(
        widthFactor: (percentuale / 100).clamp(0, 1).toDouble(),
        heightFactor: 1,
        child: ColoredBox(color: chiara ? Token.brassPale : Token.brass),
      ),
    );
    return etichetta.isEmpty ? ExcludeSemantics(child: barra) : Semantics(label: etichetta, image: true, child: barra);
  }
}

/// Le carte d'esempio di un candidato (`campioni-voto.tsx`): una fila di miniature che va a capo (mai uno scorrimento
/// orizzontale); un tocco ne apre l'ingrandimento in un dialogo, con le frecce ai lati.
class CampioniVoto extends ConsumerWidget {
  /// I campioni del candidato [nome].
  const CampioniVoto({super.key, required this.nome, required this.campioni});

  /// Il nome del candidato.
  final String nome;

  /// Le immagini (percorsi relativi dell'API).
  final List<CampioneVoto> campioni;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final validi = campioni.where((c) => c.url != null).toList();
    if (validi.isEmpty) return const SizedBox.shrink();
    final immagine = ref.watch(immagineMediaProvider);
    final w = larghezza(context);
    final lato = w.clampVw(56, 16, 88);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Semantics(
        label: t.mazzi_campioni_titolo(nome),
        container: true,
        child: Wrap(
          spacing: 9.6,
          runSpacing: 9.6,
          children: [
            for (final (i, c) in validi.indexed)
              Premibile(
                alTocco: () => unawaited(_apri(context, validi, i)),
                etichetta: t.mazzi_campione_ingrandisci(i + 1, nome),
                costruisci: (context, premuto) => AnimatedContainer(
                  duration: MediaQuery.disableAnimationsOf(context) ? Duration.zero : const Duration(milliseconds: 150),
                  curve: Curves.ease,
                  transform: Matrix4.translationValues(0, premuto ? -2 : 0, 0),
                  constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                  decoration: BoxDecoration(
                    color: Token.paperDeep,
                    border: Border.all(color: Colori.cornice, width: 2),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: SizedBox(
                      width: lato,
                      height: lato * 16 / 9,
                      child: Image(
                        image: immagine(c.mini ?? c.url!),
                        fit: BoxFit.cover,
                        excludeFromSemantics: true,
                        errorBuilder: (context, e, s) => const SizedBox.shrink(),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _apri(BuildContext context, List<CampioneVoto> validi, int indice) {
    return showGeneralDialog<void>(
      context: context,
      barrierDismissible: true,
      barrierLabel: context.t.comune_chiudi,
      barrierColor: const Color(0x00000000),
      transitionDuration: Token.durataTransizione,
      pageBuilder: (context, _, _) => _ZoomCampioni(nome: nome, campioni: validi, iniziale: indice),
      transitionBuilder: (context, animazione, _, figlio) => FadeTransition(opacity: animazione, child: figlio),
    );
  }
}

class _ZoomCampioni extends ConsumerStatefulWidget {
  const _ZoomCampioni({required this.nome, required this.campioni, required this.iniziale});

  final String nome;
  final List<CampioneVoto> campioni;
  final int iniziale;

  @override
  ConsumerState<_ZoomCampioni> createState() => _ZoomCampioniState();
}

class _ZoomCampioniState extends ConsumerState<_ZoomCampioni> {
  late int _i = widget.iniziale;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final totale = widget.campioni.length;
    final c = widget.campioni[_i];
    final titolo = t.mazzi_campione_zoom(widget.nome, _i + 1, totale);
    void chiudi() => Navigator.of(context).pop();
    return Focus(
      autofocus: true,
      onKeyEvent: (_, e) {
        if (totale < 2 || e is! KeyDownEvent) return KeyEventResult.ignored;
        if (e.logicalKey == LogicalKeyboardKey.arrowRight) {
          setState(() => _i = (_i + 1) % totale);
          return KeyEventResult.handled;
        }
        if (e.logicalKey == LogicalKeyboardKey.arrowLeft) {
          setState(() => _i = (_i - 1 + totale) % totale);
          return KeyEventResult.handled;
        }
        return KeyEventResult.ignored;
      },
      child: FinestraModale(
        titolo: titolo,
        alChiudi: chiudi,
        child: ZoomCarte(
          totale: totale,
          indice: _i,
          alCambio: (i) => setState(() => _i = i),
          alChiudi: chiudi,
          etichettaChiudi: t.mazzi_campione_chiudi,
          didascalia: c.etichetta,
          carta: ImmagineNoveSedici(ref.watch(immagineMediaProvider)(c.url!), alt: c.etichetta ?? titolo),
        ),
      ),
    );
  }
}

/// «Suggerisci un tema»: il testo libero (da 3 a 1000 caratteri) per un mazzo futuro.
class _Suggerisci extends ConsumerStatefulWidget {
  const _Suggerisci();

  @override
  ConsumerState<_Suggerisci> createState() => _SuggerisciState();
}

class _SuggerisciState extends ConsumerState<_Suggerisci> {
  final TextEditingController _testo = TextEditingController();
  bool _inCorso = false;
  bool _inviato = false;
  String? _errore;

  @override
  void dispose() {
    _testo.dispose();
    super.dispose();
  }

  Future<void> _invia() async {
    setState(() {
      _inCorso = true;
      _errore = null;
    });
    try {
      await ref.read(apiProvider).suggerisciTemaMazzo(_testo.text.trim());
      _testo.clear();
      _inviato = true;
    } on ErroreApi catch (e) {
      if (mounted) _errore = e.messaggio(context.t);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Pannello(
      titolo: t.mazzi_suggerisci_titolo,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 13.44),
            child: Paragrafo(t.mazzi_suggerisci_testo, style: Stile.sans(13.44)),
          ),
          CampoTesto(
            controllore: _testo,
            semantica: t.mazzi_suggerisci_titolo,
            segnaposto: t.mazzi_suggerisci_segnaposto,
            righe: null,
            lunghezzaMassima: 1000,
            alCambio: (_) => setState(() => _inviato = false),
          ),
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: Bottone(
              t.mazzi_suggerisci_invia,
              variante: Variante.quieto,
              alTocco: _inCorso || _testo.text.trim().length < 3 ? null : () => unawaited(_invia()),
            ),
          ),
          if (_inviato) Successo(t.mazzi_suggerisci_grazie),
          if (_errore != null) Errore(_errore!),
        ],
      ),
    );
  }
}
