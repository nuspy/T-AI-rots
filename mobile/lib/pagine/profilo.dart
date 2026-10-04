/// Il profilo (`frontend/v2/pagine/profilo.tsx`): le parti di una storia personale — i tuoi dati e la posizione, l'abbonamento,
/// le carte personali, genere e persona ricordata, il registro del lettore e il mazzo, gli inviti e le condivisioni,
/// l'immagine e il nome pubblico, gli ordini col PDF, gli indirizzi, l'opposizione alle statistiche, «Privacy e consensi».
/// La memoria vive in «La mia storia», come nel sito.
///
/// Differenze volute dal sito: la sezione «Sicurezza» (verifica in due passaggi di Keycloak) non c'è, perché nell'app
/// si entra con Google o con Apple, che hanno la loro; il PDF di un ordine, l'invito e il bigliettino passano dal foglio
/// di condivisione del telefono invece che dal download e dagli appunti.
library;

import 'dart:async';

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' show DateFormat;
import 'package:share_plus/share_plus.dart';

import '../api/api.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/diario.dart' show immagineMediaProvider;
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../config.dart';
import '../dati/dati.dart';
import '../dati/inviti.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../modelli/cassa.dart';
import '../profilo/abbonamento.dart';
import '../profilo/bigliettino.dart';
import '../profilo/codice_app.dart';
import '../profilo/comuni.dart';
import '../profilo/dati_account.dart';
import '../profilo/genere.dart';
import '../profilo/notifiche_profilo.dart';
import '../profilo/privacy_profilo.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// La pagina del profilo (`/profile`).
class PaginaProfilo extends ConsumerWidget {
  /// Il profilo; [parametri] è la query (`?checkout=…` al ritorno da un pagamento).
  const PaginaProfilo({super.key, required this.parametri});

  /// La query dell'indirizzo.
  final Map<String, String> parametri;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.profilo_eyebrow, titolo: t.profilo_titolo, intro: t.profilo_intro, compatta: true),
        if (!sessione.pronta)
          const SizedBox.shrink()
        else if (!sessione.autenticata)
          const _Fuori()
        else
          const _Dentro(),
      ],
    );
  }
}

/// Chi non è entrato: l'invito a entrare.
class _Fuori extends ConsumerWidget {
  const _Fuori();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          IntroSezione(t.profilo_fuori),
          const SizedBox(height: 16),
          Bottone(t.profilo_entra, alTocco: () => unawaited(entraDa(ref))),
        ],
      ),
    );
  }
}

class _Dentro extends ConsumerStatefulWidget {
  const _Dentro();

  @override
  ConsumerState<_Dentro> createState() => _DentroState();
}

class _DentroState extends ConsumerState<_Dentro> {
  void _ricarica() => ref.invalidate(profiloProvider);

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final profilo = ref.watch(profiloProvider);
    if (profilo.hasError && !profilo.hasValue) return StatoFascia(errore: profilo.error);
    final p = profilo.value;
    if (p == null) return const StatoFascia();
    final w = MediaQuery.sizeOf(context).width;

    // `.share-band`: l'email, il rimando alla storia e l'uscita.
    final testa = Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: EdgeInsets.symmetric(horizontal: w.clampVw(24, 4, 40), vertical: w.clampVw(12, 2, 20)),
      decoration: BoxDecoration(
        color: Token.paperLight,
        border: Border.all(color: Token.line),
      ),
      child: Builder(
        builder: (context) {
          final testo = Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Eyebrow(p.email ?? '', sotto: 0),
              Padding(
                padding: const EdgeInsets.only(top: 9.6),
                child: Paragrafo(t.profilo_storia_link, style: Stile.sans(16, colore: Token.inkSoft)),
              ),
            ],
          );
          final bottoni = FilaBottoni(
            children: [
              Bottone(t.profilo_storia_cta, href: R.storia),
              Bottone(
                t.profilo_esci,
                variante: Variante.quieto,
                alTocco: () => unawaited(ref.read(sessioneProvider.notifier).esci()),
              ),
            ],
          );
          return w.telefono
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [testo, const SizedBox(height: 11.2), bottoni],
                )
              : Row(
                  children: [
                    Expanded(flex: 12, child: testo),
                    const SizedBox(width: 11.2),
                    Expanded(flex: 8, child: bottoni),
                  ],
                );
        },
      ),
    );

    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          testa,
          GrigliaProfilo(
            celle: [
              (widget: _DatiPersonali(p: p, ricarica: _ricarica), larga: false),
              (widget: const AbbonamentoProfilo(), larga: true),
              (widget: _Carte(p: p, ricarica: _ricarica), larga: false),
              (widget: _Genere(p: p, ricarica: _ricarica), larga: false),
              (widget: _Registro(p: p, ricarica: _ricarica), larga: false),
              (widget: _Invito(p: p, ricarica: _ricarica), larga: false),
              (widget: _Immagine(p: p, ricarica: _ricarica), larga: false),
              // Fase 6: il codice che sposta l'accesso dell'app sull'account del sito (non con la sessione di sviluppo,
              // come «Modi di accesso» del sito senza Keycloak).
              if (!ref.watch(sessioneProvider.select((s) => s.sviluppo)))
                (widget: const SezioneCodiceApp(), larga: false),
              (widget: const _Ordini(), larga: false),
              (widget: const _Indirizzi(), larga: false),
              (widget: const _Statistiche(), larga: false),
              // Fase 9: le notifiche, come la sezione del sito fra le statistiche e la privacy.
              (widget: const NotificheProfilo(), larga: true),
              (widget: PrivacyProfilo(alCambio: _ricarica), larga: true),
            ],
          ),
        ],
      ),
    );
  }
}

/* ---- pezzi comuni ----------------------------------------------------------------------------------------------- */

const Map<String, String> _nomiSocial = {
  'google': 'Google',
  'facebook': 'Facebook',
  'microsoft': 'Microsoft',
  'github': 'GitHub',
  'linkedin': 'LinkedIn',
  'apple': 'Apple',
};

/// «da Google, 3 ott 2026» accanto a un campo compilato da un social; niente se l'ha scritto la persona.
class _Provenienza extends ConsumerWidget {
  const _Provenienza({required this.p, required this.campo});

  final Profilo p;
  final String campo;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final voce = p.datiSocial[campo];
    if (voce == null || voce.da == 'utente') return const SizedBox.shrink();
    if (voce.da == 'account') return TestoPiccolo(t.profilo_da_account, tenue: true, sopra: 13.44);
    final lingua = ref.watch(linguaProvider);
    final d = DateTime.tryParse(voce.il);
    final data = d == null ? voce.il : DateFormat.yMMMd(localeIntl(lingua)).format(d.toLocal());
    return TestoPiccolo(t.profilo_da_social(_nomiSocial[voce.da] ?? voce.da, data), tenue: true, sopra: 13.44);
  }
}

/// La base di un campo in una riga (`flex: 1 1 12rem`).
const double _baseCampo = 192;

/* ---- i tuoi dati ------------------------------------------------------------------------------------------------- */

class _DatiPersonali extends ConsumerStatefulWidget {
  const _DatiPersonali({required this.p, required this.ricarica});

  final Profilo p;
  final VoidCallback ricarica;

  @override
  ConsumerState<_DatiPersonali> createState() => _DatiPersonaliState();
}

class _DatiPersonaliState extends ConsumerState<_DatiPersonali> with AzioneAccount {
  late final TextEditingController _nome = TextEditingController(text: widget.p.nome ?? '');
  late final TextEditingController _cognome = TextEditingController(text: widget.p.cognome ?? '');
  late final TextEditingController _citta = TextEditingController(text: widget.p.posizione?.citta ?? '');
  late final TextEditingController _paese = TextEditingController(text: widget.p.posizione?.paese ?? '');
  bool _nomiCambiati = false;
  bool _posizioneCambiata = false;
  String? _salvato;

  @override
  void didUpdateWidget(_DatiPersonali vecchio) {
    super.didUpdateWidget(vecchio);
    if (!_nomiCambiati) {
      _nome.text = widget.p.nome ?? '';
      _cognome.text = widget.p.cognome ?? '';
    }
    if (!_posizioneCambiata) {
      _citta.text = widget.p.posizione?.citta ?? '';
      _paese.text = widget.p.posizione?.paese ?? '';
    }
  }

  @override
  void dispose() {
    _nome.dispose();
    _cognome.dispose();
    _citta.dispose();
    _paese.dispose();
    super.dispose();
  }

  Future<bool> _salva(Map<String, Object?> dati) async {
    final t = context.t;
    setState(() => _salvato = null);
    final r = await esegui((api) => api.aggiornaProfilo(dati));
    if (r == null || !mounted) return false;
    setState(() => _salvato = t.profilo_salvato);
    widget.ricarica();
    return true;
  }

  Future<void> _dimentica() async {
    final t = context.t;
    final si = await apriModale<bool>(
      context,
      titolo: t.profilo_dimentica_social,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 16), child: Text(t.profilo_dimentica_conferma)),
          FilaBottoni(
            children: [
              Bottone(
                t.profilo_dimentica_social,
                variante: Variante.pericolo,
                alTocco: () => Navigator.of(context).pop(true),
              ),
              Bottone(t.comune_annulla, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop(false)),
            ],
          ),
        ],
      ),
    );
    if (si != true) return;
    setState(() => _salvato = null);
    final r = await esegui((api) async {
      await api.dimenticaDatiSocial();
      return true;
    });
    if (r == true && mounted) {
      setState(() => _salvato = t.profilo_dimentica_fatto);
      widget.ricarica();
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final p = widget.p;
    final lingua = ref.watch(linguaProvider);
    final pos = p.posizione;
    final quando = pos?.il == null
        ? ''
        : DateFormat.yMMMd(localeIntl(lingua)).format(DateTime.parse(pos!.il!).toLocal());
    final fonte = pos == null
        ? ''
        : pos.fonte == 'utente'
        ? t.profilo_posizione_utente
        : pos.fonte == 'ip'
        ? t.profilo_posizione_ip(quando)
        : t.profilo_da_social(_nomiSocial[pos.fonte ?? ''] ?? pos.fonte ?? '', quando);
    final paeseValido = _paese.text.length != 1;

    return Sezione(
      titolo: t.profilo_dati_titolo,
      id: 'dati',
      children: [
        TestoPiccolo(t.profilo_dati_testo),
        // Fase 6: Apple manda il nome solo al primo accesso e Keycloak non lo legge; lo si chiede, con garbo.
        if ((widget.p.nome ?? '').isEmpty)
          Semantics(
            container: true,
            child: Container(
              margin: const EdgeInsets.only(bottom: 13.44),
              padding: const EdgeInsets.only(left: 9.6),
              decoration: const BoxDecoration(border: Border(left: BorderSide(color: Token.ink, width: 2))),
              child: TestoPiccolo(t.profilo_nome_manca, sotto: 0),
            ),
          ),
        RigaFlessibile(
          pezzi: [
            (
              widget: CampoTesto(
                etichetta: t.profilo_nome,
                controllore: _nome,
                lunghezzaMassima: 100,
                margineSotto: 0,
                alCambio: (_) => setState(() => _nomiCambiati = true),
              ),
              base: _baseCampo,
              cresce: true,
            ),
            (
              widget: CampoTesto(
                etichetta: t.profilo_cognome,
                controllore: _cognome,
                lunghezzaMassima: 100,
                margineSotto: 0,
                alCambio: (_) => setState(() => _nomiCambiati = true),
              ),
              base: _baseCampo,
              cresce: true,
            ),
            (
              widget: Bottone(
                t.comune_salva,
                piccolo: true,
                alTocco: inCorso || !_nomiCambiati
                    ? null
                    : () async {
                        if (await _salva({'nome': _nome.text, 'cognome': _cognome.text})) {
                          setState(() => _nomiCambiati = false);
                        }
                      },
              ),
              base: larghezzaBottonePiccolo(context, t.comune_salva),
              cresce: false,
            ),
          ],
        ),
        _Provenienza(p: p, campo: 'nome'),
        // `<h3 style={{ marginTop: ".8rem" }}>`
        Padding(padding: const EdgeInsets.only(top: 4.8), child: TitoloPannello(t.profilo_posizione_titolo)),
        TestoPiccolo(t.profilo_posizione_testo),
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Semantics(
            liveRegion: true,
            child: pos == null
                ? Text(t.profilo_posizione_nessuna, style: Stile.sans(16, colore: Token.inkSoft))
                : Text.rich(
                    TextSpan(
                      children: [
                        TextSpan(
                          text: [pos.citta, pos.paese].whereType<String>().where((s) => s.isNotEmpty).join(', '),
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        TextSpan(
                          text: ' · $fonte',
                          style: Stile.sans(13.44, colore: Token.inkSoft),
                        ),
                      ],
                    ),
                    style: Stile.sans(16, colore: Token.ink),
                  ),
          ),
        ),
        RigaFlessibile(
          pezzi: [
            (
              widget: CampoTesto(
                etichetta: t.profilo_posizione_citta,
                controllore: _citta,
                lunghezzaMassima: 100,
                margineSotto: 0,
                alCambio: (_) => setState(() => _posizioneCambiata = true),
              ),
              base: _baseCampo,
              cresce: true,
            ),
            (
              widget: CampoTesto(
                etichetta: t.profilo_posizione_paese,
                controllore: _paese,
                lunghezzaMassima: 2,
                maiuscole: true,
                margineSotto: 0,
                formattatori: [FilteringTextInputFormatter.allow(RegExp('[A-Za-z]'))],
                alCambio: (_) => setState(() => _posizioneCambiata = true),
              ),
              base: 144,
              cresce: false,
            ),
            (
              widget: Bottone(
                t.profilo_posizione_correggi,
                piccolo: true,
                alTocco: inCorso || !_posizioneCambiata || !paeseValido
                    ? null
                    : () async {
                        final ok = await _salva({'posizione_paese': _paese.text, 'posizione_citta': _citta.text});
                        if (ok) setState(() => _posizioneCambiata = false);
                      },
              ),
              base: larghezzaBottonePiccolo(context, t.profilo_posizione_correggi),
              cresce: false,
            ),
          ],
        ),
        if (pos?.fonte == 'utente')
          Padding(
            padding: const EdgeInsets.only(top: 9.6),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: Bottone(
                t.profilo_posizione_automatica,
                variante: Variante.quieto,
                piccolo: true,
                alTocco: inCorso ? null : () => unawaited(_salva({'posizione_paese': '', 'posizione_citta': ''})),
              ),
            ),
          ),
        Casella(
          valore: p.importaSocial ?? true,
          attiva: !inCorso,
          titolo: t.profilo_importa_social,
          alCambio: (v) => unawaited(_salva({'importa_social': v})),
        ),
        Casella(
          valore: p.rilevaPosizione ?? true,
          attiva: !inCorso,
          titolo: t.profilo_rileva_posizione,
          alCambio: (v) => unawaited(_salva({'rileva_posizione': v})),
        ),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(
            t.profilo_dimentica_social,
            variante: Variante.quieto,
            piccolo: true,
            alTocco: inCorso ? null : () => unawaited(_dimentica()),
          ),
        ),
        if (_salvato != null) Successo(_salvato!),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

/* ---- le carte personali ------------------------------------------------------------------------------------------ */

class _Carte extends ConsumerStatefulWidget {
  const _Carte({required this.p, required this.ricarica});

  final Profilo p;
  final VoidCallback ricarica;

  @override
  ConsumerState<_Carte> createState() => _CarteState();
}

class _CarteState extends ConsumerState<_Carte> with AzioneAccount {
  String? _nascita;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final p = widget.p;
    final lingua = ref.watch(linguaProvider);
    final anima = p.cartaAnima;
    final anno = p.cartaAnno;
    return Sezione(
      titolo: t.profilo_carte_titolo,
      id: 'carte',
      children: [
        TestoPiccolo(t.profilo_carte_testo),
        RigaFlessibile(
          pezzi: [
            (
              widget: CampoData(
                etichetta: t.profilo_nascita,
                valore: _nascita ?? p.birthDate ?? '',
                alCambio: (v) => setState(() => _nascita = v),
              ),
              base: 190,
              cresce: false,
            ),
            (
              widget: Bottone(
                t.comune_salva,
                piccolo: true,
                alTocco: inCorso || _nascita == null
                    ? null
                    : () async {
                        await esegui((api) => api.aggiornaProfilo({'birth_date': _nascita}));
                        widget.ricarica();
                      },
              ),
              base: larghezzaBottonePiccolo(context, t.comune_salva),
              cresce: false,
            ),
          ],
        ),
        _Provenienza(p: p, campo: 'birth_date'),
        if (anima != null && anno != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Wrap(
              spacing: 22.4,
              runSpacing: 9.6,
              children: [
                for (final (titolo, carta) in [(t.profilo_carta_anima, anima), (t.profilo_carta_anno, anno)])
                  SizedBox(
                    width: 120,
                    child: Column(
                      children: [
                        CartaV2(carta: carta, rivelata: true, larghezza: 120, nome: carta.nomeIn(lingua)),
                        Padding(
                          padding: const EdgeInsets.only(top: 13.44),
                          child: Text(
                            titolo,
                            textAlign: TextAlign.center,
                            style: Stile.sans(13.44, colore: Token.ink),
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

/* ---- genere e persona ricordata ---------------------------------------------------------------------------------- */

class _Genere extends ConsumerStatefulWidget {
  const _Genere({required this.p, required this.ricarica});

  final Profilo p;
  final VoidCallback ricarica;

  @override
  ConsumerState<_Genere> createState() => _GenereState();
}

class _GenereState extends ConsumerState<_Genere> with AzioneAccount {
  String? _genere;
  late final TextEditingController _altro = TextEditingController(text: widget.p.genderCustom ?? '');
  bool _altroCambiato = false;
  bool? _trans;

  @override
  void dispose() {
    _altro.dispose();
    super.dispose();
  }

  Future<void> _dimentica() async {
    final t = context.t;
    final si = await apriModale<bool>(
      context,
      titolo: t.profilo_partner_conferma,
      costruisci: (context) => FilaBottoni(
        children: [
          Bottone(
            t.profilo_partner_dimentica,
            variante: Variante.pericolo,
            alTocco: () => Navigator.of(context).pop(true),
          ),
          Bottone(t.comune_annulla, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop(false)),
        ],
      ),
    );
    if (si != true) return;
    await esegui((api) async {
      await api.cancellaPartner();
      return true;
    });
    widget.ricarica();
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final p = widget.p;
    final lingua = ref.watch(linguaProvider);
    final genere = _genere ?? p.gender ?? '';
    final trans = _trans ?? p.isTrans;
    final cambiato = _genere != null || _altroCambiato || _trans != null;
    final partner = p.partnerRicordato;
    return Sezione(
      titolo: t.profilo_genere_titolo,
      id: 'genere',
      children: [
        TestoPiccolo(t.profilo_genere_testo),
        CampiGenere(
          genere: genere,
          altro: _altro,
          trans: trans,
          alGenere: (g) => setState(() => _genere = g),
          alAltro: (_) => setState(() => _altroCambiato = true),
          alTrans: (v) => setState(() => _trans = v),
        ),
        _Provenienza(p: p, campo: 'gender'),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(
            t.comune_salva,
            piccolo: true,
            alTocco: inCorso || genere.isEmpty || !cambiato
                ? null
                : () async {
                    await esegui(
                      (api) => api.aggiornaProfilo({
                        'gender': genere,
                        'gender_custom': genere == 'altro' ? _altro.text : null,
                        'is_trans': trans,
                      }),
                    );
                    setState(() {
                      _genere = null;
                      _altroCambiato = false;
                      _trans = null;
                    });
                    widget.ricarica();
                  },
          ),
        ),
        Padding(padding: const EdgeInsets.only(top: 8.8), child: TitoloPannello(t.profilo_partner_titolo)),
        if (partner != null) ...[
          TestoPiccolo(
            '${[partner.nome, partner.cognome].whereType<String>().where((s) => s.isNotEmpty).join(' ')}'
            ' · ${dataLunga(partner.nascita, lingua)}',
          ),
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: Bottone(
              t.profilo_partner_dimentica,
              variante: Variante.pericolo,
              piccolo: true,
              alTocco: () => unawaited(_dimentica()),
            ),
          ),
        ] else
          TestoPiccolo(t.profilo_partner_vuoto, tenue: true, sotto: 0),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

/* ---- registro e mazzo --------------------------------------------------------------------------------------------- */

class _Registro extends ConsumerStatefulWidget {
  const _Registro({required this.p, required this.ricarica});

  final Profilo p;
  final VoidCallback ricarica;

  @override
  ConsumerState<_Registro> createState() => _RegistroState();
}

class _RegistroState extends ConsumerState<_Registro> with AzioneAccount {
  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final p = widget.p;
    final tutti = ref.watch(mazziProvider).value ?? const <Mazzo>[];
    final miei = ref.watch(mieiMazziProvider).value ?? const <int>[];
    final utilizzabili = tutti.where((m) => m.predefinito || m.prezzoDigitale == null || miei.contains(m.id)).toList();
    return Sezione(
      titolo: t.profilo_registro_titolo,
      id: 'registro',
      children: [
        TestoPiccolo(t.profilo_registro_testo),
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: SceltaSemplice<String>(
            etichetta: t.profilo_registro_titolo,
            voci: [('esoterico', t.profilo_registro_esoterico), ('quotidiano', t.profilo_registro_quotidiano)],
            valore: p.registroLinguistico,
            attiva: !inCorso,
            alCambio: (v) async {
              await esegui((api) => api.aggiornaProfilo({'registro_linguistico': v}));
              widget.ricarica();
            },
          ),
        ),
        if (utilizzabili.length > 1) ...[
          TitoloPannello(t.profilo_mazzo_titolo),
          TestoPiccolo(t.profilo_mazzo_testo),
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: SceltaSemplice<int>(
              etichetta: t.profilo_mazzo_titolo,
              voci: [
                for (final m in utilizzabili)
                  (m.predefinito ? 0 : m.id, m.predefinito ? '${m.nome} ${t.profilo_mazzo_predefinito}' : m.nome),
              ],
              valore: p.mazzoPredefinitoId ?? 0,
              attiva: !inCorso,
              alCambio: (id) async {
                await esegui((api) => api.aggiornaProfilo({'mazzo_predefinito_id': id}));
                widget.ricarica();
              },
            ),
          ),
        ],
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

/* ---- inviti e condivisioni ----------------------------------------------------------------------------------------- */

class _Invito extends ConsumerStatefulWidget {
  const _Invito({required this.p, required this.ricarica});

  final Profilo p;
  final VoidCallback ricarica;

  @override
  ConsumerState<_Invito> createState() => _InvitoState();
}

class _InvitoState extends ConsumerState<_Invito> with AzioneAccount {
  final TextEditingController _codice = TextEditingController();
  String? _esito;
  bool _componendo = false;

  @override
  void initState() {
    super.initState();
    // Il codice arrivato con un collegamento d'invito (`?invito=`), come `leggiInvito()` del sito.
    _codice.text = leggiInvito(ref.read(archivioProvider)) ?? '';
    _codice.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _codice.dispose();
    super.dispose();
  }

  String get _invito => '${Config.sitoPubblico}${R.home}?invito=${widget.p.referralCode ?? ''}';

  Future<void> _condividi(BuildContext bottone) async {
    final t = context.t;
    await ref.read(condivisioneProvider)(
      ShareParams(
        title: 'TAROTS chat',
        text: '${t.profilo_invito_testo_condivisione(widget.p.referralCode ?? '')}\n$_invito',
        sharePositionOrigin: origineCondivisione(bottone),
      ),
    );
  }

  Future<void> _bigliettino(BuildContext bottone, int? omaggio) async {
    final t = context.t;
    final codice = widget.p.referralCode;
    if (codice == null) return;
    setState(() => _componendo = true);
    try {
      final png = await componiBigliettino(
        codice,
        t.profilo_bigliettino_claim,
        omaggio == null ? '' : t.profilo_bigliettino_omaggio(omaggio),
      );
      if (png != null && bottone.mounted) {
        await condividiFile(ref, bottone, byte: png, nome: 'tarots-chat-invite-$codice.png', tipo: 'image/png');
      }
    } finally {
      if (mounted) setState(() => _componendo = false);
    }
  }

  Future<void> _riscatta() async {
    final t = context.t;
    final r = await esegui((api) => api.riscattaInvito(_codice.text));
    if (r == null || !mounted) return;
    unawaited(ref.read(archivioProvider).scrivi(chiaveInvito, null));
    setState(() => _esito = t.profilo_regalo(r.crediti));
    widget.ricarica();
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final p = widget.p;
    final c = p.condivisioni;
    final omaggi = ref.watch(impostazioniProvider).value;
    final w = MediaQuery.sizeOf(context).width;
    final fatte = (c.soglia - c.prossimoTra).clamp(0, c.soglia);
    final piccolo = Stile.sans(12.8, colore: Token.inkSoft);

    Widget numero(int n, String etichetta) => Container(
      padding: const EdgeInsets.all(16),
      color: Token.paperLight,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('$n', style: Stile.serif(28.8, colore: Token.ink)),
          Text(etichetta, style: piccolo),
        ],
      ),
    );

    return Sezione(
      titolo: t.profilo_invito_titolo,
      id: 'invito',
      children: [
        if (omaggi != null) ...[
          TestoPiccolo(t.profilo_invito_testo(omaggi.creditiIscrizione, omaggi.creditiInvito)),
          TestoPiccolo(t.profilo_invito_commissione(omaggi.commissioneReferralPercentuale)),
        ],
        // `.invite-code`
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12.8),
          child: Text(p.referralCode ?? '', style: Stile.serif(28.8, colore: Token.plum, em: .12)),
        ),
        Builder(
          builder: (bottone) => FilaBottoni(
            children: [
              Bottone(
                t.profilo_invito_condividi,
                piccolo: true,
                an: 'share_started',
                anProprieta: const {'cosa': 'invito'},
                alTocco: () => unawaited(_condividi(bottone)),
              ),
              Bottone(
                t.profilo_bigliettino,
                piccolo: true,
                variante: Variante.quieto,
                alTocco: _componendo || p.referralCode == null
                    ? null
                    : () => unawaited(_bigliettino(bottone, omaggi?.creditiInvito)),
              ),
            ],
          ),
        ),
        if (!p.invitato)
          RigaFlessibile(
            sopra: 16,
            pezzi: [
              (
                widget: CampoTesto(
                  etichetta: t.profilo_hai_codice,
                  controllore: _codice,
                  lunghezzaMassima: 16,
                  maiuscole: true,
                  margineSotto: 0,
                ),
                base: 190,
                cresce: false,
              ),
              (
                widget: Bottone(
                  t.profilo_riscatta,
                  piccolo: true,
                  alTocco: inCorso || _codice.text.length < 4 ? null : () => unawaited(_riscatta()),
                ),
                base: larghezzaBottonePiccolo(context, t.profilo_riscatta),
                cresce: false,
              ),
            ],
          ),
        if (_esito != null) Successo(_esito!),
        if (errore != null) Errore(errore!),
        Padding(padding: const EdgeInsets.only(top: 8.8), child: TitoloPannello(t.profilo_cond_titolo)),
        TestoPiccolo(t.profilo_cond_testo(c.soglia, c.creditiIscrizione)),
        // `.stat-bar`
        Semantics(
          label: t.profilo_cond_titolo,
          value: '$fatte / ${c.soglia}',
          child: Container(
            height: 6,
            margin: const EdgeInsets.only(bottom: 4.8),
            color: const Color(0x1F3C1846),
            alignment: Alignment.centerLeft,
            child: FractionallySizedBox(
              widthFactor: c.soglia == 0 ? 0 : fatte / c.soglia,
              child: const ColoredBox(color: Token.brass, child: SizedBox.expand()),
            ),
          ),
        ),
        TestoPiccolo(t.profilo_cond_prossimo(c.prossimoTra)),
        // `.stat-row`: tre numeri (una colonna sul telefono), separati da una riga sottile.
        Container(
          decoration: BoxDecoration(
            color: Token.line,
            border: Border.all(color: Token.line),
          ),
          padding: const EdgeInsets.all(1),
          child: w.telefono
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    numero(c.verificate, t.profilo_cond_verificate),
                    const SizedBox(height: 1),
                    numero(c.premi, t.profilo_cond_premi),
                    const SizedBox(height: 1),
                    numero(c.iscrizioni, t.profilo_cond_iscritti),
                  ],
                )
              : IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(child: numero(c.verificate, t.profilo_cond_verificate)),
                      const SizedBox(width: 1),
                      Expanded(child: numero(c.premi, t.profilo_cond_premi)),
                      const SizedBox(width: 1),
                      Expanded(child: numero(c.iscrizioni, t.profilo_cond_iscritti)),
                    ],
                  ),
                ),
        ),
      ],
    );
  }
}

/* ---- immagine e nome pubblico -------------------------------------------------------------------------------------- */

class _Immagine extends ConsumerStatefulWidget {
  const _Immagine({required this.p, required this.ricarica});

  final Profilo p;
  final VoidCallback ricarica;

  @override
  ConsumerState<_Immagine> createState() => _ImmagineState();
}

class _ImmagineState extends ConsumerState<_Immagine> with AzioneAccount {
  late final TextEditingController _nome = TextEditingController(text: widget.p.nomePubblico ?? '');
  bool _cambiato = false;
  bool _salvato = false;
  bool _erroreAvatar = false;

  @override
  void dispose() {
    _nome.dispose();
    super.dispose();
  }

  Future<void> _carica() async {
    final scelta = await ref.read(sceltaImmagineProvider)();
    if (scelta == null) return;
    setState(() => _erroreAvatar = false);
    final r = await esegui((api) async => await api.caricaAvatar(scelta.byte, scelta.tipo) ?? '');
    if (!mounted) return;
    if (r != null) {
      widget.ricarica();
    } else {
      setState(() {
        _erroreAvatar = true;
        errore = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final p = widget.p;
    final iniziale = p.nomeMostrato.isEmpty ? '?' : p.nomeMostrato.characters.first.toUpperCase();
    return Sezione(
      titolo: t.profilo_avatar_titolo,
      id: 'immagine',
      children: [
        TestoPiccolo(t.profilo_avatar_testo),
        Wrap(
          spacing: 9.6,
          runSpacing: 9.6,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            if (p.avatar != null)
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(border: Border.all(color: Colori.cornice, width: 2)),
                child: Image(
                  image: ref.watch(immagineMediaProvider)(p.avatar!),
                  fit: BoxFit.cover,
                  excludeFromSemantics: true,
                  errorBuilder: (context, e, s) => const ColoredBox(color: Token.plum),
                ),
              )
            else
              ExcludeSemantics(
                child: Container(
                  width: 72,
                  height: 72,
                  alignment: Alignment.center,
                  color: Token.plum,
                  child: Text(iniziale, style: Stile.serif(28.8, colore: const Color(0xFFFFF7E8))),
                ),
              ),
            Bottone(
              t.profilo_avatar_carica,
              variante: Variante.quieto,
              piccolo: true,
              alTocco: inCorso ? null : () => unawaited(_carica()),
            ),
            if (p.avatar != null)
              Bottone(
                t.profilo_avatar_togli,
                variante: Variante.quieto,
                piccolo: true,
                alTocco: inCorso
                    ? null
                    : () async {
                        await esegui((api) async {
                          await api.togliAvatar();
                          return true;
                        });
                        widget.ricarica();
                      },
              ),
          ],
        ),
        if (_erroreAvatar) Errore(t.profilo_avatar_errore),
        RigaFlessibile(
          sopra: 16,
          pezzi: [
            (
              widget: _CampoNomePubblico(
                etichetta: t.profilo_nome_pubblico,
                controllore: _nome,
                segnaposto: p.nomeMostrato,
                alCambio: () => setState(() {
                  _cambiato = true;
                  _salvato = false;
                }),
              ),
              base: 190,
              cresce: false,
            ),
            (
              widget: Bottone(
                t.comune_salva,
                piccolo: true,
                alTocco: inCorso || !_cambiato
                    ? null
                    : () async {
                        final r = await esegui((api) => api.aggiornaProfilo({'nome_pubblico': _nome.text}));
                        if (r == null || !mounted) return;
                        setState(() {
                          _salvato = true;
                          _cambiato = false;
                        });
                        widget.ricarica();
                      },
              ),
              base: larghezzaBottonePiccolo(context, t.comune_salva),
              cresce: false,
            ),
          ],
        ),
        TestoPiccolo(t.profilo_nome_pubblico_testo, tenue: true, sopra: 13.44, sotto: 0),
        if (_salvato) Successo(t.profilo_nome_salvato),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

class _CampoNomePubblico extends StatelessWidget {
  const _CampoNomePubblico({
    required this.etichetta,
    required this.controllore,
    required this.segnaposto,
    required this.alCambio,
  });

  final String etichetta;
  final TextEditingController controllore;
  final String segnaposto;
  final VoidCallback alCambio;

  @override
  Widget build(BuildContext context) => CampoTesto(
    etichetta: etichetta,
    controllore: controllore,
    segnaposto: segnaposto,
    lunghezzaMassima: 60,
    margineSotto: 0,
    alCambio: (_) => alCambio(),
  );
}

/* ---- ordini ------------------------------------------------------------------------------------------------------- */

/// `.memory-entry`: una voce d'elenco con l'occhiello, il titolo serif e il testo, la riga sotto.
class _Voce extends StatelessWidget {
  const _Voce({this.occhiello, required this.titolo, required this.children});

  final String? occhiello;
  final String titolo;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return Container(
      padding: EdgeInsets.symmetric(vertical: w.telefono ? 12.8 : 17.6),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Token.line)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (occhiello != null)
            Text(
              occhiello!.toUpperCase(),
              style: Stile.sans(11.52, peso: FontWeight.w700, em: .05, colore: Token.verdigris),
            ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.8),
            child: Text(titolo, style: Stile.serif(17.6, colore: Token.ink)),
          ),
          ...children,
        ],
      ),
    );
  }
}

class _Ordini extends ConsumerWidget {
  const _Ordini();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final elenco = ref.watch(ordiniProvider).value ?? const <Ordine>[];
    final mazzi = ref.watch(mazziProvider).value ?? const <Mazzo>[];
    String nome(int id) => mazzi.where((m) => m.id == id).firstOrNull?.nome ?? '#$id';
    final piccolo = Stile.sans(13.44, colore: Token.ink, altezza: 1.6);
    return Sezione(
      titolo: t.profilo_ordini_titolo,
      id: 'ordini',
      children: [
        if (elenco.isEmpty)
          TestoPiccolo(t.profilo_ordini_vuoto, tenue: true, sotto: 0)
        else
          for (final o in elenco)
            _Voce(
              occhiello:
                  '${o.creato == null ? '' : DateFormat.yMd(localeIntl(lingua)).format(DateTime.parse(o.creato!).toLocal())}'
                  ' · ${t.profiloOrdiniStato[o.status] ?? o.status}',
              titolo: euro(o.importoTotale, lingua, valuta: o.valuta),
              children: [
                for (final r in o.righe)
                  Text(
                    '${r.mazzo?.nome ?? nome(r.deckId)} — ${t.profiloOrdiniTipo[r.tipo] ?? r.tipo}'
                    '${r.quantita > 1 ? ' × ${r.quantita}' : ''}'
                    '${r.tipo == 'fisico' && r.statoEvasione != null ? ' · ${t.profiloOrdiniEvasione[r.statoEvasione] ?? r.statoEvasione}' : ''}',
                    style: piccolo,
                  ),
                if (o.scontoScaglioni > 0)
                  TestoPiccolo(
                    '−${euro(o.scontoScaglioni, lingua, valuta: o.valuta)} (${t.profilo_ordini_sconto})',
                    sopra: 13.44,
                    sotto: 0,
                  ),
                if (o.status == 'pagato')
                  for (final r in o.righe.where((r) => r.tipo == 'pdf'))
                    _BottonePdf(ordineId: o.id, deckId: r.deckId, nome: r.mazzo?.nome ?? nome(r.deckId)),
              ],
            ),
      ],
    );
  }
}

/// Il PDF «Stampa i tuoi Tarocchi» di una riga pagata: scaricato e passato al foglio del telefono.
class _BottonePdf extends ConsumerStatefulWidget {
  const _BottonePdf({required this.ordineId, required this.deckId, required this.nome});

  final String ordineId;
  final int deckId;
  final String nome;

  @override
  ConsumerState<_BottonePdf> createState() => _BottonePdfState();
}

class _BottonePdfState extends ConsumerState<_BottonePdf> {
  bool _inCorso = false;
  bool _errore = false;

  Future<void> _scarica(BuildContext bottone) async {
    setState(() {
      _inCorso = true;
      _errore = false;
    });
    try {
      final r = await ref.read(apiProvider).pdfOrdine(widget.ordineId, widget.deckId);
      if (bottone.mounted) {
        await condividiFile(
          ref,
          bottone,
          byte: r.byte,
          nome: r.nome ?? '${widget.nome.isEmpty ? 'deck' : widget.nome}.pdf',
          tipo: 'application/pdf',
        );
      }
    } on Object {
      if (mounted) setState(() => _errore = true);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Builder(
            builder: (bottone) => Bottone(
              _inCorso
                  ? t.negozio_pdf_in_corso
                  : '${t.negozio_scarica_pdf}${widget.nome.isEmpty ? '' : ' — ${widget.nome}'}',
              variante: Variante.quieto,
              piccolo: true,
              an: 'deck_pdf_viewed',
              alTocco: _inCorso ? null : () => unawaited(_scarica(bottone)),
            ),
          ),
          if (_errore) Errore(t.negozio_pdf_errore),
        ],
      ),
    );
  }
}

/* ---- indirizzi ---------------------------------------------------------------------------------------------------- */

class _Indirizzi extends ConsumerStatefulWidget {
  const _Indirizzi();

  @override
  ConsumerState<_Indirizzi> createState() => _IndirizziState();
}

class _IndirizziState extends ConsumerState<_Indirizzi> with AzioneAccount {
  bool _aggiunta = false;
  final Map<String, TextEditingController> _campi = {
    for (final k in ['nome', 'via', 'citta', 'cap', 'provincia', 'paese', 'telefono']) k: TextEditingController(),
  };

  @override
  void initState() {
    super.initState();
    for (final c in _campi.values) {
      c.addListener(() => setState(() {}));
    }
  }

  @override
  void dispose() {
    for (final c in _campi.values) {
      c.dispose();
    }
    super.dispose();
  }

  String _v(String k) => _campi[k]!.text;

  bool get _pronto =>
      _v('nome').trim().isNotEmpty &&
      _v('via').trim().isNotEmpty &&
      _v('citta').trim().isNotEmpty &&
      _v('cap').trim().isNotEmpty &&
      _v('paese').trim().length == 2;

  Future<void> _salva() async {
    final dati = <String, Object?>{
      for (final k in ['nome', 'via', 'citta', 'cap', 'paese']) k: _v(k),
      if (_v('provincia').isNotEmpty) 'provincia': _v('provincia'),
      if (_v('telefono').isNotEmpty) 'telefono': _v('telefono'),
    };
    final r = await esegui((api) => api.creaIndirizzo(dati));
    if (r == null || !mounted) return;
    setState(() => _aggiunta = false);
    for (final c in _campi.values) {
      c.clear();
    }
    ref.invalidate(indirizziProvider);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final elenco = ref.watch(indirizziProvider).value ?? const <Indirizzo>[];
    final w = MediaQuery.sizeOf(context).width;
    Widget campo(String k, String etichetta, {int? massimo, bool maiuscole = false, TextInputType? tastiera}) =>
        CampoTesto(
          etichetta: etichetta,
          controllore: _campi[k],
          lunghezzaMassima: massimo,
          maiuscole: maiuscole,
          tastiera: tastiera,
        );
    // `.form-grid`: due colonne oltre 760 px.
    Widget coppia(Widget a, Widget b) => w.telefono
        ? Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [a, b])
        : Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: a),
              const SizedBox(width: 16),
              Expanded(child: b),
            ],
          );
    return Sezione(
      titolo: t.profilo_indirizzi_titolo,
      id: 'indirizzi',
      children: [
        TestoPiccolo(t.profilo_indirizzi_testo),
        if (elenco.isEmpty && !_aggiunta) TestoPiccolo(t.profilo_indirizzi_vuoto, tenue: true, sotto: 0),
        for (final i in elenco)
          _Voce(
            occhiello: i.predefinito ? t.profilo_indirizzi_predefinito : null,
            titolo: i.nome,
            children: [
              Text(
                '${i.via}, ${i.cap} ${i.citta}${i.provincia == null ? '' : ' (${i.provincia})'}, ${i.paese}',
                style: Stile.sans(14.08, colore: Token.inkSoft),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: FilaBottoni(
                  children: [
                    if (!i.predefinito)
                      Bottone(
                        t.profilo_indirizzi_imposta,
                        variante: Variante.quieto,
                        piccolo: true,
                        alTocco: inCorso
                            ? null
                            : () async {
                                await esegui((api) => api.modificaIndirizzo(i.id, {'predefinito': true}));
                                ref.invalidate(indirizziProvider);
                              },
                      ),
                    Bottone(
                      t.profilo_indirizzi_elimina,
                      variante: Variante.pericolo,
                      piccolo: true,
                      alTocco: inCorso
                          ? null
                          : () async {
                              await esegui((api) async {
                                await api.eliminaIndirizzo(i.id);
                                return true;
                              });
                              ref.invalidate(indirizziProvider);
                            },
                    ),
                  ],
                ),
              ),
            ],
          ),
        if (_aggiunta)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                campo('nome', t.profilo_indirizzi_nome),
                campo('via', t.profilo_indirizzi_via),
                coppia(campo('citta', t.profilo_indirizzi_citta), campo('cap', t.profilo_indirizzi_cap)),
                coppia(
                  campo('provincia', t.profilo_indirizzi_provincia),
                  campo('paese', t.profilo_indirizzi_paese, massimo: 2, maiuscole: true),
                ),
                campo('telefono', t.profilo_indirizzi_telefono, tastiera: TextInputType.phone),
                FilaBottoni(
                  children: [
                    Bottone(
                      t.profilo_indirizzi_salva,
                      piccolo: true,
                      alTocco: inCorso || !_pronto ? null : () => unawaited(_salva()),
                    ),
                    Bottone(
                      t.comune_annulla,
                      variante: Variante.quieto,
                      piccolo: true,
                      alTocco: () => setState(() => _aggiunta = false),
                    ),
                  ],
                ),
                if (errore != null) Errore(errore!),
              ],
            ),
          )
        else
          Padding(
            padding: const EdgeInsets.only(top: 12.8),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: Bottone(
                t.profilo_indirizzi_aggiungi,
                variante: Variante.quieto,
                piccolo: true,
                alTocco: () => setState(() => _aggiunta = true),
              ),
            ),
          ),
      ],
    );
  }
}

/* ---- statistiche -------------------------------------------------------------------------------------------------- */

class _Statistiche extends ConsumerStatefulWidget {
  const _Statistiche();

  @override
  ConsumerState<_Statistiche> createState() => _StatisticheState();
}

class _StatisticheState extends ConsumerState<_Statistiche> with AzioneAccount {
  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final opposizione = ref.watch(opposizioneProvider).value;
    if (opposizione == null) return const SizedBox.shrink();
    return Sezione(
      titolo: t.profilo_stat_titolo,
      id: 'statistiche',
      children: [
        TestoPiccolo(
          t.profilo_stat_testo,
          figlio: Collegamento(t.profilo_stat_privacy, href: R.privacy, stile: Stile.sans(13.44, altezza: 1.6)),
        ),
        Casella(
          valore: opposizione,
          attiva: !inCorso,
          titolo: t.profilo_stat_opponi,
          alCambio: (v) async {
            await esegui((api) => api.impostaOpposizioneStatistiche(v));
            ref.invalidate(opposizioneProvider);
          },
        ),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}
