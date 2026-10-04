/// La mia storia (`frontend/v2/pagine/storia.tsx`): le letture tenute (il filo) e ciò che il lettore ricorda —
/// visibile e gestibile. Chi non è entrato legge che cosa si ricorda, perché, e chi decide.
///
/// Le due colonne di `.story-grid` (la memoria a sinistra sul verde nebbia, il filo a destra; una sotto l'altra sul
/// telefono); le letture come `.memory-entry`; la memoria con la modifica in linea e la cancellazione singola o
/// multipla, con la doppia conferma del sito.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lettura/immagine_condivisione.dart' show nomeStesaDaNomi;
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// Le letture della storia.
final lettureStoriaProvider = FutureProvider.autoDispose<ElencoLetture>((ref) {
  ref.watch(sessioneProvider.select((s) => s.autenticata));
  return ref.read(apiProvider).letture();
});

/// Ciò che il lettore ricorda.
final memorieProvider = FutureProvider.autoDispose<List<Memoria>>((ref) {
  ref.watch(sessioneProvider.select((s) => s.autenticata));
  return ref.read(apiProvider).memorie();
});

/// `.story-sidebar h2, .story-main h2`: `font: 400 1.45rem var(--serif); margin-top: 0` (sotto, il margine del
/// browser: .83em).
Widget _titolo(String testo, {double sopra = 0}) => Padding(
  padding: EdgeInsets.only(top: sopra, bottom: 19.26),
  child: Semantics(
    header: true,
    child: TestoBilanciato(testo, stile: Stile.serif(23.2, colore: Token.ink)),
  ),
);

/// `p.small` col suo margine di paragrafo (1em).
Widget _piccolo(String testo, {Color colore = Token.ink}) => Padding(
  padding: const EdgeInsets.symmetric(vertical: 13.44),
  child: Paragrafo(testo, style: Stile.sans(13.44, colore: colore, altezza: 1.6)),
);

/// La pagina.
class Storia extends ConsumerWidget {
  /// La mia storia.
  const Storia({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.storia_eyebrow, titolo: t.storia_titolo, intro: t.storia_intro, compatta: true),
        if (sessione.pronta) sessione.autenticata ? const _Dentro() : const _Fuori(),
      ],
    );
  }
}

/// `.story-grid`: `.75fr 1.25fr`, `gap: .7rem`, in alto; una colonna sul telefono.
class _Griglia extends StatelessWidget {
  const _Griglia({required this.laterale, required this.principale});

  final Widget laterale;
  final Widget principale;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final lato = Container(
      color: Token.mist,
      padding: const EdgeInsets.symmetric(horizontal: 20.8, vertical: 10.4),
      child: laterale,
    );
    return Fascia(
      compatta: true,
      child: w.telefono
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [lato, const SizedBox(height: 11.2), principale],
            )
          : Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 75, child: lato),
                const SizedBox(width: 11.2),
                Expanded(flex: 125, child: principale),
              ],
            ),
    );
  }
}

/* ---- chi non è entrato --------------------------------------------------------------------------------------------- */

class _Fuori extends ConsumerWidget {
  const _Fuori();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final laterale = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _titolo(t.storia_cosa_titolo),
        // `.memory-list` con `margin: 0 0 1.4rem`.
        Padding(
          padding: const EdgeInsets.only(bottom: 22.4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (final c in t.storiaCosa)
                Container(
                  padding: EdgeInsets.symmetric(vertical: telefono ? 9.6 : 13.6),
                  decoration: const BoxDecoration(
                    border: Border(bottom: BorderSide(color: Token.line)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(c.titolo, style: Stile.sans(14.72, peso: FontWeight.w700, altezza: 1.6)),
                      Text(c.testo, style: Stile.sans(13.76, colore: Token.inkSoft, altezza: 1.6)),
                    ],
                  ),
                ),
            ],
          ),
        ),
        _titolo(t.storia_perche_titolo),
        _piccolo(t.storia_perche_testo),
      ],
    );
    final principale = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _SchedaMemoria(),
        _titolo(t.storia_fuori_titolo, sopra: 14.4),
        IntroSezione(t.storia_fuori_testo),
        Padding(
          padding: const EdgeInsets.only(top: 16),
          child: FilaBottoni(
            children: [
              Bottone(t.storia_fuori_entra, alTocco: () => unawaited(entraDa(ref))),
              Bottone(t.storia_fuori_inizia, href: R.leggi, variante: Variante.ottone),
            ],
          ),
        ),
      ],
    );
    return _Griglia(laterale: laterale, principale: principale);
  }
}

/// `.memory-card`: la citazione del lettore che ricorda, sul prugna con l'ombra d'ottone spostata.
class _SchedaMemoria extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final ombra = telefono ? 9.0 : 15.0;
    final px = telefono ? 19.2 : 23.2;
    return Container(
      padding: EdgeInsets.symmetric(horizontal: telefono ? 22.4 : 35.2, vertical: 17.6),
      decoration: BoxDecoration(
        color: Token.plum,
        boxShadow: [BoxShadow(color: const Color(0x59B28336), offset: Offset(ombra, ombra))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 11.2),
            child: Text(
              t.home_memoria_etichetta.toUpperCase(),
              style: Stile.sans(11.2, peso: FontWeight.w700, em: .1, colore: Token.brassPale, altezza: 1.6),
            ),
          ),
          ConstrainedBox(
            constraints: BoxConstraints(maxWidth: larghezzaCh(Stile.serif(px), MediaQuery.textScalerOf(context)) * 28),
            child: TestoBilanciato(
              t.home_memoria_citazione,
              stile: Stile.serif(px, stile: FontStyle.italic, altezza: 1.45, colore: const Color(0xFFF8F0E1)),
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(top: 9.6),
            child: Text(t.home_memoria_piede, style: Stile.sans(12.8, colore: const Color(0xFFD5C4DA), altezza: 1.6)),
          ),
        ],
      ),
    );
  }
}

/* ---- chi è dentro ------------------------------------------------------------------------------------------------- */

class _Dentro extends ConsumerStatefulWidget {
  const _Dentro();

  @override
  ConsumerState<_Dentro> createState() => _DentroState();
}

class _DentroState extends ConsumerState<_Dentro> {
  @override
  void initState() {
    super.initState();
    // Una volta, all'apertura (come il sito appena l'osservatore c'è).
    ref.read(lanternaProvider).traccia('memory_viewed');
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return _Griglia(
      laterale: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [const _Memorie(), _titolo(t.storia_perche_titolo, sopra: 10.4), _piccolo(t.storia_perche_testo)],
      ),
      principale: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [_titolo(t.storia_letture_titolo), const _Letture()],
      ),
    );
  }
}

/// Il filo: le letture dalla più recente.
class _Letture extends ConsumerWidget {
  const _Letture();

  Future<void> _cancella(BuildContext context, WidgetRef ref, LetturaBreve l) async {
    final t = context.t;
    final testo = Stile.sans(15.2, colore: Token.inkSoft, altezza: 1.6);
    final si = await apriModale<bool>(
      context,
      titolo: t.storia_cancella_conferma_titolo,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Paragrafo('«${l.question}»', style: testo),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 15.2),
            child: Paragrafo(t.storia_cancella_conferma_testo, style: testo),
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
    if (si != true) return;
    try {
      await ref.read(apiProvider).cancellaLettura(l.id);
    } on ErroreApi catch (e) {
      debugPrint('Lettura non cancellata: ${e.stato}');
    }
    ref.invalidate(lettureStoriaProvider);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final letture = ref.watch(lettureStoriaProvider);
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final dati = letture.value;
    if (dati == null) {
      return letture.hasError
          ? Errore(messaggioErrore(letture.error!, t), sopra: 0)
          : Text(t.comune_carica, style: Stile.sans(16, colore: Token.inkSoft));
    }
    if (dati.letture.isEmpty) {
      return Pannello(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(padding: const EdgeInsets.only(bottom: 16), child: Paragrafo(t.storia_letture_vuoto)),
            Bottone(t.storia_letture_inizia, href: R.leggi, variante: Variante.ottone),
          ],
        ),
      );
    }
    final stati = t.storiaStati;
    final badge = t.storiaBadge;
    final esiti = t.storiaEsiti;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final l in dati.letture)
          Builder(
            builder: (context) {
              final finita = l.status == 'completata';
              final testa = [
                if (l.categoria != 'standard') '${badge[l.categoria] ?? ''} · ',
                nomeStesaDaNomi(l.stesa, l.stesaNomi, lingua),
                if (l.partnerNome != null) ' · ${t.lettura_tu_e(l.partnerNome!)}',
                ' · ${dataLunga(l.createdAt, lingua)}',
              ].join();
              final carte = l.carte.isEmpty ? '' : ' · ${l.carte.take(4).join(', ')}${l.carte.length > 4 ? '…' : ''}';
              final esito = l.feedback == null ? '' : ' · ${t.storia_esito} ${esiti[l.feedback] ?? l.feedback}';
              return Container(
                padding: EdgeInsets.symmetric(vertical: telefono ? 12.8 : 17.6),
                decoration: const BoxDecoration(
                  border: Border(bottom: BorderSide(color: Token.line)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      testa.toUpperCase(),
                      style: Stile.sans(11.52, peso: FontWeight.w700, em: .05, colore: Token.verdigris, altezza: 1.6),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4.8),
                      child: Semantics(
                        header: true,
                        child: TestoBilanciato(l.question, stile: Stile.serif(17.6, colore: Token.ink)),
                      ),
                    ),
                    Paragrafo(
                      '${stati[l.status] ?? l.status}$carte$esito',
                      style: Stile.sans(14.08, colore: Token.inkSoft, altezza: 1.6),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(top: 9.6),
                      child: FilaBottoni(
                        children: [
                          Bottone(
                            finita ? t.storia_rileggi : t.storia_continua,
                            href: finita ? R.lettura(l.id) : '${R.leggi}?id=${l.id}',
                            piccolo: true,
                            variante: Variante.quieto,
                          ),
                          if (finita)
                            Bottone(
                              t.storia_riprendi_tema,
                              href: '${R.leggi}?question=${Uri.encodeComponent(l.question)}&source=story',
                              piccolo: true,
                              variante: Variante.quieto,
                              an: 'followup_started',
                            ),
                          Semantics(
                            label: '${t.storia_cancella}: ${l.question}',
                            excludeSemantics: true,
                            button: true,
                            child: Bottone(
                              t.storia_cancella,
                              piccolo: true,
                              variante: Variante.pericolo,
                              alTocco: () => unawaited(_cancella(context, ref, l)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
      ],
    );
  }
}

/* ---- la memoria --------------------------------------------------------------------------------------------------- */

/// La memoria: elenco, modifica in linea, cancellazione singola e multipla con doppia conferma. Il bottone in fondo
/// è uno solo — «elimina selezionate» se ce n'è almeno una, altrimenti «elimina tutte».
class _Memorie extends ConsumerStatefulWidget {
  const _Memorie();

  @override
  ConsumerState<_Memorie> createState() => _MemorieState();
}

class _MemorieState extends ConsumerState<_Memorie> {
  final Set<String> _selezionate = {};
  String? _errore;

  Future<void> _conferma() async {
    final t = context.t;
    final alcune = _selezionate.isNotEmpty;
    final testo = Stile.sans(15.2, colore: Token.inkSoft, altezza: 1.6);
    final si = await apriModale<bool>(
      context,
      titolo: t.storia_conferma_titolo,
      costruisci: (context) => _DoppiaConferma(
        domanda: alcune
            ? (_selezionate.length == 1 ? t.storia_conferma_una : t.storia_conferma_n(_selezionate.length))
            : t.storia_conferma_tutte,
        stile: testo,
      ),
    );
    if (si != true || !mounted) return;
    try {
      if (alcune) {
        await ref.read(apiProvider).eliminaMemorie(ids: [..._selezionate]);
      } else {
        await ref.read(apiProvider).eliminaMemorie(tutte: true);
      }
      ref.read(lanternaProvider).traccia('memory_updated', {'azione': alcune ? 'elimina_alcune' : 'elimina_tutte'});
      setState(() {
        _selezionate.clear();
        _errore = null;
      });
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _errore = e.messaggio(context.t));
    }
    ref.invalidate(memorieProvider);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final memorie = ref.watch(memorieProvider);
    final elenco = memorie.value ?? const <Memoria>[];
    return Semantics(
      container: true,
      label: t.storia_memoria_titolo,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _titolo(t.storia_memoria_titolo),
          _piccolo(t.storia_memoria_testo),
          if (memorie.hasError && !memorie.hasValue) Errore(messaggioErrore(memorie.error!, t)),
          if (memorie.hasValue && elenco.isEmpty) _piccolo(t.storia_memoria_vuoto, colore: Token.inkSoft),
          if (elenco.isNotEmpty) ...[
            for (final m in elenco)
              _RigaMemoria(
                key: ValueKey(m.id),
                memoria: m,
                selezionata: _selezionate.contains(m.id),
                alSeleziona: () => setState(() {
                  if (!_selezionate.remove(m.id)) _selezionate.add(m.id);
                }),
                alCambio: () {
                  ref.read(lanternaProvider).traccia('memory_updated', {'azione': 'modifica'});
                  ref.invalidate(memorieProvider);
                },
              ),
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Align(
                alignment: AlignmentDirectional.centerStart,
                child: Bottone(
                  _selezionate.isNotEmpty ? t.storia_elimina_selezionate : t.storia_elimina_tutte,
                  piccolo: true,
                  variante: Variante.pericolo,
                  alTocco: () => unawaited(_conferma()),
                ),
              ),
            ),
          ],
          if (_errore != null) Errore(_errore!),
        ],
      ),
    );
  }
}

/// I due passi della conferma: prima «continua», poi la casella «ho capito che non si torna indietro».
class _DoppiaConferma extends StatefulWidget {
  const _DoppiaConferma({required this.domanda, required this.stile});

  final String domanda;
  final TextStyle stile;

  @override
  State<_DoppiaConferma> createState() => _DoppiaConfermaState();
}

class _DoppiaConfermaState extends State<_DoppiaConferma> {
  bool _secondo = false;
  bool _casella = false;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    if (!_secondo) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 15.2),
            child: Paragrafo(widget.domanda, style: widget.stile),
          ),
          FilaBottoni(
            children: [
              Bottone(t.storia_conferma_continua, alTocco: () => setState(() => _secondo = true)),
              Bottone(t.storia_annulla, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop(false)),
            ],
          ),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Casella(valore: _casella, alCambio: (v) => setState(() => _casella = v), titolo: t.storia_conferma_casella),
        const SizedBox(height: 8),
        FilaBottoni(
          children: [
            Bottone(
              t.storia_conferma_elimina,
              variante: Variante.pericolo,
              alTocco: _casella ? () => Navigator.of(context).pop(true) : null,
            ),
            Bottone(t.storia_annulla, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop(false)),
          ],
        ),
      ],
    );
  }
}

/// Una memoria (`.memory-entry`), con la modifica in linea.
class _RigaMemoria extends ConsumerStatefulWidget {
  const _RigaMemoria({
    super.key,
    required this.memoria,
    required this.selezionata,
    required this.alSeleziona,
    required this.alCambio,
  });

  final Memoria memoria;
  final bool selezionata;
  final VoidCallback alSeleziona;
  final VoidCallback alCambio;

  @override
  ConsumerState<_RigaMemoria> createState() => _RigaMemoriaState();
}

class _RigaMemoriaState extends ConsumerState<_RigaMemoria> {
  bool _modifica = false;
  bool _inCorso = false;
  late final TextEditingController _contenuto = TextEditingController(text: widget.memoria.contenuto);
  late final TextEditingController _campo = TextEditingController(text: widget.memoria.campoAttinenza);

  @override
  void initState() {
    super.initState();
    _contenuto.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _contenuto.dispose();
    _campo.dispose();
    super.dispose();
  }

  Future<void> _esegui(Future<void> Function() azione) async {
    setState(() => _inCorso = true);
    try {
      await azione();
      widget.alCambio();
    } on ErroreApi catch (e) {
      debugPrint('Memoria non cambiata: ${e.stato}');
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final m = widget.memoria;
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final fonte = t.storiaFonte[m.fonte];
    final api = ref.read(apiProvider);
    return Container(
      padding: EdgeInsets.symmetric(vertical: telefono ? 12.8 : 17.6),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Token.line)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            '${m.tipo == 'stabile' ? t.storia_tipo_stabile : t.storia_tipo_variabile} · ${m.campoAttinenza}'
                    '${fonte != null ? ' · $fonte' : ''}'
                .toUpperCase(),
            style: Stile.sans(11.52, peso: FontWeight.w700, em: .05, colore: Token.verdigris, altezza: 1.6),
          ),
          if (_modifica)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  CampoTesto(etichetta: t.storia_memoria_titolo, controllore: _contenuto, righe: 6, minimoRighe: 3),
                  CampoTesto(etichetta: t.storia_campo, controllore: _campo),
                  FilaBottoni(
                    children: [
                      Bottone(
                        t.storia_salva,
                        piccolo: true,
                        alTocco: _inCorso || _contenuto.text.trim().isEmpty
                            ? null
                            : () => unawaited(
                                _esegui(() async {
                                  await api.modificaMemoria(
                                    m.id,
                                    contenuto: _contenuto.text.trim(),
                                    campoAttinenza: _campo.text.trim(),
                                  );
                                  if (mounted) setState(() => _modifica = false);
                                }),
                              ),
                      ),
                      Bottone(
                        t.storia_annulla,
                        piccolo: true,
                        variante: Variante.quieto,
                        alTocco: () => setState(() {
                          _modifica = false;
                          _contenuto.text = m.contenuto;
                          _campo.text = m.campoAttinenza;
                        }),
                      ),
                    ],
                  ),
                ],
              ),
            )
          else
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4.8),
              child: Paragrafo(m.contenuto, style: Stile.sans(14.08, colore: Token.inkSoft, altezza: 1.6)),
            ),
          Wrap(
            spacing: 9.6,
            runSpacing: 9.6,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              IntrinsicWidth(
                child: Casella(
                  valore: widget.selezionata,
                  alCambio: (_) => widget.alSeleziona(),
                  titolo: t.storia_seleziona,
                  stileTitolo: Stile.sans(13.44, colore: Token.ink, altezza: 1.6),
                ),
              ),
              Bottone(
                t.storia_modifica,
                piccolo: true,
                variante: Variante.quieto,
                alTocco: () => setState(() => _modifica = !_modifica),
              ),
              Bottone(
                t.storia_elimina,
                piccolo: true,
                variante: Variante.pericolo,
                alTocco: _inCorso ? null : () => unawaited(_esegui(() => api.eliminaMemoria(m.id))),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
