/// Oltre un limite dell'abbonamento (`frontend/v2/componenti/dialogo-limite.tsx`, v9 Fase 2b): quale limite, quante
/// letture fatte nel periodo, e poi una delle tre strade — il condono (le prime letture oltre il limite sono un regalo,
/// e lo si dice con calore), il consenso a usare un credito, o i pacchetti se i crediti sono finiti. La lettura
/// riparte solo con un tocco esplicito.
library;

import 'package:flutter/widgets.dart';

import '../l10n/testi.dart';
import '../modelli/cassa.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'bottoni.dart';
import 'formati.dart';
import 'modale.dart';
import 'testi.dart';

/// Il titolo del limite superato (`limite_titolo_<limite>`).
String titoloLimite(AppLocalizations t, String limite) => switch (limite) {
  'letture_alla_settimana' => t.abbonamento_limite_titolo_letture_alla_settimana,
  'letture_al_mese' => t.abbonamento_limite_titolo_letture_al_mese,
  'letture_totali' => t.abbonamento_limite_titolo_letture_totali,
  _ => t.abbonamento_limite_titolo_letture_al_giorno,
};

/// Il periodo del limite (`limite_periodo_<limite>`).
String periodoLimite(AppLocalizations t, String limite) => switch (limite) {
  'letture_alla_settimana' => t.abbonamento_limite_periodo_letture_alla_settimana,
  'letture_al_mese' => t.abbonamento_limite_periodo_letture_al_mese,
  'letture_totali' => t.abbonamento_limite_periodo_letture_totali,
  'letture_al_giorno' => t.abbonamento_limite_periodo_letture_al_giorno,
  _ => '',
};

/// Apre il dialogo del limite [d]: restituisce `condono` o `credito` se si sceglie di continuare, `null` altrimenti.
/// «Vedi i pacchetti» va ai prezzi con [ritorno] (la lettura interrotta), dove si torna dopo l'acquisto.
Future<String?> apriDialogoLimite(BuildContext context, LimiteSuperato d, {required String ritorno}) async {
  final t = context.t;
  final condono = d.condoniRimasti > 0;
  final scelta = await apriModale<String>(
    context,
    titolo: condono ? t.abbonamento_condono_titolo : titoloLimite(t, d.limite),
    costruisci: (context) => ContenutoLimite(dettaglio: d),
  );
  if (scelta == 'acquisto') {
    if (context.mounted) vai(context, '${R.prezzi}?ritorno=${Uri.encodeComponent(ritorno)}');
    return null;
  }
  return scelta;
}

/// Il contenuto del dialogo (`.dialogo-limite`).
class ContenutoLimite extends StatelessWidget {
  /// Per il limite [dettaglio].
  const ContenutoLimite({super.key, required this.dettaglio});

  /// Il corpo del 402 `limite_superato`.
  final LimiteSuperato dettaglio;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final d = dettaglio;
    final lingua = Localizations.localeOf(context).languageCode;
    final condono = d.condoniRimasti > 0;
    final libera = d.siLibera == null ? null : dataOra(d.siLibera, lingua);
    final testo = Stile.sans(16, colore: Token.ink);
    Widget p(Widget figlio) => Padding(padding: const EdgeInsets.only(bottom: 12.8), child: figlio);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (condono)
          p(
            Text(
              titoloLimite(t, d.limite).toUpperCase(),
              style: Stile.sans(12.48, peso: FontWeight.w700, em: .08, colore: Token.verdigris),
            ),
          ),
        p(Paragrafo(t.abbonamento_limite_testo(d.valore, periodoLimite(t, d.limite), d.lettureFatte), style: testo)),
        if (condono)
          p(
            // `.dialogo-limite-dono`: il regalo, detto con calore.
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
              decoration: const BoxDecoration(
                color: Color(0xFFFFF6E2),
                border: Border(left: BorderSide(color: Token.brass, width: 3)),
              ),
              child: Paragrafo(
                t.abbonamento_condono_testo(d.condoniRimasti - 1),
                style: Stile.serif(16, altezza: 1.55, colore: Token.ink),
              ),
            ),
          )
        else if (d.scelta == 'credito')
          p(Paragrafo(t.abbonamento_credito_domanda(d.saldo), style: testo))
        else
          p(Paragrafo(t.abbonamento_acquisto_testo, style: testo)),
        if (libera != null && !condono)
          p(Paragrafo(t.abbonamento_limite_si_libera(libera), style: Stile.sans(13.44, colore: Token.inkSoft))),
        FilaBottoni(
          children: [
            if (condono)
              Bottone(
                t.abbonamento_condono_cta,
                variante: Variante.ottone,
                an: 'limite_condono',
                alTocco: () => Navigator.of(context).pop('condono'),
              )
            else if (d.scelta == 'credito')
              Bottone(
                t.abbonamento_credito_cta,
                variante: Variante.ottone,
                an: 'limite_credito',
                alTocco: () => Navigator.of(context).pop('credito'),
              )
            else
              Bottone(
                t.abbonamento_acquisto_cta,
                variante: Variante.ottone,
                an: 'limite_acquisto',
                alTocco: () => Navigator.of(context).pop('acquisto'),
              ),
            Bottone(t.abbonamento_non_ora, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop()),
          ],
        ),
      ],
    );
  }
}
