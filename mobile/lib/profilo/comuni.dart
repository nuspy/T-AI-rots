/// I pezzi comuni delle pagine dell'account (profilo, privacy, eliminazione), come il CSS del sito:
///
/// - [GrigliaProfilo]: `.profile-grid` (due colonne oltre 760 px, una sotto; `.wide` le prende tutte e due);
/// - [Sezione]: `section.panel` con il titolo `h2`;
/// - [TestoPiccolo]: `p.small` (anche `.muted`), coi margini del paragrafo;
/// - [RigaFlessibile]: `.button-row` con i campi che crescono (`flex: 1 1 12rem`) e vanno a capo come nel browser;
/// - [SceltaSemplice]: un `<select>` senza etichetta visibile (`.sr-only`);
/// - [CampoData]: `<input type="date">`;
/// - [ElencoPuntato]: `ul`/`ol` con i segni del browser;
/// - [AzioneAccount]: `useAzione()` del sito (in corso, errore, solo con una sessione);
/// - la condivisione di un file (l'archivio dei dati, un PDF, il bigliettino) col foglio del telefono.
library;

import 'dart:async';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart' show DateFormat;
import 'package:material_ui/material_ui.dart' show showDatePicker;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../rotte/ancore.dart';
import '../tema/tema.dart';

/* ---- servizi del telefono (finti nei test) ---------------------------------------------------------------------- */

/// Il foglio di condivisione del telefono.
final condivisioneProvider = Provider<Future<void> Function(ShareParams parametri)>(
  (ref) => (parametri) async {
    await SharePlus.instance.share(parametri);
  },
);

/// La scelta di un'immagine dalla galleria: i byte e il tipo, o `null` se si annulla.
final sceltaImmagineProvider = Provider<Future<({Uint8List byte, String tipo})?> Function()>(
  (ref) => () async {
    final file = await ImagePicker().pickImage(source: ImageSource.gallery, maxWidth: 2048, maxHeight: 2048);
    if (file == null) return null;
    final nome = file.name.toLowerCase();
    final tipo =
        file.mimeType ??
        (nome.endsWith('.png')
            ? 'image/png'
            : nome.endsWith('.webp')
            ? 'image/webp'
            : 'image/jpeg');
    return (byte: await file.readAsBytes(), tipo: tipo);
  },
);

/// Il punto da cui si apre il foglio di condivisione (l'iPad lo vuole: un riquadro accanto al bottone).
Rect? origineCondivisione(BuildContext context) {
  final box = context.findRenderObject();
  if (box is! RenderBox || !box.hasSize) return null;
  return box.localToGlobal(Offset.zero) & box.size;
}

/// Salva [byte] in un file temporaneo chiamato [nome] e lo passa al foglio di condivisione del telefono (dove si
/// sceglie se salvarlo o a chi mandarlo): l'equivalente del download del sito.
Future<void> condividiFile(
  WidgetRef ref,
  BuildContext context, {
  required Uint8List byte,
  required String nome,
  required String tipo,
  String? testo,
}) async {
  final origine = origineCondivisione(context);
  final cartella = await getTemporaryDirectory();
  final file = File('${cartella.path}/${nome.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_')}');
  await file.writeAsBytes(byte, flush: true);
  await ref.read(condivisioneProvider)(
    ShareParams(
      files: [XFile(file.path, mimeType: tipo, name: nome)],
      text: testo,
      sharePositionOrigin: origine,
    ),
  );
}

/* ---- le azioni -------------------------------------------------------------------------------------------------- */

/// `useAzione()` del sito: esegue un'azione che modifica (solo con una sessione) e ne tiene lo stato.
mixin AzioneAccount<W extends ConsumerStatefulWidget> on ConsumerState<W> {
  /// Un'azione in corso.
  bool inCorso = false;

  /// L'errore dell'ultima azione.
  String? errore;

  /// Esegue [azione]; `null` se non c'è una sessione o se non è riuscita (l'errore resta in [errore]).
  Future<R?> esegui<R>(Future<R> Function(Api api) azione) async {
    if (!ref.read(sessioneProvider).autenticata) return null;
    final t = context.t;
    setState(() {
      inCorso = true;
      errore = null;
    });
    try {
      return await azione(ref.read(apiProvider));
    } on ErroreApi catch (e) {
      if (mounted) setState(() => errore = e.messaggio(t));
      return null;
    } finally {
      if (mounted) setState(() => inCorso = false);
    }
  }
}

/* ---- testi ------------------------------------------------------------------------------------------------------- */

/// `p.small` (`.84rem`, inchiostro; `.muted` tenue), con il margine del paragrafo sotto (1em) e, se serve, sopra.
class TestoPiccolo extends StatelessWidget {
  /// Un paragrafo piccolo.
  const TestoPiccolo(this.testo, {super.key, this.tenue = false, this.sotto = 13.44, this.sopra = 0, this.figlio});

  /// Il testo.
  final String testo;

  /// `.muted`.
  final bool tenue;

  /// Il margine sotto.
  final double sotto;

  /// Il margine sopra.
  final double sopra;

  /// Un collegamento in fondo al paragrafo (`<LinkV2 className="inline">`).
  final Widget? figlio;

  @override
  Widget build(BuildContext context) {
    final stile = Stile.sans(13.44, colore: tenue ? Token.inkSoft : Token.ink, altezza: 1.6);
    return Padding(
      padding: EdgeInsets.only(top: sopra, bottom: sotto),
      child: figlio == null
          ? Paragrafo(testo, style: stile)
          : Wrap(
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text('$testo ', style: stile),
                figlio!,
              ],
            ),
    );
  }
}

/// `section.panel` con il titolo (`h2`, 1.35rem serif).
class Sezione extends StatelessWidget {
  /// Una sezione.
  const Sezione({super.key, required this.titolo, required this.children, this.chiave, this.id});

  /// Il titolo.
  final String titolo;

  /// Il contenuto.
  final List<Widget> children;

  /// Una chiave per il pannello.
  final GlobalKey? chiave;

  /// L'`id` della sezione: `/profile#privacy` la porta in vista ([Ancora]).
  final String? id;

  @override
  Widget build(BuildContext context) {
    final pannello = Pannello(
      key: chiave,
      titolo: titolo,
      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, mainAxisSize: MainAxisSize.min, children: children),
    );
    return id == null ? pannello : Ancora(id: id!, child: pannello);
  }
}

/// Una cella di [GrigliaProfilo]: larga (`.wide`) o in una colonna.
typedef CellaProfilo = ({Widget widget, bool larga});

/// `.profile-grid`: due colonne (`gap: 1.2rem`, righe a `.5rem`, `align-items: start`) oltre 760 px, una sotto. Una
/// cella `.wide` va su una riga sua, come il posizionamento automatico della griglia (che lascia il buco a destra).
class GrigliaProfilo extends StatelessWidget {
  /// La griglia.
  const GrigliaProfilo({super.key, required this.celle});

  /// Le celle, in ordine.
  final List<CellaProfilo> celle;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    const righe = 8.0;
    if (w.telefono) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (var i = 0; i < celle.length; i++) ...[if (i > 0) const SizedBox(height: righe), celle[i].widget],
        ],
      );
    }
    final file = <Widget>[];
    Widget? sospesa;
    void chiudi() {
      if (sospesa == null) return;
      file.add(
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(child: sospesa!),
            const SizedBox(width: 19.2),
            const Expanded(child: SizedBox()),
          ],
        ),
      );
      sospesa = null;
    }

    for (final c in celle) {
      if (c.larga) {
        chiudi();
        file.add(c.widget);
      } else if (sospesa == null) {
        sospesa = c.widget;
      } else {
        file.add(
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: sospesa!),
              const SizedBox(width: 19.2),
              Expanded(child: c.widget),
            ],
          ),
        );
        sospesa = null;
      }
    }
    chiudi();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < file.length; i++) ...[if (i > 0) const SizedBox(height: righe), file[i]],
      ],
    );
  }
}

/// La larghezza di un `.button.button-small` con il [testo] (per sapere se sta nella riga).
double larghezzaBottonePiccolo(BuildContext context, String testo) {
  final p = TextPainter(
    text: TextSpan(text: testo, style: Stile.bottone(px: 12.8)),
    textDirection: TextDirection.ltr,
    textScaler: MediaQuery.textScalerOf(context),
    maxLines: 1,
  )..layout();
  final w = p.width + 12.8 * 2 + 2;
  p.dispose();
  return w.ceilToDouble();
}

/// Un pezzo di [RigaFlessibile]: il widget, la base (`flex-basis`) e se cresce (`flex-grow`).
typedef PezzoRiga = ({Widget widget, double base, bool cresce});

/// `.button-row` (`display: flex; flex-wrap: wrap; gap: .6rem; align-items: end`): i pezzi stanno in riga finché la
/// loro base ci sta, poi vanno a capo; in ogni riga lo spazio che avanza va a chi cresce, e un pezzo più largo della
/// riga si stringe a tutta riga (`flex-shrink`).
class RigaFlessibile extends StatelessWidget {
  /// Una riga.
  const RigaFlessibile({super.key, required this.pezzi, this.sopra = 0});

  /// I pezzi.
  final List<PezzoRiga> pezzi;

  /// Il margine sopra.
  final double sopra;

  @override
  Widget build(BuildContext context) {
    const gap = 9.6;
    return Padding(
      padding: EdgeInsets.only(top: sopra),
      child: LayoutBuilder(
        builder: (context, vincoli) {
          final w = vincoli.maxWidth;
          final linee = <List<PezzoRiga>>[];
          var corrente = <PezzoRiga>[];
          var somma = 0.0;
          for (final p in pezzi) {
            final serve = (corrente.isEmpty ? 0 : gap) + p.base;
            if (corrente.isNotEmpty && somma + serve > w) {
              linee.add(corrente);
              corrente = [];
              somma = 0;
            }
            corrente.add(p);
            somma += (corrente.length == 1 ? 0 : gap) + p.base;
          }
          if (corrente.isNotEmpty) linee.add(corrente);
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (var i = 0; i < linee.length; i++) ...[
                if (i > 0) const SizedBox(height: gap),
                Builder(
                  builder: (context) {
                    final l = linee[i];
                    final basi = l.fold(0.0, (s, p) => s + p.base) + gap * (l.length - 1);
                    final crescono = l.where((p) => p.cresce).length;
                    final avanzo = w - basi;
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        for (var j = 0; j < l.length; j++) ...[
                          if (j > 0) const SizedBox(width: gap),
                          SizedBox(
                            width: math.max(
                              0,
                              math.min(w, l[j].base + (avanzo > 0 && l[j].cresce ? avanzo / crescono : 0)),
                            ),
                            child: l[j].widget,
                          ),
                        ],
                      ],
                    );
                  },
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}

/* ---- campi ------------------------------------------------------------------------------------------------------- */

/// Il campo bianco del sito (`.field select`), senza etichetta visibile: il valore e «▾»; al tocco l'elenco.
class SceltaSemplice<T> extends StatelessWidget {
  /// Una scelta.
  const SceltaSemplice({
    super.key,
    required this.etichetta,
    required this.voci,
    required this.valore,
    required this.alCambio,
    this.attiva = true,
  });

  /// L'etichetta per i lettori di schermo (e il titolo del dialogo).
  final String etichetta;

  /// Le voci (valore, testo).
  final List<(T, String)> voci;

  /// Il valore scelto.
  final T valore;

  /// Una scelta fatta.
  final ValueChanged<T> alCambio;

  /// Attiva.
  final bool attiva;

  Future<void> _apri(BuildContext context) async {
    final scelta = await apriModale<(T,)>(
      context,
      titolo: etichetta,
      costruisci: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final (v, testo) in voci)
            Premibile(
              alTocco: () => Navigator.of(context).pop((v,)),
              selezionato: v == valore,
              costruisci: (context, premuto) => Container(
                constraints: const BoxConstraints(minHeight: 48),
                alignment: AlignmentDirectional.centerStart,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: v == valore ? Token.plum : (premuto ? Token.mist : null),
                  border: const Border(bottom: BorderSide(color: Token.line)),
                ),
                child: Text(testo, style: Stile.sans(16, colore: v == valore ? const Color(0xFFFFF7E8) : Token.ink)),
              ),
            ),
        ],
      ),
    );
    if (scelta != null) alCambio(scelta.$1);
  }

  @override
  Widget build(BuildContext context) {
    final testo = voci.where((v) => v.$1 == valore).map((v) => v.$2).firstOrNull ?? '';
    return Opacity(
      opacity: attiva ? 1 : .55,
      child: Premibile(
        alTocco: attiva ? () => unawaited(_apri(context)) : null,
        etichetta: '$etichetta: $testo',
        costruisci: (context, premuto) => Container(
          constraints: const BoxConstraints(minHeight: Token.altezzaBottone),
          padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 11.2),
          decoration: BoxDecoration(
            color: premuto ? const Color(0xFFF7F3EC) : const Color(0xFFFFFFFF),
            border: Border.all(color: Token.line),
          ),
          child: Row(
            children: [
              Expanded(
                child: Text(testo, style: Stile.sans(16, colore: Token.ink, altezza: 1.5)),
              ),
              Text('▾', style: Stile.sans(12, colore: Token.inkSoft)),
            ],
          ),
        ),
      ),
    );
  }
}

/// `<input type="date">` dentro `.field`: la data nel formato della lingua; al tocco il calendario del sistema.
class CampoData extends ConsumerWidget {
  /// Un campo data.
  const CampoData({super.key, required this.etichetta, required this.valore, required this.alCambio});

  /// L'etichetta sopra.
  final String etichetta;

  /// La data ISO (`yyyy-mm-dd`), o vuoto.
  final String valore;

  /// La data scelta (ISO).
  final ValueChanged<String> alCambio;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lingua = ref.watch(linguaProvider);
    final d = DateTime.tryParse(valore);
    final testo = d == null ? '' : DateFormat('dd/MM/yyyy', localeIntl(lingua)).format(d);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 5.6),
          child: Text(etichetta, style: stileEtichettaCampo()),
        ),
        Premibile(
          etichetta: '$etichetta: $testo',
          alTocco: () async {
            final scelta = await showDatePicker(
              context: context,
              initialDate: d ?? DateTime(1990),
              firstDate: DateTime(1900),
              lastDate: DateTime.now(),
            );
            if (scelta != null) alCambio(DateFormat('yyyy-MM-dd').format(scelta));
          },
          costruisci: (context, premuto) => Container(
            constraints: const BoxConstraints(minHeight: Token.altezzaBottone),
            padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 11.2),
            decoration: BoxDecoration(
              color: premuto ? const Color(0xFFF7F3EC) : const Color(0xFFFFFFFF),
              border: Border.all(color: Token.line),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    testo.isEmpty ? 'dd/mm/yyyy' : testo,
                    style: Stile.sans(16, colore: testo.isEmpty ? Colori.segnaposto : Token.ink, altezza: 1.5),
                  ),
                ),
                Text('▾', style: Stile.sans(12, colore: Token.inkSoft)),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// Un elenco col segno del browser (`ul`: il pallino; `ol`: il numero), rientrato di 1.2rem.
class ElencoPuntato extends StatelessWidget {
  /// Un elenco.
  const ElencoPuntato({super.key, required this.voci, this.numerato = false, this.spazio = 6.4, this.stile});

  /// Le voci.
  final List<Widget> voci;

  /// `ol`.
  final bool numerato;

  /// Lo spazio fra una voce e l'altra (`li + li { margin-top }`).
  final double spazio;

  /// Lo stile del segno.
  final TextStyle? stile;

  @override
  Widget build(BuildContext context) {
    final s = stile ?? Stile.sans(13.44, colore: Token.ink, altezza: 1.6);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < voci.length; i++)
          Padding(
            padding: EdgeInsets.only(top: i == 0 ? 0 : spazio),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 19.2,
                  child: Text(numerato ? '${i + 1}.' : '•', style: s, textAlign: TextAlign.right),
                ),
                const SizedBox(width: 6),
                Expanded(child: voci[i]),
              ],
            ),
          ),
      ],
    );
  }
}

/// Un testo con una parte in grassetto davanti (`<b>…</b> resto`).
class TestoConGrassetto extends StatelessWidget {
  /// Il testo.
  const TestoConGrassetto({super.key, required this.grassetto, required this.resto, this.stile});

  /// La parte in grassetto.
  final String grassetto;

  /// Il resto.
  final String resto;

  /// Lo stile di base.
  final TextStyle? stile;

  @override
  Widget build(BuildContext context) {
    final s = stile ?? Stile.sans(13.44, colore: Token.ink, altezza: 1.6);
    return Text.rich(
      TextSpan(
        style: s,
        children: [
          TextSpan(
            text: grassetto,
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
          TextSpan(text: resto),
        ],
      ),
    );
  }
}
