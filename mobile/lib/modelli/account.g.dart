// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'account.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_PersonaSalvata _$PersonaSalvataFromJson(Map<String, dynamic> json) =>
    _PersonaSalvata(
      nome: json['nome'] as String,
      cognome: json['cognome'] as String?,
      genere: json['genere'] as String,
      genereAltro: json['genere_altro'] as String?,
      trans: json['trans'] as bool? ?? false,
      nascita: json['nascita'] as String,
    );

Map<String, dynamic> _$PersonaSalvataToJson(_PersonaSalvata instance) =>
    <String, dynamic>{
      'nome': instance.nome,
      'cognome': ?instance.cognome,
      'genere': instance.genere,
      'genere_altro': ?instance.genereAltro,
      'trans': instance.trans,
      'nascita': instance.nascita,
    };

_Condivisioni _$CondivisioniFromJson(Map<String, dynamic> json) =>
    _Condivisioni(
      verificate: (json['verificate'] as num?)?.toInt() ?? 0,
      premi: (json['premi'] as num?)?.toInt() ?? 0,
      prossimoTra: (json['prossimo_tra'] as num?)?.toInt() ?? 0,
      iscrizioni: (json['iscrizioni'] as num?)?.toInt() ?? 0,
      soglia: (json['soglia'] as num?)?.toInt() ?? 5,
      creditiIscrizione: (json['crediti_iscrizione'] as num?)?.toInt() ?? 5,
    );

Map<String, dynamic> _$CondivisioniToJson(_Condivisioni instance) =>
    <String, dynamic>{
      'verificate': instance.verificate,
      'premi': instance.premi,
      'prossimo_tra': instance.prossimoTra,
      'iscrizioni': instance.iscrizioni,
      'soglia': instance.soglia,
      'crediti_iscrizione': instance.creditiIscrizione,
    };

_PosizioneAttuale _$PosizioneAttualeFromJson(Map<String, dynamic> json) =>
    _PosizioneAttuale(
      paese: json['paese'] as String?,
      citta: json['citta'] as String?,
      fonte: json['fonte'] as String?,
      il: json['il'] as String?,
    );

Map<String, dynamic> _$PosizioneAttualeToJson(_PosizioneAttuale instance) =>
    <String, dynamic>{
      'paese': ?instance.paese,
      'citta': ?instance.citta,
      'fonte': ?instance.fonte,
      'il': ?instance.il,
    };

_Relazioni _$RelazioniFromJson(Map<String, dynamic> json) => _Relazioni(
  completo: json['completo'] as bool? ?? true,
  mancanti:
      (json['mancanti'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const <String>[],
);

Map<String, dynamic> _$RelazioniToJson(_Relazioni instance) =>
    <String, dynamic>{
      'completo': instance.completo,
      'mancanti': instance.mancanti,
    };

_OrigineDato _$OrigineDatoFromJson(Map<String, dynamic> json) =>
    _OrigineDato(da: json['da'] as String, il: json['il'] as String);

Map<String, dynamic> _$OrigineDatoToJson(_OrigineDato instance) =>
    <String, dynamic>{'da': instance.da, 'il': instance.il};

_Profilo _$ProfiloFromJson(Map<String, dynamic> json) => _Profilo(
  id: (json['id'] as num).toInt(),
  email: json['email'] as String?,
  displayName: json['display_name'] as String?,
  locale: json['locale'] as String? ?? 'it',
  varianteLettura: json['variante_lettura'] as String?,
  localeSceltaIl: json['locale_scelta_il'] as String?,
  birthDate: json['birth_date'] as String?,
  gender: json['gender'] as String?,
  genderCustom: json['gender_custom'] as String?,
  isTrans: json['is_trans'] as bool? ?? false,
  promemoria2fa: json['promemoria_2fa'] as bool? ?? true,
  nomePubblico: json['nome_pubblico'] as String?,
  registroLinguistico: json['registro_linguistico'] as String? ?? 'esoterico',
  mazzoPredefinitoId: (json['mazzo_predefinito_id'] as num?)?.toInt(),
  nomeMostrato: json['nome_mostrato'] as String? ?? '',
  avatar: json['avatar'] as String?,
  partnerRicordato: json['partner_ricordato'] == null
      ? null
      : PersonaSalvata.fromJson(
          json['partner_ricordato'] as Map<String, dynamic>,
        ),
  relazioni: json['relazioni'] == null
      ? const Relazioni()
      : Relazioni.fromJson(json['relazioni'] as Map<String, dynamic>),
  referralCode: json['referral_code'] as String?,
  invitato: json['invitato'] as bool? ?? false,
  condivisioni: json['condivisioni'] == null
      ? const Condivisioni()
      : Condivisioni.fromJson(json['condivisioni'] as Map<String, dynamic>),
  cartaAnima: json['carta_anima'] == null
      ? null
      : Carta.fromJson(json['carta_anima'] as Map<String, dynamic>),
  cartaAnno: json['carta_anno'] == null
      ? null
      : Carta.fromJson(json['carta_anno'] as Map<String, dynamic>),
  nome: json['nome'] as String?,
  cognome: json['cognome'] as String?,
  posizione: json['posizione'] == null
      ? null
      : PosizioneAttuale.fromJson(json['posizione'] as Map<String, dynamic>),
  datiSocial:
      (json['dati_social'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, OrigineDato.fromJson(e as Map<String, dynamic>)),
      ) ??
      const <String, OrigineDato>{},
  importaSocial: json['importa_social'] as bool?,
  rilevaPosizione: json['rileva_posizione'] as bool?,
);

Map<String, dynamic> _$ProfiloToJson(_Profilo instance) => <String, dynamic>{
  'id': instance.id,
  'email': ?instance.email,
  'display_name': ?instance.displayName,
  'locale': instance.locale,
  'variante_lettura': ?instance.varianteLettura,
  'locale_scelta_il': ?instance.localeSceltaIl,
  'birth_date': ?instance.birthDate,
  'gender': ?instance.gender,
  'gender_custom': ?instance.genderCustom,
  'is_trans': instance.isTrans,
  'promemoria_2fa': instance.promemoria2fa,
  'nome_pubblico': ?instance.nomePubblico,
  'registro_linguistico': instance.registroLinguistico,
  'mazzo_predefinito_id': ?instance.mazzoPredefinitoId,
  'nome_mostrato': instance.nomeMostrato,
  'avatar': ?instance.avatar,
  'partner_ricordato': ?instance.partnerRicordato?.toJson(),
  'relazioni': instance.relazioni.toJson(),
  'referral_code': ?instance.referralCode,
  'invitato': instance.invitato,
  'condivisioni': instance.condivisioni.toJson(),
  'carta_anima': ?instance.cartaAnima?.toJson(),
  'carta_anno': ?instance.cartaAnno?.toJson(),
  'nome': ?instance.nome,
  'cognome': ?instance.cognome,
  'posizione': ?instance.posizione?.toJson(),
  'dati_social': instance.datiSocial.map((k, e) => MapEntry(k, e.toJson())),
  'importa_social': ?instance.importaSocial,
  'rileva_posizione': ?instance.rilevaPosizione,
};

_Dignita _$DignitaFromJson(Map<String, dynamic> json) => _Dignita(
  elemento: json['elemento'] as String,
  punteggio: json['punteggio'] as num,
  giudizio: json['giudizio'] as String,
  relazioni:
      (json['relazioni'] as List<dynamic>?)
          ?.map((e) => RelazioneDignita.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <RelazioneDignita>[],
);

Map<String, dynamic> _$DignitaToJson(_Dignita instance) => <String, dynamic>{
  'elemento': instance.elemento,
  'punteggio': instance.punteggio,
  'giudizio': instance.giudizio,
  'relazioni': instance.relazioni.map((e) => e.toJson()).toList(),
};

_RelazioneDignita _$RelazioneDignitaFromJson(Map<String, dynamic> json) =>
    _RelazioneDignita(
      posizione: (json['posizione'] as num).toInt(),
      elemento: json['elemento'] as String,
      relazione: json['relazione'] as String,
    );

Map<String, dynamic> _$RelazioneDignitaToJson(_RelazioneDignita instance) =>
    <String, dynamic>{
      'posizione': instance.posizione,
      'elemento': instance.elemento,
      'relazione': instance.relazione,
    };

_CartaPosata _$CartaPosataFromJson(Map<String, dynamic> json) => _CartaPosata(
  posizione: (json['posizione'] as num).toInt(),
  calcolata: json['calcolata'] as bool,
  rivelata: json['rivelata'] as bool,
  carta: json['carta'] == null
      ? null
      : Carta.fromJson(json['carta'] as Map<String, dynamic>),
  rovescio: json['rovescio'] as bool?,
  interpretazione: json['interpretazione'] as String?,
);

Map<String, dynamic> _$CartaPosataToJson(_CartaPosata instance) =>
    <String, dynamic>{
      'posizione': instance.posizione,
      'calcolata': instance.calcolata,
      'rivelata': instance.rivelata,
      'carta': ?instance.carta?.toJson(),
      'rovescio': ?instance.rovescio,
      'interpretazione': ?instance.interpretazione,
    };

_TurnoIntervista _$TurnoIntervistaFromJson(Map<String, dynamic> json) =>
    _TurnoIntervista(
      ruolo: json['ruolo'] as String,
      testo: json['testo'] as String,
      ordine: (json['ordine'] as num).toInt(),
    );

Map<String, dynamic> _$TurnoIntervistaToJson(_TurnoIntervista instance) =>
    <String, dynamic>{
      'ruolo': instance.ruolo,
      'testo': instance.testo,
      'ordine': instance.ordine,
    };

_PersonaTu _$PersonaTuFromJson(Map<String, dynamic> json) => _PersonaTu(
  genere: json['genere'] as String?,
  genereAltro: json['genere_altro'] as String?,
  trans: json['trans'] as bool? ?? false,
  nascita: json['nascita'] as String,
);

Map<String, dynamic> _$PersonaTuToJson(_PersonaTu instance) =>
    <String, dynamic>{
      'genere': ?instance.genere,
      'genere_altro': ?instance.genereAltro,
      'trans': instance.trans,
      'nascita': instance.nascita,
    };

_PersoneLettura _$PersoneLetturaFromJson(Map<String, dynamic> json) =>
    _PersoneLettura(
      v: (json['v'] as num?)?.toInt() ?? 1,
      tu: PersonaTu.fromJson(json['tu'] as Map<String, dynamic>),
      partner: PersonaSalvata.fromJson(json['partner'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$PersoneLetturaToJson(_PersoneLettura instance) =>
    <String, dynamic>{
      'v': instance.v,
      'tu': instance.tu.toJson(),
      'partner': instance.partner.toJson(),
    };

_SegnoCalcolato _$SegnoCalcolatoFromJson(Map<String, dynamic> json) =>
    _SegnoCalcolato(
      codice: json['codice'] as String,
      elemento: json['elemento'] as String,
      modalita: json['modalita'] as String,
      cuspide: json['cuspide'] as bool? ?? false,
      vicino: json['vicino'] as String?,
    );

Map<String, dynamic> _$SegnoCalcolatoToJson(_SegnoCalcolato instance) =>
    <String, dynamic>{
      'codice': instance.codice,
      'elemento': instance.elemento,
      'modalita': instance.modalita,
      'cuspide': instance.cuspide,
      'vicino': ?instance.vicino,
    };

_SegniCoppia _$SegniCoppiaFromJson(Map<String, dynamic> json) => _SegniCoppia(
  tu: SegnoCalcolato.fromJson(json['tu'] as Map<String, dynamic>),
  partner: SegnoCalcolato.fromJson(json['partner'] as Map<String, dynamic>),
);

Map<String, dynamic> _$SegniCoppiaToJson(_SegniCoppia instance) =>
    <String, dynamic>{
      'tu': instance.tu.toJson(),
      'partner': instance.partner.toJson(),
    };

_Compatibilita _$CompatibilitaFromJson(Map<String, dynamic> json) =>
    _Compatibilita(
      segni: SegniCoppia.fromJson(json['segni'] as Map<String, dynamic>),
      distanza: (json['distanza'] as num).toInt(),
      aspetto: json['aspetto'] as String,
      relazioneElementi: json['relazione_elementi'] as String,
      stessaModalita: json['stessa_modalita'] as bool? ?? false,
      armonia: json['armonia'] as String,
      cartaCoppia: Carta.fromJson(json['carta_coppia'] as Map<String, dynamic>),
      cartaAnimaTu: Carta.fromJson(
        json['carta_anima_tu'] as Map<String, dynamic>,
      ),
      cartaAnimaPartner: Carta.fromJson(
        json['carta_anima_partner'] as Map<String, dynamic>,
      ),
    );

Map<String, dynamic> _$CompatibilitaToJson(_Compatibilita instance) =>
    <String, dynamic>{
      'segni': instance.segni.toJson(),
      'distanza': instance.distanza,
      'aspetto': instance.aspetto,
      'relazione_elementi': instance.relazioneElementi,
      'stessa_modalita': instance.stessaModalita,
      'armonia': instance.armonia,
      'carta_coppia': instance.cartaCoppia.toJson(),
      'carta_anima_tu': instance.cartaAnimaTu.toJson(),
      'carta_anima_partner': instance.cartaAnimaPartner.toJson(),
    };

_Lettura _$LetturaFromJson(Map<String, dynamic> json) => _Lettura(
  id: json['id'] as String,
  mazzo: json['mazzo'] as String?,
  spreadId: json['spread_id'] as String,
  stesa: json['stesa'] as String,
  stesaNomi:
      (json['stesa_nomi'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as String),
      ) ??
      const <String, String>{},
  categoria: json['categoria'] as String,
  stile: json['stile'] as String?,
  persone: json['persone'] == null
      ? null
      : PersoneLettura.fromJson(json['persone'] as Map<String, dynamic>),
  compatibilita: json['compatibilita'] == null
      ? null
      : Compatibilita.fromJson(json['compatibilita'] as Map<String, dynamic>),
  question: json['question'] as String,
  status: json['status'] as String,
  lang: json['lang'] as String,
  consumo: json['consumo'] as String? ?? '',
  createdAt: json['created_at'] as String,
  completedAt: json['completed_at'] as String?,
  feedback: json['feedback'] as String?,
  shared: json['shared'] as bool? ?? false,
  manuale: json['manuale'] as bool? ?? false,
  contextSummary: json['context_summary'] as String?,
  interview:
      (json['interview'] as List<dynamic>?)
          ?.map((e) => TurnoIntervista.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <TurnoIntervista>[],
  cards:
      (json['cards'] as List<dynamic>?)
          ?.map((e) => CartaPosata.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <CartaPosata>[],
  slotCount: (json['slot_count'] as num?)?.toInt(),
  pickedSlots:
      (json['picked_slots'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const <int>[],
  commitment: json['commitment'] as String?,
  deckSalt: json['deck_salt'] as String?,
  synthesis: json['synthesis'] as String?,
  guardOutcome: json['guard_outcome'] as String?,
  shareToken: json['share_token'] as String?,
  shareText: json['share_text'] as String?,
  feedbackNote: json['feedback_note'] as String?,
  disclaimer: json['disclaimer'] as String? ?? '',
  dignita:
      (json['dignita'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, Dignita.fromJson(e as Map<String, dynamic>)),
      ) ??
      const <String, Dignita>{},
  stesaDati: json['stesa_dati'] == null
      ? null
      : Stesa.fromJson(json['stesa_dati'] as Map<String, dynamic>),
);

Map<String, dynamic> _$LetturaToJson(_Lettura instance) => <String, dynamic>{
  'id': instance.id,
  'mazzo': ?instance.mazzo,
  'spread_id': instance.spreadId,
  'stesa': instance.stesa,
  'stesa_nomi': instance.stesaNomi,
  'categoria': instance.categoria,
  'stile': ?instance.stile,
  'persone': ?instance.persone?.toJson(),
  'compatibilita': ?instance.compatibilita?.toJson(),
  'question': instance.question,
  'status': instance.status,
  'lang': instance.lang,
  'consumo': instance.consumo,
  'created_at': instance.createdAt,
  'completed_at': ?instance.completedAt,
  'feedback': ?instance.feedback,
  'shared': instance.shared,
  'manuale': instance.manuale,
  'context_summary': ?instance.contextSummary,
  'interview': instance.interview.map((e) => e.toJson()).toList(),
  'cards': instance.cards.map((e) => e.toJson()).toList(),
  'slot_count': ?instance.slotCount,
  'picked_slots': instance.pickedSlots,
  'commitment': ?instance.commitment,
  'deck_salt': ?instance.deckSalt,
  'synthesis': ?instance.synthesis,
  'guard_outcome': ?instance.guardOutcome,
  'share_token': ?instance.shareToken,
  'share_text': ?instance.shareText,
  'feedback_note': ?instance.feedbackNote,
  'disclaimer': instance.disclaimer,
  'dignita': instance.dignita.map((k, e) => MapEntry(k, e.toJson())),
  'stesa_dati': ?instance.stesaDati?.toJson(),
};

_LetturaBreve _$LetturaBreveFromJson(Map<String, dynamic> json) =>
    _LetturaBreve(
      id: json['id'] as String,
      mazzo: json['mazzo'] as String?,
      spreadId: json['spread_id'] as String,
      stesa: json['stesa'] as String,
      stesaNomi:
          (json['stesa_nomi'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as String),
          ) ??
          const <String, String>{},
      categoria: json['categoria'] as String,
      stile: json['stile'] as String?,
      partnerNome: json['partner_nome'] as String?,
      question: json['question'] as String,
      status: json['status'] as String,
      createdAt: json['created_at'] as String,
      completedAt: json['completed_at'] as String?,
      feedback: json['feedback'] as String?,
      shared: json['shared'] as bool? ?? false,
      carte:
          (json['carte'] as List<dynamic>?)?.map((e) => e as String).toList() ??
          const <String>[],
    );

Map<String, dynamic> _$LetturaBreveToJson(_LetturaBreve instance) =>
    <String, dynamic>{
      'id': instance.id,
      'mazzo': ?instance.mazzo,
      'spread_id': instance.spreadId,
      'stesa': instance.stesa,
      'stesa_nomi': instance.stesaNomi,
      'categoria': instance.categoria,
      'stile': ?instance.stile,
      'partner_nome': ?instance.partnerNome,
      'question': instance.question,
      'status': instance.status,
      'created_at': instance.createdAt,
      'completed_at': ?instance.completedAt,
      'feedback': ?instance.feedback,
      'shared': instance.shared,
      'carte': instance.carte,
    };

_ElencoLetture _$ElencoLettureFromJson(Map<String, dynamic> json) =>
    _ElencoLetture(
      totale: (json['totale'] as num).toInt(),
      letture:
          (json['letture'] as List<dynamic>?)
              ?.map((e) => LetturaBreve.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <LetturaBreve>[],
    );

Map<String, dynamic> _$ElencoLettureToJson(_ElencoLetture instance) =>
    <String, dynamic>{
      'totale': instance.totale,
      'letture': instance.letture.map((e) => e.toJson()).toList(),
    };

_Apertura _$AperturaFromJson(Map<String, dynamic> json) => _Apertura(
  id: json['id'] as String?,
  status: json['status'] as String?,
  categoria: json['categoria'] as String?,
  lang: json['lang'] as String?,
  consumo: json['consumo'] as String?,
  disclaimer: json['disclaimer'] as String?,
  stesa: json['stesa'] == null
      ? null
      : Stesa.fromJson(json['stesa'] as Map<String, dynamic>),
  saldo: (json['saldo'] as num?)?.toInt(),
  crisi: json['crisi'] as bool? ?? false,
  messaggio: json['messaggio'] as String?,
);

Map<String, dynamic> _$AperturaToJson(_Apertura instance) => <String, dynamic>{
  'id': ?instance.id,
  'status': ?instance.status,
  'categoria': ?instance.categoria,
  'lang': ?instance.lang,
  'consumo': ?instance.consumo,
  'disclaimer': ?instance.disclaimer,
  'stesa': ?instance.stesa?.toJson(),
  'saldo': ?instance.saldo,
  'crisi': instance.crisi,
  'messaggio': ?instance.messaggio,
};

_PassoIntervista _$PassoIntervistaFromJson(Map<String, dynamic> json) =>
    _PassoIntervista(
      completa: json['completa'] as bool? ?? false,
      domanda: json['domanda'] as String?,
      ordine: (json['ordine'] as num?)?.toInt(),
      riassunto: json['riassunto'] as String?,
      crisi: json['crisi'] as bool? ?? false,
      messaggio: json['messaggio'] as String?,
      facoltativa: json['facoltativa'] as bool? ?? false,
      scelta: json['scelta'] as bool? ?? false,
      poste: (json['poste'] as num?)?.toInt(),
      minDomande: (json['min_domande'] as num?)?.toInt(),
      maxDomande: (json['max_domande'] as num?)?.toInt(),
    );

Map<String, dynamic> _$PassoIntervistaToJson(_PassoIntervista instance) =>
    <String, dynamic>{
      'completa': instance.completa,
      'domanda': ?instance.domanda,
      'ordine': ?instance.ordine,
      'riassunto': ?instance.riassunto,
      'crisi': instance.crisi,
      'messaggio': ?instance.messaggio,
      'facoltativa': instance.facoltativa,
      'scelta': instance.scelta,
      'poste': ?instance.poste,
      'min_domande': ?instance.minDomande,
      'max_domande': ?instance.maxDomande,
    };

_Ventaglio _$VentaglioFromJson(Map<String, dynamic> json) => _Ventaglio(
  slotCount: (json['slot_count'] as num).toInt(),
  commitment: json['commitment'] as String,
  daScegliere: (json['da_scegliere'] as num).toInt(),
  pickedSlots:
      (json['picked_slots'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const <int>[],
);

Map<String, dynamic> _$VentaglioToJson(_Ventaglio instance) =>
    <String, dynamic>{
      'slot_count': instance.slotCount,
      'commitment': instance.commitment,
      'da_scegliere': instance.daScegliere,
      'picked_slots': instance.pickedSlots,
    };

_Scelta _$SceltaFromJson(Map<String, dynamic> json) => _Scelta(
  posizione: (json['posizione'] as num).toInt(),
  slot: (json['slot'] as num).toInt(),
  tutteScelte: json['tutte_scelte'] as bool? ?? false,
  posizioniCalcolate:
      (json['posizioni_calcolate'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const <int>[],
);

Map<String, dynamic> _$SceltaToJson(_Scelta instance) => <String, dynamic>{
  'posizione': instance.posizione,
  'slot': instance.slot,
  'tutte_scelte': instance.tutteScelte,
  'posizioni_calcolate': instance.posizioniCalcolate,
};

_StatoCondivisione _$StatoCondivisioneFromJson(Map<String, dynamic> json) =>
    _StatoCondivisione(
      shareToken: json['share_token'] as String?,
      shareText: json['share_text'] as String?,
    );

Map<String, dynamic> _$StatoCondivisioneToJson(_StatoCondivisione instance) =>
    <String, dynamic>{
      'share_token': ?instance.shareToken,
      'share_text': ?instance.shareText,
    };

_LetturaCondivisa _$LetturaCondivisaFromJson(Map<String, dynamic> json) =>
    _LetturaCondivisa(
      question: json['question'] as String,
      mazzo: json['mazzo'] as String?,
      lang: json['lang'] as String,
      stesa: json['stesa'] == null
          ? null
          : Stesa.fromJson(json['stesa'] as Map<String, dynamic>),
      categoria: json['categoria'] as String,
      speciale: json['speciale'] as bool? ?? false,
      partnerSimbolo: json['partner_simbolo'] as String?,
      partnerFrase: json['partner_frase'] as String?,
      cards:
          (json['cards'] as List<dynamic>?)
              ?.map((e) => CartaPosata.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <CartaPosata>[],
      synthesis: json['synthesis'] as String?,
      shareText: json['share_text'] as String?,
      immagine: json['immagine'] as bool? ?? false,
      createdAt: json['created_at'] as String,
      disclaimer: json['disclaimer'] as String? ?? '',
    );

Map<String, dynamic> _$LetturaCondivisaToJson(_LetturaCondivisa instance) =>
    <String, dynamic>{
      'question': instance.question,
      'mazzo': ?instance.mazzo,
      'lang': instance.lang,
      'stesa': ?instance.stesa?.toJson(),
      'categoria': instance.categoria,
      'speciale': instance.speciale,
      'partner_simbolo': ?instance.partnerSimbolo,
      'partner_frase': ?instance.partnerFrase,
      'cards': instance.cards.map((e) => e.toJson()).toList(),
      'synthesis': ?instance.synthesis,
      'share_text': ?instance.shareText,
      'immagine': instance.immagine,
      'created_at': instance.createdAt,
      'disclaimer': instance.disclaimer,
    };

_Memoria _$MemoriaFromJson(Map<String, dynamic> json) => _Memoria(
  id: json['id'] as String,
  contenuto: json['contenuto'] as String,
  tipo: json['tipo'] as String,
  campoAttinenza: json['campo_attinenza'] as String,
  fonte: json['fonte'] as String,
  aggiornata: json['aggiornata'] as String?,
);

Map<String, dynamic> _$MemoriaToJson(_Memoria instance) => <String, dynamic>{
  'id': instance.id,
  'contenuto': instance.contenuto,
  'tipo': instance.tipo,
  'campo_attinenza': instance.campoAttinenza,
  'fonte': instance.fonte,
  'aggiornata': ?instance.aggiornata,
};

_PropostaLettura _$PropostaLetturaFromJson(Map<String, dynamic> json) =>
    _PropostaLettura(
      argomento: json['argomento'] as String,
      categoria: json['categoria'] as String,
    );

Map<String, dynamic> _$PropostaLetturaToJson(_PropostaLettura instance) =>
    <String, dynamic>{
      'argomento': instance.argomento,
      'categoria': instance.categoria,
    };

_TurnoChat _$TurnoChatFromJson(Map<String, dynamic> json) => _TurnoChat(
  id: json['id'] as String,
  ruolo: json['ruolo'] as String,
  testo: json['testo'] as String,
  proposta: json['proposta'] == null
      ? null
      : PropostaLettura.fromJson(json['proposta'] as Map<String, dynamic>),
  creato: json['creato'] as String?,
);

Map<String, dynamic> _$TurnoChatToJson(_TurnoChat instance) =>
    <String, dynamic>{
      'id': instance.id,
      'ruolo': instance.ruolo,
      'testo': instance.testo,
      'proposta': ?instance.proposta?.toJson(),
      'creato': ?instance.creato,
    };

_ImpostazioniChat _$ImpostazioniChatFromJson(Map<String, dynamic> json) =>
    _ImpostazioniChat(
      proattivaMinutiInattivita:
          (json['proattiva_minuti_inattivita'] as num?)?.toInt() ?? 30,
      proattivaMaxPerVisita:
          (json['proattiva_max_per_visita'] as num?)?.toInt() ?? 3,
    );

Map<String, dynamic> _$ImpostazioniChatToJson(_ImpostazioniChat instance) =>
    <String, dynamic>{
      'proattiva_minuti_inattivita': instance.proattivaMinutiInattivita,
      'proattiva_max_per_visita': instance.proattivaMaxPerVisita,
    };
