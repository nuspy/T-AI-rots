/// I prezzi (`frontend/v2/pagine/prezzi.tsx`, `app/(v2)/pricing/page.tsx`): il cuore del modello — letture, pacchetti,
/// abbonamenti — presentato come continuità, dopo il valore, non come un cancello. Piani, prezzi e diritti vengono
/// dall'API (niente cifre inventate).
///
/// - Il conto di chi è dentro (saldo, piano, letture di oggi), il codice sconto applicato (`?coupon=`, Fase 2d), i
///   pacchetti con la lettura gratuita in testa, gli abbonamenti (mensile o annuale, col rinnovo automatico o senza,
///   Fase 2b) con la banda della prova, i codici e i movimenti, la nota di fiducia.
/// - **Fase 9: si compra nello store** (Google Play, App Store: `acquisti/`): pacchetti e abbonamenti coi prezzi
///   localizzati dello store, il ripristino, la verifica sul server prima di chiudere l'acquisto. Il **pagamento con
///   carta** (Stripe) resta solo dove il catalogo dello store lo ammette per il paese ([_SceltaMetodo]), ed è l'unico
///   dove valgono i codici sconto.
/// - **Il pagamento con carta** si apre nel browser di sistema e torna all'app (deep link su iOS, App Link
///   `https://tarots.chat/pricing?checkout=<id>` su Android): qui si chiede al server com'è andata, come il sito. Se il
///   pagamento era partito da una lettura interrotta (`?ritorno=`), si torna alla lettura (`?dopo=`).
/// - Chi è già abbonato cambia piano col conguaglio ([apriCambioPiano]), non ne apre un secondo.
///
/// Niente spazi pubblicitari (niente pubblicità nell'app al lancio).
library;

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../acquisti/acquisti.dart';
import '../acquisti/negozio.dart';
import '../acquisti/vista.dart';
import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../cassa/cambio_piano.dart';
import '../cassa/coupon.dart';
import '../cassa/pagamento.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/griglia.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../modelli/store.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// Un ritorno accettato solo dentro l'app (`dentroV2` del sito): un percorso, non un indirizzo esterno.
bool ritornoInterno(String? r) =>
    r != null && r.startsWith('/') && !r.startsWith('//') && !RegExp(r'^/old(/|\?|$)').hasMatch(r);

/// I movimenti dei crediti (con un account): si rileggono a ogni cambio di pagina, come il conto.
final movimentiProvider = FutureProvider<Movimenti?>((ref) async {
  ref.watch(contoProvider);
  if (!ref.watch(sessioneProvider.select((s) => s.autenticata))) return null;
  return ref.read(apiProvider).movimenti();
});

/// Rilegge conto, saldo e movimenti (dopo un acquisto, un riscatto, un piano gratuito).
void ricaricaConto(WidgetRef ref) {
  ref.invalidate(contoProvider);
  ref.invalidate(saldoProvider);
  ref.invalidate(movimentiProvider);
}

/// `.band.band-tight`, anche senza l'imbottitura sotto (`style={{ paddingBottom: 0 }}` del sito).
class FasciaStretta extends StatelessWidget {
  /// Una fascia stretta.
  const FasciaStretta({super.key, required this.child, this.sottoZero = false});

  /// Il contenuto.
  final Widget child;

  /// Senza l'imbottitura sotto.
  final bool sottoZero;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final v = w.telefono ? 16.0 : w.clampVw(16, 1.75, 22.4);
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: Token.larghezzaBanda),
        child: Padding(
          padding: EdgeInsets.fromLTRB(w.gutter, v, w.gutter, sottoZero ? 0 : v),
          // Una fascia è larga quanto la pagina: il contenuto non si stringe attorno al testo.
          child: SizedBox(width: double.infinity, child: child),
        ),
      ),
    );
  }
}

/// La pagina dei prezzi.
class Prezzi extends ConsumerStatefulWidget {
  /// I prezzi, coi parametri dell'indirizzo (`coupon`, `checkout`, `dopo`, `ritorno`).
  const Prezzi({super.key, required this.parametri});

  /// I parametri della query.
  final Map<String, String> parametri;

  @override
  ConsumerState<Prezzi> createState() => _PrezziState();
}

class _PrezziState extends ConsumerState<Prezzi> {
  ({bool buono, String testo})? _esito;

  /// Fase 9: la carta scelta al posto dello store (`null`: non ancora scelta).
  bool? _carta;
  Timer? _torna;

  @override
  void initState() {
    super.initState();
    // L'esito di un acquisto nello store di prima non è di questa visita.
    Future.microtask(() => ref.read(acquistiProvider.notifier).letto());
    final dalLink = widget.parametri['coupon'];
    if (dalLink != null && dalLink.isNotEmpty) {
      // Il codice del collegamento vale per la sessione dell'app (come la `sessionStorage` del sito).
      Future.microtask(() => ref.read(couponAttivoProvider.notifier).imposta(dalLink));
    }
    final checkout = widget.parametri['checkout'];
    if (checkout != null && checkout.isNotEmpty) {
      Future.microtask(() {
        ref.read(pagamentoInSospesoProvider.notifier).concluso();
        unawaited(_verifica(checkout));
      });
    }
  }

  @override
  void dispose() {
    _torna?.cancel();
    super.dispose();
  }

  /// Il ritorno dal pagamento: com'è andata la chiede al server (l'indirizzo lo può scrivere chiunque).
  Future<void> _verifica(String checkout) async {
    if (!ref.read(sessioneProvider).autenticata) return;
    final t = context.t;
    final dopo = widget.parametri['dopo'];
    try {
      final s = await ref.read(apiProvider).statoPagamento(checkout);
      if (!mounted) return;
      final buono = s.stato == 'pagato';
      setState(() {
        _esito = (
          buono: buono,
          testo: buono
              ? (s.tipo == 'pacchetto' ? t.prezzi_pagato_pacchetto(s.nome) : t.prezzi_pagato_piano(s.nome)) +
                    (ritornoInterno(dopo) ? ' ${t.prezzi_torno}' : '')
              : t.prezzi_non_completato,
        );
      });
      if (buono) {
        ref.read(lanternaProvider).traccia('purchase_completed', {'tipo': s.tipo});
        ricaricaConto(ref);
        ref.read(couponAttivoProvider.notifier).imposta(null);
        if (ritornoInterno(dopo)) {
          _torna = Timer(const Duration(milliseconds: 1400), () {
            if (mounted) vai(context, dopo!);
          });
        }
      }
    } on ErroreApi {
      if (mounted) setState(() => _esito = (buono: false, testo: t.prezzi_non_verificato));
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final autenticata = ref.watch(sessioneProvider.select((s) => s.autenticata));
    final piani = ref.watch(pianiProvider);
    final conto = autenticata ? ref.watch(contoProvider).value : null;
    // Fase 9: nell'app si compra nello store; la carta (Stripe, nel browser) solo dove il catalogo lo ammette, ed è lì
    // che valgono i codici sconto. Con un codice già scelto (`?coupon=`) si parte dalla carta, se c'è.
    final negozio = ref.watch(negozioProvider);
    final store = negozio == null ? null : ref.watch(offerteStoreProvider);
    final stripeAmmesso = store?.value?.catalogo.stripe.mostra ?? false;
    final carta = negozio == null || (stripeAmmesso && (_carta ?? ref.watch(couponAttivoProvider) != null));
    final codice = carta ? ref.watch(couponAttivoProvider) : null;
    final coupon = codice == null ? null : ref.watch(anteprimaCouponProvider(codice)).value;
    final anteprima = coupon?.ok;
    final elenco = piani.value ?? const <Piano>[];
    final pacchetti = elenco.where((p) => p.tipo == 'pacchetto').toList();
    final abbonamenti = elenco.where((p) => p.tipo == 'abbonamento' && p.prezzoMensile > 0).toList();
    final provaSu = elenco.where((p) => p.prezzoMensile > 0).firstOrNull?.slug;
    final ritorno = widget.parametri['ritorno'];
    final dopo = ritornoInterno(ritorno) ? ritorno : null;

    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.prezzi_eyebrow, titolo: t.prezzi_titolo, intro: t.prezzi_intro, compatta: true),
        if (_esito != null)
          FasciaStretta(sottoZero: true, child: _esito!.buono ? Successo(_esito!.testo) : Errore(_esito!.testo)),
        if (negozio != null) FasciaStretta(sottoZero: true, child: EsitoAcquistoStore(negozio: negozio)),
        if (conto != null) FasciaStretta(sottoZero: true, child: _Attuale(conto: conto)),
        if (negozio != null && stripeAmmesso)
          FasciaStretta(
            sottoZero: true,
            child: _SceltaMetodo(
              store: negozio.nome,
              carta: carta,
              avviso: store?.value?.catalogo.stripe.avviso,
              alCambio: (v) => setState(() => _carta = v),
            ),
          ),
        if (!carta)
          ..._sezioniStore(
            context,
            negozio: negozio,
            dati: store,
            pacchetti: pacchetti,
            abbonamenti: abbonamenti,
            conto: conto,
          ),
        if (carta && codice != null && coupon != null)
          FasciaStretta(
            sottoZero: true,
            child: BandaCoupon(
              codice: codice,
              esito: coupon,
              valuta: elenco.firstOrNull?.valuta ?? 'EUR',
              alTogli: () => ref.read(couponAttivoProvider.notifier).imposta(null),
            ),
          ),
        if (carta) ...[
        FasciaStretta(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _GrigliaPiani(
                children: [
                  const _Gratis(),
                  for (final (i, p) in pacchetti.indexed)
                    _Offerta(
                      piano: p,
                      conto: conto,
                      codice: codice,
                      anteprima: anteprima,
                      evidente: i == pacchetti.length ~/ 2,
                      dopo: dopo,
                    ),
                ],
              ),
              Padding(
                padding: const EdgeInsets.only(top: 16),
                child: Semantics(header: true, child: Text(t.prezzi_pacchetti_testo, style: stilePiccolo())),
              ),
            ],
          ),
        ),
        if (abbonamenti.isNotEmpty)
          FasciaStretta(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TitoloSezione(t.prezzi_abbonamenti),
                IntroSezione(t.prezzi_abbonamenti_testo),
                _Abbonamenti(piani: abbonamenti, conto: conto, codice: codice, anteprima: anteprima, dopo: dopo),
              ],
            ),
          ),
        ],
        if (piani.hasError && !piani.hasValue) StatoFascia(errore: piani.error),
        if (autenticata)
          FasciaStretta(
            child: _Colonne(
              // Nello store i codici sconto non valgono: resta il codice regalo, e la nota se c'è la carta.
              sinistra: _Codici(
                provaSu: provaSu,
                soloRegalo: !carta,
                nota: !carta && stripeAmmesso ? t.app_store_codici : null,
              ),
              destra: const _Movimenti(),
            ),
          ),
        FasciaStretta(child: Avviso(t.prezzi_fiducia, sopra: 16)),
      ],
    );
  }
}

/// `.story-grid`: `.75fr 1.25fr`, una colonna sul telefono.
class _Colonne extends StatelessWidget {
  const _Colonne({required this.sinistra, required this.destra});

  final Widget sinistra;
  final Widget destra;

  @override
  Widget build(BuildContext context) {
    if (MediaQuery.sizeOf(context).width.telefono) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [sinistra, const SizedBox(height: 11.2), destra],
      );
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(flex: 75, child: sinistra),
        const SizedBox(width: 11.2),
        Expanded(flex: 125, child: destra),
      ],
    );
  }
}

/// `.pricing-grid`: tre colonne (`gap: 1rem`, righe a `.5rem`), una sul telefono; le carte di una riga alte uguali.
class _GrigliaPiani extends StatelessWidget {
  const _GrigliaPiani({required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    return Griglia(colonne: telefono ? 1 : 3, spazioColonne: 16, spazioRighe: 8, children: children);
  }
}

/// `.stat-row`: saldo, piano, letture di oggi.
class _Attuale extends ConsumerWidget {
  const _Attuale({required this.conto});

  final Conto conto;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final a = conto.abbonamento;
    final quota = conto.uso['letture_al_giorno'];
    final pagato = a != null && a.piano != 'free';
    final etichetta = Stile.sans(12.8, colore: Token.inkSoft, altezza: 1.6);
    Widget cella(List<Widget> figli) => Container(
      color: Token.paperLight,
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: figli),
    );
    final limite = quota?.limite ?? 0;
    final celle = [
      cella([
        Text(t.prezzi_saldo, style: etichetta),
        Text('${conto.saldo}', style: Stile.serif(28.8, colore: Token.ink)),
        Text(t.prezzi_crediti(conto.saldo), style: etichetta),
      ]),
      cella([
        Text(t.prezzi_piano, style: etichetta),
        Text(a?.nome ?? t.prezzi_gratuito, style: Stile.serif(20.8, colore: Token.ink)),
        if (pagato)
          Text(
            a.disdettoIl != null
                ? t.prezzi_disdetto(dataMedia(a.periodoFine, lingua))
                : t.prezzi_rinnovo(dataMedia(a.periodoFine, lingua)),
            style: etichetta,
          ),
        // Il rinnovo automatico si spegne dal profilo, con la conferma formale (Fase 2b).
        if (pagato)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Bottone(
              t.abbonamento_rinnovo_titolo,
              href: '${R.profilo}#abbonamento',
              variante: Variante.quieto,
              piccolo: true,
            ),
          ),
      ]),
      cella([
        Text(t.prezzi_oggi, style: etichetta),
        Text(limite > 0 ? '${quota!.usati} / $limite' : '—', style: Stile.serif(28.8, colore: Token.ink)),
        if (limite > 0)
          // `.stat-bar`: 6 px, la parte usata in ottone.
          Container(
            height: 6,
            margin: const EdgeInsets.only(top: 8, bottom: 4.8),
            color: const Color(0x1F3C1846),
            alignment: AlignmentDirectional.centerStart,
            child: FractionallySizedBox(
              widthFactor: math.min(1, quota!.usati / limite).toDouble(),
              child: const ColoredBox(color: Token.brass, child: SizedBox.expand()),
            ),
          ),
      ]),
    ];
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    return Griglia.righe(colonne: telefono ? 1 : 3, linea: Token.line, children: celle);
  }
}

/* ---- le carte dei piani -------------------------------------------------------------------------------------------- */

/// `.plan` (e `.plan.featured`): una colonna flessibile, quindi i margini non si fondono — si sommano.
class _Carta extends StatelessWidget {
  const _Carta({required this.children, this.evidente = false});

  final List<Widget> children;
  final bool evidente;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 27.2, vertical: 13.6),
      decoration: BoxDecoration(
        color: evidente ? Token.plum : Colori.carta,
        border: Border.all(color: evidente ? Token.plum : Token.line),
        boxShadow: evidente ? const [BoxShadow(color: Token.brassPale, offset: Offset(10, 10))] : null,
      ),
      child: DefaultTextStyle.merge(
        style: TextStyle(color: evidente ? const Color(0xFFFFF7E8) : Token.ink),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: children),
      ),
    );
  }
}

/// I testi di una carta, con i margini del browser (`p`: 1em della sua dimensione; `ul`: 1em di 16 px).
class _Testi {
  _Testi(this.evidente);

  final bool evidente;

  Color get tenue => evidente ? const Color(0xFFD9CADE) : Token.inkSoft;

  /// `.plan h2, .plan h3`.
  Widget titolo(String testo) => Semantics(
    header: true,
    child: TestoBilanciato(testo, stile: Stile.serif(23.2, colore: evidente ? const Color(0xFFFFF7E8) : Token.ink)),
  );

  /// `.plan .price` (margine `.5rem 0`) con il `small`.
  Widget prezzo(List<InlineSpan> parti) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Text.rich(
      TextSpan(children: parti),
      style: Stile.serif(38.4, colore: evidente ? const Color(0xFFFFF7E8) : Token.ink),
    ),
  );

  /// Il `small` del prezzo.
  InlineSpan piccolo(String testo) => TextSpan(
    text: ' $testo',
    style: Stile.sans(14.4, colore: tenue),
  );

  /// `.prezzo-barrato`.
  InlineSpan barrato(String testo) => TextSpan(
    text: testo,
    style: Stile.serif(
      18.4,
      colore: Token.inkSoft,
    ).copyWith(decoration: TextDecoration.lineThrough, decorationThickness: 2, decorationColor: Token.inkSoft),
  );

  /// `.plan p` (`.88rem`, margine 1em).
  Widget paragrafo(String testo, {double sopra = 14.08, double sotto = 14.08}) => Padding(
    padding: EdgeInsets.only(top: sopra, bottom: sotto),
    child: Paragrafo(testo, style: Stile.sans(14.08, colore: tenue, altezza: 1.6)),
  );

  /// `.plan ul` (`padding-left: 1rem`, margine 1em di 16 px) con le voci `.88rem`.
  Widget elenco(List<String> voci) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 16),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final v in voci)
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 16,
                child: Text('•', style: Stile.sans(14.08, colore: tenue, altezza: 1.6)),
              ),
              Expanded(
                child: Text(v, style: Stile.sans(14.08, colore: tenue, altezza: 1.6)),
              ),
            ],
          ),
      ],
    ),
  );
}

/// La lettura gratuita, in testa ai pacchetti.
class _Gratis extends ConsumerWidget {
  const _Gratis();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final n = ref.watch(impostazioniProvider).value?.creditiIscrizione ?? 3;
    final x = _Testi(false);
    return _Carta(
      children: [
        x.titolo(t.prezzi_gratis_titolo),
        x.prezzo([TextSpan(text: t.prezzi_gratis_prezzo)]),
        x.paragrafo(t.prezzi_gratis_testo),
        x.elenco(t.prezziGratisVoci(n: n)),
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Bottone(
            t.prezzi_gratis_cta,
            href: '${R.leggi}?source=pricing',
            variante: Variante.quieto,
            pieno: true,
          ),
        ),
      ],
    );
  }
}

/// Le azioni della pagina: comprare, abbonarsi, gestire gli errori.
mixin _Acquisto<T extends ConsumerStatefulWidget> on ConsumerState<T> {
  bool inCorso = false;
  String? errore;

  /// L'indirizzo di ritorno e la pagina dove l'app torna se il deep link non arriva.
  ({String ritorno, String Function(String id) inSospeso}) ritorni(String? dopo) {
    final coda = dopo == null ? '' : '?dopo=${Uri.encodeComponent(dopo)}';
    return (
      ritorno: ritornoApp('${R.prezzi}$coda'),
      inSospeso: (id) =>
          '${R.prezzi}?checkout=${Uri.encodeComponent(id)}${dopo == null ? '' : '&dopo=${Uri.encodeComponent(dopo)}'}',
    );
  }

  /// Un'azione con l'esito: `null` se non è riuscita (l'errore si mostra).
  Future<X?> esegui<X>(Future<X> Function() azione) async {
    setState(() {
      inCorso = true;
      errore = null;
    });
    try {
      return await azione();
    } on ErroreApi catch (e) {
      if (mounted) setState(() => errore = e.messaggio(context.t));
      rethrow;
    } finally {
      if (mounted) setState(() => inCorso = false);
    }
  }

  /// Apre la pagina di pagamento nel browser e ricorda dove tornare.
  Future<void> apriCheckout(Checkout c, String? dopo) async {
    if (c.url.isEmpty) {
      ricaricaConto(ref);
      return;
    }
    await ref.read(pagamentoInSospesoProvider.notifier).apri(c.url, ritorno: ritorni(dopo).inSospeso(c.checkoutId));
  }
}

/// Un pacchetto (o un abbonamento elencato fra i pacchetti).
class _Offerta extends ConsumerStatefulWidget {
  const _Offerta({
    required this.piano,
    required this.conto,
    required this.codice,
    required this.anteprima,
    required this.evidente,
    required this.dopo,
  });

  final Piano piano;
  final Conto? conto;
  final String? codice;
  final AnteprimaCouponPubblica? anteprima;
  final bool evidente;
  final String? dopo;

  @override
  ConsumerState<_Offerta> createState() => _OffertaState();
}

class _OffertaState extends ConsumerState<_Offerta> with _Acquisto<_Offerta> {
  Future<void> _compra(VoceCoupon? voce) async {
    final p = widget.piano;
    final pacchetto = p.pacchetto;
    ref.read(lanternaProvider).traccia(pacchetto ? 'package_selected' : 'subscription_started', {'piano': p.slug});
    if (!ref.read(sessioneProvider).autenticata) {
      await entraDa(ref);
      return;
    }
    try {
      if (p.prezzoMensile == 0) {
        await esegui(() => ref.read(apiProvider).abbonaGratis(p.slug));
        ricaricaConto(ref);
        return;
      }
      final scontato = (voce?.applicato ?? false) && voce?.importo != null;
      final c = await esegui(
        () => ref
            .read(apiProvider)
            .apriPagamento(p.slug, ritorno: ritorni(widget.dopo).ritorno, coupon: scontato ? widget.codice : null),
      );
      if (c != null) await apriCheckout(c, widget.dopo);
    } on ErroreApi {
      // il messaggio è già nella carta
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final p = widget.piano;
    final x = _Testi(widget.evidente);
    final attuale = widget.conto?.abbonamento?.piano == p.slug;
    final pacchetto = p.pacchetto;
    final gratuito = p.prezzoMensile == 0;
    // Fase 2d: il prezzo col codice viene dall'anteprima di tutte le offerte (`/coupon/anteprima`).
    final voce = widget.codice != null && !gratuito
        ? widget.anteprima?.voce(p.slug, annuale: false, rinnovo: false)
        : null;
    final scontato = (voce?.applicato ?? false) && voce?.importo != null ? voce!.importo! : null;
    String soldi(int c) => euro(c, lingua, valuta: p.valuta);
    final perLettura = soldi((p.prezzoMensile / math.max(1, p.creditiPerPeriodo)).round());
    return _Carta(
      evidente: widget.evidente,
      children: [
        x.titolo(p.nome),
        x.prezzo([
          if (gratuito)
            TextSpan(text: t.prezzi_gratuito)
          else if (scontato != null) ...[
            x.barrato(soldi(p.prezzoMensile)),
            TextSpan(text: ' ${scontato == 0 ? t.prezzi_gratuito : soldi(scontato)}'),
          ] else
            TextSpan(text: soldi(p.prezzoMensile)),
          if (!pacchetto && !gratuito) x.piccolo(t.prezzi_al_mese),
        ]),
        if (scontato == 0) x.paragrafo(t.prezzi_gratis_codice),
        RigheCoupon(voce: voce, valuta: p.valuta, scuro: widget.evidente),
        if (p.descrizione != null) x.paragrafo(p.descrizione!),
        x.elenco([
          if (pacchetto)
            t.prezzi_per_lettura(p.creditiPerPeriodo, perLettura)
          else if ((p.limiti['letture_al_giorno'] ?? 0) > 0)
            t.prezzi_al_giorno(p.limiti['letture_al_giorno']!)
          else
            t.prezzi_giorno_gratis,
        ]),
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Bottone(
            attuale && !pacchetto
                ? t.prezzi_il_tuo
                : pacchetto
                ? t.prezzi_acquista
                : gratuito
                ? t.prezzi_scegli
                : t.prezzi_abbonati,
            variante: widget.evidente ? Variante.ottone : Variante.quieto,
            pieno: true,
            an: 'piano_scelto',
            anProprieta: {'piano': p.slug},
            alTocco: inCorso || (attuale && !pacchetto) ? null : () => unawaited(_compra(voce)),
          ),
        ),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

/* ---- gli abbonamenti (Fase 2b) ---------------------------------------------------------------------------------- */

/// Mensile o annuale, col rinnovo automatico (acceso per default, −20%) o senza (listino, un periodo). Il prezzo grande
/// è quello che si paga davvero; il listino barrato e lo sconto si vedono accanto.
class _Abbonamenti extends ConsumerStatefulWidget {
  const _Abbonamenti({
    required this.piani,
    required this.conto,
    required this.codice,
    required this.anteprima,
    required this.dopo,
  });

  final List<Piano> piani;
  final Conto? conto;
  final String? codice;
  final AnteprimaCouponPubblica? anteprima;
  final String? dopo;

  @override
  ConsumerState<_Abbonamenti> createState() => _AbbonamentiState();
}

class _AbbonamentiState extends ConsumerState<_Abbonamenti> with _Acquisto<_Abbonamenti> {
  bool _annuale = false;
  bool _rinnovo = true;
  String? _motivo;

  Future<void> _abbonati(Piano piano, num sconto, AbbonamentoBreve? attuale) async {
    ref.read(lanternaProvider).traccia('subscription_started', {
      'piano': piano.slug,
      'annuale': _annuale,
      'rinnovo': _rinnovo,
    });
    if (!ref.read(sessioneProvider).autenticata) {
      await entraDa(ref);
      return;
    }
    if (attuale != null) {
      await apriCambioPiano(
        context,
        piano: piano,
        annuale: _annuale,
        scontoRinnovo: sconto,
        alFatto: () => ricaricaConto(ref),
      );
      return;
    }
    setState(() => _motivo = null);
    try {
      final c = await esegui(
        () => ref
            .read(apiProvider)
            .apriPagamento(
              piano.slug,
              annuale: _annuale,
              rinnovo: _rinnovo,
              ritorno: ritorni(widget.dopo).ritorno,
              coupon: widget.codice,
            ),
      );
      if (c != null) await apriCheckout(c, widget.dopo);
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _motivo = e.codice);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final impostazioni = ref.watch(impostazioniAbbonamentiProvider).value;
    final autenticata = ref.watch(sessioneProvider.select((s) => s.autenticata));
    final sconto = impostazioni?.scontoRinnovo ?? 20;
    final a = widget.conto?.abbonamento;
    final attuale = a != null && a.piano != 'free' ? a : null;
    final provaPossibile =
        (impostazioni?.provaDisponibile ?? false) && (!autenticata || (widget.conto?.prova?.idonea ?? false));
    final conAnnuale = widget.piani.any((p) => p.prezzoAnnuale > 0);
    final telefono = MediaQuery.sizeOf(context).width.telefono;

    final carte = <Widget>[];
    for (final p in widget.piani) {
      final voce = _annuale ? p.prezzi?.annuale : p.prezzi?.mensile;
      final listino = _annuale ? p.prezzoAnnuale : p.prezzoMensile;
      if (_annuale && listino <= 0) continue;
      final conSconto = voce?.conRinnovo ?? listino;
      // Fase 2d: col codice il prezzo è quello dell'anteprima. Non per chi è già abbonato: il cambio ha il conguaglio.
      final conCodice = widget.codice != null && attuale == null
          ? widget.anteprima?.voce(p.slug, annuale: _annuale, rinnovo: _rinnovo)
          : null;
      final mostrato = (conCodice?.applicato ?? false) && conCodice?.importo != null
          ? conCodice!.importo!
          : (_rinnovo || attuale != null ? conSconto : listino);
      final suo = attuale?.piano == p.slug && (attuale?.annuale ?? false) == _annuale;
      // Quando vince lo sconto del codice, il bollino del rinnovo (−20%) non vale su questo prezzo: al suo posto
      // quello del codice (ritocco della Fase 2d del sito).
      final vinceCodice = (conCodice?.applicato ?? false) && conCodice?.vince == 'coupon' && widget.anteprima != null;
      final periodo = _annuale ? t.abbonamento_al_anno : t.prezzi_al_mese;
      String soldi(int c) => euro(c, lingua, valuta: p.valuta);
      final x = _Testi(false);
      carte.add(
        _Carta(
          children: [
            if (vinceCodice || (_rinnovo && conSconto < listino))
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 8.8, vertical: 3.52),
                  color: Token.brassPale,
                  child: Text(
                    (vinceCodice
                            ? t.prezzi_coupon_badge(etichettaSconto(widget.anteprima!.coupon, p.valuta, lingua))
                            : t.abbonamento_badge_rinnovo(sconto))
                        .toUpperCase(),
                    style: Stile.sans(11.2, peso: FontWeight.w700, em: .07, colore: Colori.testoOttone, altezza: 1.6),
                  ),
                ),
              ),
            x.titolo(p.nome),
            x.prezzo([
              if (mostrato < listino) ...[x.barrato(soldi(listino)), const TextSpan(text: ' ')],
              TextSpan(text: soldi(mostrato)),
              x.piccolo(periodo),
            ]),
            RigheCoupon(voce: conCodice, valuta: p.valuta, perPeriodo: ' $periodo'),
            x.paragrafo(
              _rinnovo ? t.abbonamento_con_rinnovo : t.abbonamento_senza_rinnovo(soldi(listino)),
              sopra: 13.44,
              sotto: 13.44,
            ),
            if (p.descrizione != null) x.paragrafo(p.descrizione!),
            x.elenco([
              if ((p.limiti['letture_al_giorno'] ?? 0) > 0)
                t.prezzi_al_giorno(p.limiti['letture_al_giorno']!)
              else
                t.prezzi_giorno_gratis,
            ]),
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Bottone(
                suo
                    ? t.prezzi_il_tuo
                    : attuale != null
                    ? t.abbonamento_passa
                    : t.prezzi_abbonati,
                variante: Variante.ottone,
                pieno: true,
                an: 'piano_scelto',
                anProprieta: {'piano': p.slug},
                alTocco: inCorso || suo ? null : () => unawaited(_abbonati(p, sconto, attuale)),
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (provaPossibile && impostazioni != null)
          _BandaProva(giorni: impostazioni.giorniProva, sconto: impostazioni.scontoProva),
        // `.abbonamenti-comandi`: il periodo e il rinnovo automatico, in fila (a capo quando non c'è posto).
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Wrap(
            spacing: 22.4,
            runSpacing: 9.6,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              if (conAnnuale)
                Semantics(
                  label: t.abbonamento_scegli_periodo,
                  child: Pillole(
                    children: [
                      Pillola(
                        t.abbonamento_periodo_mensile,
                        acceso: !_annuale,
                        alTocco: () => setState(() => _annuale = false),
                      ),
                      Pillola(
                        t.abbonamento_periodo_annuale,
                        acceso: _annuale,
                        alTocco: () => setState(() => _annuale = true),
                      ),
                    ],
                  ),
                ),
              if (attuale == null)
                _LevettaRinnovo(
                  valore: _rinnovo,
                  titolo: t.abbonamento_rinnovo_prezzi,
                  testo: t.abbonamento_rinnovo_prezzi_testo(sconto),
                  alCambio: (v) => setState(() => _rinnovo = v),
                ),
            ],
          ),
        ),
        Griglia(colonne: telefono ? 1 : 3, spazioColonne: 16, spazioRighe: 8, children: carte),
        if (_motivo == 'fattura_aperta')
          Avviso(
            null,
            figlio: Wrap(
              crossAxisAlignment: WrapCrossAlignment.end,
              children: [
                Text('${t.abbonamento_sospeso_testo} ', style: Stile.sans(14.4, colore: Token.inkSoft, altezza: 1.6)),
                Collegamento(
                  t.abbonamento_sistema,
                  href: '${R.profilo}#abbonamento',
                  stile: Stile.sans(14.4, altezza: 1.6),
                ),
              ],
            ),
          ),
        if (errore != null && _motivo != 'fattura_aperta') Errore(errore!),
      ],
    );
  }
}

/// `.prova-banda`: «Non sei sicuro? Provalo gratis…», col bottone verso la prova.
class _BandaProva extends StatelessWidget {
  const _BandaProva({required this.giorni, required this.sconto});

  final int giorni;
  final num sconto;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(t.abbonamento_prova_banda_titolo(giorni), style: Stile.serif(17.6, altezza: 1.35, colore: Token.ink)),
        Text(t.abbonamento_prova_banda_testo(sconto), style: Stile.sans(13.44, colore: Token.ink, altezza: 1.6)),
      ],
    );
    final bottone = Bottone(
      t.abbonamento_prova_banda_cta,
      href: R.prova,
      variante: Variante.ottone,
      piccolo: true,
      an: 'prezzi_prova',
    );
    return Container(
      margin: const EdgeInsets.only(bottom: 19.2),
      padding: const EdgeInsets.symmetric(horizontal: 19.2, vertical: 16),
      decoration: const BoxDecoration(
        color: Color(0xFFFBF2DC),
        border: Border(
          top: BorderSide(color: Color(0x80B28336)),
          right: BorderSide(color: Color(0x80B28336)),
          bottom: BorderSide(color: Color(0x80B28336)),
          left: BorderSide(color: Token.brass, width: 4),
        ),
      ),
      child: LayoutBuilder(
        builder: (context, v) => v.maxWidth < 560
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [testo, const SizedBox(height: 9.6), bottone],
              )
            : Row(
                children: [
                  Expanded(child: testo),
                  const SizedBox(width: 19.2),
                  bottone,
                ],
              ),
      ),
    );
  }
}

/// `.abbonamenti-comandi .interruttore`: la levetta col titolo in grassetto e la spiegazione piccola sotto
/// (`max-width: 52ch`).
class _LevettaRinnovo extends StatelessWidget {
  const _LevettaRinnovo({required this.valore, required this.titolo, required this.testo, required this.alCambio});

  final bool valore;
  final String titolo;
  final String testo;
  final ValueChanged<bool> alCambio;

  @override
  Widget build(BuildContext context) {
    final durata = MediaQuery.disableAnimationsOf(context) ? Duration.zero : Token.durataTransizione;
    final stileTesto = Stile.sans(12.8, colore: Token.inkSoft, altezza: 1.4);
    return Semantics(
      toggled: valore,
      label: '$titolo. $testo',
      excludeSemantics: true,
      onTap: () => alCambio(!valore),
      child: Premibile(
        alTocco: () => alCambio(!valore),
        pulsante: false,
        costruisci: (context, premuto) => ConstrainedBox(
          constraints: BoxConstraints(
            minHeight: 44,
            maxWidth: larghezzaCh(stileTesto, MediaQuery.textScalerOf(context)) * 52 + 57.2,
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.8),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedContainer(
                  duration: durata,
                  width: 46,
                  height: 26,
                  decoration: BoxDecoration(
                    color: valore ? Token.verdigris : const Color(0xFFE3DACE),
                    border: Border.all(color: valore ? Token.verdigris : Token.inkSoft),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: AnimatedAlign(
                    duration: durata,
                    alignment: valore ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.all(2),
                      width: 20,
                      height: 20,
                      decoration: const BoxDecoration(
                        color: Color(0xFFFFFFFF),
                        shape: BoxShape.circle,
                        boxShadow: [BoxShadow(color: Color(0x59201026), offset: Offset(0, 1), blurRadius: 3)],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 11.2),
                Flexible(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        titolo,
                        style: Stile.sans(16, peso: FontWeight.w700, colore: Token.ink, altezza: 1.6),
                      ),
                      const SizedBox(height: 1.6),
                      Text(testo, style: stileTesto),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/* ---- codici e movimenti ------------------------------------------------------------------------------------------- */

/// «Hai un codice?»: il codice sconto (si applica alle offerte sopra) e il codice regalo (crediti subito).
class _Codici extends ConsumerStatefulWidget {
  const _Codici({required this.provaSu, this.soloRegalo = false, this.nota});

  /// Un piano a pagamento su cui provare il codice (senza, il comando resta spento).
  final String? provaSu;

  /// Fase 9: nello store i codici sconto non valgono; resta solo il codice regalo.
  final bool soloRegalo;

  /// Una nota in testa (dove valgono i codici sconto).
  final String? nota;

  @override
  ConsumerState<_Codici> createState() => _CodiciState();
}

class _CodiciState extends ConsumerState<_Codici> {
  final TextEditingController _sconto = TextEditingController();
  final TextEditingController _regalo = TextEditingController();
  String? _erroreSconto;
  ({bool buono, String testo})? _esitoRegalo;
  bool _inCorso = false;

  @override
  void initState() {
    super.initState();
    _sconto.addListener(() => setState(() {}));
    _regalo.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _sconto.dispose();
    _regalo.dispose();
    super.dispose();
  }

  Future<void> _applica() async {
    final c = normalizzaCodice(_sconto.text);
    if (c.isEmpty || widget.provaSu == null) return;
    final t = context.t;
    setState(() {
      _erroreSconto = null;
      _inCorso = true;
    });
    // Le regole del codice (e della persona) sull'anteprima di tutte le offerte; quelle della singola offerta si
    // vedono poi offerta per offerta.
    try {
      await ref.read(apiProvider).anteprimaCoupon(c);
      ref.read(couponAttivoProvider.notifier).imposta(c);
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _erroreSconto = messaggioCodice(t, motivoCodice(e)));
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  Future<void> _riscatta() async {
    final c = normalizzaCodice(_regalo.text);
    if (c.isEmpty) return;
    final t = context.t;
    setState(() {
      _esitoRegalo = null;
      _inCorso = true;
    });
    try {
      final r = await ref.read(apiProvider).riscattaCodice(c);
      if (!mounted) return;
      setState(() => _esitoRegalo = (buono: true, testo: t.prezzi_riscattato(r.crediti)));
      _regalo.clear();
      ricaricaConto(ref);
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _esitoRegalo = (buono: false, testo: messaggioCodice(t, motivoCodice(e))));
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final applicato = ref.watch(couponAttivoProvider);
    return Pannello(
      titolo: t.prezzi_codici,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (widget.nota != null) Padding(
            padding: const EdgeInsets.only(bottom: 9.6),
            child: Text(widget.nota!, style: stilePiccolo()),
          ),
          if (widget.soloRegalo)
            const SizedBox.shrink()
          else if (applicato != null)
            _successoCon(
              Wrap(
                crossAxisAlignment: WrapCrossAlignment.center,
                spacing: 4,
                children: [
                  Text(t.prezzi_applicato(applicato)),
                  Bottone(
                    t.prezzi_togli,
                    variante: Variante.quieto,
                    piccolo: true,
                    alTocco: () {
                      ref.read(couponAttivoProvider.notifier).imposta(null);
                      _sconto.clear();
                    },
                  ),
                ],
              ),
            )
          else ...[
            CampoTesto(
              etichetta: t.prezzi_codice_sconto,
              nota: t.prezzi_codice_sconto_aiuto,
              controllore: _sconto,
              maiuscole: true,
              lunghezzaMassima: 60,
              azione: TextInputAction.done,
              alInvio: (_) => unawaited(_applica()),
            ),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Bottone(
                t.prezzi_applica,
                variante: Variante.quieto,
                piccolo: true,
                alTocco: _inCorso || _sconto.text.trim().isEmpty || widget.provaSu == null
                    ? null
                    : () => unawaited(_applica()),
              ),
            ),
            if (_erroreSconto != null) Errore(_erroreSconto!),
          ],
          if (!widget.soloRegalo) const SizedBox(height: 8),
          CampoTesto(
            etichetta: t.prezzi_codice_regalo,
            nota: t.prezzi_codice_regalo_aiuto,
            controllore: _regalo,
            maiuscole: true,
            lunghezzaMassima: 60,
            azione: TextInputAction.done,
            alInvio: (_) => unawaited(_riscatta()),
          ),
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: Bottone(
              t.prezzi_riscatta,
              variante: Variante.quieto,
              piccolo: true,
              alTocco: _inCorso || _regalo.text.trim().isEmpty ? null : () => unawaited(_riscatta()),
            ),
          ),
          if (_esitoRegalo != null) _esitoRegalo!.buono ? Successo(_esitoRegalo!.testo) : Errore(_esitoRegalo!.testo),
        ],
      ),
    );
  }
}

/// Un `.success` con un contenuto qualunque (il testo e il bottone «togli», come nel sito).
Widget _successoCon(Widget figlio) => Semantics(
  liveRegion: true,
  child: Container(
    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
    decoration: const BoxDecoration(
      color: Color(0xFFE7F2EE),
      border: Border(left: BorderSide(color: Token.verdigris, width: 3)),
    ),
    child: DefaultTextStyle.merge(
      style: Stile.sans(14.4, colore: const Color(0xFF0F4D4C), altezza: 1.6),
      child: figlio,
    ),
  ),
);

/// «Movimenti recenti»: ogni movimento col motivo, la data e il segno.
class _Movimenti extends ConsumerWidget {
  const _Movimenti();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final dati = ref.watch(movimentiProvider).value;
    final locale = localeIntl(lingua);
    String quando(String iso) {
      final d = DateTime.tryParse(iso)?.toLocal();
      return d == null ? iso : '${DateFormat.yMd(locale).format(d)}, ${DateFormat.Hms(locale).format(d)}';
    }

    return Pannello(
      titolo: t.prezzi_movimenti,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (dati != null && dati.movimenti.isEmpty) Text(t.prezzi_nessun_movimento, style: stilePiccolo()),
          for (final m in dati?.movimenti ?? const <Movimento>[])
            Container(
              padding: const EdgeInsets.symmetric(vertical: 8),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Token.line)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text.rich(
                      TextSpan(
                        children: [
                          TextSpan(text: t.prezziMotivi[m.reason] ?? m.reason),
                          const TextSpan(text: '\n'),
                          TextSpan(
                            text: '${quando(m.quando)}${m.note != null ? ' · ${m.note}' : ''}',
                            style: Stile.sans(13.28, colore: Token.inkSoft, altezza: 1.6),
                          ),
                        ],
                      ),
                      style: Stile.sans(16, colore: Token.ink, altezza: 1.6),
                    ),
                  ),
                  const SizedBox(width: 9.6),
                  Text(
                    '${m.delta > 0 ? '+' : ''}${m.delta}',
                    style: Stile.sans(
                      16,
                      peso: FontWeight.w700,
                      colore: m.delta >= 0 ? Token.verdigris : Token.danger,
                      altezza: 1.6,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

/* ---- gli store (Fase 9) ------------------------------------------------------------------------------------------ */

/// Come pagare, dove la politica della console ammette la carta: lo store o la carta (Stripe, nel browser).
class _SceltaMetodo extends StatelessWidget {
  const _SceltaMetodo({required this.store, required this.carta, required this.avviso, required this.alCambio});

  final String store;
  final bool carta;

  /// Il testo della console per questo paese, se c'è.
  final String? avviso;
  final ValueChanged<bool> alCambio;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Semantics(
          label: t.app_store_metodo,
          child: Pillole(
            children: [
              Pillola(store, acceso: !carta, an: 'metodo_store', alTocco: () => alCambio(false)),
              Pillola(t.app_store_carta, acceso: carta, an: 'metodo_carta', alTocco: () => alCambio(true)),
            ],
          ),
        ),
        if (carta)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              avviso != null && avviso!.trim().isNotEmpty ? avviso! : t.app_store_carta_testo,
              style: stilePiccolo(),
            ),
          ),
      ],
    );
  }
}

/// Le fasce della pagina quando si compra nello store: i pacchetti, gli abbonamenti, la nota con il ripristino.
List<Widget> _sezioniStore(
  BuildContext context, {
  required Negozio? negozio,
  required AsyncValue<({CatalogoStore catalogo, List<OffertaStore> offerte, bool disponibile})?>? dati,
  required List<Piano> pacchetti,
  required List<Piano> abbonamenti,
  required Conto? conto,
}) {
  final t = context.t;
  if (negozio == null) return const [];
  final v = dati?.value;
  if (v == null) {
    if (dati?.hasError ?? false) return [StatoFascia(errore: dati!.error)];
    return [
      const FasciaStretta(child: _GrigliaPiani(children: [_Gratis()])),
    ];
  }
  final perPiano = {
    for (final o in v.offerte)
      if (o.consumabile) o.piano: o,
  };
  final inVendita = [
    for (final p in pacchetti)
      if (perPiano[p.slug] case final o?) (p, o),
  ];
  final daAbbonamento = v.offerte.where((o) => !o.consumabile && !o.prodotto.prova).toList();
  return [
    FasciaStretta(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (!v.disponibile || v.offerte.isEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Avviso(t.app_store_non_disponibile(negozio.nome), sopra: 0),
            ),
          _GrigliaPiani(
            children: [
              const _Gratis(),
              for (final (i, (p, o)) in inVendita.indexed)
                _PacchettoStore(piano: p, offerta: o, evidente: i == inVendita.length ~/ 2),
            ],
          ),
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Semantics(header: true, child: Text(t.prezzi_pacchetti_testo, style: stilePiccolo())),
          ),
        ],
      ),
    ),
    if (daAbbonamento.isNotEmpty)
      FasciaStretta(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TitoloSezione(t.prezzi_abbonamenti),
            IntroSezione(t.prezzi_abbonamenti_testo),
            _AbbonamentiStore(piani: abbonamenti, offerte: daAbbonamento, conto: conto, negozio: negozio),
          ],
        ),
      ),
    FasciaStretta(child: NotaStore(negozio: negozio)),
  ];
}

/// Compra nello store, dopo l'accesso se manca.
Future<void> _compraNelloStore(WidgetRef ref, OffertaStore offerta) async {
  if (!ref.read(sessioneProvider).autenticata && !await entraDa(ref)) return;
  await ref.read(acquistiProvider.notifier).compra(offerta);
}

/// Un pacchetto di crediti nello store, col prezzo dello store.
class _PacchettoStore extends ConsumerWidget {
  const _PacchettoStore({required this.piano, required this.offerta, required this.evidente});

  final Piano piano;
  final OffertaStore offerta;
  final bool evidente;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final inCorso = ref.watch(acquistiProvider.select((s) => s.inCorso));
    final x = _Testi(evidente);
    final d = offerta.dettagli;
    final crediti = math.max(1, piano.creditiPerPeriodo);
    // Il prezzo di una lettura nella valuta dello store (il prezzo grande è già quello dello store, localizzato).
    final perLettura = NumberFormat.currency(
      locale: localeIntl(lingua),
      name: d.currencyCode,
      symbol: d.currencySymbol,
    ).format(d.rawPrice / crediti);
    return _Carta(
      evidente: evidente,
      children: [
        x.titolo(piano.nome),
        x.prezzo([TextSpan(text: offerta.prezzo)]),
        if (piano.descrizione != null) x.paragrafo(piano.descrizione!),
        x.elenco([t.prezzi_per_lettura(piano.creditiPerPeriodo, perLettura)]),
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Bottone(
            t.prezzi_acquista,
            variante: evidente ? Variante.ottone : Variante.quieto,
            pieno: true,
            an: 'piano_scelto',
            anProprieta: {'piano': piano.slug, 'canale': 'store'},
            alTocco: inCorso
                ? null
                : () {
                    ref.read(lanternaProvider).traccia('package_selected', {'piano': piano.slug});
                    unawaited(_compraNelloStore(ref, offerta));
                  },
          ),
        ),
      ],
    );
  }
}

/// Gli abbonamenti nello store: mensile o annuale, col prezzo dello store. Il rinnovo automatico è sempre acceso (si
/// disdice nello store); chi ha già un abbonamento dello stesso store passa all'altro (Google col conguaglio, Apple
/// nello stesso gruppo), chi l'ha altrove lo legge.
class _AbbonamentiStore extends ConsumerStatefulWidget {
  const _AbbonamentiStore({required this.piani, required this.offerte, required this.conto, required this.negozio});

  final List<Piano> piani;
  final List<OffertaStore> offerte;
  final Conto? conto;
  final Negozio negozio;

  @override
  ConsumerState<_AbbonamentiStore> createState() => _AbbonamentiStoreState();
}

class _AbbonamentiStoreState extends ConsumerState<_AbbonamentiStore> {
  bool _annuale = false;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final impostazioni = ref.watch(impostazioniAbbonamentiProvider).value;
    final autenticata = ref.watch(sessioneProvider.select((s) => s.autenticata));
    final inCorso = ref.watch(acquistiProvider.select((s) => s.inCorso));
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final a = widget.conto?.abbonamento;
    final attuale = a != null && a.piano != 'free' ? a : null;
    final questoStore = widget.negozio.piattaforma == 'ios' ? 'app_store' : 'google_play';
    // Un abbonamento che questo store non può cambiare: pagato con carta, o nell'altro store.
    final altrove = attuale != null && attuale.provider != questoStore;
    final provaPossibile =
        (impostazioni?.provaDisponibile ?? false) && (!autenticata || (widget.conto?.prova?.idonea ?? false));
    final conAnnuale = widget.offerte.any((o) => o.prodotto.annuale);
    final annuale = _annuale && conAnnuale;

    final carte = <Widget>[];
    for (final p in widget.piani) {
      final o = widget.offerte.where((o) => o.piano == p.slug && o.prodotto.annuale == annuale).firstOrNull;
      if (o == null) continue;
      final suo = attuale?.piano == p.slug && (attuale?.annuale ?? false) == annuale && !altrove;
      final x = _Testi(false);
      carte.add(
        _Carta(
          children: [
            x.titolo(p.nome),
            x.prezzo([TextSpan(text: o.prezzo), x.piccolo(annuale ? t.abbonamento_al_anno : t.prezzi_al_mese)]),
            if (p.descrizione != null) x.paragrafo(p.descrizione!),
            x.elenco([
              if ((p.limiti['letture_al_giorno'] ?? 0) > 0)
                t.prezzi_al_giorno(p.limiti['letture_al_giorno']!)
              else
                t.prezzi_giorno_gratis,
            ]),
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Bottone(
                suo
                    ? t.prezzi_il_tuo
                    : attuale != null
                    ? t.abbonamento_passa
                    : t.prezzi_abbonati,
                variante: Variante.ottone,
                pieno: true,
                an: 'piano_scelto',
                anProprieta: {'piano': p.slug, 'canale': 'store'},
                alTocco: inCorso || suo || altrove
                    ? null
                    : () {
                        ref.read(lanternaProvider).traccia('subscription_started', {
                          'piano': p.slug,
                          'annuale': annuale,
                          'canale': 'store',
                        });
                        unawaited(_compraNelloStore(ref, o));
                      },
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (provaPossibile && impostazioni != null)
          _BandaProva(giorni: impostazioni.giorniProva, sconto: impostazioni.scontoProva),
        if (conAnnuale)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: Semantics(
                label: t.abbonamento_scegli_periodo,
                child: Pillole(
                  children: [
                    Pillola(
                      t.abbonamento_periodo_mensile,
                      acceso: !annuale,
                      alTocco: () => setState(() => _annuale = false),
                    ),
                    Pillola(
                      t.abbonamento_periodo_annuale,
                      acceso: annuale,
                      alTocco: () => setState(() => _annuale = true),
                    ),
                  ],
                ),
              ),
            ),
          ),
        Griglia(colonne: telefono ? 1 : 3, spazioColonne: 16, spazioRighe: 8, children: carte),
        if (altrove)
          Avviso(
            attuale.store
                ? t.app_store_altro_store(
                    attuale.provider == 'app_store' ? t.abbonamento_store_app_store : t.abbonamento_store_google_play,
                  )
                : t.app_store_abbonamento_web(widget.negozio.nome),
          ),
      ],
    );
  }
}
