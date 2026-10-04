// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cassa.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_PrezzoRinnovo _$PrezzoRinnovoFromJson(Map<String, dynamic> json) =>
    _PrezzoRinnovo(
      listino: (json['listino'] as num).toInt(),
      conRinnovo: (json['con_rinnovo'] as num).toInt(),
      sconto: json['sconto'] as num? ?? 0,
    );

Map<String, dynamic> _$PrezzoRinnovoToJson(_PrezzoRinnovo instance) =>
    <String, dynamic>{
      'listino': instance.listino,
      'con_rinnovo': instance.conRinnovo,
      'sconto': instance.sconto,
    };

_PrezziPiano _$PrezziPianoFromJson(Map<String, dynamic> json) => _PrezziPiano(
  mensile: PrezzoRinnovo.fromJson(json['mensile'] as Map<String, dynamic>),
  annuale: json['annuale'] == null
      ? null
      : PrezzoRinnovo.fromJson(json['annuale'] as Map<String, dynamic>),
  provaAnnuale: (json['prova_annuale'] as num?)?.toInt(),
);

Map<String, dynamic> _$PrezziPianoToJson(_PrezziPiano instance) =>
    <String, dynamic>{
      'mensile': instance.mensile.toJson(),
      'annuale': ?instance.annuale?.toJson(),
      'prova_annuale': ?instance.provaAnnuale,
    };

_Piano _$PianoFromJson(Map<String, dynamic> json) => _Piano(
  slug: json['slug'] as String,
  nome: json['nome'] as String,
  tipo: json['tipo'] as String,
  descrizione: json['descrizione'] as String?,
  valuta: json['valuta'] as String? ?? 'EUR',
  prezzoMensile: (json['prezzo_mensile'] as num?)?.toInt() ?? 0,
  prezzoAnnuale: (json['prezzo_annuale'] as num?)?.toInt() ?? 0,
  creditiPerPeriodo: (json['crediti_per_periodo'] as num?)?.toInt() ?? 0,
  limiti:
      (json['limiti'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as num),
      ) ??
      const <String, num>{},
  livello: (json['livello'] as num?)?.toInt(),
  prezzi: json['prezzi'] == null
      ? null
      : PrezziPiano.fromJson(json['prezzi'] as Map<String, dynamic>),
);

Map<String, dynamic> _$PianoToJson(_Piano instance) => <String, dynamic>{
  'slug': instance.slug,
  'nome': instance.nome,
  'tipo': instance.tipo,
  'descrizione': ?instance.descrizione,
  'valuta': instance.valuta,
  'prezzo_mensile': instance.prezzoMensile,
  'prezzo_annuale': instance.prezzoAnnuale,
  'crediti_per_periodo': instance.creditiPerPeriodo,
  'limiti': instance.limiti,
  'livello': ?instance.livello,
  'prezzi': ?instance.prezzi?.toJson(),
};

_AbbonamentoBreve _$AbbonamentoBreveFromJson(Map<String, dynamic> json) =>
    _AbbonamentoBreve(
      id: json['id'] as String,
      piano: json['piano'] as String,
      nome: json['nome'] as String,
      stato: json['stato'] as String,
      periodoInizio: json['periodo_inizio'] as String,
      periodoFine: json['periodo_fine'] as String,
      disdettoIl: json['disdetto_il'] as String?,
      annuale: json['annuale'] as bool?,
      rinnovoAutomatico: json['rinnovo_automatico'] as bool?,
      provider: json['provider'] as String?,
      store: json['store'] as bool? ?? false,
    );

Map<String, dynamic> _$AbbonamentoBreveToJson(_AbbonamentoBreve instance) =>
    <String, dynamic>{
      'id': instance.id,
      'piano': instance.piano,
      'nome': instance.nome,
      'stato': instance.stato,
      'periodo_inizio': instance.periodoInizio,
      'periodo_fine': instance.periodoFine,
      'disdetto_il': ?instance.disdettoIl,
      'annuale': ?instance.annuale,
      'rinnovo_automatico': ?instance.rinnovoAutomatico,
      'provider': ?instance.provider,
      'store': instance.store,
    };

_Diritti _$DirittiFromJson(Map<String, dynamic> json) => _Diritti(
  piano: json['piano'] as String,
  nome: json['nome'] as String,
  limiti:
      (json['limiti'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as num),
      ) ??
      const <String, num>{},
  predefiniti: json['predefiniti'] as bool? ?? false,
);

Map<String, dynamic> _$DirittiToJson(_Diritti instance) => <String, dynamic>{
  'piano': instance.piano,
  'nome': instance.nome,
  'limiti': instance.limiti,
  'predefiniti': instance.predefiniti,
};

_UsoLimite _$UsoLimiteFromJson(Map<String, dynamic> json) => _UsoLimite(
  usati: (json['usati'] as num?)?.toInt() ?? 0,
  limite: (json['limite'] as num?)?.toInt(),
  restanti: (json['restanti'] as num?)?.toInt(),
);

Map<String, dynamic> _$UsoLimiteToJson(_UsoLimite instance) =>
    <String, dynamic>{
      'usati': instance.usati,
      'limite': ?instance.limite,
      'restanti': ?instance.restanti,
    };

_IdoneitaProva _$IdoneitaProvaFromJson(Map<String, dynamic> json) =>
    _IdoneitaProva(
      idonea: json['idonea'] as bool,
      motivo: json['motivo'] as String?,
      usataIl: json['usata_il'] as String?,
    );

Map<String, dynamic> _$IdoneitaProvaToJson(_IdoneitaProva instance) =>
    <String, dynamic>{
      'idonea': instance.idonea,
      'motivo': ?instance.motivo,
      'usata_il': ?instance.usataIl,
    };

_Conto _$ContoFromJson(Map<String, dynamic> json) => _Conto(
  abbonamento: json['abbonamento'] == null
      ? null
      : AbbonamentoBreve.fromJson(json['abbonamento'] as Map<String, dynamic>),
  diritti: json['diritti'] == null
      ? null
      : Diritti.fromJson(json['diritti'] as Map<String, dynamic>),
  saldo: (json['saldo'] as num?)?.toInt() ?? 0,
  uso:
      (json['uso'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, UsoLimite.fromJson(e as Map<String, dynamic>)),
      ) ??
      const <String, UsoLimite>{},
  limitiAttivi: json['limiti_attivi'] as bool? ?? false,
  lettureComprese: json['letture_comprese'] as bool?,
  prova: json['prova'] == null
      ? null
      : IdoneitaProva.fromJson(json['prova'] as Map<String, dynamic>),
);

Map<String, dynamic> _$ContoToJson(_Conto instance) => <String, dynamic>{
  'abbonamento': ?instance.abbonamento?.toJson(),
  'diritti': ?instance.diritti?.toJson(),
  'saldo': instance.saldo,
  'uso': instance.uso.map((k, e) => MapEntry(k, e.toJson())),
  'limiti_attivi': instance.limitiAttivi,
  'letture_comprese': ?instance.lettureComprese,
  'prova': ?instance.prova?.toJson(),
};

_Movimento _$MovimentoFromJson(Map<String, dynamic> json) => _Movimento(
  delta: (json['delta'] as num).toInt(),
  reason: json['reason'] as String,
  quando: json['quando'] as String,
  note: json['note'] as String?,
  readingId: json['reading_id'] as String?,
);

Map<String, dynamic> _$MovimentoToJson(_Movimento instance) =>
    <String, dynamic>{
      'delta': instance.delta,
      'reason': instance.reason,
      'quando': instance.quando,
      'note': ?instance.note,
      'reading_id': ?instance.readingId,
    };

_Movimenti _$MovimentiFromJson(Map<String, dynamic> json) => _Movimenti(
  saldo: (json['saldo'] as num?)?.toInt() ?? 0,
  movimenti:
      (json['movimenti'] as List<dynamic>?)
          ?.map((e) => Movimento.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <Movimento>[],
);

Map<String, dynamic> _$MovimentiToJson(_Movimenti instance) =>
    <String, dynamic>{
      'saldo': instance.saldo,
      'movimenti': instance.movimenti.map((e) => e.toJson()).toList(),
    };

_Checkout _$CheckoutFromJson(Map<String, dynamic> json) => _Checkout(
  checkoutId: json['checkout_id'] as String,
  url: json['url'] as String,
  importo: (json['importo'] as num?)?.toInt() ?? 0,
  sconto: (json['sconto'] as num?)?.toInt(),
  valuta: json['valuta'] as String? ?? 'EUR',
  gratis: json['gratis'] as bool? ?? false,
);

Map<String, dynamic> _$CheckoutToJson(_Checkout instance) => <String, dynamic>{
  'checkout_id': instance.checkoutId,
  'url': instance.url,
  'importo': instance.importo,
  'sconto': ?instance.sconto,
  'valuta': instance.valuta,
  'gratis': instance.gratis,
};

_StatoCheckout _$StatoCheckoutFromJson(Map<String, dynamic> json) =>
    _StatoCheckout(
      checkoutId: json['checkout_id'] as String,
      stato: json['stato'] as String,
      piano: json['piano'] as String,
      nome: json['nome'] as String,
      tipo: json['tipo'] as String,
      prova: json['prova'] as bool?,
      cambio: json['cambio'] as bool?,
      esito: json['esito'] as String?,
    );

Map<String, dynamic> _$StatoCheckoutToJson(_StatoCheckout instance) =>
    <String, dynamic>{
      'checkout_id': instance.checkoutId,
      'stato': instance.stato,
      'piano': instance.piano,
      'nome': instance.nome,
      'tipo': instance.tipo,
      'prova': ?instance.prova,
      'cambio': ?instance.cambio,
      'esito': ?instance.esito,
    };

_PianoSuccessivo _$PianoSuccessivoFromJson(Map<String, dynamic> json) =>
    _PianoSuccessivo(
      piano: json['piano'] as String,
      nome: json['nome'] as String,
      annuale: json['annuale'] as bool? ?? false,
      dal: json['dal'] as String,
    );

Map<String, dynamic> _$PianoSuccessivoToJson(_PianoSuccessivo instance) =>
    <String, dynamic>{
      'piano': instance.piano,
      'nome': instance.nome,
      'annuale': instance.annuale,
      'dal': instance.dal,
    };

_CouponAbbonamento _$CouponAbbonamentoFromJson(Map<String, dynamic> json) =>
    _CouponAbbonamento(
      codice: json['codice'] as String,
      tipo: json['tipo'] as String,
      valore: json['valore'] as num,
      cumulabile: json['cumulabile'] as bool? ?? false,
      sconto: json['sconto'] as num? ?? 0,
      perSempre: json['per_sempre'] as bool? ?? false,
      rinnoviRimasti: (json['rinnovi_rimasti'] as num?)?.toInt(),
    );

Map<String, dynamic> _$CouponAbbonamentoToJson(_CouponAbbonamento instance) =>
    <String, dynamic>{
      'codice': instance.codice,
      'tipo': instance.tipo,
      'valore': instance.valore,
      'cumulabile': instance.cumulabile,
      'sconto': instance.sconto,
      'per_sempre': instance.perSempre,
      'rinnovi_rimasti': ?instance.rinnoviRimasti,
    };

_AbbonamentoDettaglio _$AbbonamentoDettaglioFromJson(
  Map<String, dynamic> json,
) => _AbbonamentoDettaglio(
  id: json['id'] as String,
  piano: json['piano'] as String,
  nome: json['nome'] as String,
  stato: json['stato'] as String,
  provider: json['provider'] as String,
  store: json['store'] as bool? ?? false,
  gestioneStore: json['gestione_store'] as String?,
  gratuito: json['gratuito'] as bool? ?? false,
  annuale: json['annuale'] as bool? ?? false,
  prova: json['prova'] as bool? ?? false,
  periodoInizio: json['periodo_inizio'] as String,
  periodoFine: json['periodo_fine'] as String,
  disdettoIl: json['disdetto_il'] as String?,
  rinnovoAutomatico: json['rinnovo_automatico'] as bool? ?? false,
  listino: (json['listino'] as num?)?.toInt(),
  importoPeriodo: (json['importo_periodo'] as num?)?.toInt(),
  scontoRicorrente: json['sconto_ricorrente'] as num? ?? 0,
  prossimoRinnovo: (json['prossimo_rinnovo'] as num?)?.toInt(),
  valuta: json['valuta'] as String? ?? 'EUR',
  fatturaAperta: json['fattura_aperta'] as bool? ?? false,
  pagamentoFallitoIl: json['pagamento_fallito_il'] as String?,
  fineTolleranza: json['fine_tolleranza'] as String?,
  pianoSuccessivo: json['piano_successivo'] == null
      ? null
      : PianoSuccessivo.fromJson(
          json['piano_successivo'] as Map<String, dynamic>,
        ),
  coupon: json['coupon'] == null
      ? null
      : CouponAbbonamento.fromJson(json['coupon'] as Map<String, dynamic>),
);

Map<String, dynamic> _$AbbonamentoDettaglioToJson(
  _AbbonamentoDettaglio instance,
) => <String, dynamic>{
  'id': instance.id,
  'piano': instance.piano,
  'nome': instance.nome,
  'stato': instance.stato,
  'provider': instance.provider,
  'store': instance.store,
  'gestione_store': ?instance.gestioneStore,
  'gratuito': instance.gratuito,
  'annuale': instance.annuale,
  'prova': instance.prova,
  'periodo_inizio': instance.periodoInizio,
  'periodo_fine': instance.periodoFine,
  'disdetto_il': ?instance.disdettoIl,
  'rinnovo_automatico': instance.rinnovoAutomatico,
  'listino': ?instance.listino,
  'importo_periodo': ?instance.importoPeriodo,
  'sconto_ricorrente': instance.scontoRicorrente,
  'prossimo_rinnovo': ?instance.prossimoRinnovo,
  'valuta': instance.valuta,
  'fattura_aperta': instance.fatturaAperta,
  'pagamento_fallito_il': ?instance.pagamentoFallitoIl,
  'fine_tolleranza': ?instance.fineTolleranza,
  'piano_successivo': ?instance.pianoSuccessivo?.toJson(),
  'coupon': ?instance.coupon?.toJson(),
};

_ImpostazioniAbbonamenti _$ImpostazioniAbbonamentiFromJson(
  Map<String, dynamic> json,
) => _ImpostazioniAbbonamenti(
  bannerProva: json['banner_prova'] as bool? ?? false,
  provaDisponibile: json['prova_disponibile'] as bool? ?? false,
  giorniProva: (json['giorni_prova'] as num?)?.toInt() ?? 14,
  scontoProva: json['sconto_prova'] as num? ?? 50,
  scontoRinnovo: json['sconto_rinnovo'] as num? ?? 20,
  condoniPerPeriodo: (json['condoni_per_periodo'] as num?)?.toInt() ?? 2,
  giorniPromemoriaProva:
      (json['giorni_promemoria_prova'] as num?)?.toInt() ?? 2,
  giorniTolleranza: (json['giorni_tolleranza'] as num?)?.toInt() ?? 7,
);

Map<String, dynamic> _$ImpostazioniAbbonamentiToJson(
  _ImpostazioniAbbonamenti instance,
) => <String, dynamic>{
  'banner_prova': instance.bannerProva,
  'prova_disponibile': instance.provaDisponibile,
  'giorni_prova': instance.giorniProva,
  'sconto_prova': instance.scontoProva,
  'sconto_rinnovo': instance.scontoRinnovo,
  'condoni_per_periodo': instance.condoniPerPeriodo,
  'giorni_promemoria_prova': instance.giorniPromemoriaProva,
  'giorni_tolleranza': instance.giorniTolleranza,
};

_NumeriAbbonamento _$NumeriAbbonamentoFromJson(Map<String, dynamic> json) =>
    _NumeriAbbonamento(
      scontoRinnovo: json['sconto_rinnovo'] as num? ?? 20,
      scontoProva: json['sconto_prova'] as num? ?? 50,
      giorniProva: (json['giorni_prova'] as num?)?.toInt() ?? 14,
      giorniTolleranza: (json['giorni_tolleranza'] as num?)?.toInt() ?? 7,
    );

Map<String, dynamic> _$NumeriAbbonamentoToJson(_NumeriAbbonamento instance) =>
    <String, dynamic>{
      'sconto_rinnovo': instance.scontoRinnovo,
      'sconto_prova': instance.scontoProva,
      'giorni_prova': instance.giorniProva,
      'giorni_tolleranza': instance.giorniTolleranza,
    };

_MioAbbonamento _$MioAbbonamentoFromJson(Map<String, dynamic> json) =>
    _MioAbbonamento(
      abbonamento: json['abbonamento'] == null
          ? null
          : AbbonamentoDettaglio.fromJson(
              json['abbonamento'] as Map<String, dynamic>,
            ),
      prova: IdoneitaProva.fromJson(json['prova'] as Map<String, dynamic>),
      impostazioni: json['impostazioni'] == null
          ? const NumeriAbbonamento()
          : NumeriAbbonamento.fromJson(
              json['impostazioni'] as Map<String, dynamic>,
            ),
      saldo: (json['saldo'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$MioAbbonamentoToJson(_MioAbbonamento instance) =>
    <String, dynamic>{
      'abbonamento': ?instance.abbonamento?.toJson(),
      'prova': instance.prova.toJson(),
      'impostazioni': instance.impostazioni.toJson(),
      'saldo': instance.saldo,
    };

_Conguaglio _$ConguaglioFromJson(Map<String, dynamic> json) => _Conguaglio(
  tipo: json['tipo'] as String,
  piano: json['piano'] as String,
  nome: json['nome'] as String,
  annuale: json['annuale'] as bool? ?? false,
  rinnovo: json['rinnovo'] as bool? ?? false,
  listino: (json['listino'] as num?)?.toInt() ?? 0,
  scontoRinnovo: json['sconto_rinnovo'] as num? ?? 0,
  nuovo: (json['nuovo'] as num?)?.toInt() ?? 0,
  residuo: (json['residuo'] as num?)?.toInt() ?? 0,
  totale: (json['totale'] as num?)?.toInt() ?? 0,
  pagato: (json['pagato'] as num?)?.toInt() ?? 0,
  giorniRimasti: (json['giorni_rimasti'] as num?)?.toInt() ?? 0,
  giorniPeriodo: (json['giorni_periodo'] as num?)?.toInt() ?? 0,
  decorre: json['decorre'] as String,
  valuta: json['valuta'] as String? ?? 'EUR',
);

Map<String, dynamic> _$ConguaglioToJson(_Conguaglio instance) =>
    <String, dynamic>{
      'tipo': instance.tipo,
      'piano': instance.piano,
      'nome': instance.nome,
      'annuale': instance.annuale,
      'rinnovo': instance.rinnovo,
      'listino': instance.listino,
      'sconto_rinnovo': instance.scontoRinnovo,
      'nuovo': instance.nuovo,
      'residuo': instance.residuo,
      'totale': instance.totale,
      'pagato': instance.pagato,
      'giorni_rimasti': instance.giorniRimasti,
      'giorni_periodo': instance.giorniPeriodo,
      'decorre': instance.decorre,
      'valuta': instance.valuta,
    };

_EsitoCambio _$EsitoCambioFromJson(Map<String, dynamic> json) => _EsitoCambio(
  tipo: json['tipo'] as String,
  conguaglio: Conguaglio.fromJson(json['conguaglio'] as Map<String, dynamic>),
  url: json['url'] as String?,
  importo: (json['importo'] as num?)?.toInt(),
  abbonamento: json['abbonamento'] == null
      ? null
      : AbbonamentoDettaglio.fromJson(
          json['abbonamento'] as Map<String, dynamic>,
        ),
);

Map<String, dynamic> _$EsitoCambioToJson(_EsitoCambio instance) =>
    <String, dynamic>{
      'tipo': instance.tipo,
      'conguaglio': instance.conguaglio.toJson(),
      'url': ?instance.url,
      'importo': ?instance.importo,
      'abbonamento': ?instance.abbonamento?.toJson(),
    };

_PagamentoDaSistemare _$PagamentoDaSistemareFromJson(
  Map<String, dynamic> json,
) => _PagamentoDaSistemare(
  provider: json['provider'] as String,
  store: json['store'] as bool? ?? false,
  url: json['url'] as String?,
  giaPagata: json['gia_pagata'] as bool? ?? false,
);

Map<String, dynamic> _$PagamentoDaSistemareToJson(
  _PagamentoDaSistemare instance,
) => <String, dynamic>{
  'provider': instance.provider,
  'store': instance.store,
  'url': ?instance.url,
  'gia_pagata': instance.giaPagata,
};

_LimiteSuperato _$LimiteSuperatoFromJson(Map<String, dynamic> json) =>
    _LimiteSuperato(
      limite: json['limite'] as String,
      valore: (json['valore'] as num?)?.toInt() ?? 0,
      usate: (json['usate'] as num?)?.toInt() ?? 0,
      lettureFatte: (json['letture_fatte'] as num?)?.toInt() ?? 0,
      siLibera: json['si_libera'] as String?,
      condoniRimasti: (json['condoni_rimasti'] as num?)?.toInt() ?? 0,
      condoniPerPeriodo: (json['condoni_per_periodo'] as num?)?.toInt() ?? 0,
      saldo: (json['saldo'] as num?)?.toInt() ?? 0,
      scelta: json['scelta'] as String,
    );

Map<String, dynamic> _$LimiteSuperatoToJson(_LimiteSuperato instance) =>
    <String, dynamic>{
      'limite': instance.limite,
      'valore': instance.valore,
      'usate': instance.usate,
      'letture_fatte': instance.lettureFatte,
      'si_libera': ?instance.siLibera,
      'condoni_rimasti': instance.condoniRimasti,
      'condoni_per_periodo': instance.condoniPerPeriodo,
      'saldo': instance.saldo,
      'scelta': instance.scelta,
    };

_CouponPubblico _$CouponPubblicoFromJson(Map<String, dynamic> json) =>
    _CouponPubblico(
      codice: json['codice'] as String,
      tipo: json['tipo'] as String,
      valore: json['valore'] as num,
      durata: json['durata'] as String,
      periodi: (json['periodi'] as num?)?.toInt(),
      cumulabile: json['cumulabile'] as bool? ?? false,
      piani:
          (json['piani'] as List<dynamic>?)?.map((e) => e as String).toList() ??
          const <String>[],
      validoFino: json['valido_fino'] as String?,
    );

Map<String, dynamic> _$CouponPubblicoToJson(_CouponPubblico instance) =>
    <String, dynamic>{
      'codice': instance.codice,
      'tipo': instance.tipo,
      'valore': instance.valore,
      'durata': instance.durata,
      'periodi': ?instance.periodi,
      'cumulabile': instance.cumulabile,
      'piani': instance.piani,
      'valido_fino': ?instance.validoFino,
    };

_VoceCoupon _$VoceCouponFromJson(Map<String, dynamic> json) => _VoceCoupon(
  piano: json['piano'] as String,
  annuale: json['annuale'] as bool? ?? false,
  rinnovo: json['rinnovo'] as bool? ?? false,
  prova: json['prova'] as bool? ?? false,
  motivo: json['motivo'] as String?,
  listino: (json['listino'] as num?)?.toInt(),
  scontoBase: json['sconto_base'] as num?,
  scontoCoupon: json['sconto_coupon'] as num?,
  sconto: json['sconto'] as num?,
  importo: (json['importo'] as num?)?.toInt(),
  risparmio: (json['risparmio'] as num?)?.toInt(),
  vince: json['vince'] as String?,
  applicato: json['applicato'] as bool?,
  cumulabile: json['cumulabile'] as bool?,
  scontoRicorrente: json['sconto_ricorrente'] as num?,
  rinnoviCoupon: (json['rinnovi_coupon'] as num?)?.toInt(),
  nota: json['nota'] as String?,
);

Map<String, dynamic> _$VoceCouponToJson(_VoceCoupon instance) =>
    <String, dynamic>{
      'piano': instance.piano,
      'annuale': instance.annuale,
      'rinnovo': instance.rinnovo,
      'prova': instance.prova,
      'motivo': ?instance.motivo,
      'listino': ?instance.listino,
      'sconto_base': ?instance.scontoBase,
      'sconto_coupon': ?instance.scontoCoupon,
      'sconto': ?instance.sconto,
      'importo': ?instance.importo,
      'risparmio': ?instance.risparmio,
      'vince': ?instance.vince,
      'applicato': ?instance.applicato,
      'cumulabile': ?instance.cumulabile,
      'sconto_ricorrente': ?instance.scontoRicorrente,
      'rinnovi_coupon': ?instance.rinnoviCoupon,
      'nota': ?instance.nota,
    };

_AnteprimaCouponPubblica _$AnteprimaCouponPubblicaFromJson(
  Map<String, dynamic> json,
) => _AnteprimaCouponPubblica(
  coupon: CouponPubblico.fromJson(json['coupon'] as Map<String, dynamic>),
  offerte:
      (json['offerte'] as List<dynamic>?)
          ?.map((e) => VoceCoupon.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <VoceCoupon>[],
);

Map<String, dynamic> _$AnteprimaCouponPubblicaToJson(
  _AnteprimaCouponPubblica instance,
) => <String, dynamic>{
  'coupon': instance.coupon.toJson(),
  'offerte': instance.offerte.map((e) => e.toJson()).toList(),
};

_Riscatto _$RiscattoFromJson(Map<String, dynamic> json) => _Riscatto(
  crediti: (json['crediti'] as num?)?.toInt() ?? 0,
  saldo: (json['saldo'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$RiscattoToJson(_Riscatto instance) => <String, dynamic>{
  'crediti': instance.crediti,
  'saldo': instance.saldo,
};

_Mazzo _$MazzoFromJson(Map<String, dynamic> json) => _Mazzo(
  id: (json['id'] as num).toInt(),
  slug: json['slug'] as String,
  nome: json['nome'] as String,
  descrizione: json['descrizione'] as String?,
  predefinito: json['predefinito'] as bool? ?? false,
  attivo: json['attivo'] as bool? ?? true,
  attivoOra: json['attivo_ora'] as bool? ?? true,
  attivazioneDa: json['attivazione_da'] as String?,
  attivazioneFino: json['attivazione_fino'] as String?,
  prezzoDigitale: (json['prezzo_digitale'] as num?)?.toInt(),
  prezzoDigitaleScontato: (json['prezzo_digitale_scontato'] as num?)?.toInt(),
  prezzoStampaScontato: (json['prezzo_stampa_scontato'] as num?)?.toInt(),
  prezzoFisicoScontato: (json['prezzo_fisico_scontato'] as num?)?.toInt(),
  offertaFormati:
      (json['offerta_formati'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const <String>[],
  offertaAttiva: json['offerta_attiva'] as bool? ?? false,
  offertaValidoFino: json['offerta_valido_fino'] as String?,
  prezzoStampa: (json['prezzo_stampa'] as num?)?.toInt(),
  prezzoFisico: (json['prezzo_fisico'] as num?)?.toInt(),
  richiedeSpedizione: json['richiede_spedizione'] as bool? ?? false,
  valuta: json['valuta'] as String? ?? 'EUR',
  rank: (json['rank'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$MazzoToJson(_Mazzo instance) => <String, dynamic>{
  'id': instance.id,
  'slug': instance.slug,
  'nome': instance.nome,
  'descrizione': ?instance.descrizione,
  'predefinito': instance.predefinito,
  'attivo': instance.attivo,
  'attivo_ora': instance.attivoOra,
  'attivazione_da': ?instance.attivazioneDa,
  'attivazione_fino': ?instance.attivazioneFino,
  'prezzo_digitale': ?instance.prezzoDigitale,
  'prezzo_digitale_scontato': ?instance.prezzoDigitaleScontato,
  'prezzo_stampa_scontato': ?instance.prezzoStampaScontato,
  'prezzo_fisico_scontato': ?instance.prezzoFisicoScontato,
  'offerta_formati': instance.offertaFormati,
  'offerta_attiva': instance.offertaAttiva,
  'offerta_valido_fino': ?instance.offertaValidoFino,
  'prezzo_stampa': ?instance.prezzoStampa,
  'prezzo_fisico': ?instance.prezzoFisico,
  'richiede_spedizione': instance.richiedeSpedizione,
  'valuta': instance.valuta,
  'rank': instance.rank,
};

_MazzoRiga _$MazzoRigaFromJson(Map<String, dynamic> json) =>
    _MazzoRiga(nome: json['nome'] as String, slug: json['slug'] as String);

Map<String, dynamic> _$MazzoRigaToJson(_MazzoRiga instance) =>
    <String, dynamic>{'nome': instance.nome, 'slug': instance.slug};

_RigaOrdine _$RigaOrdineFromJson(Map<String, dynamic> json) => _RigaOrdine(
  id: (json['id'] as num).toInt(),
  tipo: json['tipo'] as String,
  deckId: (json['deck_id'] as num).toInt(),
  mazzo: json['mazzo'] == null
      ? null
      : MazzoRiga.fromJson(json['mazzo'] as Map<String, dynamic>),
  quantita: (json['quantita'] as num?)?.toInt() ?? 1,
  prezzoPienoUnitario: (json['prezzo_pieno_unitario'] as num?)?.toInt() ?? 0,
  prezzoFinaleUnitario: (json['prezzo_finale_unitario'] as num?)?.toInt() ?? 0,
  statoEvasione: json['stato_evasione'] as String?,
);

Map<String, dynamic> _$RigaOrdineToJson(_RigaOrdine instance) =>
    <String, dynamic>{
      'id': instance.id,
      'tipo': instance.tipo,
      'deck_id': instance.deckId,
      'mazzo': ?instance.mazzo?.toJson(),
      'quantita': instance.quantita,
      'prezzo_pieno_unitario': instance.prezzoPienoUnitario,
      'prezzo_finale_unitario': instance.prezzoFinaleUnitario,
      'stato_evasione': ?instance.statoEvasione,
    };

_Ordine _$OrdineFromJson(Map<String, dynamic> json) => _Ordine(
  id: json['id'] as String,
  status: json['status'] as String,
  importoTotale: (json['importo_totale'] as num?)?.toInt() ?? 0,
  scontoScaglioni: (json['sconto_scaglioni'] as num?)?.toInt() ?? 0,
  valuta: json['valuta'] as String? ?? 'EUR',
  righe:
      (json['righe'] as List<dynamic>?)
          ?.map((e) => RigaOrdine.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <RigaOrdine>[],
  indirizzoSpedizione: (json['indirizzo_spedizione'] as Map<String, dynamic>?)
      ?.map((k, e) => MapEntry(k, e as String?)),
  creato: json['creato'] as String?,
  completato: json['completato'] as String?,
  url: json['url'] as String?,
  pagamentoAttivo: json['pagamento_attivo'] as bool?,
);

Map<String, dynamic> _$OrdineToJson(_Ordine instance) => <String, dynamic>{
  'id': instance.id,
  'status': instance.status,
  'importo_totale': instance.importoTotale,
  'sconto_scaglioni': instance.scontoScaglioni,
  'valuta': instance.valuta,
  'righe': instance.righe.map((e) => e.toJson()).toList(),
  'indirizzo_spedizione': ?instance.indirizzoSpedizione,
  'creato': ?instance.creato,
  'completato': ?instance.completato,
  'url': ?instance.url,
  'pagamento_attivo': ?instance.pagamentoAttivo,
};

_RigaPreventivo _$RigaPreventivoFromJson(
  Map<String, dynamic> json,
) => _RigaPreventivo(
  deckId: (json['deck_id'] as num).toInt(),
  tipo: json['tipo'] as String,
  quantita: (json['quantita'] as num?)?.toInt() ?? 1,
  prezzoPienoUnitario: (json['prezzo_pieno_unitario'] as num?)?.toInt() ?? 0,
  prezzoFinaleUnitario: (json['prezzo_finale_unitario'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$RigaPreventivoToJson(_RigaPreventivo instance) =>
    <String, dynamic>{
      'deck_id': instance.deckId,
      'tipo': instance.tipo,
      'quantita': instance.quantita,
      'prezzo_pieno_unitario': instance.prezzoPienoUnitario,
      'prezzo_finale_unitario': instance.prezzoFinaleUnitario,
    };

_Preventivo _$PreventivoFromJson(Map<String, dynamic> json) => _Preventivo(
  righe:
      (json['righe'] as List<dynamic>?)
          ?.map((e) => RigaPreventivo.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <RigaPreventivo>[],
  subtotale: (json['subtotale'] as num?)?.toInt() ?? 0,
  scaglionePercentuale: json['scaglione_percentuale'] as num? ?? 0,
  scontoScaglioni: (json['sconto_scaglioni'] as num?)?.toInt() ?? 0,
  totale: (json['totale'] as num?)?.toInt() ?? 0,
  richiedeIndirizzo: json['richiede_indirizzo'] as bool? ?? false,
  pagamentoAttivo: json['pagamento_attivo'] as bool? ?? false,
);

Map<String, dynamic> _$PreventivoToJson(_Preventivo instance) =>
    <String, dynamic>{
      'righe': instance.righe.map((e) => e.toJson()).toList(),
      'subtotale': instance.subtotale,
      'scaglione_percentuale': instance.scaglionePercentuale,
      'sconto_scaglioni': instance.scontoScaglioni,
      'totale': instance.totale,
      'richiede_indirizzo': instance.richiedeIndirizzo,
      'pagamento_attivo': instance.pagamentoAttivo,
    };

_Indirizzo _$IndirizzoFromJson(Map<String, dynamic> json) => _Indirizzo(
  id: json['id'] as String,
  nome: json['nome'] as String,
  via: json['via'] as String,
  citta: json['citta'] as String,
  cap: json['cap'] as String,
  provincia: json['provincia'] as String?,
  paese: json['paese'] as String,
  telefono: json['telefono'] as String?,
  predefinito: json['predefinito'] as bool? ?? false,
);

Map<String, dynamic> _$IndirizzoToJson(_Indirizzo instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nome': instance.nome,
      'via': instance.via,
      'citta': instance.citta,
      'cap': instance.cap,
      'provincia': ?instance.provincia,
      'paese': instance.paese,
      'telefono': ?instance.telefono,
      'predefinito': instance.predefinito,
    };
