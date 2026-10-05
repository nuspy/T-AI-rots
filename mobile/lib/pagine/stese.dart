/// Le stese (`frontend/v2/pagine/stese.tsx`, montate da `app/(v2)/spreads/page.tsx` e `spreads/[id]/page.tsx`): una
/// forma che aiuta la domanda a dispiegarsi. L'elenco per categoria (le classiche, poi compatibilità e coppia divise per
/// stile) porta alla scheda; la scheda mostra lo schema sul tavolo, le posizioni, come leggerla, le altre stese dello
/// stesso tipo e i nove articoli del diario. Gli spazi pubblicitari del sito non ci sono.
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../catalogo/comuni.dart';
import '../componenti/bottoni.dart';
import '../componenti/diario.dart';
import '../componenti/miniatura_stesa.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lettura/tavolo.dart';
import '../lingua/lingua.dart';
import '../modelli/carta.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'blog.dart' show ArticoliSu;

/// L'ordine degli stili delle stese speciali.
const List<String> ordineStili = ['tradizionale', 'moderna', 'tendenza'];

/// Tutte le stese nella lingua dei contenuti (`P.stese(lingua)`).
final steseProvider = FutureProvider<List<Stesa>>((ref) {
  final lingua = ref.watch(linguaProvider.select(linguaContenuti));
  return ref.read(apiProvider).stese(lingua);
});

/// Il nome di una stesa nella lingua dell'interfaccia (`nomeSt` del sito).
String nomeStesa(Stesa s, String lingua) {
  if (s.lang == linguaContenuti(lingua)) return s.nome;
  if (lingua == 'it') return s.nome;
  return s.nomi?[lingua] ?? s.nomi?['en'] ?? s.nomeEn;
}

/// Il nome di una posizione nella lingua dell'interfaccia (`nomePosizione` del sito).
String nomePosizione(Stesa s, Posizione p, String lingua) {
  if (s.lang == linguaContenuti(lingua) || lingua == 'it') return p.nome;
  return p.nomi?[lingua] ?? p.nomi?['en'] ?? p.nomeEn;
}

/// Il nome e lo stile di un gruppo di stese speciali (`lettura.stili.<stile>`).
({String nome, String testo}) stileStesa(AppLocalizations t, String stile) {
  final m = switch (stile) {
    'tradizionale' => t.letturaStiliTradizionale,
    'moderna' => t.letturaStiliModerna,
    _ => t.letturaStiliTendenza,
  };
  return (nome: m['nome'] ?? stile, testo: m['testo'] ?? '');
}

/// `Tessera`: una stesa nell'elenco (la miniatura, il nome, le carte e il mazzo).
class TesseraStesa extends ConsumerWidget {
  /// La tessera della [stesa].
  const TesseraStesa({super.key, required this.stesa});

  /// La stesa.
  final Stesa stesa;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    return TesseraDifferenza(
      href: R.stesa(stesa.slug ?? stesa.id),
      // `.spread-mini`: larga al massimo 220 px, 100:64, sul fondo prugna, `margin-bottom: 1.2rem`.
      testa: Padding(
        padding: const EdgeInsets.only(bottom: 19.2),
        child: Align(
          alignment: AlignmentDirectional.centerStart,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 220),
            child: ColoredBox(color: Token.plumDeep, child: MiniaturaStesa(stesa: stesa)),
          ),
        ),
      ),
      titolo: nomeStesa(stesa, lingua),
      testi: [
        '${t.lettura_n_carte(stesa.posizioni.length)} · ${stesa.mazzo == 'maggiori' ? t.stese_maggiori : t.stese_completo}',
      ],
    );
  }
}

/// La pagina delle stese.
class Stese extends ConsumerWidget {
  /// L'elenco.
  const Stese({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final stese = ref.watch(steseProvider);
    final apertura = Sottotitolo(eyebrow: t.stese_eyebrow, titolo: t.stese_titolo, intro: t.stese_intro, compatta: true);
    if (stese.hasError && !stese.hasValue) {
      return Pagina(sezioni: [apertura, StatoFascia(errore: stese.error)]);
    }
    final tutte = stese.value ?? const <Stesa>[];
    List<Stesa> per(String c) => tutte.where((s) => s.categoria == c).toList();

    Widget gruppo(String c, String titolo, String testo) {
      final elenco = per(c);
      return Fascia(
        compatta: true,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TitoloSezione(titolo),
            IntroSezione(testo),
            if (c == 'standard')
              GrigliaDifferenze(
                children: [
                  for (final s in elenco) TesseraStesa(stesa: s),
                  TesseraDifferenza(
                    href: R.fisica,
                    simbolo: '✋',
                    titolo: t.stese_fisica,
                    testi: [t.stese_fisica_testo],
                  ),
                ],
              )
            else
              for (final stile in ordineStili)
                if (elenco.any((s) => s.stile == stile))
                  Padding(
                    padding: const EdgeInsets.only(top: 8.8),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Eyebrow('${stileStesa(t, stile).nome} · ${stileStesa(t, stile).testo}'),
                        GrigliaDifferenze(
                          children: [
                            for (final s in elenco.where((s) => s.stile == stile)) TesseraStesa(stesa: s),
                          ],
                        ),
                      ],
                    ),
                  ),
          ],
        ),
      );
    }

    return Pagina(
      sezioni: [
        apertura,
        gruppo('standard', t.stese_standard, t.stese_standard_testo),
        gruppo('compatibilita', t.stese_compat, t.stese_compat_testo),
        gruppo('coppia', t.stese_coppia, t.stese_coppia_testo),
      ],
    );
  }
}

/// La pagina di una stesa.
class DettaglioStesa extends ConsumerWidget {
  /// La stesa [id] (id o slug in qualunque lingua).
  const DettaglioStesa({super.key, required this.id, this.parametri = const {}});

  /// L'id o lo slug.
  final String id;

  /// I parametri della query (`page`, `per`: l'elenco degli articoli sulla stesa).
  final Map<String, String> parametri;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final stese = ref.watch(steseProvider);
    if (stese.hasError && !stese.hasValue) return Pagina(sezioni: [StatoFascia(errore: stese.error)]);
    final tutte = stese.value;
    if (tutte == null) return const Pagina(sezioni: [StatoFascia()]);
    final s = tutte.where((x) => x.id == id || x.slug == id || (x.slugs?.values.contains(id) ?? false)).firstOrNull;
    if (s == null) {
      return Pagina(
        sezioni: [
          Fascia(
            compatta: true,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                IntroSezione(t.stese_non_trovata_stesa, sopra: 0),
                const SizedBox(height: 16),
                Bottone(t.stese_stesa_tutte, href: R.stese, variante: Variante.quieto),
              ],
            ),
          ),
        ],
      );
    }
    String nomePos(int n) {
      final p = s.posizioni.where((x) => x.n == n).firstOrNull;
      return p == null ? '$n' : nomePosizione(s, p, lingua);
    }

    final altre = tutte.where((x) => x.categoria == s.categoria && x.id != s.id).take(4).toList();
    final w = larghezza(context);
    final posizioni = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TitoloPannelloLettura(t.stese_stesa_posizioni),
        for (final p in s.posizioni)
          VoceMemoria(
            occhiello: t.stese_stesa_posizione(p.n),
            titolo: nomePos(p.n),
            figli: [
              Paragrafo(p.significato, style: stileVoceMemoria()),
              if (p.domanda.isNotEmpty)
                // `p.small` in corsivo: dentro `.memory-entry` vale la sua misura (.88rem), senza margini.
                Paragrafo(p.domanda, style: stileVoceMemoria().copyWith(fontStyle: FontStyle.italic)),
            ],
          ),
      ],
    );

    return Pagina(
      sezioni: [
        AperturaCatalogo(
          eyebrow: '${t.stese_stesa_eyebrow} · ${t.lettura_n_carte(s.posizioni.length)}',
          titolo: nomeStesa(s, lingua),
          intro: s.descrizione,
          sotto: Padding(
            padding: EdgeInsets.only(top: w.telefono ? 8 : 0),
            child: FilaBottoni(
              children: [
                Bottone(
                  t.stese_stesa_cta,
                  href: '${R.leggi}?spread=${Uri.encodeQueryComponent(s.id)}&source=spread',
                  variante: Variante.ottone,
                ),
                Bottone(t.stese_stesa_tutte, href: R.stese, variante: Variante.quieto),
              ],
            ),
          ),
        ),
        Fascia(
          compatta: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              LayoutLettura(
                scuro: Semantics(
                  label: t.stese_stesa_diagramma,
                  image: true,
                  child: Tavolo(stesa: s, posate: const []),
                ),
                chiaro: posizioni,
              ),
              Padding(
                padding: const EdgeInsets.only(top: 11.2),
                child: BloccoProsa([
                  if (s.regole.isNotEmpty) ...[
                    TitoloProsa(t.stese_stesa_come),
                    ElencoProsa([for (final r in s.regole) (null, r)]),
                  ],
                  if (s.coppie.isNotEmpty) ...[
                    TitoloProsa(t.stese_stesa_coppie),
                    ElencoProsa([
                      for (final c in s.coppie)
                        if (c.length >= 3)
                          ('${nomePos((c[0]! as num).toInt())} ↔ ${nomePos((c[1]! as num).toInt())}.', '${c[2]}'),
                    ]),
                  ],
                  if (s.origine.isNotEmpty) ...[TitoloProsa(t.stese_stesa_origine), ParagrafoProsa(s.origine)],
                ]),
              ),
            ],
          ),
        ),
        if (altre.isNotEmpty)
          Fascia(
            compatta: true,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Eyebrow(t.stese_stesa_altre),
                GrigliaDifferenze(children: [for (final x in altre) TesseraStesa(stesa: x)]),
              ],
            ),
          ),
        // Prima gli articoli che parlano di questa stesa, poi gli ultimi; sotto, l'elenco completo a pagine.
        DiarioNove(contesto: 'stesa=${Uri.encodeQueryComponent(s.id)}', sceltiPrima: true),
        ArticoliSu(tipo: 'stesa', id: s.id, nome: nomeStesa(s, lingua), base: R.stesa(id), parametri: parametri),
      ],
    );
  }
}
