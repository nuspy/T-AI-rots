// GENERATO da frontend/scripts/genera-arb.mjs: non modificare a mano.
// Gli elenchi e le mappe dei dizionari della v2, ricomposti dalle voci appiattite dell'ARB.

// I campi dei record hanno i nomi delle chiavi dei dizionari (`fornitori_ai`), come nel sito.
// ignore_for_file: lines_longer_than_80_chars, public_member_api_docs, non_constant_identifier_names

import 'generato/app_localizations.dart';

/// Le lingue tradotte davvero; le altre sono copie dell'inglese (il verso della pagina resta sinistra→destra).
const Set<String> lingueTradotte = {'en', 'es', 'hu', 'it', 'ru', 'uk'};

/// Elenchi e mappe dei dizionari, come nel sito (`h.temi.map(…)`).
extension ListeL10n on AppLocalizations {
  /// `comune.oracolo_temi` del dizionario della v2 (12 voci).
  List<({String testo, String domanda})> get comuneOracoloTemi => [(testo: comune_oracolo_temi_0_testo, domanda: comune_oracolo_temi_0_domanda), (testo: comune_oracolo_temi_1_testo, domanda: comune_oracolo_temi_1_domanda), (testo: comune_oracolo_temi_2_testo, domanda: comune_oracolo_temi_2_domanda), (testo: comune_oracolo_temi_3_testo, domanda: comune_oracolo_temi_3_domanda), (testo: comune_oracolo_temi_4_testo, domanda: comune_oracolo_temi_4_domanda), (testo: comune_oracolo_temi_5_testo, domanda: comune_oracolo_temi_5_domanda), (testo: comune_oracolo_temi_6_testo, domanda: comune_oracolo_temi_6_domanda), (testo: comune_oracolo_temi_7_testo, domanda: comune_oracolo_temi_7_domanda), (testo: comune_oracolo_temi_8_testo, domanda: comune_oracolo_temi_8_domanda), (testo: comune_oracolo_temi_9_testo, domanda: comune_oracolo_temi_9_domanda), (testo: comune_oracolo_temi_10_testo, domanda: comune_oracolo_temi_10_domanda), (testo: comune_oracolo_temi_11_testo, domanda: comune_oracolo_temi_11_domanda)];
  /// `home.temi` del dizionario della v2 (6 voci).
  List<({String chiave, String simbolo, String nome, String nota})> get homeTemi => [(chiave: home_temi_0_chiave, simbolo: home_temi_0_simbolo, nome: home_temi_0_nome, nota: home_temi_0_nota), (chiave: home_temi_1_chiave, simbolo: home_temi_1_simbolo, nome: home_temi_1_nome, nota: home_temi_1_nota), (chiave: home_temi_2_chiave, simbolo: home_temi_2_simbolo, nome: home_temi_2_nome, nota: home_temi_2_nota), (chiave: home_temi_3_chiave, simbolo: home_temi_3_simbolo, nome: home_temi_3_nome, nota: home_temi_3_nota), (chiave: home_temi_4_chiave, simbolo: home_temi_4_simbolo, nome: home_temi_4_nome, nota: home_temi_4_nota), (chiave: home_temi_5_chiave, simbolo: home_temi_5_simbolo, nome: home_temi_5_nome, nota: home_temi_5_nota)];
  /// `home.rito_passi` del dizionario della v2 (6 voci).
  List<({String titolo, String testo})> get homeRitoPassi => [(titolo: home_rito_passi_0_titolo, testo: home_rito_passi_0_testo), (titolo: home_rito_passi_1_titolo, testo: home_rito_passi_1_testo), (titolo: home_rito_passi_2_titolo, testo: home_rito_passi_2_testo), (titolo: home_rito_passi_3_titolo, testo: home_rito_passi_3_testo), (titolo: home_rito_passi_4_titolo, testo: home_rito_passi_4_testo), (titolo: home_rito_passi_5_titolo, testo: home_rito_passi_5_testo)];
  /// `home.vero_fatti` del dizionario della v2 (3 voci).
  List<({String titolo, String testo})> get homeVeroFatti => [(titolo: home_vero_fatti_0_titolo, testo: home_vero_fatti_0_testo), (titolo: home_vero_fatti_1_titolo, testo: home_vero_fatti_1_testo), (titolo: home_vero_fatti_2_titolo, testo: home_vero_fatti_2_testo)];
  /// `home.memoria_voci` del dizionario della v2 (3 voci).
  List<({String titolo, String testo})> get homeMemoriaVoci => [(titolo: home_memoria_voci_0_titolo, testo: home_memoria_voci_0_testo), (titolo: home_memoria_voci_1_titolo, testo: home_memoria_voci_1_testo), (titolo: home_memoria_voci_2_titolo, testo: home_memoria_voci_2_testo)];
  /// `home.diff` del dizionario della v2 (4 voci).
  List<({String simbolo, String titolo, String testo})> get homeDiff => [(simbolo: home_diff_0_simbolo, titolo: home_diff_0_titolo, testo: home_diff_0_testo), (simbolo: home_diff_1_simbolo, titolo: home_diff_1_titolo, testo: home_diff_1_testo), (simbolo: home_diff_2_simbolo, titolo: home_diff_2_titolo, testo: home_diff_2_testo), (simbolo: home_diff_3_simbolo, titolo: home_diff_3_titolo, testo: home_diff_3_testo)];
  /// `home.mazzi_futuri` del dizionario della v2 (3 voci).
  List<String> get homeMazziFuturi => [home_mazzi_futuri_0, home_mazzi_futuri_1, home_mazzi_futuri_2];
  /// `home.metodo` del dizionario della v2 (4 voci).
  List<({String titolo, String testo})> get homeMetodo => [(titolo: home_metodo_0_titolo, testo: home_metodo_0_testo), (titolo: home_metodo_1_titolo, testo: home_metodo_1_testo), (titolo: home_metodo_2_titolo, testo: home_metodo_2_testo), (titolo: home_metodo_3_titolo, testo: home_metodo_3_testo)];
  /// `home.funnel_passi` del dizionario della v2 (4 voci).
  List<({String etichetta, String testo})> get homeFunnelPassi => [(etichetta: home_funnel_passi_0_etichetta, testo: home_funnel_passi_0_testo), (etichetta: home_funnel_passi_1_etichetta, testo: home_funnel_passi_1_testo), (etichetta: home_funnel_passi_2_etichetta, testo: home_funnel_passi_2_testo), (etichetta: home_funnel_passi_3_etichetta, testo: home_funnel_passi_3_testo)];
  /// `home.diario_riserva` del dizionario della v2 (3 voci).
  List<({String etichetta, String titolo})> get homeDiarioRiserva => [(etichetta: home_diario_riserva_0_etichetta, titolo: home_diario_riserva_0_titolo), (etichetta: home_diario_riserva_1_etichetta, titolo: home_diario_riserva_1_titolo), (etichetta: home_diario_riserva_2_etichetta, titolo: home_diario_riserva_2_titolo)];
  /// `home.faq` del dizionario della v2 (5 voci).
  List<({String d, String r})> get homeFaq => [(d: home_faq_0_d, r: home_faq_0_r), (d: home_faq_1_d, r: home_faq_1_r), (d: home_faq_2_d, r: home_faq_2_r), (d: home_faq_3_d, r: home_faq_3_r), (d: home_faq_4_d, r: home_faq_4_r)];
  /// `lettura.temi` come mappa, con le chiavi originali.
  Map<String, String> get letturaTemi => {'amore': lettura_temi_amore, 'relazione': lettura_temi_relazione, 'lavoro': lettura_temi_lavoro, 'decisione': lettura_temi_decisione, 'inspiegabile': lettura_temi_inspiegabile, 'se': lettura_temi_se};
  /// `lettura.tipi_standard` come mappa, con le chiavi originali.
  Map<String, String> get letturaTipiStandard => {'nome': lettura_tipi_standard_nome, 'testo': lettura_tipi_standard_testo};
  /// `lettura.tipi_compatibilita` come mappa, con le chiavi originali.
  Map<String, String> get letturaTipiCompatibilita => {'nome': lettura_tipi_compatibilita_nome, 'testo': lettura_tipi_compatibilita_testo};
  /// `lettura.tipi_coppia` come mappa, con le chiavi originali.
  Map<String, String> get letturaTipiCoppia => {'nome': lettura_tipi_coppia_nome, 'testo': lettura_tipi_coppia_testo};
  /// `lettura.tipi_amore` come mappa, con le chiavi originali.
  Map<String, String> get letturaTipiAmore => {'nome': lettura_tipi_amore_nome, 'testo': lettura_tipi_amore_testo};
  /// `lettura.tipi_lavoro` come mappa, con le chiavi originali.
  Map<String, String> get letturaTipiLavoro => {'nome': lettura_tipi_lavoro_nome, 'testo': lettura_tipi_lavoro_testo};
  /// `lettura.stili_tradizionale` come mappa, con le chiavi originali.
  Map<String, String> get letturaStiliTradizionale => {'nome': lettura_stili_tradizionale_nome, 'testo': lettura_stili_tradizionale_testo};
  /// `lettura.stili_moderna` come mappa, con le chiavi originali.
  Map<String, String> get letturaStiliModerna => {'nome': lettura_stili_moderna_nome, 'testo': lettura_stili_moderna_testo};
  /// `lettura.stili_tendenza` come mappa, con le chiavi originali.
  Map<String, String> get letturaStiliTendenza => {'nome': lettura_stili_tendenza_nome, 'testo': lettura_stili_tendenza_testo};
  /// `lettura.generi` come mappa, con le chiavi originali.
  Map<String, String> get letturaGeneri => {'donna': lettura_generi_donna, 'uomo': lettura_generi_uomo, 'non_binario': lettura_generi_non_binario, 'altro': lettura_generi_altro, 'non_dice': lettura_generi_non_dice};
  /// `lettura.soggetti` come mappa, con le chiavi originali.
  Map<String, String> get letturaSoggetti => {'tu': lettura_soggetti_tu, 'partner': lettura_soggetti_partner, 'coppia': lettura_soggetti_coppia, 'strada_a': lettura_soggetti_strada_a, 'strada_b': lettura_soggetti_strada_b};
  /// `lettura.fasi` come mappa, con le chiavi originali.
  Map<String, String> get letturaFasi => {'unione': lettura_fasi_unione, 'guardia': lettura_fasi_guardia, 'revisione': lettura_fasi_revisione};
  /// `fisica.semi` come mappa, con le chiavi originali.
  Map<String, String> get fisicaSemi => {'maggiori': fisica_semi_maggiori, 'bastoni': fisica_semi_bastoni, 'coppe': fisica_semi_coppe, 'spade': fisica_semi_spade, 'dischi': fisica_semi_dischi};
  /// `storia.cosa` del dizionario della v2 (3 voci).
  List<({String titolo, String testo})> get storiaCosa => [(titolo: storia_cosa_0_titolo, testo: storia_cosa_0_testo), (titolo: storia_cosa_1_titolo, testo: storia_cosa_1_testo), (titolo: storia_cosa_2_titolo, testo: storia_cosa_2_testo)];
  /// `storia.stati` come mappa, con le chiavi originali.
  Map<String, String> get storiaStati => {'intervista': storia_stati_intervista, 'ventaglio': storia_stati_ventaglio, 'scelta': storia_stati_scelta, 'rivelazione': storia_stati_rivelazione, 'sintesi': storia_stati_sintesi, 'completata': storia_stati_completata, 'annullata': storia_stati_annullata};
  /// `storia.badge` come mappa, con le chiavi originali.
  Map<String, String> get storiaBadge => {'compatibilita': storia_badge_compatibilita, 'coppia': storia_badge_coppia};
  /// `storia.esiti` come mappa, con le chiavi originali.
  Map<String, String> get storiaEsiti => {'si': storia_esiti_si, 'in_parte': storia_esiti_in_parte, 'no': storia_esiti_no};
  /// `storia.segni` come mappa, con le chiavi originali.
  Map<String, String> get storiaSegni => {'ariete': storia_segni_ariete, 'toro': storia_segni_toro, 'gemelli': storia_segni_gemelli, 'cancro': storia_segni_cancro, 'leone': storia_segni_leone, 'vergine': storia_segni_vergine, 'bilancia': storia_segni_bilancia, 'scorpione': storia_segni_scorpione, 'sagittario': storia_segni_sagittario, 'capricorno': storia_segni_capricorno, 'acquario': storia_segni_acquario, 'pesci': storia_segni_pesci};
  /// `storia.aspetti` come mappa, con le chiavi originali.
  Map<String, String> get storiaAspetti => {'congiunzione': storia_aspetti_congiunzione, 'semisestile': storia_aspetti_semisestile, 'sestile': storia_aspetti_sestile, 'quadrato': storia_aspetti_quadrato, 'trigono': storia_aspetti_trigono, 'quinconce': storia_aspetti_quinconce, 'opposizione': storia_aspetti_opposizione};
  /// `storia.armonie` come mappa, con le chiavi originali.
  Map<String, String> get storiaArmonie => {'alta': storia_armonie_alta, 'buona': storia_armonie_buona, 'mista': storia_armonie_mista, 'impegnativa': storia_armonie_impegnativa};
  /// `storia.nomi_elementi` come mappa, con le chiavi originali.
  Map<String, String> get storiaNomiElementi => {'fuoco': storia_nomi_elementi_fuoco, 'terra': storia_nomi_elementi_terra, 'aria': storia_nomi_elementi_aria, 'acqua': storia_nomi_elementi_acqua};
  /// `storia.relazioni_elementi` come mappa, con le chiavi originali.
  Map<String, String> get storiaRelazioniElementi => {'rafforzata': storia_relazioni_elementi_rafforzata, 'amica': storia_relazioni_elementi_amica, 'moderata': storia_relazioni_elementi_moderata, 'ostile': storia_relazioni_elementi_ostile, 'neutra': storia_relazioni_elementi_neutra};
  /// `storia.generi` come mappa, con le chiavi originali.
  Map<String, String> get storiaGeneri => {'donna': storia_generi_donna, 'uomo': storia_generi_uomo, 'non_binario': storia_generi_non_binario, 'altro': storia_generi_altro, 'non_dice': storia_generi_non_dice};
  /// `storia.fonte` come mappa, con le chiavi originali.
  Map<String, String> get storiaFonte => {'lettura': storia_fonte_lettura, 'chat': storia_fonte_chat, 'conversione': storia_fonte_conversione};
  /// `storia.categoria` come mappa, con le chiavi originali.
  Map<String, String> get storiaCategoria => {'stabile': storia_categoria_stabile, 'tema': storia_categoria_tema, 'volatile': storia_categoria_volatile};
  /// `storia.campi` come mappa, con le chiavi originali.
  Map<String, String> get storiaCampi => {'amore': storia_campi_amore, 'lavoro': storia_campi_lavoro, 'salute': storia_campi_salute, 'famiglia': storia_campi_famiglia, 'denaro': storia_campi_denaro, 'spirituale': storia_campi_spirituale, 'altro': storia_campi_altro};
  /// `carte.filtri` come mappa, con le chiavi originali.
  Map<String, String> get carteFiltri => {'tutte': carte_filtri_tutte, 'maggiori': carte_filtri_maggiori, 'bastoni': carte_filtri_bastoni, 'coppe': carte_filtri_coppe, 'spade': carte_filtri_spade, 'dischi': carte_filtri_dischi};
  /// `carte.livelli` come mappa, con le chiavi originali.
  Map<String, String> get carteLivelli => {'essoterico': carte_livelli_essoterico, 'psicologico': carte_livelli_psicologico, 'iniziatico': carte_livelli_iniziatico, 'ombra': carte_livelli_ombra};
  /// `carte.ambiti` come mappa, con le chiavi originali.
  Map<String, String> get carteAmbiti => {'amore': carte_ambiti_amore, 'lavoro': carte_ambiti_lavoro, 'spirito': carte_ambiti_spirito};
  /// `mazzi.futuri` del dizionario della v2 (4 voci).
  List<({String simbolo, String nome})> get mazziFuturi => [(simbolo: mazzi_futuri_0_simbolo, nome: mazzi_futuri_0_nome), (simbolo: mazzi_futuri_1_simbolo, nome: mazzi_futuri_1_nome), (simbolo: mazzi_futuri_2_simbolo, nome: mazzi_futuri_2_nome), (simbolo: mazzi_futuri_3_simbolo, nome: mazzi_futuri_3_nome)];
  /// `prezzi.gratis_voci` del dizionario della v2 (3 voci).
  List<String> prezziGratisVoci({required Object n}) => [prezzi_gratis_voci_0, prezzi_gratis_voci_1(n), prezzi_gratis_voci_2];
  /// `prezzi.errori_codice` come mappa, con le chiavi originali.
  Map<String, String> get prezziErroriCodice => {'coupon_sconosciuto': prezzi_errori_codice_coupon_sconosciuto, 'coupon_non_attivo': prezzi_errori_codice_coupon_non_attivo, 'coupon_non_ancora_valido': prezzi_errori_codice_coupon_non_ancora_valido, 'coupon_scaduto': prezzi_errori_codice_coupon_scaduto, 'coupon_esaurito': prezzi_errori_codice_coupon_esaurito, 'coupon_gia_usato': prezzi_errori_codice_coupon_gia_usato, 'coupon_non_per_questo_piano': prezzi_errori_codice_coupon_non_per_questo_piano, 'coupon_solo_primo_acquisto': prezzi_errori_codice_coupon_solo_primo_acquisto, 'coupon_azzera_abbonamento': prezzi_errori_codice_coupon_azzera_abbonamento, 'coupon_sconto': prezzi_errori_codice_coupon_sconto, 'coupon_regalo': prezzi_errori_codice_coupon_regalo, 'coupon_non_cumulabile': prezzi_errori_codice_coupon_non_cumulabile, 'troppi_tentativi': prezzi_errori_codice_troppi_tentativi};
  /// `prezzi.motivi` come mappa, con le chiavi originali.
  Map<String, String> get prezziMotivi => {'accredito_piano': prezzi_motivi_accredito_piano, 'acquisto': prezzi_motivi_acquisto, 'consumo': prezzi_motivi_consumo, 'rimborso': prezzi_motivi_rimborso, 'rettifica': prezzi_motivi_rettifica, 'scadenza': prezzi_motivi_scadenza, 'omaggio': prezzi_motivi_omaggio, 'storno': prezzi_motivi_storno, 'storno_annullato': prezzi_motivi_storno_annullato};
  /// `blog.esplora_voci` del dizionario della v2 (6 voci).
  List<({String chiave, String simbolo, String titolo, String testo})> get blogEsploraVoci => [(chiave: blog_esplora_voci_0_chiave, simbolo: blog_esplora_voci_0_simbolo, titolo: blog_esplora_voci_0_titolo, testo: blog_esplora_voci_0_testo), (chiave: blog_esplora_voci_1_chiave, simbolo: blog_esplora_voci_1_simbolo, titolo: blog_esplora_voci_1_titolo, testo: blog_esplora_voci_1_testo), (chiave: blog_esplora_voci_2_chiave, simbolo: blog_esplora_voci_2_simbolo, titolo: blog_esplora_voci_2_titolo, testo: blog_esplora_voci_2_testo), (chiave: blog_esplora_voci_3_chiave, simbolo: blog_esplora_voci_3_simbolo, titolo: blog_esplora_voci_3_titolo, testo: blog_esplora_voci_3_testo), (chiave: blog_esplora_voci_4_chiave, simbolo: blog_esplora_voci_4_simbolo, titolo: blog_esplora_voci_4_titolo, testo: blog_esplora_voci_4_testo), (chiave: blog_esplora_voci_5_chiave, simbolo: blog_esplora_voci_5_simbolo, titolo: blog_esplora_voci_5_titolo, testo: blog_esplora_voci_5_testo)];
  /// `profilo.ordini_stato` come mappa, con le chiavi originali.
  Map<String, String> get profiloOrdiniStato => {'aperto': profilo_ordini_stato_aperto, 'pagato': profilo_ordini_stato_pagato, 'annullato': profilo_ordini_stato_annullato, 'scaduto': profilo_ordini_stato_scaduto};
  /// `profilo.ordini_evasione` come mappa, con le chiavi originali.
  Map<String, String> get profiloOrdiniEvasione => {'in_attesa': profilo_ordini_evasione_in_attesa, 'spedito': profilo_ordini_evasione_spedito, 'consegnato': profilo_ordini_evasione_consegnato};
  /// `profilo.ordini_tipo` come mappa, con le chiavi originali.
  Map<String, String> get profiloOrdiniTipo => {'digitale': profilo_ordini_tipo_digitale, 'pdf': profilo_ordini_tipo_pdf, 'fisico': profilo_ordini_tipo_fisico};
  /// `profilo.acc_codice_errori` come mappa, con le chiavi originali.
  Map<String, String> profiloAccCodiceErrori({required Object provider}) => {'codice_non_valido': profilo_acc_codice_errori_codice_non_valido, 'stesso_account': profilo_acc_codice_errori_stesso_account, 'gia_collegato': profilo_acc_codice_errori_gia_collegato(provider), 'abbonamento_attivo': profilo_acc_codice_errori_abbonamento_attivo, 'troppi_tentativi': profilo_acc_codice_errori_troppi_tentativi, 'nessuna_identita': profilo_acc_codice_errori_nessuna_identita, 'keycloak': profilo_acc_codice_errori_keycloak, 'generico': profilo_acc_codice_errori_generico};
  /// `privacy.finalita` del dizionario della v2 (13 voci).
  List<({String cosa, String perche, String base})> get privacyFinalita => [(cosa: privacy_finalita_0_cosa, perche: privacy_finalita_0_perche, base: privacy_finalita_0_base), (cosa: privacy_finalita_1_cosa, perche: privacy_finalita_1_perche, base: privacy_finalita_1_base), (cosa: privacy_finalita_2_cosa, perche: privacy_finalita_2_perche, base: privacy_finalita_2_base), (cosa: privacy_finalita_3_cosa, perche: privacy_finalita_3_perche, base: privacy_finalita_3_base), (cosa: privacy_finalita_4_cosa, perche: privacy_finalita_4_perche, base: privacy_finalita_4_base), (cosa: privacy_finalita_5_cosa, perche: privacy_finalita_5_perche, base: privacy_finalita_5_base), (cosa: privacy_finalita_6_cosa, perche: privacy_finalita_6_perche, base: privacy_finalita_6_base), (cosa: privacy_finalita_7_cosa, perche: privacy_finalita_7_perche, base: privacy_finalita_7_base), (cosa: privacy_finalita_8_cosa, perche: privacy_finalita_8_perche, base: privacy_finalita_8_base), (cosa: privacy_finalita_9_cosa, perche: privacy_finalita_9_perche, base: privacy_finalita_9_base), (cosa: privacy_finalita_10_cosa, perche: privacy_finalita_10_perche, base: privacy_finalita_10_base), (cosa: privacy_finalita_11_cosa, perche: privacy_finalita_11_perche, base: privacy_finalita_11_base), (cosa: privacy_finalita_12_cosa, perche: privacy_finalita_12_perche, base: privacy_finalita_12_base)];
  /// `privacy.responsabili` del dizionario della v2 (7 voci).
  List<({String chi, String cosa})> privacyResponsabili({required Object hosting, required Object fornitori_ai}) => [(chi: privacy_responsabili_0_chi, cosa: privacy_responsabili_0_cosa(hosting)), (chi: privacy_responsabili_1_chi, cosa: privacy_responsabili_1_cosa(fornitori_ai)), (chi: privacy_responsabili_2_chi, cosa: privacy_responsabili_2_cosa), (chi: privacy_responsabili_3_chi, cosa: privacy_responsabili_3_cosa), (chi: privacy_responsabili_4_chi, cosa: privacy_responsabili_4_cosa), (chi: privacy_responsabili_5_chi, cosa: privacy_responsabili_5_cosa), (chi: privacy_responsabili_6_chi, cosa: privacy_responsabili_6_cosa)];
  /// `privacy.conservazione` del dizionario della v2 (6 voci).
  List<String> get privacyConservazione => [privacy_conservazione_0, privacy_conservazione_1, privacy_conservazione_2, privacy_conservazione_3, privacy_conservazione_4, privacy_conservazione_5];
}
