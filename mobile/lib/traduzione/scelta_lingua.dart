/// v9.5: la scelta della lingua di lettura (`lingua_contenuti.dart`): al primo avvio in un dialogo che non si chiude
/// senza una scelta ([DialogoLinguaContenuti]), poi dal piè di pagina ([VoceLinguaContenuti]). Tutte le lingue di ML
/// Kit, con la ricerca; in cima quella dell'interfaccia e l'inglese. Scegliendo una lingua diversa dall'inglese se ne
/// scarica subito il modello (circa 30 MB), così la prima pagina è già tradotta; se non riesce, la scelta resta e si
/// riprova quando si apre un contenuto.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/modale.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../tema/tema.dart';
import 'lingua_contenuti.dart';
import 'motore.dart';

/// Le lingue nell'ordine del dialogo: [prima] (quella dell'interfaccia) e l'inglese in cima, poi le altre per nome.
List<String> ordineLingue(String prima) {
  final tutte = lingueMlKit;
  final altre = [
    for (final l in tutte)
      if (l != prima && l != 'en') l,
  ]..sort((a, b) => nomeLingua(a).toLowerCase().compareTo(nomeLingua(b).toLowerCase()));
  return [if (tutte.contains(prima)) prima, if (prima != 'en') 'en', ...altre];
}

/// Il contenuto della scelta: testo, ricerca, elenco, «Continua».
class SceltaLinguaContenuti extends ConsumerStatefulWidget {
  /// La scelta; [alFatto] quando si è scelto (e scaricato, se serviva).
  const SceltaLinguaContenuti({super.key, required this.alFatto});

  /// Scelta fatta.
  final VoidCallback alFatto;

  @override
  ConsumerState<SceltaLinguaContenuti> createState() => _SceltaLinguaContenutiState();
}

class _SceltaLinguaContenutiState extends ConsumerState<SceltaLinguaContenuti> {
  final TextEditingController _cerca = TextEditingController();
  late String _scelta;
  bool _scarico = false;
  bool _errore = false;

  @override
  void initState() {
    super.initState();
    final interfaccia = ref.read(linguaProvider).split(RegExp('[-_]')).first;
    _scelta = ref.read(linguaContenutiProvider) ?? (lingueMlKit.contains(interfaccia) ? interfaccia : 'en');
    _cerca.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _cerca.dispose();
    super.dispose();
  }

  /// Salva la scelta e chiude. Al primo avvio salvarla chiude il dialogo: per questo si salva solo alla fine.
  void _fatto() {
    ref.read(linguaContenutiProvider.notifier).scegli(_scelta);
    widget.alFatto();
  }

  Future<void> _continua() async {
    if (_scelta == 'en') {
      _fatto();
      return;
    }
    setState(() {
      _scarico = true;
      _errore = false;
    });
    var riuscito = false;
    try {
      riuscito = await ref.read(motoreTraduzioneProvider).scarica(_scelta);
    } on Object {
      riuscito = false;
    }
    if (!mounted) return;
    if (riuscito) {
      _fatto();
    } else {
      setState(() {
        _scarico = false;
        _errore = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final interfaccia = ref.watch(linguaProvider).split(RegExp('[-_]')).first;
    final filtro = _cerca.text.trim().toLowerCase();
    final lingue = [
      for (final l in ordineLingue(interfaccia))
        if (filtro.isEmpty || nomeLingua(l).toLowerCase().contains(filtro) || l.startsWith(filtro)) l,
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Paragrafo(t.app_lingua_testo, style: Stile.sans(15.2, colore: Token.inkSoft, altezza: 1.6)),
        const SizedBox(height: 12.8),
        CampoTesto(controllore: _cerca, segnaposto: t.app_lingua_cerca, semantica: t.app_lingua_cerca, margineSotto: 8),
        for (final l in lingue)
          Premibile(
            alTocco: _scarico ? null : () => setState(() => _scelta = l),
            selezionato: l == _scelta,
            etichetta: nomeLingua(l),
            costruisci: (context, premuto) => Container(
              constraints: const BoxConstraints(minHeight: 48),
              padding: const EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: l == _scelta ? const Color(0x1A19706F) : (premuto ? Token.paper : null),
                border: const Border(bottom: BorderSide(color: Token.line)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      nomeLingua(l),
                      style: Stile.sans(16, colore: Token.ink, peso: l == _scelta ? FontWeight.w700 : FontWeight.w400),
                    ),
                  ),
                  if (l == _scelta)
                    Text(
                      '✓',
                      style: Stile.sans(16, colore: Token.verdigris, peso: FontWeight.w700),
                    ),
                ],
              ),
            ),
          ),
        const SizedBox(height: 16),
        if (_scarico)
          Row(
            children: [
              const Puntini(colore: Token.brass),
              const SizedBox(width: 9.6),
              Expanded(child: Text(t.app_lingua_scarico(nomeLingua(_scelta)), style: Stile.sans(14.4))),
            ],
          )
        else ...[
          if (_errore) Errore(t.app_lingua_errore, sopra: 0),
          if (_errore) const SizedBox(height: 12),
          FilaBottoni(
            children: [
              Bottone(
                t.app_lingua_continua,
                variante: Variante.ottone,
                an: 'lingua_contenuti',
                anProprieta: {'lingua': _scelta},
                // Dopo un errore «Continua» tiene la scelta: il modello si riscarica alla prima pagina tradotta.
                alTocco: _errore ? _fatto : () => unawaited(_continua()),
              ),
            ],
          ),
        ],
      ],
    );
  }
}

/// Il dialogo del primo avvio (sopra l'app, senza ✕: si chiude scegliendo).
class DialogoLinguaContenuti extends StatelessWidget {
  /// Il dialogo.
  const DialogoLinguaContenuti({super.key});

  @override
  Widget build(BuildContext context) => FinestraModale(
    titolo: context.t.app_lingua_titolo,
    // La scelta salvata chiude il dialogo: il primo avvio non la chiede più.
    child: SceltaLinguaContenuti(alFatto: () {}),
  );
}

/// La voce del piè di pagina: «Lingua di lettura: Magyar · Cambia» (solo dove il telefono sa tradurre).
class VoceLinguaContenuti extends ConsumerWidget {
  /// La voce, col [colore] del piè di pagina.
  const VoceLinguaContenuti({super.key, required this.colore});

  /// Il colore del testo.
  final Color colore;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (!ref.watch(motoreTraduzioneProvider).disponibile) return const SizedBox.shrink();
    final t = context.t;
    final lingua = ref.watch(linguaContenutiProvider) ?? 'en';
    return Premibile(
      collegamento: true,
      etichetta: '${t.app_lingua_voce(nomeLingua(lingua))} · ${t.app_lingua_cambia}',
      alTocco: () => unawaited(
        apriModale<void>(
          context,
          titolo: t.app_lingua_titolo,
          costruisci: (dialogo) => SceltaLinguaContenuti(alFatto: () => Navigator.of(dialogo).pop()),
        ),
      ),
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 44),
        child: Align(
          alignment: AlignmentDirectional.centerStart,
          widthFactor: 1,
          heightFactor: 1,
          child: TestoSottolineato(
            '${t.app_lingua_voce(nomeLingua(lingua))} · ${t.app_lingua_cambia}',
            stile: Stile.sans(14.4, colore: colore),
            colore: colore,
          ),
        ),
      ),
    );
  }
}
