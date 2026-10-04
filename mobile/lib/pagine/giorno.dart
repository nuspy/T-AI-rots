/// La carta del giorno (`frontend/v2/pagine/giorno.tsx`): per tutti, la carta di oggi (uguale per chiunque fino a
/// mezzanotte UTC); per chi è dentro, la sua carta personale da girare, con i giorni di fila. Porta a una domanda più
/// ampia: la carta come spunto, non come promessa. Sotto, i nove articoli del diario. Gli spazi pubblicitari del sito
/// non ci sono (niente pubblicità nell'app al lancio).
library;

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../api/errori.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/carta.dart';
import '../componenti/diario.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/carta.dart';
import '../notifiche/invito.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// La pagina della carta del giorno.
class Giorno extends ConsumerWidget {
  /// La carta del giorno.
  const Giorno({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final autenticata = ref.watch(sessioneProvider.select((s) => s.autenticata));
    return Pagina(
      sezioni: [
        // `<Sottotitolo sezione="giorno" compatto />` della pagina del sito; chi è dentro legge `intro_dentro`.
        Sottotitolo(
          eyebrow: context.t.giorno_eyebrow,
          titolo: context.t.giorno_titolo,
          intro: autenticata ? context.t.giorno_intro_dentro : context.t.giorno_intro,
          compatta: true,
        ),
        if (autenticata) const _Personale() else const _PerTutti(),
        const DiarioNove(),
      ],
    );
  }
}

/// `.band.band-tight.deck-layout` con `align-items: start`: la carta (centrata) e il testo; una colonna sul telefono.
class _Disposizione extends StatelessWidget {
  const _Disposizione({required this.carta, required this.testo});

  final Widget carta;
  final Widget testo;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final spazio = w.clampVw(11.2, 2.1, 28);
    return Fascia(
      compatta: true,
      child: w.telefono
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(child: carta),
                SizedBox(height: spazio),
                testo,
              ],
            )
          : Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 8, child: Center(child: carta)),
                SizedBox(width: spazio),
                Expanded(flex: 12, child: testo),
              ],
            ),
    );
  }
}

/// `min(260px, 70vw)`.
double _larghezzaCarta(BuildContext context) => math.min(260, MediaQuery.sizeOf(context).width * .7);

/// `.small.muted`.
TextStyle _piccolo() => Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6);

/// `.prose-block p { font: 1rem/1.75 var(--serif); margin: 0 0 .9rem }`, al massimo 64ch.
class _Prosa extends StatelessWidget {
  const _Prosa(this.paragrafi);

  final List<String> paragrafi;

  @override
  Widget build(BuildContext context) {
    final stile = Stile.serif(16, altezza: 1.75, colore: Token.ink);
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: larghezzaCh(stile, MediaQuery.textScalerOf(context)) * 64),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final p in paragrafi)
            Padding(
              padding: const EdgeInsets.only(bottom: 14.4),
              child: Paragrafo(p, style: stile),
            ),
        ],
      ),
    );
  }
}

/// Un messaggio mentre si carica o se qualcosa non va (`.muted` / `.error`).
class _Stato extends StatelessWidget {
  const _Stato({this.errore});

  final String? errore;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final e = errore;
    return Fascia(
      compatta: true,
      child: e == null
          ? Text(t.comune_carica, style: Stile.sans(16, colore: Token.inkSoft, altezza: 1.6))
          : Container(
              margin: const EdgeInsets.only(top: 16),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
              decoration: const BoxDecoration(
                color: Colori.fondoErrore,
                border: Border(left: BorderSide(color: Token.danger, width: 3)),
              ),
              child: Text(e, style: Stile.sans(14.4, colore: Token.danger, altezza: 1.6)),
            ),
    );
  }
}

String _messaggio(Object e, AppLocalizations t) => e is ErroreApi ? e.messaggio(t) : t.comune_err_generico;

/// Il nome della carta e la riga sotto (lettera ebraica, elemento, astrologia), come il sito.
String _meta(Carta c) => [
  c.letteraEbraica?.nome,
  c.elementoLabel ?? c.elemento,
  c.astrologia,
].whereType<String>().where((s) => s.isNotEmpty).join(' · ');

/* ---- per tutti ---------------------------------------------------------------------------------------------------- */

class _PerTutti extends ConsumerWidget {
  const _PerTutti();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final oggi = ref.watch(cartaOggiProvider);
    final sessione = ref.watch(sessioneProvider);
    if (oggi.hasError && !oggi.hasValue) return _Stato(errore: _messaggio(oggi.error!, t));
    final dati = oggi.value;
    if (dati == null) return const _Stato();
    final c = dati.carta;
    final nome = c.nomeIn(lingua);
    final spirito = c.ambiti?['spirito'];
    return _Disposizione(
      carta: CartaV2(carta: c, rivelata: true, larghezza: _larghezzaCarta(context), nome: nome),
      testo: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Eyebrow(t.giorno_di_tutti),
          TitoloSezione(nome),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 13.44),
            child: Text(_meta(c), style: _piccolo()),
          ),
          _Prosa([dati.testo, ?spirito]),
          IntroSezione(t.giorno_domanda, sopra: 8),
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: FilaBottoni(
              children: [
                Bottone(t.giorno_cta, href: '${R.leggi}?source=daily'),
                Bottone(t.giorno_significato(nome), href: R.carta(c.slug ?? c.id), variante: Variante.quieto),
              ],
            ),
          ),
          Container(
            margin: const EdgeInsets.only(top: 16),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
            decoration: const BoxDecoration(
              color: Colori.avviso,
              border: Border(left: BorderSide(color: Token.brass, width: 3)),
            ),
            child: Paragrafo(t.giorno_personale, style: Stile.sans(14.4, colore: Token.inkSoft, altezza: 1.6)),
          ),
          if (sessione.pronta)
            Padding(
              padding: const EdgeInsets.only(top: 12.8),
              child: FilaBottoni(
                children: [
                  Bottone(
                    t.giorno_entra,
                    variante: Variante.quieto,
                    piccolo: true,
                    alTocco: () => unawaited(_entra(ref)),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _entra(WidgetRef ref) async {
    try {
      await ref.read(sessioneProvider.notifier).entra();
    } on Object catch (e) {
      debugPrint('Accesso non riuscito: $e');
    }
  }
}

/* ---- la carta personale -------------------------------------------------------------------------------------------- */

class _Personale extends ConsumerStatefulWidget {
  const _Personale();

  @override
  ConsumerState<_Personale> createState() => _PersonaleState();
}

class _PersonaleState extends ConsumerState<_Personale> {
  bool _girata = false;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final giorno = ref.watch(cartaDelGiornoProvider);
    if (giorno.hasError && !giorno.hasValue) return _Stato(errore: _messaggio(giorno.error!, t));
    final g = giorno.value;
    if (g == null) return const _Stato();
    final nome = g.carta.nomeIn(lingua);
    final data = DateTime.tryParse(g.giorno);
    final quando = data == null
        ? g.giorno
        : DateFormat('EEEE d MMMM', datiLingua(lingua).locale.replaceAll('-', '_')).format(data);
    final spirito = g.carta.ambiti?['spirito'];
    void gira() => setState(() => _girata = true);
    return _Disposizione(
      carta: CartaV2(
        carta: g.carta,
        rivelata: _girata,
        rovescio: g.rovescio,
        larghezza: _larghezzaCarta(context),
        nome: nome,
        brilla: !_girata,
        alTocco: _girata ? null : gira,
        etichetta: _girata ? nome : t.giorno_gira,
      ),
      testo: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Eyebrow(t.giorno_tua),
          Padding(
            padding: const EdgeInsets.only(bottom: 13.44),
            child: Text('$quando · ${t.giorno_serie(g.serie)}', style: _piccolo()),
          ),
          if (!_girata)
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Bottone(t.giorno_gira, variante: Variante.ottone, alTocco: gira),
            )
          else ...[
            Text.rich(
              TextSpan(
                children: [
                  TextSpan(text: '$nome '),
                  TextSpan(text: '· ${g.rovescio ? t.lettura_rovesciata : t.lettura_dritta}', style: _piccolo()),
                ],
              ),
              style: Stile.titoloSezione(MediaQuery.sizeOf(context).width),
            ),
            const SizedBox(height: 16),
            _Prosa([g.testo, ?spirito]),
            IntroSezione(t.giorno_domanda),
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: FilaBottoni(
                children: [
                  Bottone(t.giorno_cta, href: '${R.leggi}?source=daily'),
                  Bottone(
                    t.giorno_significato(nome),
                    href: R.carta(g.carta.slug ?? g.carta.id),
                    variante: Variante.quieto,
                  ),
                ],
              ),
            ),
            // Fase 9: il permesso delle notifiche si chiede qui (dopo la carta) o dal profilo, mai all'avvio.
            const InvitoNotifiche(),
          ],
        ],
      ),
    );
  }
}
