/// I codici sconto nell'app (v9, Fase 2d), come `frontend/v2/lib/coupon.ts` e `v2/componenti/coupon-prezzi.tsx`:
///
/// - **il collegamento applica il codice da solo**: `/pricing?coupon=CODICE` (anche da un collegamento del sito che apre
///   l'app); il codice resta per la sessione dell'app (la `sessionStorage` del sito: la scheda), sopravvive all'accesso
///   e si precompila al pagamento e alla prova; si toglie a pagamento avvenuto o a mano;
/// - **i conti li fa il server** (`POST /coupon/anteprima`, anche senza account): l'app non ricalcola niente;
/// - la banda del codice ([BandaCoupon]) e le righe sotto ogni prezzo ([RigheCoupon]): mai solo il colore, il prezzo
///   pieno è barrato e il risparmio è scritto.
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../componenti/bottoni.dart';
import '../componenti/formati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../tema/tema.dart';

/// Maiuscolo e senza spazi, come il server: chi lo scrive non deve indovinare le maiuscole.
String normalizzaCodice(String s) => s.replaceAll(RegExp(r'\s+'), '').toUpperCase();

/// Giorni di calendario alla scadenza, nell'ora di chi guarda (0 = scade oggi, 1 = domani), o `null` se non scade, è
/// passata o è lontana (oltre [entro] giorni). La console fa scadere i codici a fine giornata: contano i giorni.
int? giorniAllaScadenza(String? validoFino, {int entro = 7, DateTime? adesso}) {
  final fine = DateTime.tryParse(validoFino ?? '')?.toLocal();
  final ora = adesso ?? DateTime.now();
  if (fine == null || fine.isBefore(ora)) return null;
  final giorni = DateTime.utc(
    fine.year,
    fine.month,
    fine.day,
  ).difference(DateTime.utc(ora.year, ora.month, ora.day)).inDays;
  return giorni <= entro ? giorni : null;
}

/// «−30%» o «−5,00 €».
String etichettaSconto(CouponPubblico c, String valuta, String lingua) =>
    c.tipo == 'percentuale' ? '−${_numero(c.valore)}%' : '−${euro(c.valore, lingua, valuta: valuta)}';

String _numero(num n) => n == n.roundToDouble() ? '${n.toInt()}' : '$n';

/// Il codice attivo nella sessione dell'app (`useCouponAttivo` del sito).
class CouponAttivo extends Notifier<String?> {
  @override
  String? build() => null;

  /// Il codice di un collegamento (`?coupon=`) o scritto a mano; `null` lo toglie.
  void imposta(String? codice) {
    final c = codice == null ? null : normalizzaCodice(codice);
    state = c == null || c.isEmpty ? null : c;
  }
}

/// Il codice attivo.
final couponAttivoProvider = NotifierProvider<CouponAttivo, String?>(CouponAttivo.new);

/// L'esito dell'anteprima: il coupon con le offerte, o perché non vale (`motivo`).
typedef EsitoCoupon = ({AnteprimaCouponPubblica? ok, String? motivo});

/// Il motivo stabile per cui un codice non vale (`coupon_scaduto`…), se l'errore ne porta uno.
String? motivoCodice(Object e) => e is ErroreApi ? e.codice : null;

/// L'anteprima di un codice su tutte le offerte (anche senza account).
final anteprimaCouponProvider = FutureProvider.family<EsitoCoupon, String>((ref, codice) async {
  try {
    return (ok: await ref.read(apiProvider).anteprimaCoupon(codice), motivo: null);
  } on ErroreApi catch (e) {
    return (ok: null, motivo: motivoCodice(e) ?? 'coupon_sconosciuto');
  }
});

/// Il messaggio di un motivo dei codici (`prezzi.errori_codice`), o quello generico.
String messaggioCodice(AppLocalizations t, String? motivo, {String? altrimenti}) =>
    t.prezziErroriCodice[motivo ?? ''] ?? altrimenti ?? t.comune_err_richiesta;

/// `.coupon-banda`: il codice applicato — cosa sconta, per quanto, se si somma, quando scade — o perché non vale.
class BandaCoupon extends ConsumerWidget {
  /// La banda del [codice] con il suo [esito].
  const BandaCoupon({super.key, required this.codice, required this.esito, this.valuta = 'EUR', required this.alTogli});

  /// Il codice.
  final String codice;

  /// L'anteprima.
  final EsitoCoupon esito;

  /// La valuta delle offerte.
  final String valuta;

  /// «Togli il codice».
  final VoidCallback alTogli;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final w = MediaQuery.sizeOf(context).width;
    final stretta = w <= 480;
    final errore = esito.ok == null;
    final togli = Bottone(
      t.prezzi_coupon_togli,
      variante: Variante.quieto,
      piccolo: true,
      pieno: stretta,
      alTocco: alTogli,
    );
    final titolo = Stile.serif(18.4, altezza: 1.35, colore: Token.ink);
    final paragrafo = Stile.sans(16, colore: Token.ink, altezza: 1.6);
    final List<Widget> testo;
    if (errore) {
      testo = [
        Padding(
          padding: const EdgeInsets.only(bottom: 4.8),
          child: Text(
            codice,
            style: Stile.sans(18.4, peso: FontWeight.w700, em: .06, altezza: 1.35, colore: Token.ink),
          ),
        ),
        Text(messaggioCodice(t, esito.motivo), style: paragrafo),
      ];
    } else {
      final c = esito.ok!.coupon;
      final sconto = etichettaSconto(c, valuta, lingua);
      final durata = switch (c.durata) {
        'sempre' => t.prezzi_coupon_durata_sempre(sconto),
        'periodi' => t.prezzi_coupon_durata_periodi(sconto, c.periodi ?? 2),
        _ => t.prezzi_coupon_durata_una_volta(sconto),
      };
      final giorni = giorniAllaScadenza(c.validoFino);
      testo = [
        Padding(
          padding: const EdgeInsets.only(bottom: 4.8),
          child: Text(t.prezzi_coupon_applicato(c.codice), style: titolo),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 4.8),
          child: Text(
            '$durata. ${c.cumulabile ? t.prezzi_coupon_cumulabile : t.prezzi_coupon_non_cumulabile}',
            style: paragrafo,
          ),
        ),
        if (giorni != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 4.8),
            // `.coupon-scadenza`: una frase, non solo il rosso.
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2.4),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFFFF),
                border: Border.all(color: const Color(0x599B2C2C)),
              ),
              child: Text(
                giorni == 0 ? t.prezzi_coupon_scade_oggi : t.prezzi_coupon_scade_tra(giorni),
                style: Stile.sans(13.12, peso: FontWeight.w700, colore: Token.danger, altezza: 1.6),
              ),
            ),
          ),
        Text(t.prezzi_coupon_solo_stripe, style: Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6)),
      ];
    }
    final corpo = Column(crossAxisAlignment: CrossAxisAlignment.start, children: testo);
    return Semantics(
      liveRegion: true,
      child: Container(
        width: double.infinity,
        padding: stretta
            ? const EdgeInsets.symmetric(horizontal: 16, vertical: 14.4)
            : const EdgeInsets.symmetric(horizontal: 19.2, vertical: 16),
        decoration: BoxDecoration(
          color: errore ? const Color(0xFFFDF1EE) : const Color(0xFFEEF6F2),
          border: Border(
            top: BorderSide(color: errore ? const Color(0x669B2C2C) : const Color(0x7319706F)),
            right: BorderSide(color: errore ? const Color(0x669B2C2C) : const Color(0x7319706F)),
            bottom: BorderSide(color: errore ? const Color(0x669B2C2C) : const Color(0x7319706F)),
            left: BorderSide(color: errore ? Token.danger : Token.verdigris, width: 4),
          ),
        ),
        // `display: flex; flex-wrap: wrap; justify-content: space-between`: il testo (almeno 18rem) e il bottone accanto,
        // il bottone sotto quando non c'è posto.
        child: LayoutBuilder(
          builder: (context, vincoli) {
            final accanto = !stretta && vincoli.maxWidth >= 288 + 19.2 + 180;
            if (!accanto) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  corpo,
                  const SizedBox(height: 9.6),
                  Align(alignment: AlignmentDirectional.centerStart, child: togli),
                ],
              );
            }
            return Row(
              children: [
                Expanded(child: corpo),
                const SizedBox(width: 19.2),
                togli,
              ],
            );
          },
        ),
      ),
    );
  }
}

/// Sotto il prezzo di un'offerta: il risparmio, quale sconto vale e perché, e il prezzo dopo lo sconto del codice.
class RigheCoupon extends ConsumerWidget {
  /// Le righe della [voce].
  const RigheCoupon({super.key, required this.voce, required this.valuta, this.perPeriodo = '', this.scuro = false});

  /// La variante dell'offerta (assente: niente).
  final VoceCoupon? voce;

  /// La valuta.
  final String valuta;

  /// « / mese», « / anno» dopo il prezzo dei rinnovi.
  final String perPeriodo;

  /// Sulla carta prugna (`.plan.featured`).
  final bool scuro;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final v = voce;
    if (v == null) return const SizedBox.shrink();
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final nota = Stile.sans(13.44, colore: scuro ? const Color(0xFFD9CADE) : Token.inkSoft, altezza: 1.6);
    Widget riga(String testo, TextStyle stile, {double sopra = 3.2, double sotto = 6.4}) => Padding(
      padding: EdgeInsets.only(top: sopra, bottom: sotto),
      child: Text(testo, style: stile),
    );
    if (v.motivo != null) return riga(messaggioCodice(t, v.motivo, altrimenti: t.prezzi_non_vale), nota);
    String soldi(num? n) => euro(n ?? 0, lingua, valuta: valuta);
    final base = '−${soldi(v.scontoBase)}';
    final spiegazione = switch (v.vince) {
      'entrambi' => t.prezzi_coupon_vince_entrambi,
      'coupon' when (v.scontoBase ?? 0) > 0 => t.prezzi_coupon_vince_coupon(base),
      'rinnovo' => t.prezzi_coupon_vince_rinnovo(base),
      'prova' => t.prezzi_coupon_vince_prova(base),
      _ => null,
    };
    // Il prezzo dei rinnovi quando lo sconto del codice finisce (se finisce, e se c'è un rinnovo).
    final finisce = (v.applicato ?? false) && v.rinnovo && v.rinnoviCoupon != null;
    final dopo = finisce ? (v.listino ?? 0) - (v.scontoBase ?? 0) : null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if ((v.applicato ?? false) && (v.risparmio ?? 0) > 0)
          riga(
            t.prezzi_coupon_risparmi(soldi(v.risparmio)),
            Stile.sans(16, peso: FontWeight.w700, colore: scuro ? Token.mist : const Color(0xFF0F4D4C), altezza: 1.6),
            sopra: 3.2,
            sotto: 4.8,
          ),
        if (spiegazione != null) riga(spiegazione, nota),
        if (dopo != null && dopo != v.importo) riga(t.prezzi_coupon_poi('${soldi(dopo)}$perPeriodo'), nota),
      ],
    );
  }
}
