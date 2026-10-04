/// Le pagine d'errore (`frontend/v2/pagine/errori.tsx`, montate da `app/(v2)/not-found.tsx` ed `error.tsx`): la
/// pagina che non esiste e l'interruzione imprevista. Dicono cosa è successo e dove andare, con la voce della v2.
library;

import 'package:flutter/widgets.dart';

import '../componenti/bottoni.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../rotte/percorsi.dart';

/// Le uscite: la lettura gratuita, l'inizio, «Esplora».
class _Uscite extends StatelessWidget {
  const _Uscite();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Padding(
      padding: const EdgeInsets.only(top: 8.8),
      child: FilaBottoni(
        children: [
          Bottone(t.home_cta_gratis, href: R.leggi, variante: Variante.ottone),
          Bottone(t.comune_e_home, href: R.home, variante: Variante.quieto),
          Bottone(t.comune_nav_esplora, href: R.esplora, variante: Variante.quieto),
        ],
      ),
    );
  }
}

/// La pagina che non esiste (`NonTrovataV2`): un `.subhero` con le uscite.
class Errore404 extends StatelessWidget {
  /// La pagina che non c'è.
  const Errore404({super.key});

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Pagina(
      sezioni: [
        Sottotitolo(
          eyebrow: t.comune_e404_eyebrow,
          titolo: t.comune_e404_titolo,
          intro: t.comune_e404_testo,
          figlio: const _Uscite(),
        ),
      ],
    );
  }
}

/// L'interruzione imprevista (`ErroreV2`): si può riprovare, o andare altrove.
class Errore500 extends StatelessWidget {
  /// L'interruzione; [alRiprova] è «Riprova» (assente: niente bottone).
  const Errore500({super.key, this.alRiprova});

  /// Riprovare.
  final VoidCallback? alRiprova;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Pagina(
      sezioni: [
        Semantics(
          liveRegion: true,
          child: Sottotitolo(
            eyebrow: t.comune_e500_eyebrow,
            titolo: t.comune_e500_titolo,
            intro: t.comune_e500_testo,
            figlio: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (alRiprova != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8.8),
                    child: Bottone(t.comune_riprova, alTocco: alRiprova),
                  ),
                const _Uscite(),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
