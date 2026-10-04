/// La prova gratuita (`frontend/v2/pagine/prova.tsx`, `app/(v2)/trial/page.tsx`, Fase 2b): tutto quello che serve
/// sapere prima di cominciare, detto in chiaro — quando si paga (alla fine, non prima), quanto (l'annuale del livello
/// scelto col −50% per sempre), come si disdice (dal profilo; durante la prova non si paga nulla), il promemoria due
/// giorni prima. Il «−50% per sempre» è il vantaggio grande, e lo si dice grande.
///
/// Si sceglie il livello e si comincia. **Fase 9**: nell'app la prova è il prodotto «prova» dello store (l'annuale a
/// metà prezzo con 14 giorni gratis; chi ne ha diritto lo decide lo store) e si compra lì; la carta (Stripe, nel
/// browser di sistema, col ritorno `?checkout=`) solo dove il catalogo dello store la ammette e lo store non ha il
/// prodotto. Chi non ha un account entra (con
/// Google o Apple l'account nasce da sé) e resta qui; chi ha già usato la prova lo legge subito, col collegamento ai
/// prezzi. Il codice sconto della sessione (`?coupon=` sui prezzi, Fase 2d) vale anche sulla prova.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../acquisti/acquisti.dart';
import '../acquisti/negozio.dart';
import '../acquisti/vista.dart';
import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../cassa/coupon.dart';
import '../cassa/pagamento.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'prezzi.dart' show FasciaStretta;

/// La pagina della prova.
class PaginaProva extends ConsumerStatefulWidget {
  /// La prova, coi parametri dell'indirizzo (`checkout` al ritorno dal pagamento).
  const PaginaProva({super.key, required this.parametri});

  /// I parametri della query.
  final Map<String, String> parametri;

  @override
  ConsumerState<PaginaProva> createState() => _PaginaProvaState();
}

class _PaginaProvaState extends ConsumerState<PaginaProva> {
  String? _scelto;
  bool _inCorso = false;
  String? _errore;
  ({bool buono, String testo})? _esito;

  @override
  void initState() {
    super.initState();
    final checkout = widget.parametri['checkout'];
    if (checkout != null && checkout.isNotEmpty) {
      Future.microtask(() {
        ref.read(pagamentoInSospesoProvider.notifier).concluso();
        unawaited(_verifica(checkout));
      });
    }
  }

  Future<void> _verifica(String checkout) async {
    if (!ref.read(sessioneProvider).autenticata) return;
    final t = context.t;
    try {
      final s = await ref.read(apiProvider).statoPagamento(checkout);
      if (!mounted) return;
      setState(() {
        if (s.esito != null) {
          _esito = (buono: false, testo: t.abbonamento_prova_rifiutata);
        } else if (s.stato == 'pagato') {
          _esito = (buono: true, testo: t.abbonamento_prova_attivata);
        } else {
          _esito = (buono: false, testo: t.prezzi_non_completato);
        }
      });
      if (s.stato == 'pagato') {
        ref.invalidate(contoProvider);
        ref.invalidate(saldoProvider);
      }
    } on ErroreApi {
      if (mounted) setState(() => _esito = (buono: false, testo: t.prezzi_non_verificato));
    }
  }

  Future<void> _inizia(Piano piano, String? codice) async {
    ref.read(lanternaProvider).traccia('trial_started', {'piano': piano.slug});
    setState(() {
      _inCorso = true;
      _errore = null;
    });
    try {
      final c = await ref.read(apiProvider).iniziaProva(piano.slug, ritorno: ritornoApp(R.prova), coupon: codice);
      if (c.url.isNotEmpty) {
        await ref
            .read(pagamentoInSospesoProvider.notifier)
            .apri(c.url, ritorno: '${R.prova}?checkout=${Uri.encodeComponent(c.checkoutId)}');
      }
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _errore = e.messaggio(context.t));
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final sessione = ref.watch(sessioneProvider);
    final impostazioni = ref.watch(impostazioniAbbonamentiProvider).value;
    final piani = ref.watch(pianiProvider).value ?? const <Piano>[];
    final conto = sessione.autenticata ? ref.watch(contoProvider).value : null;
    // Fase 9: nello store, i livelli che hanno il prodotto della prova (prezzo e idoneità li dà lo store).
    final negozio = ref.watch(negozioProvider);
    final store = negozio == null ? null : ref.watch(offerteStoreProvider).value;
    final provaStore = {
      for (final o in store?.offerte ?? const <OffertaStore>[])
        if (o.prodotto.prova) o.piano: o,
    };
    final nelloStore = negozio != null && (provaStore.isNotEmpty || !(store?.catalogo.stripe.mostra ?? false));
    final elenco = piani
        .where((p) => p.tipo == 'abbonamento' && p.prezzoAnnuale > 0)
        .where((p) => !nelloStore || provaStore.containsKey(p.slug))
        .toList();
    final piano = elenco.where((p) => p.slug == _scelto).firstOrNull ?? elenco.lastOrNull;
    final giorni = impostazioni?.giorniProva ?? 14;
    final sconto = impostazioni?.scontoProva ?? 50;
    final promemoria = impostazioni?.giorniPromemoriaProva ?? 2;
    final offerta = piano == null ? null : provaStore[piano.slug];
    // Nello store decide lo store (Google dà l'offerta gratuita solo a chi ne ha diritto; Apple lo decide all'acquisto).
    final idonea = nelloStore
        ? offerta == null || offerta.provaGratuita
        : !sessione.autenticata || (conto?.prova?.idonea ?? true);
    final disponibile = impostazioni?.provaDisponibile ?? true;
    // I codici sconto valgono solo con la carta.
    final codice = nelloStore ? null : ref.watch(couponAttivoProvider);
    final coupon = codice == null ? null : ref.watch(anteprimaCouponProvider(codice)).value;
    final voce = piano == null ? null : coupon?.ok?.voce(piano.slug, annuale: true, rinnovo: false, prova: true);
    final w = MediaQuery.sizeOf(context).width;
    final telefono = w.telefono;
    String soldi(num c, [String? valuta]) => euro(c, lingua, valuta: valuta ?? piano?.valuta ?? 'EUR');

    // `.prova-vantaggio`: il numero grande e la promessa, sul prugna con l'ombra d'ottone.
    final numero = Text(
      '−${sconto is int ? sconto : sconto.toString()}%',
      style: Stile.serif(w.clampVw(44.8, 9, 73.6), altezza: 1, em: -.04, colore: Token.brassPale),
    );
    final promessa = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 4.8),
          child: Semantics(
            header: true,
            child: Text(t.abbonamento_prova_vantaggio_titolo(sconto), style: Stile.serif(24, colore: Token.brassPale)),
          ),
        ),
        Paragrafo(
          t.abbonamento_prova_vantaggio_testo(sconto),
          style: Stile.sans(16, colore: const Color(0xFFEADBE9), altezza: 1.6),
        ),
      ],
    );
    final vantaggio = Container(
      margin: const EdgeInsets.only(bottom: 22.4),
      padding: EdgeInsets.all(w.clampVw(17.6, 3, 28.8)),
      decoration: const BoxDecoration(
        color: Token.plum,
        boxShadow: [BoxShadow(color: Token.brassPale, offset: Offset(8, 8))],
      ),
      child: telefono
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ExcludeSemantics(child: numero),
                const SizedBox(height: 6.4),
                promessa,
              ],
            )
          : Row(
              children: [
                ExcludeSemantics(child: numero),
                const SizedBox(width: 22.4),
                Expanded(child: promessa),
              ],
            ),
    );

    final passi = Pannello(
      titolo: t.abbonamento_prova_come_titolo,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Passi(
            voci: [
              t.abbonamento_prova_passo_oggi(soldi(0)),
              t.abbonamento_prova_passo_promemoria(promemoria),
              t.abbonamento_prova_passo_fine(giorni, sconto),
              t.abbonamento_prova_passo_disdici,
            ],
          ),
          Text(t.abbonamento_prova_onesta, style: stilePiccolo()),
        ],
      ),
    );

    final acquisto = ref.watch(acquistiProvider);
    final Widget azione;
    if (!disponibile) {
      azione = Avviso(t.abbonamento_prova_non_disponibile, sopra: 0);
    } else if (nelloStore && store != null && elenco.isEmpty) {
      azione = Avviso(t.app_store_non_disponibile(negozio.nome), sopra: 0);
    } else if (!sessione.pronta) {
      azione = const SizedBox.shrink();
    } else if (!sessione.autenticata) {
      azione = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 13.44),
            child: Text(t.abbonamento_prova_entra_testo, style: Stile.sans(13.44, colore: Token.ink, altezza: 1.6)),
          ),
          Bottone(
            t.abbonamento_prova_entra,
            variante: Variante.ottone,
            pieno: true,
            an: 'trial_registrati',
            alTocco: () => unawaited(entraDa(ref)),
          ),
        ],
      );
    } else if (!idonea) {
      azione = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Avviso(t.abbonamento_prova_non_idonea, sopra: 0),
          const SizedBox(height: 16),
          Bottone(t.abbonamento_prova_vai_prezzi, href: R.prezzi, variante: Variante.quieto, pieno: true),
        ],
      );
    } else if (nelloStore) {
      azione = Bottone(
        piano != null ? t.abbonamento_prova_cta(piano.nome) : t.abbonamento_prova_eyebrow,
        variante: Variante.ottone,
        pieno: true,
        an: 'trial_inizia',
        anProprieta: const {'canale': 'store'},
        alTocco: acquisto.inCorso || piano == null || offerta == null
            ? null
            : () {
                ref.read(lanternaProvider).traccia('trial_started', {'piano': piano.slug, 'canale': 'store'});
                unawaited(ref.read(acquistiProvider.notifier).compra(offerta));
              },
      );
    } else {
      azione = Bottone(
        piano != null ? t.abbonamento_prova_cta(piano.nome) : t.abbonamento_prova_eyebrow,
        variante: Variante.ottone,
        pieno: true,
        an: 'trial_inizia',
        alTocco: _inCorso || piano == null
            ? null
            : () => unawaited(_inizia(piano, (voce?.applicato ?? false) ? codice : null)),
      );
    }

    String? notaCodice;
    if (codice != null && coupon?.motivo != null) {
      notaCodice = '$codice: ${messaggioCodice(t, coupon!.motivo, altrimenti: t.prezzi_non_vale)}';
    } else if (codice != null && voce != null && piano != null) {
      notaCodice = voce.motivo != null
          ? messaggioCodice(t, voce.motivo, altrimenti: t.prezzi_non_vale)
          : (voce.applicato ?? false)
          ? t.prezzi_coupon_nella_prova(
              codice,
              soldi((voce.listino ?? 0) - (voce.scontoRicorrente ?? 0)),
              soldi((voce.listino ?? 0) - (voce.scontoBase ?? 0)),
            )
          : t.prezzi_coupon_nella_prova_no(codice);
    }

    final scelta = Pannello(
      titolo: t.abbonamento_prova_scegli,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (elenco.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Semantics(
                label: t.abbonamento_prova_scegli,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    for (final (i, p) in elenco.indexed) ...[
                      if (i > 0) const SizedBox(height: 9.6),
                      _Livello(
                        piano: p,
                        attivo: piano?.slug == p.slug,
                        dopo: p.prezzi?.provaAnnuale ?? (p.prezzoAnnuale * (100 - sconto) / 100).round(),
                        soldi: (c) => soldi(c, p.valuta),
                        prezzoStore: nelloStore ? provaStore[p.slug]?.prezzo : null,
                        alTocco: () => setState(() => _scelto = p.slug),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          azione,
          if (notaCodice != null)
            Padding(
              padding: const EdgeInsets.only(top: 3.2, bottom: 6.4),
              child: Semantics(liveRegion: true, child: Text(notaCodice, style: stilePiccolo())),
            ),
          if (_errore != null) Errore(_errore!),
          if (nelloStore) ...[
            const SizedBox(height: 12.8),
            EsitoAcquistoStore(negozio: negozio),
            const SizedBox(height: 12.8),
            NotaStore(negozio: negozio),
          ],
        ],
      ),
    );

    return Pagina(
      sezioni: [
        FasciaStretta(
          sottoZero: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Eyebrow(t.abbonamento_prova_eyebrow),
              Semantics(
                header: true,
                child: TestoBilanciato(t.abbonamento_prova_titolo(giorni), stile: Stile.titoloSezione(w), maxCh: 19),
              ),
              IntroSezione(t.abbonamento_prova_intro(giorni, sconto)),
              if (_esito != null) _esito!.buono ? Successo(_esito!.testo) : Errore(_esito!.testo),
            ],
          ),
        ),
        FasciaStretta(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              vantaggio,
              // `.prova-griglia`: due colonne (`gap: 1.2rem`, in alto), una sul telefono.
              if (telefono)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [passi, const SizedBox(height: 19.2), scelta],
                )
              else
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: passi),
                    const SizedBox(width: 19.2),
                    Expanded(child: scelta),
                  ],
                ),
            ],
          ),
        ),
      ],
    );
  }
}

/// `ol.prova-passi`: i passi numerati (`padding-left: 1.3rem`, `.55rem` fra uno e l'altro).
class _Passi extends StatelessWidget {
  const _Passi({required this.voci});

  final List<String> voci;

  @override
  Widget build(BuildContext context) {
    final stile = Stile.sans(16, colore: Token.ink, altezza: 1.6);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final (i, v) in voci.indexed)
            Padding(
              padding: EdgeInsets.only(top: i > 0 ? 8.8 : 0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(
                    width: 20.8,
                    child: Text('${i + 1}.', textAlign: TextAlign.end, style: stile),
                  ),
                  const SizedBox(width: 6),
                  Expanded(child: Paragrafo(v, style: stile)),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

/// `.prova-livello`: un livello da scegliere (un `radio`), col listino annuale barrato e il prezzo dopo la prova.
class _Livello extends StatelessWidget {
  const _Livello({
    required this.piano,
    required this.attivo,
    required this.dopo,
    required this.soldi,
    required this.alTocco,
    this.prezzoStore,
  });

  final Piano piano;
  final bool attivo;
  final int dopo;
  final String Function(num) soldi;
  final VoidCallback alTocco;

  /// Fase 9: il prezzo dello store dopo la prova (localizzato, nella valuta dello store): senza il listino in euro.
  final String? prezzoStore;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Semantics(
      inMutuallyExclusiveGroup: true,
      checked: attivo,
      child: Premibile(
        alTocco: alTocco,
        selezionato: attivo,
        raggioFuoco: Token.raggio,
        costruisci: (context, premuto) => Container(
          constraints: const BoxConstraints(minHeight: 56),
          padding: EdgeInsets.symmetric(horizontal: attivo ? 15 : 16, vertical: attivo ? 11 : 12),
          decoration: BoxDecoration(
            color: attivo ? const Color(0xFFF1F7F4) : const Color(0xFFFFFFFF),
            border: Border.all(color: attivo ? Token.verdigris : Token.line, width: attivo ? 2 : 1),
            borderRadius: BorderRadius.circular(Token.raggio),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Expanded(
                    child: Text(piano.nome, style: Stile.serif(17.6, colore: Token.ink)),
                  ),
                  const SizedBox(width: 16),
                  Text.rich(
                    TextSpan(
                      children: [
                        if (prezzoStore == null) ...[
                        TextSpan(
                          text: soldi(piano.prezzoAnnuale),
                          semanticsLabel: '${t.abbonamento_prova_listino} ${soldi(piano.prezzoAnnuale)}',
                          style: Stile.sans(
                            13.6,
                            colore: Token.inkSoft,
                          ).copyWith(decoration: TextDecoration.lineThrough, decorationColor: Token.inkSoft),
                        ),
                        const TextSpan(text: ' '),
                        ],
                        TextSpan(
                          text: prezzoStore ?? soldi(dopo),
                          style: Stile.serif(18.4, colore: Token.ink).copyWith(fontWeight: FontWeight.w700),
                        ),
                        TextSpan(
                          text: ' ${t.abbonamento_al_anno}',
                          style: Stile.sans(13.28, colore: Token.ink),
                        ),
                      ],
                    ),
                    softWrap: false,
                    textAlign: TextAlign.end,
                    style: Stile.sans(16, colore: Token.ink),
                  ),
                ],
              ),
              Padding(
                padding: const EdgeInsets.only(top: 1.6),
                child: Text(t.abbonamento_prova_dopo, style: Stile.sans(12.48, colore: Token.inkSoft, altezza: 1.6)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
