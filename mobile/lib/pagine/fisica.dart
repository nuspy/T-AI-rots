/// Le proprie carte (`frontend/v2/lettura/fisica.tsx`): il mazzo è fisico e già estratto. Si sceglie la stesa usata, si
/// dice quale carta c'è in ogni posizione, si scrive la domanda; poi la stessa apertura di sempre (`POST /readings`
/// con `manual_cards`) e la lettura continua nella pagina della lettura (`/read?id=…`), che mostra le carte già
/// scoperte.
///
/// Il tavolo e la domanda si ricordano sul telefono (`tarots.v2.fisica`, la chiave della sessione del browser nel
/// sito): chi deve entrare nell'account per continuare li ritrova al ritorno. Niente spazi pubblicitari.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/miniatura_stesa.dart';
import '../componenti/modale.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lettura/comuni.dart' show PannelliLettura;
import '../lettura/domanda.dart';
import '../lettura/immagine_condivisione.dart' show nomeCartaIn, nomePosizioneIn, nomeStesaIn;
import '../lettura/tavolo.dart';
import '../lingua/lingua.dart';
import '../modelli/carta.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'lettura_dettaglio.dart' show EyebrowPannello, PannelloLettura, TitoloPannelloLettura;

/// La chiave della bozza (quella della sessione del browser nel sito).
const String chiaveBozzaFisica = 'tarots.v2.fisica';

/// I semi, nell'ordine del dialogo.
const List<String> semiFisica = ['maggiori', 'bastoni', 'coppe', 'spade', 'dischi'];

/// Le stese standard, nella lingua dei contenuti.
final steseFisicaProvider = FutureProvider.autoDispose.family<List<Stesa>, String>(
  (ref, lingua) => ref.read(apiProvider).stese(lingua, categoria: 'standard'),
);

/// Le 78 carte, nella lingua dei contenuti.
final carteFisicaProvider = FutureProvider.autoDispose.family<List<Carta>, String>(
  (ref, lingua) => ref.read(apiProvider).carte(lingua),
);

/// La pagina.
class LetturaFisica extends ConsumerStatefulWidget {
  /// La lettura delle proprie carte (con `?source=` dai QR e dai collegamenti).
  const LetturaFisica({super.key, required this.parametri});

  /// La query dell'indirizzo.
  final Map<String, String> parametri;

  @override
  ConsumerState<LetturaFisica> createState() => _LetturaFisicaState();
}

class _LetturaFisicaState extends ConsumerState<LetturaFisica> {
  final TextEditingController _domanda = TextEditingController();
  String? _stesaId;
  Map<int, String> _assegnazioni = {};
  bool _inCorso = false;
  String? _errore;

  @override
  void initState() {
    super.initState();
    _leggiBozza();
    _domanda.addListener(() {
      setState(() {});
      _salvaBozza();
    });
    final sorgente = widget.parametri['source'];
    if (sorgente != null && sorgente.isNotEmpty) {
      ref.read(lanternaProvider).traccia(sorgente == 'qr' ? 'qr_entry' : 'reading_entry', {
        'sorgente': sorgente,
        'pagina': 'fisica',
      });
    }
  }

  @override
  void dispose() {
    _domanda.dispose();
    super.dispose();
  }

  void _leggiBozza() {
    try {
      final b = jsonDecode(ref.read(archivioProvider).leggi(chiaveBozzaFisica) ?? 'null');
      if (b is! Map) return;
      _stesaId = b['stesaId'] as String?;
      final a = b['assegnazioni'];
      if (a is Map) {
        _assegnazioni = {
          for (final e in a.entries)
            if (int.tryParse('${e.key}') != null && e.value is String) int.parse('${e.key}'): e.value as String,
        };
      }
      _domanda.text = b['domanda'] is String ? b['domanda'] as String : '';
    } on FormatException {
      // una bozza illeggibile si dimentica
    }
  }

  void _salvaBozza() {
    unawaited(
      ref
          .read(archivioProvider)
          .scrivi(
            chiaveBozzaFisica,
            jsonEncode({
              'stesaId': _stesaId,
              'assegnazioni': {for (final e in _assegnazioni.entries) '${e.key}': e.value},
              'domanda': _domanda.text,
            }),
          ),
    );
  }

  void _scegliStesa(String id) {
    if (id == _stesaId) return;
    setState(() {
      _stesaId = id;
      _assegnazioni = {};
    });
    _salvaBozza();
    ref.read(lanternaProvider).traccia('physical_reading_started');
  }

  /// Il dialogo della carta di una posizione: prima il seme, poi la carta.
  Future<void> _scegliCarta(Stesa stesa, int posizione, List<Carta> carte, String lingua) async {
    final t = context.t;
    final nome = nomePosizioneIn(stesa.posizioni.firstWhere((p) => p.n == posizione), lingua);
    final occupate = _assegnazioni.values.toSet();
    while (mounted) {
      final seme = await apriModale<String>(
        context,
        titolo: t.fisica_seme_titolo(nome),
        costruisci: (context) => Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (final s in semiFisica)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _VoceSeme(testo: t.fisicaSemi[s] ?? s, alTocco: () => Navigator.of(context).pop(s)),
              ),
          ],
        ),
      );
      if (seme == null || !mounted) return;
      final visibili = carte.where((c) => seme == 'maggiori' ? c.arcano == 'maggiore' : c.seme == seme).toList();
      final scelta = await apriModale<String>(
        context,
        titolo: t.fisica_carta_titolo(nome),
        costruisci: (context) =>
            _SceltaCarta(carte: visibili, occupate: occupate.difference({_assegnazioni[posizione]}), lingua: lingua),
      );
      if (!mounted) return;
      if (scelta == _SceltaCarta.indietro) continue;
      if (scelta != null) {
        setState(() => _assegnazioni = {..._assegnazioni, posizione: scelta});
        _salvaBozza();
      }
      return;
    }
  }

  Future<void> _chiediInizio() async {
    final sessione = ref.read(sessioneProvider);
    if (!sessione.autenticata) {
      await entraDa(ref);
      return;
    }
    final t = context.t;
    String testo = '';
    try {
      testo = await ref.read(apiProvider).disclaimer(ref.read(linguaProvider));
    } on ErroreApi {
      // arriva con la lettura
    }
    if (!mounted) return;
    final si = await apriModale<bool>(
      context,
      titolo: t.lettura_avviso_titolo,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 15.2),
            child: Text(testo, style: Stile.sans(15.2, colore: Token.inkSoft, altezza: 1.6)),
          ),
          FilaBottoni(
            children: [
              Bottone(
                t.lettura_avviso_accetta,
                variante: Variante.ottone,
                alTocco: () => Navigator.of(context).pop(true),
              ),
            ],
          ),
        ],
      ),
    );
    if (si == true) await _apri();
  }

  Future<void> _apri() async {
    final id = _stesaId;
    if (id == null) return;
    setState(() {
      _inCorso = true;
      _errore = null;
    });
    try {
      final a = await ref
          .read(apiProvider)
          .apriLettura(
            spreadId: id,
            domanda: _domanda.text.trim(),
            lingua: ref.read(linguaProvider),
            carteManuali: [for (final e in _assegnazioni.entries) (posizione: e.key, cardId: e.value)],
          );
      ref.read(lanternaProvider).traccia('reading_started', {'categoria': 'manuale'});
      unawaited(ref.read(archivioProvider).scrivi(chiaveBozzaFisica, null));
      if (a.id != null && mounted) unawaited(GoRouter.of(context).replace<void>('${R.leggi}?id=${a.id}'));
    } on ErroreApi catch (e) {
      if (mounted) {
        setState(() {
          _errore = e.motivo ?? context.t.lettura_err_lettura;
          _inCorso = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final contenuti = linguaContenuti(lingua);
    final sessione = ref.watch(sessioneProvider);
    final stese = ref.watch(steseFisicaProvider(contenuti));
    final carte = ref.watch(carteFisicaProvider(contenuti)).value ?? const <Carta>[];
    final stesa = stese.value?.where((s) => s.id == _stesaId).firstOrNull;
    final daRiempire = stesa == null ? const <Posizione>[] : stesa.posizioni.where((p) => !p.calcolata).toList();
    final mancano = daRiempire.where((p) => !_assegnazioni.containsKey(p.n)).length;
    final pronta = stesa != null && mancano == 0 && domandaBasta(_domanda.text);
    final posate = [
      for (final e in _assegnazioni.entries)
        Posata(
          posizione: e.key,
          calcolata: false,
          rivelata: false,
          carta: carte.where((c) => c.id == e.value).firstOrNull,
        ),
    ];

    final sinistra = PannelloLettura(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          EyebrowPannello(t.fisica_passo_1),
          if (stesa == null) ...[
            TitoloPannelloLettura(t.fisica_stesa_titolo),
            if (stese.value != null)
              _SceltaStesa(stese: stese.value!, scelta: _stesaId, lingua: lingua, alScegli: _scegliStesa),
            if (stese.hasError) Errore(messaggioErrore(stese.error!, t)),
          ] else ...[
            TitoloPannelloLettura(nomeStesaIn(stesa, lingua)),
            Paragrafo(t.fisica_posiziona, style: Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6)),
            const SizedBox(height: 13.44),
            Tavolo(
              stesa: stesa,
              posate: posate,
              manuale: true,
              alSelezionaPosizione: (p) => unawaited(_scegliCarta(stesa, p, carte, lingua)),
              testoAggiungi: t.fisica_aggiungi,
              testoModifica: t.fisica_modifica,
            ),
            Semantics(
              liveRegion: true,
              child: mancano == 0
                  ? Successo(t.fisica_pronte)
                  : Avviso(mancano == 1 ? t.fisica_manca_una : t.fisica_mancano(mancano)),
            ),
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Align(
                alignment: AlignmentDirectional.centerStart,
                child: Bottone(
                  t.fisica_cambia_stesa,
                  piccolo: true,
                  variante: Variante.quieto,
                  alTocco: () {
                    setState(() {
                      _stesaId = null;
                      _assegnazioni = {};
                    });
                    _salvaBozza();
                  },
                ),
              ),
            ),
          ],
        ],
      ),
    );

    final destra = PannelloLettura(
      scuro: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          EyebrowPannello(t.fisica_passo_2, scuro: true),
          TitoloPannelloLettura(t.fisica_domanda_titolo, colore: const Color(0xFFF6ECDD)),
          _CampoDomanda(
            controllore: _domanda,
            segnaposto: t.fisica_domanda_segnaposto,
            etichetta: t.fisica_domanda_titolo,
          ),
          Padding(
            padding: const EdgeInsets.only(top: 3.2, bottom: 9.6),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: larghezzaCh(Stile.serif(18.4), MediaQuery.textScalerOf(context)) * 34,
              ),
              child: Paragrafo(
                t.fisica_domanda_testo,
                style: Stile.serif(18.4, stile: FontStyle.italic, altezza: 1.45, colore: const Color(0xFFFBF3E5)),
              ),
            ),
          ),
          if (sessione.pronta && !sessione.autenticata)
            Padding(padding: const EdgeInsets.only(bottom: 16), child: Avviso(t.fisica_serve_account, scuro: true)),
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: Bottone(
              _inCorso
                  ? t.comune_carica
                  : (sessione.autenticata || !sessione.pronta ? t.fisica_interpreta : t.fisica_entra),
              variante: Variante.ottone,
              alTocco: pronta && !_inCorso ? () => unawaited(_chiediInizio()) : null,
            ),
          ),
          if (_errore != null) Errore(_errore!),
        ],
      ),
    );

    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.fisica_eyebrow, titolo: t.fisica_titolo, intro: t.fisica_intro, compatta: true),
        Fascia(
          compatta: true,
          child: PannelliLettura(sinistra: sinistra, destra: destra),
        ),
      ],
    );
  }
}

/// `.domanda`: il campo grande della domanda (bianco, il bordo d'ottone velato, l'ombra lieve).
class _CampoDomanda extends StatefulWidget {
  const _CampoDomanda({required this.controllore, required this.segnaposto, required this.etichetta});

  final TextEditingController controllore;
  final String segnaposto;
  final String etichetta;

  @override
  State<_CampoDomanda> createState() => _CampoDomandaState();
}

class _CampoDomandaState extends State<_CampoDomanda> {
  final FocusNode _fuoco = FocusNode(debugLabel: 'domanda-fisica');
  final GlobalKey<EditableTextState> _campo = GlobalKey(debugLabel: 'campo');

  @override
  void dispose() {
    _fuoco.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final stile = Stile.sans(16, colore: Token.ink, altezza: 1.5);
    return Semantics(
      textField: true,
      label: widget.etichetta,
      child: GestureDetector(
        onTap: () => mostraTastiera(_fuoco, _campo),
        child: Container(
          constraints: const BoxConstraints(minHeight: 120),
          padding: const EdgeInsets.all(13.6),
          decoration: BoxDecoration(
            color: const Color(0xFFFFFFFF),
            border: Border.all(color: const Color(0x8CB28336)),
            boxShadow: const [BoxShadow(color: Color(0x143C1846), offset: Offset(0, 10), blurRadius: 30)],
          ),
          child: Stack(
            children: [
              ValueListenableBuilder(
                valueListenable: widget.controllore,
                builder: (context, v, _) => v.text.isEmpty
                    ? IgnorePointer(
                        child: Text(widget.segnaposto, style: stile.copyWith(color: Colori.segnaposto)),
                      )
                    : const SizedBox.shrink(),
              ),
              EditableText(
                key: _campo,
                controller: widget.controllore,
                focusNode: _fuoco,
                style: stile,
                cursorColor: Token.ink,
                backgroundCursorColor: Token.inkSoft,
                selectionColor: const Color(0x4019706F),
                minLines: 4,
                maxLines: null,
                keyboardType: TextInputType.multiline,
                textCapitalization: TextCapitalization.sentences,
                inputFormatters: [LengthLimitingTextInputFormatter(1000)],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// La scelta della stesa (`SceltaStesa` senza stili né titolo): le schede con la miniatura, il nome, le carte.
class _SceltaStesa extends StatelessWidget {
  const _SceltaStesa({required this.stese, required this.scelta, required this.lingua, required this.alScegli});

  final List<Stesa> stese;
  final String? scelta;
  final String lingua;
  final ValueChanged<String> alScegli;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final stretto = MediaQuery.sizeOf(context).width <= 640;
    return LayoutBuilder(
      builder: (context, vincoli) {
        // `.stese`: `repeat(auto-fill, minmax(150px, 1fr))`, `gap: .9rem`; fino a 640 px due colonne.
        const spazio = 14.4;
        final colonne = stretto ? 2 : math.max(1, ((vincoli.maxWidth + spazio) / (150 + spazio)).floor());
        final larghezza = (vincoli.maxWidth - spazio * (colonne - 1)) / colonne;
        return Wrap(
          spacing: spazio,
          runSpacing: spazio,
          children: [
            for (final s in stese)
              SizedBox(
                width: larghezza,
                child: Premibile(
                  alTocco: () => alScegli(s.id),
                  selezionato: s.id == scelta,
                  costruisci: (context, premuto) {
                    final scelta2 = s.id == scelta;
                    return Container(
                      padding: const EdgeInsets.all(12.8),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFFFFF),
                        border: Border.all(color: scelta2 ? Token.plum : (premuto ? Token.brass : Token.line)),
                        boxShadow: scelta2 ? const [BoxShadow(color: Token.brassPale, offset: Offset(3, 3))] : null,
                      ),
                      foregroundDecoration: scelta2
                          ? BoxDecoration(border: Border.all(color: Token.plum, width: 2))
                          : null,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          ColoredBox(
                            color: Token.plumDeep,
                            child: MiniaturaStesa(stesa: s),
                          ),
                          const SizedBox(height: 5.6),
                          Text(nomeStesaIn(s, lingua), style: Stile.serif(15.68, altezza: 1.25, colore: Token.ink)),
                          const SizedBox(height: 5.6),
                          Text(
                            '${t.lettura_n_carte(s.posizioni.length)} · '
                            '${s.mazzo == 'maggiori' ? t.lettura_maggiori : t.lettura_completo}',
                            style: Stile.sans(12.16, colore: Token.inkSoft, altezza: 1.6),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
          ],
        );
      },
    );
  }
}

/// Un seme nel dialogo: un `.button-quiet` a tutta larghezza, col testo a sinistra.
class _VoceSeme extends StatelessWidget {
  const _VoceSeme({required this.testo, required this.alTocco});

  final String testo;
  final VoidCallback alTocco;

  @override
  Widget build(BuildContext context) => Premibile(
    alTocco: alTocco,
    raggioFuoco: Token.raggio,
    costruisci: (context, premuto) => Container(
      constraints: const BoxConstraints(minHeight: Token.altezzaBottone),
      padding: const EdgeInsets.symmetric(horizontal: 17.6, vertical: 11.52),
      alignment: AlignmentDirectional.centerStart,
      decoration: BoxDecoration(
        color: premuto ? const Color(0x0F3C1846) : null,
        border: Border.all(color: Token.line),
        borderRadius: BorderRadius.circular(Token.raggio),
      ),
      child: Text(testo, style: Stile.bottone().copyWith(color: Token.plum)),
    ),
  );
}

/// Le carte di un seme come pillole (scorrono se sono tante), «indietro» e «posa questa carta».
class _SceltaCarta extends StatefulWidget {
  const _SceltaCarta({required this.carte, required this.occupate, required this.lingua});

  /// Il valore restituito da «indietro»: si torna ai semi.
  static const String indietro = '\u0000indietro';

  final List<Carta> carte;
  final Set<String?> occupate;
  final String lingua;

  @override
  State<_SceltaCarta> createState() => _SceltaCartaState();
}

class _SceltaCartaState extends State<_SceltaCarta> {
  String? _scelta;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final altezza = MediaQuery.sizeOf(context).height * .5;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ConstrainedBox(
          constraints: BoxConstraints(maxHeight: altezza),
          child: SingleChildScrollView(
            child: Pillole(
              children: [
                for (final c in widget.carte)
                  Builder(
                    builder: (context) {
                      final occupata = widget.occupate.contains(c.id) && _scelta != c.id;
                      final nome = nomeCartaIn(c, widget.lingua);
                      return Opacity(
                        opacity: occupata ? .55 : 1,
                        child: Semantics(
                          hint: occupata ? t.fisica_gia_posata : null,
                          child: Pillola(
                            nome,
                            acceso: c.id == _scelta,
                            alTocco: occupata ? null : () => setState(() => _scelta = c.id),
                          ),
                        ),
                      );
                    },
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        FilaBottoni(
          children: [
            Bottone(
              t.comune_indietro,
              variante: Variante.quieto,
              alTocco: () => Navigator.of(context).pop(_SceltaCarta.indietro),
            ),
            Bottone(t.fisica_conferma, alTocco: _scelta == null ? null : () => Navigator.of(context).pop(_scelta)),
          ],
        ),
      ],
    );
  }
}
