/// Le persone delle letture di compatibilità e di coppia (`frontend/v2/lettura/persone.tsx`): i dati che mancano a chi
/// consulta (genere, data di nascita: restano nel profilo e non si chiedono più) e quelli dell'altra persona, con
/// «ricorda». Le stesse regole del sito: il cognome non arriva mai all'AI, nessun campo sull'orientamento, «preferisco
/// non dirlo» è una risposta valida; «persona trans» (art. 9 GDPR) solo col consenso `dati_particolari`, chiesto qui.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart' show showDatePicker;

import '../api/api.dart';
import '../api/errori.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../consensi/consensi.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../tema/tema.dart';
import 'preparazione.dart' show TitoloPasso;

/// I generi, nell'ordine del sito.
const List<String> generi = ['donna', 'uomo', 'non_binario', 'altro', 'non_dice'];

/// I dati delle persone (`DatiPersone` del sito). Le date sono `AAAA-MM-GG`.
@immutable
class DatiPersone {
  /// I dati.
  const DatiPersone({
    this.tuGenere = '',
    this.tuGenereAltro = '',
    this.tuTrans = false,
    this.tuNascita = '',
    this.nome = '',
    this.cognome = '',
    this.genere = '',
    this.genereAltro = '',
    this.trans = false,
    this.nascita = '',
    this.ricorda = false,
  });

  /// Il genere di chi consulta (vuoto: non scelto).
  final String tuGenere;

  /// Come si descrive chi consulta.
  final String tuGenereAltro;

  /// Chi consulta è una persona trans.
  final bool tuTrans;

  /// La data di nascita di chi consulta.
  final String tuNascita;

  /// Il nome dell'altra persona.
  final String nome;

  /// Il cognome (facoltativo; mai all'AI).
  final String cognome;

  /// Il genere dell'altra persona.
  final String genere;

  /// Come si descrive.
  final String genereAltro;

  /// Persona trans.
  final bool trans;

  /// La data di nascita.
  final String nascita;

  /// «Ricorda questi dati».
  final bool ricorda;

  /// Una copia con qualche campo cambiato.
  DatiPersone con({
    String? tuGenere,
    String? tuGenereAltro,
    bool? tuTrans,
    String? tuNascita,
    String? nome,
    String? cognome,
    String? genere,
    String? genereAltro,
    bool? trans,
    String? nascita,
    bool? ricorda,
  }) => DatiPersone(
    tuGenere: tuGenere ?? this.tuGenere,
    tuGenereAltro: tuGenereAltro ?? this.tuGenereAltro,
    tuTrans: tuTrans ?? this.tuTrans,
    tuNascita: tuNascita ?? this.tuNascita,
    nome: nome ?? this.nome,
    cognome: cognome ?? this.cognome,
    genere: genere ?? this.genere,
    genereAltro: genereAltro ?? this.genereAltro,
    trans: trans ?? this.trans,
    nascita: nascita ?? this.nascita,
    ricorda: ricorda ?? this.ricorda,
  );

  /// I dati della persona di chi consulta, tenuti; quelli dell'altra persona vuoti (`dimenticaPartner` del sito).
  DatiPersone senzaPartner() =>
      DatiPersone(tuGenere: tuGenere, tuGenereAltro: tuGenereAltro, tuTrans: tuTrans, tuNascita: tuNascita);
}

String _oggi() => DateTime.now().toIso8601String().substring(0, 10);

bool _nascitaValida(String v) =>
    RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(v) && v.compareTo('1900-01-01') >= 0 && v.compareTo(_oggi()) <= 0;

/// Gli errori del modulo (`verificaPersone()` del sito): campo → messaggio.
Map<String, String> verificaPersone(DatiPersone d, List<String> mancanti, AppLocalizations t) {
  final e = <String, String>{};
  if (mancanti.contains('genere')) {
    if (d.tuGenere.isEmpty) {
      e['tuGenere'] = t.lettura_err_genere;
    } else if (d.tuGenere == 'altro' && d.tuGenereAltro.trim().isEmpty) {
      e['tuGenereAltro'] = t.lettura_err_altro;
    }
  }
  if (mancanti.contains('nascita') && !_nascitaValida(d.tuNascita)) e['tuNascita'] = t.lettura_err_nascita;
  if (d.nome.trim().isEmpty) e['nome'] = t.lettura_err_nome;
  if (d.genere.isEmpty) {
    e['genere'] = t.lettura_err_genere;
  } else if (d.genere == 'altro' && d.genereAltro.trim().isEmpty) {
    e['genereAltro'] = t.lettura_err_altro;
  }
  if (!_nascitaValida(d.nascita)) e['nascita'] = t.lettura_err_nascita;
  return e;
}

/// L'altra persona come la vuole il server (`partnerDa()` del sito).
Map<String, Object?> partnerDa(DatiPersone d) => {
  'nome': d.nome.trim(),
  if (d.cognome.trim().isNotEmpty) 'cognome': d.cognome.trim(),
  'genere': d.genere,
  if (d.genere == 'altro') 'genere_altro': d.genereAltro.trim(),
  'trans': d.trans,
  'nascita': d.nascita,
};

/// I dati del partner ricordato nel profilo (`personeDaProfilo()` del sito).
DatiPersone personeDaProfilo(Profilo profilo, DatiPersone attuali) {
  final p = profilo.partnerRicordato;
  if (p == null) return attuali;
  return attuali.con(
    nome: p.nome,
    cognome: p.cognome ?? '',
    genere: p.genere,
    genereAltro: p.genereAltro ?? '',
    trans: p.trans,
    nascita: p.nascita,
    ricorda: true,
  );
}

String _nomeGenere(AppLocalizations t, String g) => switch (g) {
  'donna' => t.lettura_generi_donna,
  'uomo' => t.lettura_generi_uomo,
  'non_binario' => t.lettura_generi_non_binario,
  'altro' => t.lettura_generi_altro,
  'non_dice' => t.lettura_generi_non_dice,
  _ => t.lettura_persone_genere_scegli,
};

/// Un errore sotto un campo (`small.error`).
class _ErroreCampo extends StatelessWidget {
  const _ErroreCampo(this.testo);

  final String? testo;

  @override
  Widget build(BuildContext context) => testo == null
      ? const SizedBox.shrink()
      : Padding(
          padding: const EdgeInsets.only(top: 4, bottom: 8),
          child: Semantics(liveRegion: true, child: Errore(testo!, sopra: 0)),
        );
}

/// Il genere, il «come si descrive» e la casella «persona trans» (`CampiGenere` del sito).
class CampiGenere extends StatelessWidget {
  /// I campi.
  const CampiGenere({
    super.key,
    required this.genere,
    required this.altro,
    required this.trans,
    required this.alGenere,
    required this.alAltro,
    required this.alTrans,
    this.errore,
    this.erroreAltro,
  });

  /// Il genere (vuoto: non scelto).
  final String genere;

  /// Come si descrive.
  final String altro;

  /// Persona trans.
  final bool trans;

  /// Un genere scelto.
  final ValueChanged<String> alGenere;

  /// Il testo di «altro».
  final ValueChanged<String> alAltro;

  /// La casella.
  final ValueChanged<bool> alTrans;

  /// L'errore del genere.
  final String? errore;

  /// L'errore di «altro».
  final String? erroreAltro;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        CampoScelta<String>(
          etichetta: t.lettura_persone_genere,
          voci: [('', t.lettura_persone_genere_scegli), for (final g in generi) (g, _nomeGenere(t, g))],
          valore: genere,
          alCambio: alGenere,
          margineSotto: errore == null ? 16 : 0,
        ),
        _ErroreCampo(errore),
        if (genere == 'altro') ...[
          _CampoControllato(
            etichetta: t.lettura_persone_genere_altro,
            valore: altro,
            alCambio: alAltro,
            lunghezza: 30,
            errore: erroreAltro,
          ),
        ],
        _CasellaTrans(trans: trans, alTrans: alTrans),
      ],
    );
  }
}

/// Un campo di testo che segue un valore esterno.
class _CampoControllato extends StatefulWidget {
  const _CampoControllato({
    required this.etichetta,
    required this.valore,
    required this.alCambio,
    required this.lunghezza,
    this.errore,
  });

  final String etichetta;
  final String valore;
  final ValueChanged<String> alCambio;
  final int lunghezza;
  final String? errore;

  @override
  State<_CampoControllato> createState() => _CampoControllatoState();
}

class _CampoControllatoState extends State<_CampoControllato> {
  late final TextEditingController _c = TextEditingController(text: widget.valore);

  @override
  void didUpdateWidget(_CampoControllato vecchio) {
    super.didUpdateWidget(vecchio);
    if (widget.valore != _c.text) _c.text = widget.valore;
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      CampoTesto(
        etichetta: widget.etichetta,
        controllore: _c,
        lunghezzaMassima: widget.lunghezza,
        alCambio: widget.alCambio,
        margineSotto: widget.errore == null ? 16 : 0,
      ),
      _ErroreCampo(widget.errore),
    ],
  );
}

/// La data di nascita (`<input type="date">`): il calendario del sistema, fra il 1900 e oggi.
class _CampoData extends ConsumerWidget {
  const _CampoData({required this.etichetta, required this.valore, required this.alCambio, this.errore});

  final String etichetta;
  final String valore;
  final ValueChanged<String> alCambio;
  final String? errore;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lingua = ref.watch(linguaProvider);
    final data = DateTime.tryParse(valore);
    Future<void> scegli() async {
      final scelta = await showDatePicker(
        context: context,
        initialDate: data ?? DateTime(1990),
        firstDate: DateTime(1900),
        lastDate: DateTime.now(),
      );
      if (scelta != null) alCambio(scelta.toIso8601String().substring(0, 10));
    }

    return Padding(
      padding: EdgeInsets.only(bottom: errore == null ? 16 : 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 5.6),
            child: Text(etichetta, style: stileEtichettaCampo()),
          ),
          Premibile(
            alTocco: () => unawaited(scegli()),
            etichetta: '$etichetta: ${data == null ? '' : dataLunga(valore, lingua)}',
            costruisci: (context, premuto) => Container(
              constraints: const BoxConstraints(minHeight: Token.altezzaBottone),
              padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 11.2),
              decoration: BoxDecoration(
                color: premuto ? const Color(0xFFF7F3EC) : const Color(0xFFFFFFFF),
                border: Border.all(color: Token.line),
              ),
              alignment: AlignmentDirectional.centerStart,
              child: Text(
                data == null ? '' : dataLunga(valore, lingua),
                style: Stile.sans(16, altezza: 1.5, colore: data == null ? Colori.segnaposto : Token.ink),
              ),
            ),
          ),
          _ErroreCampo(errore),
        ],
      ),
    );
  }
}

/// «Persona trans» (art. 9 GDPR): spuntandola senza il consenso `dati_particolari` si apre sotto una richiesta breve;
/// «Non ora» lascia la casella vuota. Togliere la spunta non chiede niente.
class _CasellaTrans extends ConsumerStatefulWidget {
  const _CasellaTrans({required this.trans, required this.alTrans});

  final bool trans;
  final ValueChanged<bool> alTrans;

  @override
  ConsumerState<_CasellaTrans> createState() => _CasellaTransState();
}

class _CasellaTransState extends ConsumerState<_CasellaTrans> {
  bool _chiede = false;
  bool _inCorso = false;
  bool _errore = false;

  Future<void> _spunta(bool v) async {
    if (!v) {
      setState(() => _chiede = false);
      widget.alTrans(false);
      return;
    }
    var dato = false;
    try {
      dato = (await ref.read(apiProvider).consensi())['dati_particolari'] == 'accettato';
    } on ErroreApi {
      dato = false;
    }
    if (!mounted) return;
    if (dato) {
      widget.alTrans(true);
    } else {
      setState(() => _chiede = true);
    }
  }

  Future<void> _consenti() async {
    setState(() {
      _inCorso = true;
      _errore = false;
    });
    try {
      await ref
          .read(apiProvider)
          .registraConsensi(
            [(tipo: 'dati_particolari', valore: 'accettato')],
            versione: versioneConsensi,
            origine: origineApp(),
          );
      if (!mounted) return;
      setState(() => _chiede = false);
      widget.alTrans(true);
    } on ErroreApi {
      if (mounted) setState(() => _errore = true);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Casella(valore: widget.trans, alCambio: (v) => unawaited(_spunta(v)), titolo: t.lettura_persone_trans),
        if (_chiede)
          // `.consenso-inline`
          Container(
            margin: const EdgeInsets.fromLTRB(30.4, 0, 0, 12.8),
            padding: const EdgeInsets.symmetric(horizontal: 14.4, vertical: 11.2),
            decoration: const BoxDecoration(
              color: Color(0xFFF3F7F2),
              border: Border(left: BorderSide(color: Token.verdigris, width: 3)),
            ),
            child: Semantics(
              label: t.lettura_art9_titolo,
              container: true,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text.rich(
                    TextSpan(
                      children: [
                        TextSpan(
                          text: '${t.lettura_art9_titolo}. ',
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        TextSpan(text: t.lettura_art9_testo),
                      ],
                    ),
                    style: Stile.sans(13.44, colore: Token.ink),
                  ),
                  const SizedBox(height: 8),
                  FilaBottoni(
                    children: [
                      Bottone(
                        t.lettura_art9_si,
                        piccolo: true,
                        alTocco: _inCorso ? null : () => unawaited(_consenti()),
                      ),
                      Bottone(
                        t.lettura_art9_no,
                        piccolo: true,
                        variante: Variante.quieto,
                        alTocco: () => setState(() => _chiede = false),
                      ),
                    ],
                  ),
                  if (_errore) Errore(t.comune_err_operazione, sopra: 8),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

/// Il modulo delle persone (`FormPersone` del sito).
class FormPersone extends StatefulWidget {
  /// Il modulo.
  const FormPersone({
    super.key,
    required this.dati,
    required this.alCambia,
    required this.profilo,
    required this.alAvanti,
    required this.alDimentica,
    this.errore,
  });

  /// I dati.
  final DatiPersone dati;

  /// I dati cambiati.
  final ValueChanged<DatiPersone> alCambia;

  /// Il profilo (i campi che mancano, il partner ricordato).
  final Profilo? profilo;

  /// «Avanti», coi dati validi.
  final VoidCallback alAvanti;

  /// «Dimentica» il partner ricordato.
  final VoidCallback alDimentica;

  /// Un errore del server.
  final String? errore;

  @override
  State<FormPersone> createState() => _FormPersoneState();
}

class _FormPersoneState extends State<FormPersone> {
  bool _provato = false;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final d = widget.dati;
    final mancanti = widget.profilo?.relazioni.mancanti ?? const <String>[];
    final errori = _provato ? verificaPersone(d, mancanti, t) : const <String, String>{};
    final ricordato = widget.profilo?.partnerRicordato;
    void cambia(DatiPersone n) => widget.alCambia(n);
    void avanti() {
      setState(() => _provato = true);
      if (verificaPersone(d, mancanti, t).isEmpty) widget.alAvanti();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (mancanti.isNotEmpty) ...[
          TitoloPasso(t.lettura_persone_di_te, primo: true),
          Padding(
            padding: const EdgeInsets.only(bottom: 12.8),
            child: Paragrafo(t.lettura_persone_di_te_testo, style: stilePiccolo()),
          ),
          if (mancanti.contains('genere'))
            CampiGenere(
              genere: d.tuGenere,
              altro: d.tuGenereAltro,
              trans: d.tuTrans,
              alGenere: (g) => cambia(d.con(tuGenere: g)),
              alAltro: (v) => cambia(d.con(tuGenereAltro: v)),
              alTrans: (v) => cambia(d.con(tuTrans: v)),
              errore: errori['tuGenere'],
              erroreAltro: errori['tuGenereAltro'],
            ),
          if (mancanti.contains('nascita'))
            _CampoData(
              etichetta: t.lettura_persone_nascita,
              valore: d.tuNascita,
              alCambio: (v) => cambia(d.con(tuNascita: v)),
              errore: errori['tuNascita'],
            ),
        ],
        TitoloPasso(t.lettura_persone_altra, primo: mancanti.isEmpty),
        if (ricordato != null)
          // `.ricordato`
          Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.symmetric(horizontal: 14.4, vertical: 11.2),
            decoration: const BoxDecoration(
              color: Color(0xFFE7F2EE),
              border: Border(left: BorderSide(color: Token.verdigris, width: 3)),
            ),
            child: Wrap(
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 9.6,
              runSpacing: 9.6,
              children: [
                Text(t.lettura_persone_ripresi(ricordato.nome), style: Stile.sans(14.4)),
                Bottone(
                  t.lettura_persone_dimentica,
                  piccolo: true,
                  variante: Variante.quieto,
                  alTocco: widget.alDimentica,
                ),
              ],
            ),
          ),
        _CampoControllato(
          etichetta: t.lettura_persone_nome,
          valore: d.nome,
          alCambio: (v) => cambia(d.con(nome: v)),
          lunghezza: 40,
          errore: errori['nome'],
        ),
        _CampoControllato(
          etichetta: t.lettura_persone_cognome,
          valore: d.cognome,
          alCambio: (v) => cambia(d.con(cognome: v)),
          lunghezza: 60,
        ),
        CampiGenere(
          genere: d.genere,
          altro: d.genereAltro,
          trans: d.trans,
          alGenere: (g) => cambia(d.con(genere: g)),
          alAltro: (v) => cambia(d.con(genereAltro: v)),
          alTrans: (v) => cambia(d.con(trans: v)),
          errore: errori['genere'],
          erroreAltro: errori['genereAltro'],
        ),
        _CampoData(
          etichetta: t.lettura_persone_nascita,
          valore: d.nascita,
          alCambio: (v) => cambia(d.con(nascita: v)),
          errore: errori['nascita'],
        ),
        Casella(
          valore: d.ricorda,
          alCambio: (v) => cambia(d.con(ricorda: v)),
          titolo: t.lettura_persone_ricorda,
        ),
        Avviso(t.lettura_persone_privacy),
        if (widget.errore != null || (_provato && errori.isNotEmpty)) Errore(widget.errore ?? t.lettura_err_incompleto),
        Padding(
          padding: const EdgeInsets.only(top: 16),
          child: FilaBottoni(children: [Bottone(t.comune_avanti, alTocco: avanti)]),
        ),
      ],
    );
  }
}
