/// La preparazione di una lettura (`frontend/v2/lettura/preparazione.tsx`): il tipo di lettura, il mazzo, la forma
/// della stesa, la stesa scelta nella console scura, i riquadri facoltativi (`.facoltativo`) e la dichiarazione breve
/// del rito (`Dichiarazione breve` di `v2/componenti/dichiarazione.tsx`).
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/griglia.dart';
import '../componenti/miniatura_stesa.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/carta.dart';
import '../modelli/cassa.dart';
import '../tema/tema.dart';
import 'comuni.dart';

/// I temi della lettura (v8.5): «Amore e compatibilità» riunisce le stese di compatibilità e di coppia (la categoria
/// vera della lettura viene dalla stesa scelta); «Lavoro e affari» ha le sue stese e quelle adatte del catalogo.
enum TemaLettura {
  /// Una domanda.
  standard,

  /// Amore e compatibilità.
  amore,

  /// Lavoro e affari.
  lavoro,
}

/// Il tema di una categoria (`temaDi()` del sito).
TemaLettura temaDi(String? c) => c == 'compatibilita' || c == 'coppia'
    ? TemaLettura.amore
    : c == 'lavoro'
    ? TemaLettura.lavoro
    : TemaLettura.standard;

/// Vero se la stesa [s] appartiene al tema [tema] (`nelTema()` del sito).
bool nelTema(Stesa s, TemaLettura tema) => switch (tema) {
  TemaLettura.amore => s.categoria == 'compatibilita' || s.categoria == 'coppia',
  TemaLettura.lavoro => s.categoria == 'lavoro' || (s.temi ?? const []).contains('lavoro'),
  TemaLettura.standard => s.categoria == 'standard',
};

/// Il nome e la spiegazione di un tema (`l.tipi[tema]`).
({String nome, String testo}) testiTema(AppLocalizations t, TemaLettura tema) => switch (tema) {
  TemaLettura.standard => (nome: t.lettura_tipi_standard_nome, testo: t.lettura_tipi_standard_testo),
  TemaLettura.amore => (nome: t.lettura_tipi_amore_nome, testo: t.lettura_tipi_amore_testo),
  TemaLettura.lavoro => (nome: t.lettura_tipi_lavoro_nome, testo: t.lettura_tipi_lavoro_testo),
};

/// `.passo`: il titolo di un passo della preparazione (`margin: 1.8rem 0 .8rem`; il primo senza margine sopra).
class TitoloPasso extends StatelessWidget {
  /// Un titolo.
  const TitoloPasso(this.testo, {super.key, this.primo = false});

  /// Il testo.
  final String testo;

  /// `:first-child`.
  final bool primo;

  @override
  Widget build(BuildContext context) => Padding(
    padding: EdgeInsets.only(top: primo ? 0 : 28.8, bottom: 12.8),
    child: Semantics(header: true, child: TestoBilanciato(testo, stile: Stile.serif(20))),
  );
}

/// `.tipo`: una scelta della colonna dei tipi (premuta: prugna).
class _Tipo extends StatelessWidget {
  const _Tipo({required this.scelto, required this.alTocco, required this.child, this.etichetta});

  final bool scelto;
  final VoidCallback alTocco;
  final Widget child;
  final String? etichetta;

  @override
  Widget build(BuildContext context) => Premibile(
    alTocco: alTocco,
    selezionato: scelto,
    etichetta: etichetta,
    costruisci: (context, premuto) => Container(
      constraints: const BoxConstraints(minHeight: 64),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
      color: scelto ? Token.plum : (premuto ? const Color(0xFFEFE6D6) : Token.paper),
      alignment: AlignmentDirectional.centerStart,
      child: DefaultTextStyle.merge(
        style: TextStyle(color: scelto ? const Color(0xFFFFF7E8) : Token.ink),
        child: child,
      ),
    ),
  );
}

/// `.tipi`: le voci una sotto l'altra, separate da una riga (`gap: 1px; background: var(--line)`).
class _ColonnaTipi extends StatelessWidget {
  const _ColonnaTipi({required this.etichetta, required this.children});

  final String etichetta;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Semantics(
    label: etichetta,
    container: true,
    child: Griglia.righe(linea: Token.line, children: children),
  );
}

/// La scelta del tipo di lettura (`SceltaTipo`).
class SceltaTipo extends StatelessWidget {
  /// La scelta, col [tema] corrente.
  const SceltaTipo({super.key, required this.tema, required this.alScegli, this.conTitolo = true});

  /// Il tema scelto.
  final TemaLettura tema;

  /// Un tema scelto.
  final ValueChanged<TemaLettura> alScegli;

  /// Col titolo del passo (sul telefono il dialogo ha già il suo).
  final bool conTitolo;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (conTitolo) TitoloPasso(t.lettura_tipo_titolo),
        _ColonnaTipi(
          etichetta: t.lettura_tipo_titolo,
          children: [
            for (final c in TemaLettura.values)
              _Tipo(
                scelto: c == tema,
                alTocco: () => alScegli(c),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(testiTema(t, c).nome, style: Stile.serif(16.8)),
                    const SizedBox(height: 3.2),
                    Text(
                      testiTema(t, c).testo,
                      style: Stile.sans(
                        13.12,
                        altezza: 1.45,
                        colore: c == tema ? const Color(0xFFD9CADE) : Token.inkSoft,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ],
    );
  }
}

/// Il mazzo della lettura, quando se ne possiede più d'uno (`SceltaMazzo`): il dorso piccolo e il nome. Il Thoth vale
/// `null`.
class SceltaMazzo extends StatelessWidget {
  /// La scelta fra i [mazzi], con lo [scelto].
  const SceltaMazzo({super.key, required this.mazzi, required this.scelto, required this.alScegli});

  /// I mazzi utilizzabili.
  final List<Mazzo> mazzi;

  /// Lo slug scelto (`null`: il predefinito).
  final String? scelto;

  /// Un mazzo scelto.
  final ValueChanged<String?> alScegli;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TitoloPasso(t.lettura_mazzo_titolo),
        _ColonnaTipi(
          etichetta: t.lettura_mazzo_titolo,
          children: [
            for (final m in mazzi)
              Builder(
                builder: (context) {
                  final valore = m.predefinito ? null : m.slug;
                  return _Tipo(
                    scelto: valore == scelto,
                    alTocco: () => alScegli(valore),
                    etichetta: m.nome,
                    child: Row(
                      children: [
                        Container(
                          width: 34,
                          decoration: const BoxDecoration(
                            boxShadow: [BoxShadow(color: Color(0x33201026), offset: Offset(0, 4), blurRadius: 8)],
                          ),
                          child: ImmagineCarta('dorso', mazzo: valore ?? ''),
                        ),
                        const SizedBox(width: 12.8),
                        Expanded(child: Text(m.nome, style: Stile.serif(16.8))),
                      ],
                    ),
                  );
                },
              ),
          ],
        ),
      ],
    );
  }
}

/// La scelta della stesa (`SceltaStesa`): le forme in tessere con la miniatura; per il tema dell'amore prima lo stile
/// (tradizionale, moderna, di tendenza).
class SceltaStesa extends ConsumerWidget {
  /// La scelta fra le [stese].
  const SceltaStesa({
    super.key,
    required this.stese,
    required this.scelta,
    required this.alScegli,
    required this.conStili,
    this.conTitolo = true,
  });

  /// Le stese del tema.
  final List<Stesa> stese;

  /// L'id scelto.
  final String? scelta;

  /// Una stesa scelta.
  final ValueChanged<String> alScegli;

  /// Con la scelta dello stile.
  final bool conStili;

  /// Col titolo del passo.
  final bool conTitolo;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final selezionata = stese.where((s) => s.id == scelta).firstOrNull;
    const ordine = ['tradizionale', 'moderna', 'tendenza'];
    final offerti = ordine.where((s) => stese.any((x) => x.stile == s)).toList();
    final stileAttivo = conStili ? (selezionata?.stile ?? offerti.firstOrNull) : null;
    final visibili = conStili ? stese.where((s) => s.stile == stileAttivo).toList() : stese;
    final schermo = MediaQuery.sizeOf(context).width;
    String nomeStile(String s) => switch (s) {
      'moderna' => t.lettura_stili_moderna_nome,
      'tendenza' => t.lettura_stili_tendenza_nome,
      _ => t.lettura_stili_tradizionale_nome,
    };
    String testoStile(String s) => switch (s) {
      'moderna' => t.lettura_stili_moderna_testo,
      'tendenza' => t.lettura_stili_tendenza_testo,
      _ => t.lettura_stili_tradizionale_testo,
    };
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (conTitolo) TitoloPasso(t.lettura_stesa_titolo),
        if (conStili) ...[
          Padding(
            padding: const EdgeInsets.only(bottom: 9.6),
            child: Pillole(
              children: [
                for (final s in offerti)
                  Pillola(
                    nomeStile(s),
                    acceso: s == stileAttivo,
                    alTocco: () {
                      final prima = stese.where((x) => x.stile == s).firstOrNull;
                      if (prima != null) alScegli(prima.id);
                    },
                  ),
              ],
            ),
          ),
          if (stileAttivo != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Paragrafo(testoStile(stileAttivo), style: stilePiccolo()),
            ),
        ],
        LayoutBuilder(
          builder: (context, vincoli) {
            // `repeat(auto-fill, minmax(150px, 1fr))`, due colonne fino a 640 px.
            final colonne = schermo <= 640 ? 2 : ((vincoli.maxWidth + 14.4) / (150 + 14.4)).floor().clamp(1, 12);
            return Griglia(
              colonne: colonne,
              spazioColonne: 14.4,
              spazioRighe: 14.4,
              children: [
                for (final s in visibili)
                  _TesseraStesa(
                    stesa: s,
                    scelta: s.id == scelta,
                    nome: nomeStesa(s, lingua),
                    sotto:
                        '${t.lettura_n_carte(s.posizioni.length)} · '
                        '${s.mazzo == 'maggiori' ? t.lettura_maggiori : t.lettura_completo}',
                    alTocco: () => alScegli(s.id),
                  ),
              ],
            );
          },
        ),
      ],
    );
  }
}

/// `.stesa`: la tessera di una stesa (premuta: bordo prugna e ombra d'ottone).
class _TesseraStesa extends StatelessWidget {
  const _TesseraStesa({
    required this.stesa,
    required this.scelta,
    required this.nome,
    required this.sotto,
    required this.alTocco,
  });

  final Stesa stesa;
  final bool scelta;
  final String nome;
  final String sotto;
  final VoidCallback alTocco;

  @override
  Widget build(BuildContext context) => Premibile(
    alTocco: alTocco,
    selezionato: scelta,
    costruisci: (context, premuto) => Container(
      padding: const EdgeInsets.all(12.8),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        border: Border.all(color: scelta ? Token.plum : (premuto ? Token.brass : Token.line), width: scelta ? 2 : 1),
        boxShadow: scelta ? const [BoxShadow(color: Token.brassPale, offset: Offset(3, 3))] : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ColoredBox(
            color: Token.plumDeep,
            child: MiniaturaStesa(stesa: stesa),
          ),
          const SizedBox(height: 5.6),
          Text(nome, style: Stile.serif(15.68, altezza: 1.25, colore: Token.ink)),
          const SizedBox(height: 5.6),
          Text(sotto, style: Stile.sans(12.16, colore: Token.inkSoft)),
        ],
      ),
    ),
  );
}

/// La stesa scelta, nella console scura (`StesaNellaConsole`): disegno, descrizione, origine, posizioni.
class StesaNellaConsole extends ConsumerWidget {
  /// La [stesa].
  const StesaNellaConsole({super.key, required this.stesa});

  /// La stesa.
  final Stesa stesa;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final due = MediaQuery.sizeOf(context).width > 640;
    final voci = [for (final p in stesa.posizioni) nomePosizione(p, lingua)];
    Widget voce(int i) => Padding(
      padding: const EdgeInsets.only(bottom: 5.6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 19.2,
            child: Text('${i + 1}.', style: Stile.sans(13.76, colore: const Color(0xFFEADBE9))),
          ),
          Expanded(
            child: Text(voci[i], style: Stile.sans(13.76, colore: const Color(0xFFEADBE9))),
          ),
        ],
      ),
    );
    final meta = (voci.length / 2).ceil();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 320),
            child: Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: MiniaturaStesa(stesa: stesa),
            ),
          ),
        ),
        Text(t.lettura_n_carte(stesa.posizioni.length).toUpperCase(), style: stileStatoConsole()),
        Padding(
          padding: const EdgeInsets.only(top: 3.2, bottom: 6.4),
          child: Text(nomeStesa(stesa, lingua), style: Stile.serif(24, colore: const Color(0xFFFFF7E8))),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 12.8),
          child: Paragrafo(stesa.descrizione, style: Stile.sans(14.72, colore: const Color(0xFFD9CADE))),
        ),
        if (stesa.origine.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 12.8),
            child: Text(stesa.origine, style: Stile.sans(12.48, em: .04, colore: Token.brassPale)),
          ),
        Semantics(
          label: t.lettura_posizioni,
          child: Padding(
            padding: const EdgeInsets.only(left: 0, bottom: 19.2),
            child: due
                ? Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: Column(children: [for (var i = 0; i < meta; i++) voce(i)])),
                      const SizedBox(width: 25.6),
                      Expanded(child: Column(children: [for (var i = meta; i < voci.length; i++) voce(i)])),
                    ],
                  )
                : Column(children: [for (var i = 0; i < voci.length; i++) voce(i)]),
          ),
        ),
      ],
    );
  }
}

/// `.console-status`: la riga d'ottone maiuscola della console.
TextStyle stileStatoConsole() => Stile.sans(11.52, peso: FontWeight.w700, em: .11, colore: Token.brassPale);

/// `.facoltativo`: ciò che si legge solo se si vuole, in un riquadro chiuso con «＋» (aperto: «－»).
class Facoltativo extends StatefulWidget {
  /// Un riquadro col [titolo] e il contenuto [child].
  const Facoltativo({super.key, required this.titolo, required this.child});

  /// Il `<summary>`.
  final String titolo;

  /// Il contenuto.
  final Widget child;

  @override
  State<Facoltativo> createState() => _FacoltativoState();
}

class _FacoltativoState extends State<Facoltativo> {
  bool _aperto = false;

  @override
  Widget build(BuildContext context) => Container(
    decoration: BoxDecoration(
      color: const Color(0x0AFFFFFF),
      border: Border.all(color: const Color(0x59D6B66D)),
      borderRadius: BorderRadius.circular(4),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Premibile(
          alTocco: () => setState(() => _aperto = !_aperto),
          etichetta: widget.titolo,
          raggioFuoco: 4,
          costruisci: (context, premuto) => Container(
            constraints: const BoxConstraints(minHeight: 44),
            padding: const EdgeInsets.symmetric(horizontal: 14.4, vertical: 8.8),
            alignment: AlignmentDirectional.centerStart,
            child: Row(
              children: [
                // `summary::before { content: "＋" }` (aperto «－»): disegnato, perché i caratteri a larghezza piena
                // non sono in DM Sans.
                CustomPaint(
                  size: const Size(10, 10),
                  painter: _PiuMeno(aperto: _aperto),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    widget.titolo,
                    style: Stile.sans(13.12, peso: FontWeight.w600, em: .04, colore: Token.brassPale, altezza: 1.4),
                  ),
                ),
              ],
            ),
          ),
        ),
        if (_aperto) Padding(padding: const EdgeInsets.fromLTRB(14.4, 0, 14.4, 14.4), child: widget.child),
      ],
    ),
  );
}

/// La dichiarazione breve del rito (`.declaration-short`): non un'animazione, un mazzo vero.
class DichiarazioneBreve extends StatelessWidget {
  /// La dichiarazione.
  const DichiarazioneBreve({super.key});

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Semantics(
      label: t.home_vero_eyebrow,
      container: true,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14.4),
        decoration: const BoxDecoration(
          color: Color(0x0FFFFFFF),
          border: Border(left: BorderSide(color: Token.brassPale, width: 3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(t.home_vero_titolo, style: Stile.serif(16.8, colore: const Color(0xFFFFF7E8))),
            const SizedBox(height: 4.8),
            Paragrafo(t.lettura_vero_breve, style: Stile.sans(13.76, colore: const Color(0xFFD9CADE))),
          ],
        ),
      ),
    );
  }
}

/// Il «＋» (o il «－») del riquadro facoltativo.
class _PiuMeno extends CustomPainter {
  const _PiuMeno({required this.aperto});

  final bool aperto;

  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = Token.brassPale
      ..strokeWidth = 1.2;
    canvas.drawLine(Offset(0, size.height / 2), Offset(size.width, size.height / 2), p);
    if (!aperto) canvas.drawLine(Offset(size.width / 2, 0), Offset(size.width / 2, size.height), p);
  }

  @override
  bool shouldRepaint(_PiuMeno vecchio) => vecchio.aperto != aperto;
}
