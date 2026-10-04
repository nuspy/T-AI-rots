/// La sezione «Abbonamento» del profilo (`frontend/v2/componenti/abbonamento-profilo.tsx`, Fase 2b): stato, periodo
/// pagato, rinnovo automatico con l'interruttore, il prossimo addebito, il downgrade programmato, la prova, e «Sistema il
/// pagamento» quando un rinnovo non è andato.
///
/// Spegnere il rinnovo apre un dialogo di conferma formale (il server manda poi l'email); riaccenderlo è un tocco,
/// fino alla scadenza. Il pagamento da sistemare si apre nel browser e torna al profilo (`cassa/pagamento.dart`).
///
/// **Gli abbonamenti degli store** (`store`: comprati con Google Play o nell'App Store) mostrano solo la spiegazione e
/// il collegamento alla gestione dello store: lì si disdice, si cambia piano, si sistema il pagamento (Fase 9: il deep
/// link ufficiale di Google Play sull'abbonamento, `showManageSubscriptions` dell'App Store).
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../acquisti/acquisti.dart' show apriGestioneStore;
import '../cassa/pagamento.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../componenti/pagina.dart' show messaggioErrore;
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'comuni.dart';
import 'dati_account.dart';

/// La sezione «Abbonamento».
class AbbonamentoProfilo extends ConsumerStatefulWidget {
  /// La sezione.
  const AbbonamentoProfilo({super.key});

  @override
  ConsumerState<AbbonamentoProfilo> createState() => _AbbonamentoProfiloState();
}

class _AbbonamentoProfiloState extends ConsumerState<AbbonamentoProfilo> with AzioneAccount {
  String? _esito;
  String? _pagamento;

  Future<void> _rinnovo(bool attivo) async {
    final t = context.t;
    final lingua = ref.read(linguaProvider);
    final r = await esegui((api) => api.impostaRinnovo(attivo: attivo, lingua: lingua));
    if (r == null || !mounted) return;
    setState(() => _esito = attivo ? t.abbonamento_acceso_ok : t.abbonamento_spento_ok);
    ref.invalidate(mioAbbonamentoProvider);
  }

  Future<void> _spegni(AbbonamentoDettaglio a) async {
    final t = context.t;
    final lingua = ref.read(linguaProvider);
    final si = await apriModale<bool>(
      context,
      titolo: t.abbonamento_conferma_titolo,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          // `.dialog .prose`: tenue, .95rem.
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(
              t.abbonamento_conferma_testo(a.nome, dataLunga(a.periodoFine, lingua)),
              style: Stile.sans(15.2, colore: Token.inkSoft),
            ),
          ),
          FilaBottoni(
            children: [
              Bottone(
                t.abbonamento_conferma_si,
                variante: Variante.pericolo,
                an: 'rinnovo_spento',
                alTocco: () => Navigator.of(context).pop(true),
              ),
              Bottone(
                t.abbonamento_conferma_no,
                variante: Variante.ottone,
                alTocco: () => Navigator.of(context).pop(false),
              ),
            ],
          ),
        ],
      ),
    );
    if (si == true) await _rinnovo(false);
  }

  Future<void> _sistema() async {
    final t = context.t;
    setState(() => _pagamento = null);
    final r = await esegui((api) => api.pagamentoDaSistemare());
    if (r == null || !mounted) return;
    if (r.url != null) {
      await ref.read(pagamentoInSospesoProvider.notifier).apri(r.url!, ritorno: R.profilo);
    } else if (r.giaPagata) {
      setState(() => _pagamento = t.abbonamento_sistema_pagata);
    }
  }

  Future<void> _annullaCambio() async {
    final lingua = ref.read(linguaProvider);
    if (await esegui((api) => api.annullaCambio(lingua)) != null) ref.invalidate(mioAbbonamentoProvider);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final dati = ref.watch(mioAbbonamentoProvider);
    final m = dati.value;
    final a = m?.abbonamento;
    final imp = m?.impostazioni;
    return Sezione(
      titolo: t.abbonamento_sezione_titolo,
      id: 'abbonamento',
      children: [
        if (dati.hasError && !dati.hasValue) Errore(messaggioErrore(dati.error!, t), sopra: 0),
        if (m != null && (a == null || a.gratuito)) ...[
          TestoPiccolo(t.abbonamento_nessuno),
          FilaBottoni(
            children: [
              if (m.prova.idonea)
                Bottone(
                  t.abbonamento_prova_cta_profilo(m.impostazioni.giorniProva),
                  href: R.prova,
                  variante: Variante.ottone,
                  piccolo: true,
                ),
              Bottone(t.abbonamento_vedi_piani, href: R.prezzi, variante: Variante.quieto, piccolo: true),
            ],
          ),
        ],
        if (a != null && !a.gratuito && imp != null)
          _Dettaglio(
            a: a,
            sconto: a.prova ? imp.scontoProva : imp.scontoRinnovo,
            inCorso: inCorso,
            alSpegni: () => unawaited(_spegni(a)),
            alAccendi: () => unawaited(_rinnovo(true)),
            alSistema: () => unawaited(_sistema()),
            alAnnullaCambio: () => unawaited(_annullaCambio()),
          ),
        if (_esito != null) Successo(_esito!),
        if (_pagamento != null) Avviso(_pagamento),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

class _Dettaglio extends ConsumerWidget {
  const _Dettaglio({
    required this.a,
    required this.sconto,
    required this.inCorso,
    required this.alSpegni,
    required this.alAccendi,
    required this.alSistema,
    required this.alAnnullaCambio,
  });

  final AbbonamentoDettaglio a;
  final num sconto;
  final bool inCorso;
  final VoidCallback alSpegni;
  final VoidCallback alAccendi;
  final VoidCallback alSistema;
  final VoidCallback alAnnullaCambio;

  String _stato(AppLocalizations t) => switch (a.stato) {
    'attivo' => t.abbonamento_stato_attivo,
    'in_prova' => t.abbonamento_stato_in_prova,
    'in_sospeso' => t.abbonamento_stato_in_sospeso,
    'sospeso' => t.abbonamento_stato_sospeso,
    'disdetto' => t.abbonamento_stato_disdetto,
    'scaduto' => t.abbonamento_stato_scaduto,
    _ => a.stato,
  };

  /// `.stato-attivo`, `.stato-in_sospeso`, `.stato-sospeso`…
  Color get _coloreStato => switch (a.stato) {
    'attivo' || 'in_prova' => const Color(0xFF0F5958),
    'in_sospeso' => const Color(0xFF7A4F05),
    _ => Token.danger,
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    String data(String? iso) => iso == null ? '' : dataLunga(iso, lingua);
    String soldi(int? c) => euro(c ?? 0, lingua, valuta: a.valuta);
    final nomeStore = a.provider == 'app_store' ? t.abbonamento_store_app_store : t.abbonamento_store_google_play;
    final vivo = a.stato == 'attivo' || a.stato == 'in_prova' || a.stato == 'in_sospeso';
    final coupon = a.coupon;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        // `.abbonamento-testa`: il nome, la pillola dello stato, il periodo.
        Padding(
          padding: const EdgeInsets.only(bottom: 6.4),
          child: Wrap(
            spacing: 12.8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text(a.nome, style: Stile.serif(19.2, colore: Token.ink)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8.8, vertical: 2.4),
                decoration: BoxDecoration(
                  border: Border.all(color: _coloreStato),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  _stato(t),
                  style: Stile.sans(12, peso: FontWeight.w700, em: .04, colore: _coloreStato, altezza: 1.6),
                ),
              ),
              Text(
                a.annuale ? t.abbonamento_annuale : t.abbonamento_mensile,
                style: Stile.sans(13.44, colore: Token.inkSoft),
              ),
            ],
          ),
        ),
        TestoPiccolo(
          a.stato == 'in_prova'
              ? t.abbonamento_prova_fino(data(a.periodoFine), soldi(a.prossimoRinnovo ?? a.listino), sconto)
              : t.abbonamento_periodo_fino(data(a.periodoFine)),
        ),
        if (a.store)
          Avviso(
            null,
            sopra: 0,
            figlio: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(padding: const EdgeInsets.only(bottom: 9.6), child: Text(t.abbonamento_store_testo(nomeStore))),
                // Il sito mostra il collegamento solo se il server lo dà; nell'app la pagina dello store c'è sempre.
                Bottone(
                  t.abbonamento_store_apri(nomeStore),
                  variante: Variante.quieto,
                  piccolo: true,
                  an: 'store_gestisci',
                  alTocco: () => unawaited(apriGestioneStore(ref, a.provider)),
                ),
              ],
            ),
          )
        else ...[
          if (a.stato == 'in_sospeso' || a.stato == 'sospeso')
            Container(
              margin: const EdgeInsets.only(bottom: 13.44),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
              decoration: const BoxDecoration(
                color: Color(0xFFFDF1EE),
                border: Border(left: BorderSide(color: Token.danger, width: 3)),
              ),
              child: Semantics(
                liveRegion: true,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(bottom: 9.6),
                      child: Text(
                        a.stato == 'in_sospeso'
                            ? t.abbonamento_tolleranza(data(a.fineTolleranza))
                            : t.abbonamento_sospeso_testo,
                        style: Stile.sans(14.4, colore: Token.ink),
                      ),
                    ),
                    if (a.fatturaAperta) ...[
                      Bottone(
                        t.abbonamento_sistema,
                        variante: Variante.ottone,
                        piccolo: true,
                        an: 'sistema_pagamento',
                        alTocco: inCorso ? null : alSistema,
                      ),
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text(
                          t.abbonamento_sistema_nota,
                          style: Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          if (vivo)
            // `.rinnovo-automatico`: fra due righe sottili.
            Container(
              margin: const EdgeInsets.symmetric(vertical: 9.6),
              padding: const EdgeInsets.symmetric(vertical: 11.2),
              decoration: const BoxDecoration(
                border: Border.symmetric(horizontal: BorderSide(color: Token.line)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Semantics(
                    header: true,
                    child: Text(t.abbonamento_rinnovo_titolo, style: Stile.serif(17.6, colore: Token.ink)),
                  ),
                  Interruttore(
                    valore: a.rinnovoAutomatico,
                    titolo: t.abbonamento_rinnovo_interruttore,
                    alCambio: inCorso ? null : (v) => v ? alAccendi() : alSpegni(),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(top: 3.2),
                    child: Text(
                      a.rinnovoAutomatico
                          ? '${t.abbonamento_rinnovo_acceso(data(a.periodoFine), soldi(a.prossimoRinnovo))}'
                                '${a.scontoRicorrente > 0 ? ' ${t.abbonamento_rinnovo_acceso_sconto}' : ''}'
                          : t.abbonamento_rinnovo_spento(data(a.periodoFine)),
                      style: Stile.sans(13.44, colore: Token.ink, altezza: 1.6),
                    ),
                  ),
                  if (coupon != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 3.2),
                      child: Text(
                        coupon.perSempre
                            ? t.abbonamento_coupon_sempre(coupon.codice)
                            : t.abbonamento_coupon_rinnovi(coupon.rinnoviRimasti ?? 0, coupon.codice),
                        style: Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6),
                      ),
                    ),
                ],
              ),
            ),
          if (a.pianoSuccessivo != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 13.44),
              child: Wrap(
                spacing: 6,
                runSpacing: 6,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Text(
                    t.abbonamento_successivo(
                      data(a.pianoSuccessivo!.dal),
                      a.pianoSuccessivo!.nome,
                      a.pianoSuccessivo!.annuale ? t.abbonamento_annuale : t.abbonamento_mensile,
                    ),
                    style: Stile.sans(13.44, colore: Token.ink, altezza: 1.6),
                  ),
                  Bottone(
                    t.abbonamento_annulla_successivo,
                    variante: Variante.quieto,
                    piccolo: true,
                    alTocco: inCorso ? null : alAnnullaCambio,
                  ),
                ],
              ),
            ),
          if (vivo)
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Bottone(t.abbonamento_cambia_piano, href: R.prezzi, variante: Variante.quieto, piccolo: true),
            ),
        ],
      ],
    );
  }
}
