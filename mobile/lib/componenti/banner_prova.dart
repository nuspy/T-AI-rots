/// Il banner della prova gratuita (`frontend/v2/componenti/banner-prova.tsx`, Fase 2b), sotto la testata di ogni
/// pagina, **nel flusso** (scorre con la pagina, non copre niente e non si somma alla barra dell'oracolo).
///
/// Chi lo vede: chi non ha un account e chi è dentro senza abbonamento e senza aver già usato la prova
/// (`/me/billing` → `prova.idonea`); non sulla pagina della prova. Si accende dalla console («Abbonamenti»,
/// `/abbonamenti/pubblico` → `banner_prova`). Si chiude (✕, 44 px) e torna dopo cinque giorni; chi non può più usare
/// la prova non lo rivede per un giorno (poi si ricontrolla). Il ricordo sta sul telefono con la chiave e il formato
/// del sito (`tarots.prova.banner`: `{"fino": <ms>}`).
library;

import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/tracciato.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../rotte/percorso.dart';
import '../tema/tema.dart';
import 'premibile.dart';

/// La chiave del ricordo: la stessa del sito.
const String chiaveBannerProva = 'tarots.prova.banner';

/// Chi chiude il banner lo rivede dopo cinque giorni.
const int giorniChiuso = 5;

/// Chi non può più usare la prova (già usata, o abbonato): si ricontrolla dopo un giorno.
const int giorniNonIdoneo = 1;

/// Il ricordo del banner chiuso.
class RicordoBannerProva extends Notifier<bool> {
  @override
  bool build() {
    try {
      final v = jsonDecode(ref.read(archivioProvider).leggi(chiaveBannerProva) ?? 'null');
      return v is Map && v['fino'] is num && (v['fino'] as num) > DateTime.now().millisecondsSinceEpoch;
    } on FormatException {
      return false;
    }
  }

  /// Nasconde il banner per [giorni] giorni.
  void nascondi(int giorni) {
    final fino = DateTime.now().add(Duration(days: giorni)).millisecondsSinceEpoch;
    unawaited(ref.read(archivioProvider).scrivi(chiaveBannerProva, jsonEncode({'fino': fino})));
    state = true;
  }
}

/// Vero se il banner è stato chiuso (o va nascosto) e non è ancora ora di rivederlo.
final bannerProvaNascostoProvider = NotifierProvider<RicordoBannerProva, bool>(RicordoBannerProva.new);

/// Il banner della prova.
class BannerProva extends ConsumerWidget {
  /// Il banner.
  const BannerProva({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final impostazioni = ref.watch(impostazioniAbbonamentiProvider).value;
    final nascosto = ref.watch(bannerProvaNascostoProvider);
    final sessione = ref.watch(sessioneProvider);
    final conto = sessione.autenticata ? ref.watch(contoProvider).value : null;
    final percorso = ref.watch(percorsoProvider).path;
    final nonIdoneo = sessione.autenticata && conto?.prova != null && !conto!.prova!.idonea;
    if (nonIdoneo && !nascosto) {
      WidgetsBinding.instance.addPostFrameCallback(
        (_) => ref.read(bannerProvaNascostoProvider.notifier).nascondi(giorniNonIdoneo),
      );
    }
    if (impostazioni == null || !impostazioni.bannerProva || nascosto || nonIdoneo) return const SizedBox.shrink();
    if (percorso.startsWith(R.prova)) return const SizedBox.shrink();

    final t = context.t;
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final telefono = w.telefono;
    final giorni = impostazioni.giorniProva;
    final sconto = impostazioni.scontoProva;

    void chiudi() {
      ref.read(bannerProvaNascostoProvider.notifier).nascondi(giorniChiuso);
      ref.read(lanternaProvider).traccia('trial_banner_closed');
    }

    Future<void> vaiAllaProva() async {
      // Chi non ha un account passa dall'accesso (che con Google o Apple crea l'account) e torna alla prova.
      if (!sessione.autenticata && sessione.pronta) {
        try {
          await ref.read(sessioneProvider.notifier).entra();
        } on Object catch (e) {
          debugPrint('Accesso non riuscito: $e');
        }
      }
      if (context.mounted) vai(context, R.prova);
    }

    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          t.abbonamento_banner_etichetta.toUpperCase(),
          style: Stile.sans(11.2, peso: FontWeight.w700, em: .1, colore: const Color(0xFF145A59), altezza: 1.6),
        ),
        const SizedBox(height: 1.6),
        Text(
          t.abbonamento_banner_titolo(giorni, sconto),
          style: Stile.serif(telefono ? 15.2 : 16.32, altezza: 1.35, colore: Token.ink),
        ),
        const SizedBox(height: 1.6),
        Text(
          t.abbonamento_banner_testo(sconto),
          style: Stile.sans(13.12, altezza: 1.45, colore: Token.inkSoft),
        ),
      ],
    );

    final cta = Premibile(
      alTocco: () => unawaited(vaiAllaProva()),
      collegamento: sessione.autenticata || !sessione.pronta,
      an: 'trial_banner_cta',
      raggioFuoco: Token.raggio,
      costruisci: (context, premuto) => Container(
        constraints: const BoxConstraints(minHeight: Token.altezzaBottonePiccolo),
        padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 8),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: premuto ? const Color(0xFFC69543) : Token.brass,
          border: Border.all(color: Colori.bordoOttone),
          borderRadius: BorderRadius.circular(Token.raggio),
        ),
        child: Text(
          t.abbonamento_banner_cta(giorni),
          textAlign: TextAlign.center,
          softWrap: telefono,
          style: Stile.bottone(px: 12.8).copyWith(color: Colori.testoOttone),
        ),
      ),
    );

    final chiudiBottone = Premibile(
      alTocco: chiudi,
      etichetta: t.abbonamento_banner_chiudi,
      raggioFuoco: 22,
      costruisci: (context, premuto) => Container(
        width: 44,
        height: 44,
        alignment: Alignment.center,
        decoration: BoxDecoration(color: premuto ? const Color(0x143C1846) : null, shape: BoxShape.circle),
        child: Text('✕', style: Stile.sans(16, altezza: 1, colore: Token.inkSoft)),
      ),
    );

    final gutter = w.gutter;
    return Semantics(
      container: true,
      label: t.abbonamento_banner_etichetta,
      explicitChildNodes: true,
      child: Container(
        padding: EdgeInsets.fromLTRB(
          math.max(gutter, media.padding.left),
          telefono ? 8 : 8.8,
          math.max(gutter, media.padding.right),
          telefono ? 10.4 : 8.8,
        ),
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF6E9C9), Color(0xFFEFE0BF), Color(0xFFF3E6C8)],
            stops: [0, .6, 1],
          ),
          border: Border(bottom: BorderSide(color: Color(0x73B28336))),
        ),
        child: telefono
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: testo),
                      const SizedBox(width: 16),
                      Transform.translate(offset: const Offset(0, -3.2), child: chiudiBottone),
                    ],
                  ),
                  const SizedBox(height: 6.4),
                  cta,
                ],
              )
            : Row(
                children: [
                  Expanded(child: testo),
                  const SizedBox(width: 16),
                  cta,
                  const SizedBox(width: 16),
                  chiudiBottone,
                ],
              ),
      ),
    );
  }
}
