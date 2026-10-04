/// «Stampa in PDF» di una lettura (`frontend/v2/componenti/stampa.tsx` e il foglio `@media print` di v2.css): il sito
/// apre la stampa del browser, che offre «Salva come PDF»; l'app compone lo stesso foglio in PDF (`pdf`) e apre la
/// finestra di stampa e salvataggio del sistema (`printing`).
///
/// Sul foglio, come nella stampa del sito (senza testata, piede, barra dell'oracolo e bottoni): la stesa e la data, la
/// domanda, il tavolo con le carte sul panno prugna, il ritorno sulla lettura e il quadro, le persone (nelle letture
/// speciali), le carte una per una con la loro spiegazione, l'interpretazione, l'avvertenza e la nota di copyright.
/// Margini di 14 mm, A4. I caratteri sono quelli dell'app (Libre Baskerville e DM Sans).
library;

import 'dart:typed_data';
import 'dart:ui' show Locale;

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

import '../componenti/carta.dart';
import '../componenti/formati.dart';
import '../l10n/testi.dart';
import '../modelli/account.dart';
import 'immagine_condivisione.dart';

/// I caratteri del foglio.
class CaratteriStampa {
  /// I caratteri.
  const CaratteriStampa({
    required this.serif,
    required this.serifCorsivo,
    required this.serifGrassetto,
    required this.sans,
    required this.sansGrassetto,
  });

  /// Libre Baskerville.
  final pw.Font serif;

  /// Libre Baskerville corsivo.
  final pw.Font serifCorsivo;

  /// Libre Baskerville grassetto.
  final pw.Font serifGrassetto;

  /// DM Sans.
  final pw.Font sans;

  /// DM Sans grassetto.
  final pw.Font sansGrassetto;

  /// Dagli asset dell'app.
  static Future<CaratteriStampa> carica() async {
    Future<pw.Font> f(String nome) async => pw.Font.ttf(await rootBundle.load('assets/fonts/$nome.ttf'));
    return CaratteriStampa(
      serif: await f('LibreBaskerville-Regular'),
      serifCorsivo: await f('LibreBaskerville-Italic'),
      serifGrassetto: await f('LibreBaskerville-Bold'),
      sans: await f('DMSans-Regular'),
      sansGrassetto: await f('DMSans-Bold'),
    );
  }
}

const PdfColor _inchiostro = PdfColor.fromInt(0xFF1D1320);
const PdfColor _tenue = PdfColor.fromInt(0xFF55455D);
const PdfColor _verderame = PdfColor.fromInt(0xFF19706F);
const PdfColor _prugna = PdfColor.fromInt(0xFF3C1846);
const PdfColor _grigio = PdfColor.fromInt(0xFF555555);
const PdfColor _riga = PdfColor.fromInt(0xFFDDDDDD);

/// I testi in linea del Markdown minimo (`**grassetto**`, `*corsivo*`).
List<pw.InlineSpan> _inline(String testo, CaratteriStampa c, pw.TextStyle base) {
  final spans = <pw.InlineSpan>[];
  final re = RegExp(r'(\*\*[^*]+\*\*|\*[^*]+\*)');
  var da = 0;
  for (final m in re.allMatches(testo)) {
    if (m.start > da) spans.add(pw.TextSpan(text: testo.substring(da, m.start), style: base));
    final p = m[0]!;
    if (p.startsWith('**')) {
      spans.add(
        pw.TextSpan(
          text: p.substring(2, p.length - 2),
          style: base.copyWith(font: c.serifGrassetto),
        ),
      );
    } else if (p.length > 2) {
      spans.add(
        pw.TextSpan(
          text: p.substring(1, p.length - 1),
          style: base.copyWith(font: c.serifCorsivo),
        ),
      );
    } else {
      spans.add(pw.TextSpan(text: p, style: base));
    }
    da = m.end;
  }
  if (da < testo.length) spans.add(pw.TextSpan(text: testo.substring(da), style: base));
  return spans;
}

/// Il responso in Markdown minimo (`lib/markdown.tsx`), sul foglio.
List<pw.Widget> _markdown(String testo, CaratteriStampa c) {
  final corpo = pw.TextStyle(font: c.serif, fontSize: 10.5, lineSpacing: 3, color: _inchiostro);
  final titolo = pw.TextStyle(font: c.serif, fontSize: 12.5, color: _prugna);
  final blocchi = <pw.Widget>[];
  pw.Widget p(String t) => pw.Padding(
    padding: const pw.EdgeInsets.only(bottom: 7),
    child: pw.RichText(text: pw.TextSpan(children: _inline(t, c, corpo))),
  );
  for (final b in testo.split(RegExp(r'\n{2,}'))) {
    final righe = b.trim();
    if (righe.isEmpty) continue;
    if (righe.startsWith('## ') || righe.startsWith('# ')) {
      final parti = righe.split('\n');
      blocchi.add(
        pw.Padding(
          padding: const pw.EdgeInsets.only(top: 9, bottom: 4),
          child: pw.Text(parti.first.replaceFirst(RegExp(r'^#+ '), ''), style: titolo),
        ),
      );
      if (righe.startsWith('## ') && parti.length > 1) blocchi.add(p(parti.skip(1).join(' ')));
    } else if (RegExp(r'^[-*] ').hasMatch(righe)) {
      for (final r in righe.split('\n')) {
        blocchi.add(
          pw.Padding(
            padding: const pw.EdgeInsets.only(left: 12, bottom: 3),
            child: pw.RichText(
              text: pw.TextSpan(
                children: [
                  pw.TextSpan(text: '•  ', style: corpo),
                  ..._inline(r.replaceFirst(RegExp(r'^[-*] '), ''), c, corpo),
                ],
              ),
            ),
          ),
        );
      }
    } else {
      blocchi.add(p(righe.replaceAll('\n', ' ')));
    }
  }
  return blocchi;
}

/// Il PDF della lettura [lt]: [t] i testi dell'interfaccia, [tavolo] l'immagine PNG del tavolo (se c'è).
Future<Uint8List> costruisciPdf(
  Lettura lt, {
  required AppLocalizations t,
  required String interfaccia,
  required CaratteriStampa caratteri,
  Uint8List? tavolo,
}) async {
  final c = caratteri;
  final ll = linguaLettura(lt.lang, interfaccia);
  final stesa = lt.stesaDati;
  final doc = pw.Document(title: lt.question, author: 'TAROTS chat', creator: 'TAROTS chat');
  final piccolo = pw.TextStyle(font: c.sans, fontSize: 9.5, color: _tenue, lineSpacing: 2);
  final occhiello = pw.TextStyle(font: c.sansGrassetto, fontSize: 8, color: _verderame, letterSpacing: .8);
  final etichetta = [
    if (stesa != null) nomeStesaIn(stesa, ll) else nomeStesaDaNomi(lt.stesa, lt.stesaNomi, ll),
    t.storia_dettaglio_quando(dataLunga(lt.createdAt, interfaccia)),
  ].join(' · ');
  final rivelate = [...lt.cards.where((x) => x.rivelata && x.carta != null)]
    ..sort((a, b) => a.posizione.compareTo(b.posizione));

  doc.addPage(
    pw.MultiPage(
      pageFormat: PdfPageFormat.a4.copyWith(
        marginLeft: 14 * PdfPageFormat.mm,
        marginRight: 14 * PdfPageFormat.mm,
        marginTop: 14 * PdfPageFormat.mm,
        marginBottom: 14 * PdfPageFormat.mm,
      ),
      theme: pw.ThemeData.withFont(base: c.sans, bold: c.sansGrassetto, italic: c.serifCorsivo),
      build: (context) => [
        pw.Text(etichetta.toUpperCase(), style: occhiello),
        pw.SizedBox(height: 4),
        pw.Text(
          '«${lt.question}»',
          style: pw.TextStyle(font: c.serifCorsivo, fontSize: 17, color: _inchiostro, lineSpacing: 4),
        ),
        pw.SizedBox(height: 12),
        if (tavolo != null) ...[
          pw.Container(
            color: _prugna,
            padding: const pw.EdgeInsets.all(4 * PdfPageFormat.mm),
            child: pw.Center(child: pw.Image(pw.MemoryImage(tavolo), height: 85 * PdfPageFormat.mm)),
          ),
          pw.SizedBox(height: 6 * PdfPageFormat.mm),
        ],
        pw.Text(t.storia_esito.toUpperCase(), style: occhiello),
        pw.SizedBox(height: 3),
        pw.Text(t.storia_esito_testo, style: piccolo),
        if (lt.feedback != null) ...[
          pw.SizedBox(height: 3),
          pw.Text(t.storiaEsiti[lt.feedback] ?? lt.feedback!, style: piccolo.copyWith(font: c.sansGrassetto)),
        ],
        if (lt.contextSummary != null && lt.contextSummary!.isNotEmpty) ...[
          pw.SizedBox(height: 8),
          pw.Text(t.storia_il_quadro.toUpperCase(), style: occhiello),
          pw.SizedBox(height: 3),
          pw.Text(lt.contextSummary!, style: pw.TextStyle(font: c.serif, fontSize: 10.5, lineSpacing: 3)),
        ],
        if (lt.persone != null) ...[
          pw.SizedBox(height: 8),
          pw.Text(t.storia_le_persone, style: pw.TextStyle(font: c.serif, fontSize: 13)),
          pw.SizedBox(height: 3),
          pw.Text('${t.storia_tu} — ${dataLunga(lt.persone!.tu.nascita, interfaccia)}', style: piccolo),
          pw.Text(
            '${[lt.persone!.partner.nome, lt.persone!.partner.cognome].whereType<String>().join(' ')} — '
            '${dataLunga(lt.persone!.partner.nascita, interfaccia)}',
            style: piccolo,
          ),
        ],
        if (rivelate.isNotEmpty) pw.SizedBox(height: 6 * PdfPageFormat.mm),
        for (final x in rivelate)
          pw.Container(
            margin: const pw.EdgeInsets.only(bottom: 5 * PdfPageFormat.mm),
            padding: const pw.EdgeInsets.only(bottom: 3 * PdfPageFormat.mm),
            decoration: const pw.BoxDecoration(
              border: pw.Border(bottom: pw.BorderSide(color: _riga)),
            ),
            child: pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.start,
              children: [
                pw.Text(
                  '${x.posizione}. '
                  '${stesa?.posizioni.where((q) => q.n == x.posizione).map((q) => nomePosizioneIn(q, ll)).firstOrNull ?? ''}'
                  ' — ${nomeCartaIn(x.carta!, ll)}${(x.rovescio ?? false) ? ' (${t.lettura_rovesciata})' : ''}',
                  style: pw.TextStyle(font: c.serifGrassetto, fontSize: 12),
                ),
                if (x.interpretazione != null && x.interpretazione!.isNotEmpty) ...[
                  pw.SizedBox(height: 1.5 * PdfPageFormat.mm),
                  pw.Text(x.interpretazione!, style: pw.TextStyle(font: c.sans, fontSize: 10.5, lineSpacing: 2.5)),
                ],
              ],
            ),
          ),
        if (lt.synthesis != null && lt.synthesis!.isNotEmpty) ...[
          pw.SizedBox(height: 4 * PdfPageFormat.mm),
          pw.Text(t.storia_l_interpretazione, style: pw.TextStyle(font: c.serif, fontSize: 18)),
          pw.SizedBox(height: 8),
          ..._markdown(lt.synthesis!, c),
          pw.Container(
            margin: const pw.EdgeInsets.only(top: 8),
            padding: const pw.EdgeInsets.only(top: 6),
            decoration: const pw.BoxDecoration(
              border: pw.Border(top: pw.BorderSide(color: _riga)),
            ),
            child: pw.Text(lt.disclaimer, style: piccolo),
          ),
        ],
        pw.SizedBox(height: 8 * PdfPageFormat.mm),
        pw.Center(
          child: pw.Text(
            '© ${lt.createdAt.length >= 4 ? '${lt.createdAt.substring(0, 4)} ' : ''}TAROTS chat · $dominio',
            style: pw.TextStyle(font: c.sans, fontSize: 9, color: _grigio),
          ),
        ),
      ],
    ),
  );
  return doc.save();
}

/// Compone il PDF della lettura [lt] e apre la finestra di stampa o di salvataggio del sistema.
Future<void> stampaLettura(WidgetRef ref, Lettura lt, {required String interfaccia}) async {
  final t = lookupAppLocalizations(Locale(interfaccia));
  Uint8List? tavolo;
  final stesa = lt.stesaDati;
  if (stesa != null) {
    final fornitore = ref.read(immagineCartaProvider);
    final immagini = await caricaCarte(lt.cards, fornitore, (id) => percorsoCarta(lt.mazzo, id));
    tavolo = await componiTavolo(stesa, lt.cards, immagini, linguaLettura(lt.lang, interfaccia));
    for (final i in immagini.values) {
      i?.dispose();
    }
  }
  final caratteri = await CaratteriStampa.carica();
  final byte = await costruisciPdf(lt, t: t, interfaccia: interfaccia, caratteri: caratteri, tavolo: tavolo);
  await Printing.layoutPdf(onLayout: (_) async => byte, name: 'tarots-reading.pdf');
}
