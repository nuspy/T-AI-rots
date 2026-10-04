/// Il negozio e il carrello (`frontend/v2/pagine/negozio.tsx`, montati da `app/(v2)/shop/page.tsx` e `cart/page.tsx`):
/// un'estensione fisica, non il motivo per cui si viene. Ogni mazzo si compra in tre forme separate (la scatola, il PDF
/// da stampare, il mazzo digitale per le letture; il Thoth digitale è già di tutti) e si guarda carta per carta prima
/// di comprarlo (la galleria). Il carrello sta sul telefono (`carrelloProvider`); prezzi, sconti e totale li calcola il
/// server (`POST /shop/quote`). L'ordine (`POST /orders`) si paga nel browser di sistema e si torna con il deep link
/// (`/cart?ordine=…`): lo stato vero lo dice il server. Con i pagamenti non ancora attivi l'ordine si registra lo
/// stesso, in attesa.
///
/// Differenza dal sito: la barra del carrello (`.shop-bar`, `position: sticky` in fondo alla finestra) qui sta al suo
/// posto nella pagina, sotto i mazzi.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:share_plus/share_plus.dart';

import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../cassa/pagamento.dart';
import '../catalogo/comuni.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/formati.dart';
import '../componenti/galleria_mazzo.dart';
import '../componenti/griglia.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'mazzi.dart' show cartellaDi;

/// I formati, nell'ordine del negozio.
const List<String> tipiNegozio = ['fisico', 'pdf', 'digitale'];

/// Gli id dei mazzi già posseduti (con un account).
final mieiMazziProvider = FutureProvider<List<int>>((ref) async {
  if (!ref.watch(sessioneProvider.select((s) => s.autenticata))) return const [];
  try {
    return await ref.read(apiProvider).mieiMazzi();
  } on ErroreApi {
    return const [];
  }
});

/// Gli indirizzi di spedizione (con un account).
final indirizziProvider = FutureProvider<List<Indirizzo>>((ref) async {
  if (!ref.watch(sessioneProvider.select((s) => s.autenticata))) return const [];
  return ref.read(apiProvider).indirizzi();
});

/// Il listino di un formato; `null`: non in vendita.
int? listinoDi(Mazzo m, String tipo) => switch (tipo) {
  'digitale' => m.prezzoDigitale,
  'pdf' => m.prezzoStampa,
  _ => m.prezzoFisico,
};

/// Il prezzo da pagare adesso: lo scontato se l'offerta vale per quel formato, altrimenti il listino.
int? prezzoDi(Mazzo m, String tipo) {
  final scontato = switch (tipo) {
    'digitale' => m.prezzoDigitaleScontato,
    'pdf' => m.prezzoStampaScontato,
    _ => m.prezzoFisicoScontato,
  };
  return scontato ?? listinoDi(m, tipo);
}

String _nomeTipo(AppLocalizations t, String tipo) => switch (tipo) {
  'digitale' => t.negozio_digitale,
  'pdf' => t.negozio_pdf,
  _ => t.negozio_fisico,
};

/// `.badge-offer`: «Offerta».
class _Offerta extends StatelessWidget {
  const _Offerta(this.testo);

  final String testo;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.8, vertical: 3.52),
      color: Token.brassPale,
      child: Text(
        testo.toUpperCase(),
        style: Stile.sans(11.2, peso: FontWeight.w700, em: .07, colore: Colori.testoOttone, altezza: 1.6),
      ),
    ),
  );
}

/// Il ponte verso la lettura delle proprie carte (`.static-share`).
class _Ponte extends StatelessWidget {
  const _Ponte({required this.sorgente});

  final String sorgente;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return CondivisioneStatica(
      eyebrow: t.negozio_ponte_titolo,
      citazione: t.mazzi_slogan,
      testo: t.negozio_ponte_testo,
      azione: Bottone(t.negozio_ponte_cta, href: '${R.fisica}?source=$sorgente', variante: Variante.ottone),
    );
  }
}

/// La pagina del negozio.
class Negozio extends ConsumerStatefulWidget {
  /// Il negozio.
  const Negozio({super.key});

  @override
  ConsumerState<Negozio> createState() => _NegozioState();
}

class _NegozioState extends ConsumerState<Negozio> {
  String? _aggiunto;
  Timer? _annuncio;

  @override
  void dispose() {
    _annuncio?.cancel();
    super.dispose();
  }

  void _aggiungi(Mazzo m, String tipo) {
    final t = context.t;
    ref.read(carrelloProvider.notifier).aggiungi(m.id, tipo);
    setState(() => _aggiunto = t.negozio_aggiunto('${m.nome} — ${_nomeTipo(t, tipo)}'));
    _annuncio?.cancel();
    _annuncio = Timer(const Duration(seconds: 4), () {
      if (mounted) setState(() => _aggiunto = null);
    });
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final sessione = ref.watch(sessioneProvider);
    final mazzi = ref.watch(mazziProvider);
    final posseduti = ref.watch(mieiMazziProvider).value ?? const <int>[];
    final carrello = ref.watch(carrelloProvider);
    final pezzi = carrello.fold(0, (s, v) => s + v.quantita);
    final elenco = mazzi.value ?? const <Mazzo>[];
    final w = larghezza(context);

    Widget oggetto(Mazzo m) {
      // Il digitale gratuito è di tutti, come il predefinito: nessun acquisto.
      final mioDigitale = m.predefinito || m.prezzoDigitale == 0 || posseduti.contains(m.id);
      final nelCarrello = carrello.where((v) => v.deckId == m.id).fold(0, (s, v) => s + v.quantita);
      final copertina = Premibile(
        alTocco: () => unawaited(apriGalleriaMazzo(context, m)),
        etichetta: t.negozio_vedi_carte_di(m.nome),
        costruisci: (context, premuto) => Column(
          children: [
            Container(
              width: w.telefono ? 120 : 160,
              decoration: const BoxDecoration(
                boxShadow: [BoxShadow(color: Color(0x2E201026), offset: Offset(0, 15), blurRadius: 25)],
              ),
              child: ImmagineCarta('dorso', mazzo: cartellaDi(m)),
            ),
            const SizedBox(height: 8),
            TestoSottolineato(
              t.negozio_vedi_carte,
              stile: Stile.sans(12.48, peso: FontWeight.w700, altezza: 1.6),
              scarto: 3,
            ),
          ],
        ),
      );
      final formati = <Widget>[];
      for (final tipo in tipiNegozio) {
        if (tipo == 'digitale' && mioDigitale) {
          formati.add(
            _Formato(
              nome: _nomeTipo(t, tipo),
              azione: Disponibile(
                m.predefinito || m.prezzoDigitale == 0 ? t.negozio_incluso : t.negozio_posseduto,
                sotto: 0,
              ),
            ),
          );
          continue;
        }
        final prezzo = prezzoDi(m, tipo);
        if (tipo == 'digitale' && prezzo == null) continue;
        if (tipo == 'pdf' && prezzo == 0) {
          formati.add(
            _Formato(
              nome: _nomeTipo(t, tipo),
              azione: Bottone(
                t.negozio_pdf_gratis,
                variante: Variante.quieto,
                piccolo: true,
                an: 'deck_pdf_viewed',
                alTocco: () => unawaited(apriFuori(Api.urlPdfGratuito(m.slug))),
              ),
            ),
          );
          continue;
        }
        final listino = listinoDi(m, tipo);
        formati.add(
          _Formato(
            nome: _nomeTipo(t, tipo),
            prezzo: prezzo == null
                ? Text(t.negozio_prezzo_in_arrivo, style: Stile.sans(15.2, colore: Token.inkSoft, altezza: 1.6))
                : Text.rich(
                    TextSpan(
                      children: [
                        if (listino != prezzo && listino != null)
                          TextSpan(
                            text: '${euro(listino, lingua, valuta: m.valuta)} ',
                            style: Stile.sans(13.44, colore: Token.inkSoft).copyWith(
                              decoration: TextDecoration.lineThrough,
                            ),
                          ),
                        TextSpan(text: euro(prezzo, lingua, valuta: m.valuta)),
                      ],
                    ),
                    style: Stile.sans(15.2, peso: FontWeight.w700, altezza: 1.6, colore: Token.ink),
                  ),
            azione: Bottone(
              switch (tipo) {
                'digitale' => t.negozio_aggiungi_digitale,
                'pdf' => t.negozio_aggiungi_pdf,
                _ => t.negozio_aggiungi_fisico,
              },
              piccolo: true,
              an: 'carrello_aggiunto',
              anProprieta: {'mazzo': m.slug, 'tipo': tipo},
              alTocco: prezzo == null ? null : () => _aggiungi(m, tipo),
            ),
          ),
        );
      }
      final testo = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Semantics(header: true, child: Text(m.nome, style: Stile.serif(20.8, colore: Token.ink))),
          ),
          if (m.descrizione != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 14.08),
              child: Paragrafo(m.descrizione!, style: Stile.sans(14.08, colore: Token.inkSoft)),
            ),
          if (m.offertaAttiva) _Offerta(t.negozio_offerta),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: formati),
          ),
          if (m.offertaAttiva && m.offertaValidoFino != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 13.44),
              child: Text(t.negozio_offerta_fino(dataMedia(m.offertaValidoFino, lingua)), style: stilePiccolo()),
            ),
          FilaBottoni(
            children: [
              Bottone(
                t.negozio_vedi_carte,
                variante: Variante.quieto,
                piccolo: true,
                alTocco: () => unawaited(apriGalleriaMazzo(context, m)),
              ),
              if (nelCarrello > 0)
                Bottone(
                  '${t.negozio_nel_carrello(nelCarrello)} · ${t.negozio_vai_carrello}',
                  variante: Variante.quieto,
                  piccolo: true,
                  href: R.carrello,
                ),
            ],
          ),
        ],
      );
      // `.shop-object`: due colonne (la copertina e il testo), una sul telefono.
      return Container(
        padding: EdgeInsets.all(w.telefono ? 17.6 : 24),
        decoration: BoxDecoration(
          color: Colori.carta,
          border: Border.all(color: Token.line),
        ),
        child: w.telefono
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [Center(child: copertina), const SizedBox(height: 16), testo],
              )
            : Row(
                children: [
                  Expanded(child: Center(child: copertina)),
                  const SizedBox(width: 16),
                  Expanded(child: testo),
                ],
              ),
      );
    }

    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.negozio_eyebrow, titolo: t.negozio_titolo, intro: t.negozio_intro, compatta: true),
        Fascia(
          compatta: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (mazzi.hasError && !mazzi.hasValue) Errore(messaggioErrore(mazzi.error!, t), sopra: 0),
              if (mazzi.hasValue && elenco.isEmpty) Avviso(t.negozio_vuoto, sopra: 0),
              Semantics(liveRegion: true, label: _aggiunto ?? '', child: const SizedBox.shrink()),
              // `.shop-grid`: due colonne (gap `.5rem 2rem`), una sul telefono.
              Griglia(
                colonne: w.telefono ? 1 : 2,
                spazioColonne: 32,
                spazioRighe: 8,
                allunga: false,
                children: [for (final m in elenco) oggetto(m)],
              ),
              if (pezzi > 0)
                // `.shop-bar`.
                Container(
                  margin: const EdgeInsets.only(top: 24),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: const BoxDecoration(
                    color: Token.paperLight,
                    border: Border(top: BorderSide(color: Token.brass, width: 3)),
                    boxShadow: [BoxShadow(color: Color(0x2E201026), offset: Offset(0, 10), blurRadius: 30)],
                  ),
                  child: Wrap(
                    alignment: WrapAlignment.spaceBetween,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      Text(t.negozio_pezzi(pezzi), style: Stile.sans(16, colore: Token.ink)),
                      Bottone(t.negozio_vai_carrello, href: R.carrello, variante: Variante.ottone),
                    ],
                  ),
                ),
              const Padding(padding: EdgeInsets.only(top: 14.4), child: _Ponte(sorgente: 'shop')),
              if (!sessione.autenticata && sessione.pronta)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text(t.negozio_nota_account, style: stilePiccolo()),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

/// `.shop-format`: il formato (col prezzo sotto) e l'azione, con la riga sopra.
class _Formato extends StatelessWidget {
  const _Formato({required this.nome, required this.azione, this.prezzo});

  final String nome;
  final Widget azione;
  final Widget? prezzo;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8.8),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Token.line)),
      ),
      child: Wrap(
        alignment: WrapAlignment.spaceBetween,
        crossAxisAlignment: WrapCrossAlignment.center,
        spacing: 12,
        runSpacing: 8,
        children: [
          Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(nome, style: Stile.sans(14.4, colore: Token.ink)),
              ?prezzo,
            ],
          ),
          azione,
        ],
      ),
    );
  }
}

/// La pagina del carrello.
class PaginaCarrello extends ConsumerStatefulWidget {
  /// Il carrello; [parametri] porta `ordine` al ritorno dal pagamento.
  const PaginaCarrello({super.key, required this.parametri});

  /// La query dell'indirizzo.
  final Map<String, String> parametri;

  @override
  ConsumerState<PaginaCarrello> createState() => _PaginaCarrelloState();
}

/// L'esito di un ordine o di un pagamento.
typedef _Esito = ({bool buono, String testo, String? ordine, List<RigaOrdine> pdf});

class _PaginaCarrelloState extends ConsumerState<PaginaCarrello> {
  String? _indirizzoScelto;
  ({String chiave, Preventivo? dati, String? errore})? _preventivo;
  String? _chiaveRichiesta;
  Timer? _attesa;
  _Esito? _esito;
  bool _inCorso = false;
  String? _errore;
  String? _ordineLetto;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _ritorno());
  }

  @override
  void didUpdateWidget(PaginaCarrello vecchia) {
    super.didUpdateWidget(vecchia);
    if (vecchia.parametri['ordine'] != widget.parametri['ordine']) _ritorno();
  }

  @override
  void dispose() {
    _attesa?.cancel();
    super.dispose();
  }

  /// Il ritorno dal pagamento (`?ordine=…`): lo stato vero lo dice il server.
  Future<void> _ritorno() async {
    final id = widget.parametri['ordine'];
    if (id == null || id.isEmpty || id == _ordineLetto) return;
    if (!ref.read(sessioneProvider).autenticata) return;
    _ordineLetto = id;
    ref.read(pagamentoInSospesoProvider.notifier).concluso();
    final t = context.t;
    try {
      final o = await ref.read(apiProvider).ordine(id);
      if (!mounted) return;
      if (o.status == 'pagato') {
        setState(
          () => _esito = (
            buono: true,
            testo: t.negozio_pagato,
            ordine: id,
            pdf: [for (final r in o.righe) if (r.tipo == 'pdf') r],
          ),
        );
        ref.read(carrelloProvider.notifier).svuota();
        ref.read(lanternaProvider).traccia('purchase_completed', {'tipo': 'ordine'});
      } else if (o.status != 'aperto') {
        setState(() => _esito = (buono: false, testo: t.negozio_annullato, ordine: null, pdf: const []));
      }
    } on ErroreApi {
      if (mounted) setState(() => _esito = (buono: false, testo: t.negozio_non_verificato, ordine: null, pdf: const []));
    }
  }

  /// Il preventivo dal server a ogni cambiamento del carrello (con un attimo di pausa mentre si premono i +/−).
  void _chiediPreventivo(List<VoceCarrello> voci, String chiave) {
    if (_chiaveRichiesta == chiave) return;
    _chiaveRichiesta = chiave;
    _attesa?.cancel();
    if (voci.isEmpty) return;
    _attesa = Timer(const Duration(milliseconds: 250), () async {
      final t = context.t;
      try {
        final d = await ref.read(apiProvider).preventivo([for (final v in voci) v.perApi]);
        if (mounted && _chiaveRichiesta == chiave) setState(() => _preventivo = (chiave: chiave, dati: d, errore: null));
      } on ErroreApi catch (e) {
        if (mounted && _chiaveRichiesta == chiave) {
          setState(
            () => _preventivo = (
              chiave: chiave,
              dati: null,
              errore: e.stato == 422 ? t.negozio_non_disponibile : t.comune_err_generico,
            ),
          );
        }
      }
    });
  }

  Future<void> _completa(List<VoceCarrello> voci, bool serveIndirizzo, String? indirizzo) async {
    final t = context.t;
    if (!ref.read(sessioneProvider).autenticata) {
      await entraDa(ref);
      return;
    }
    if (serveIndirizzo && indirizzo == null) return;
    setState(() {
      _inCorso = true;
      _errore = null;
    });
    try {
      final o = await ref
          .read(apiProvider)
          .apriOrdine(
            [for (final v in voci) v.perApi],
            ritorno: ritornoApp(R.carrello),
            indirizzoId: serveIndirizzo ? indirizzo : null,
          );
      if (o.url != null) {
        await ref.read(pagamentoInSospesoProvider.notifier).apri(o.url!, ritorno: '${R.carrello}?ordine=${o.id}');
        return;
      }
      // Pagamenti non ancora attivi: l'ordine è registrato, in attesa. Il carrello si svuota: l'ordine lo contiene.
      if (!mounted) return;
      final lingua = ref.read(linguaProvider);
      setState(
        () => _esito = (
          buono: true,
          testo: t.negozio_ordine_registrato(
            o.id.substring(0, 8).toUpperCase(),
            euro(o.importoTotale, lingua, valuta: o.valuta),
          ),
          ordine: o.id,
          pdf: const [],
        ),
      );
      ref.read(carrelloProvider.notifier).svuota();
      ref.read(lanternaProvider).traccia('order_registered', {'tipo': 'ordine', 'pagamento': 'non_attivo'});
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _errore = e.messaggio(t));
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final sessione = ref.watch(sessioneProvider);
    final carrello = ref.watch(carrelloProvider);
    final mazzi = ref.watch(mazziProvider);
    final perId = {for (final m in mazzi.value ?? const <Mazzo>[]) m.id: m};
    // Solo ciò che il catalogo vende ancora: una voce di un mazzo sparito non entra nel preventivo.
    final voci = mazzi.hasValue ? carrello.where((v) => perId.containsKey(v.deckId)).toList() : carrello;
    final chiave = voci.map((v) => '${v.deckId}:${v.tipo}:${v.quantita}').join(',');
    if (mazzi.hasValue) _chiediPreventivo(voci, chiave);
    final attuale = _preventivo?.chiave == chiave ? _preventivo : null;
    final q = attuale?.dati;
    final serveIndirizzo = voci.any((v) => v.tipo == 'fisico');
    final indirizzi = sessione.autenticata ? (ref.watch(indirizziProvider).value ?? const <Indirizzo>[]) : const <Indirizzo>[];
    final indirizzoAttivo =
        _indirizzoScelto ??
        indirizzi.where((i) => i.predefinito).firstOrNull?.id ??
        indirizzi.firstOrNull?.id;
    final valuta = voci.isNotEmpty ? (perId[voci.first.deckId]?.valuta ?? 'EUR') : 'EUR';
    String soldi(int c) => euro(c, lingua, valuta: valuta);
    RigaPreventivo? riga(int deckId, String tipo) =>
        q?.righe.where((r) => r.deckId == deckId && r.tipo == tipo).firstOrNull;

    final Widget pannello;
    if (!mazzi.hasValue && !mazzi.hasError) {
      pannello = Text(t.comune_carica, style: Stile.sans(16, colore: Token.inkSoft));
    } else if (voci.isEmpty) {
      pannello = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(t.negozio_carrello_vuoto, style: Stile.sans(16, colore: Token.inkSoft)),
          ),
          Bottone(t.negozio_vai_negozio, href: R.negozio),
        ],
      );
    } else {
      final totale = Stile.sans(16, colore: Token.ink);
      final grassetto = totale.copyWith(fontWeight: FontWeight.w700);
      pannello = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final v in voci)
                  _RigaCarrello(
                    voce: v,
                    mazzo: perId[v.deckId]!,
                    riga: riga(v.deckId, v.tipo),
                    soldi: soldi,
                  ),
              ],
            ),
          ),
          if (attuale?.errore != null) Errore(attuale!.errore!, sopra: 0),
          // `.cart-totals`.
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(
              children: [
                _Totale(t.negozio_subtotale, q == null ? '…' : soldi(q.subtotale), stile: totale),
                if (q != null && q.scontoScaglioni > 0)
                  _Totale(
                    t.negozio_sconto_scaglioni(q.scaglionePercentuale),
                    '−${soldi(q.scontoScaglioni)}',
                    stile: totale,
                  ),
                _Totale(t.negozio_totale, q == null ? '…' : soldi(q.totale), stile: grassetto),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 13.44),
            child: Paragrafo(t.negozio_nota_sconto, style: stilePiccolo()),
          ),
          if (serveIndirizzo && sessione.autenticata)
            indirizzi.isEmpty
                ? Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(t.negozio_indirizzo, style: stileEtichettaCampo()),
                        Text(t.negozio_indirizzo_manca, style: Stile.sans(13.44)),
                        Collegamento(t.negozio_indirizzo_profilo, href: '${R.profilo}#indirizzi'),
                      ],
                    ),
                  )
                : CampoScelta<String>(
                    etichetta: t.negozio_indirizzo,
                    voci: [for (final i in indirizzi) (i.id, '${i.nome} — ${i.via}, ${i.citta}')],
                    valore: indirizzoAttivo ?? '',
                    alCambio: (v) => setState(() => _indirizzoScelto = v),
                  ),
          if (q != null && !q.pagamentoAttivo)
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Avviso(t.negozio_pagamento_non_attivo, sopra: 0),
            ),
          FilaBottoni(
            children: [
              Bottone(
                _inCorso
                    ? t.negozio_in_corso
                    : (sessione.autenticata ? t.negozio_completa : t.negozio_entra_per),
                variante: Variante.ottone,
                alTocco:
                    _inCorso || q == null || (serveIndirizzo && sessione.autenticata && indirizzoAttivo == null)
                    ? null
                    : () => unawaited(_completa(voci, serveIndirizzo, indirizzoAttivo)),
              ),
              Bottone(t.negozio_continua, href: R.negozio, variante: Variante.quieto),
            ],
          ),
          if (_errore != null) Errore(_errore!),
        ],
      );
    }

    final esito = _esito;
    return Pagina(
      sezioni: [
        AperturaCatalogo(eyebrow: t.negozio_eyebrow, titolo: t.negozio_carrello),
        Fascia(
          compatta: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (esito != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: _RiquadroEsito(esito: esito, nomi: {for (final e in perId.entries) e.key: e.value.nome}),
                ),
              GrigliaStoria(
                sinistra: Pannello(child: pannello),
                destra: const _Ponte(sorgente: 'cart'),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Una riga di `.cart-totals`: il nome a sinistra, l'importo a destra.
class _Totale extends StatelessWidget {
  const _Totale(this.nome, this.valore, {required this.stile});

  final String nome;
  final String valore;
  final TextStyle stile;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 5.6),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(child: Text(nome, style: stile)),
        const SizedBox(width: 16),
        Text(valore, style: stile, textAlign: TextAlign.right),
      ],
    ),
  );
}

/// `.cart-line`: la miniatura, il nome e il formato, i +/−, il prezzo e «Rimuovi».
class _RigaCarrello extends ConsumerWidget {
  const _RigaCarrello({required this.voce, required this.mazzo, required this.riga, required this.soldi});

  final VoceCarrello voce;
  final Mazzo mazzo;
  final RigaPreventivo? riga;
  final String Function(int) soldi;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final telefono = larghezza(context).telefono;
    final carrello = ref.read(carrelloProvider.notifier);
    final r = riga;
    final miniatura = Container(
      width: telefono ? 40 : 48,
      decoration: const BoxDecoration(
        boxShadow: [BoxShadow(color: Color(0x29201026), offset: Offset(0, 6), blurRadius: 12)],
      ),
      child: ImmagineCarta('dorso', mazzo: cartellaDi(mazzo)),
    );
    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(mazzo.nome, style: Stile.sans(16, peso: FontWeight.w700, colore: Token.ink)),
        Text(_nomeTipo(t, voce.tipo), style: Stile.sans(13.44, colore: Token.ink)),
        if (r != null && r.prezzoFinaleUnitario != r.prezzoPienoUnitario)
          Text(
            soldi(r.prezzoPienoUnitario),
            style: Stile.sans(13.44, colore: Token.inkSoft).copyWith(decoration: TextDecoration.lineThrough),
          ),
      ],
    );
    Widget passo(String segno, String etichetta, VoidCallback? f) => Premibile(
      alTocco: f,
      etichetta: etichetta,
      costruisci: (context, premuto) => Container(
        width: 44,
        height: 44,
        alignment: Alignment.center,
        color: premuto ? const Color(0x0F3C1846) : null,
        child: Text(
          segno,
          style: Stile.sans(17.6, peso: FontWeight.w700, altezza: 1, colore: f == null ? Token.line : Token.plum),
        ),
      ),
    );
    final stepper = Semantics(
      label: t.negozio_quantita_di(mazzo.nome),
      container: true,
      child: Container(
        decoration: BoxDecoration(
          border: Border.all(color: Token.line),
          borderRadius: BorderRadius.circular(Token.raggio),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            passo('−', t.negozio_meno, () => carrello.quantita(voce.deckId, voce.tipo, voce.quantita - 1)),
            ConstrainedBox(
              constraints: const BoxConstraints(minWidth: 20),
              child: Semantics(
                liveRegion: true,
                child: Text(
                  '${voce.quantita}',
                  textAlign: TextAlign.center,
                  style: Stile.sans(16, peso: FontWeight.w700, colore: Token.ink),
                ),
              ),
            ),
            passo(
              '+',
              t.negozio_piu,
              voce.tipo == 'digitale' || voce.quantita >= maxQuantita
                  ? null
                  : () => carrello.quantita(voce.deckId, voce.tipo, voce.quantita + 1),
            ),
          ],
        ),
      ),
    );
    final prezzo = Text(
      r == null ? '…' : soldi(r.prezzoFinaleUnitario * r.quantita),
      style: Stile.sans(16, peso: FontWeight.w700, colore: Token.ink),
    );
    final togli = Premibile(
      alTocco: () => carrello.togli(voce.deckId, voce.tipo),
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 44),
        child: Center(
          widthFactor: 1,
          child: TestoSottolineato(t.negozio_rimuovi, stile: Stile.sans(12.8, altezza: 1.6), scarto: 3),
        ),
      ),
    );
    const spazio = 14.4;
    // Le aree della griglia del sito: sul computer «img testo passi prezzo / img testo passi rimuovi», sul telefono
    // «img testo prezzo / img passi rimuovi».
    final Widget destra = telefono
        ? Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [Expanded(child: testo), const SizedBox(width: spazio), prezzo],
              ),
              const SizedBox(height: 4),
              Row(
                children: [stepper, const Spacer(), togli],
              ),
            ],
          )
        : Row(
            children: [
              Expanded(child: testo),
              const SizedBox(width: spazio),
              stepper,
              const SizedBox(width: spazio),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [prezzo, togli]),
            ],
          );
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Token.line)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [miniatura, const SizedBox(width: spazio), Expanded(child: destra)],
      ),
    );
  }
}

/// L'esito dell'ordine (`.success` o `.error`), coi PDF di un ordine pagato e il collegamento agli ordini.
class _RiquadroEsito extends StatelessWidget {
  const _RiquadroEsito({required this.esito, required this.nomi});

  final _Esito esito;
  final Map<int, String> nomi;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final buono = esito.buono;
    return Semantics(
      liveRegion: true,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
        decoration: BoxDecoration(
          color: buono ? const Color(0xFFE7F2EE) : Colori.fondoErrore,
          border: Border(left: BorderSide(color: buono ? Token.verdigris : Token.danger, width: 3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Paragrafo(
              esito.testo,
              style: Stile.sans(14.4, colore: buono ? const Color(0xFF0F4D4C) : Token.danger),
            ),
            for (final r in esito.pdf)
              _BottonePdf(ordineId: esito.ordine!, deckId: r.deckId, nome: nomi[r.deckId] ?? r.mazzo?.nome ?? ''),
            if (esito.ordine != null)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Collegamento(t.negozio_vedi_ordini, href: '${R.profilo}#ordini'),
              ),
          ],
        ),
      ),
    );
  }
}

/// Il PDF di un ordine pagato (`BottonePdfV2`): si scarica con il token e si apre il foglio di condivisione del
/// telefono per salvarlo o mandarlo.
class _BottonePdf extends ConsumerStatefulWidget {
  const _BottonePdf({required this.ordineId, required this.deckId, required this.nome});

  final String ordineId;
  final int deckId;
  final String nome;

  @override
  ConsumerState<_BottonePdf> createState() => _BottonePdfState();
}

class _BottonePdfState extends ConsumerState<_BottonePdf> {
  bool _inCorso = false;
  bool _errore = false;

  Future<void> _scarica() async {
    setState(() {
      _inCorso = true;
      _errore = false;
    });
    try {
      final f = await ref.read(apiProvider).pdfOrdine(widget.ordineId, widget.deckId);
      final nome = f.nome ?? '${widget.nome.isEmpty ? 'deck' : widget.nome}.pdf';
      await SharePlus.instance.share(
        ShareParams(
          files: [XFile.fromData(f.byte, mimeType: 'application/pdf', name: nome)],
          fileNameOverrides: [nome],
        ),
      );
    } on Object {
      if (mounted) setState(() => _errore = true);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Bottone(
            _inCorso
                ? t.negozio_pdf_in_corso
                : '${t.negozio_scarica_pdf}${widget.nome.isEmpty ? '' : ' — ${widget.nome}'}',
            variante: Variante.quieto,
            piccolo: true,
            an: 'deck_pdf_viewed',
            alTocco: _inCorso ? null : () => unawaited(_scarica()),
          ),
          if (_errore) Errore(t.negozio_pdf_errore),
        ],
      ),
    );
  }
}
