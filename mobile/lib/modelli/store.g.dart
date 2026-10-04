// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'store.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_PianoStore _$PianoStoreFromJson(Map<String, dynamic> json) => _PianoStore(
  slug: json['slug'] as String,
  nome: json['nome'] as String,
  descrizione: json['descrizione'] as String?,
  tipo: json['tipo'] as String,
  crediti: (json['crediti'] as num?)?.toInt() ?? 0,
  limiti:
      (json['limiti'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, e as num),
      ) ??
      const <String, num>{},
  livello: (json['livello'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$PianoStoreToJson(_PianoStore instance) =>
    <String, dynamic>{
      'slug': instance.slug,
      'nome': instance.nome,
      'descrizione': ?instance.descrizione,
      'tipo': instance.tipo,
      'crediti': instance.crediti,
      'limiti': instance.limiti,
      'livello': instance.livello,
    };

_ProdottoStore _$ProdottoStoreFromJson(Map<String, dynamic> json) =>
    _ProdottoStore(
      productId: json['product_id'] as String,
      basePlan: json['base_plan'] as String?,
      tipo: json['tipo'] as String,
      annuale: json['annuale'] as bool? ?? false,
      prova: json['prova'] as bool? ?? false,
      piano: PianoStore.fromJson(json['piano'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$ProdottoStoreToJson(_ProdottoStore instance) =>
    <String, dynamic>{
      'product_id': instance.productId,
      'base_plan': ?instance.basePlan,
      'tipo': instance.tipo,
      'annuale': instance.annuale,
      'prova': instance.prova,
      'piano': instance.piano.toJson(),
    };

_PulsanteStripe _$PulsanteStripeFromJson(Map<String, dynamic> json) =>
    _PulsanteStripe(
      modalita: json['modalita'] as String? ?? 'nascosto',
      avviso: json['avviso'] as String?,
      mostra: json['mostra'] as bool? ?? false,
    );

Map<String, dynamic> _$PulsanteStripeToJson(_PulsanteStripe instance) =>
    <String, dynamic>{
      'modalita': instance.modalita,
      'avviso': ?instance.avviso,
      'mostra': instance.mostra,
    };

_CatalogoStore _$CatalogoStoreFromJson(Map<String, dynamic> json) =>
    _CatalogoStore(
      piattaforma: json['piattaforma'] as String,
      paese: json['paese'] as String?,
      prodotti:
          (json['prodotti'] as List<dynamic>?)
              ?.map((e) => ProdottoStore.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <ProdottoStore>[],
      stripe: json['stripe'] == null
          ? const PulsanteStripe()
          : PulsanteStripe.fromJson(json['stripe'] as Map<String, dynamic>),
      appAccountToken: json['app_account_token'] as String?,
    );

Map<String, dynamic> _$CatalogoStoreToJson(_CatalogoStore instance) =>
    <String, dynamic>{
      'piattaforma': instance.piattaforma,
      'paese': ?instance.paese,
      'prodotti': instance.prodotti.map((e) => e.toJson()).toList(),
      'stripe': instance.stripe.toJson(),
      'app_account_token': ?instance.appAccountToken,
    };

_AcquistoRegistrato _$AcquistoRegistratoFromJson(Map<String, dynamic> json) =>
    _AcquistoRegistrato(
      productId: json['product_id'] as String,
      tipo: json['tipo'] as String,
      stato: json['stato'] as String,
      confermato: json['confermato'] as bool? ?? false,
      ambiente: json['ambiente'] as String? ?? 'production',
    );

Map<String, dynamic> _$AcquistoRegistratoToJson(_AcquistoRegistrato instance) =>
    <String, dynamic>{
      'product_id': instance.productId,
      'tipo': instance.tipo,
      'stato': instance.stato,
      'confermato': instance.confermato,
      'ambiente': instance.ambiente,
    };

_EsitoVerificaStore _$EsitoVerificaStoreFromJson(Map<String, dynamic> json) =>
    _EsitoVerificaStore(
      esito: json['esito'] as String? ?? '',
      acquisto: AcquistoRegistrato.fromJson(
        json['acquisto'] as Map<String, dynamic>,
      ),
      saldo: (json['saldo'] as num?)?.toInt() ?? 0,
      abbonamento: json['abbonamento'] == null
          ? null
          : AbbonamentoDettaglio.fromJson(
              json['abbonamento'] as Map<String, dynamic>,
            ),
    );

Map<String, dynamic> _$EsitoVerificaStoreToJson(_EsitoVerificaStore instance) =>
    <String, dynamic>{
      'esito': instance.esito,
      'acquisto': instance.acquisto.toJson(),
      'saldo': instance.saldo,
      'abbonamento': ?instance.abbonamento?.toJson(),
    };
