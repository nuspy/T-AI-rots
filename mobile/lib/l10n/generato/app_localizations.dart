import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ar.dart';
import 'app_localizations_de.dart';
import 'app_localizations_en.dart';
import 'app_localizations_es.dart';
import 'app_localizations_fr.dart';
import 'app_localizations_hi.dart';
import 'app_localizations_hu.dart';
import 'app_localizations_it.dart';
import 'app_localizations_ko.dart';
import 'app_localizations_pl.dart';
import 'app_localizations_pt.dart';
import 'app_localizations_ro.dart';
import 'app_localizations_ru.dart';
import 'app_localizations_uk.dart';
import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generato/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale) : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('de'),
    Locale('en'),
    Locale('es'),
    Locale('fr'),
    Locale('hi'),
    Locale('hu'),
    Locale('it'),
    Locale('ko'),
    Locale('pl'),
    Locale('pt'),
    Locale('ro'),
    Locale('ru'),
    Locale('uk'),
    Locale('zh'),
  ];

  /// No description provided for @comune_marchio.
  ///
  /// In en, this message translates to:
  /// **'TAROTS chat'**
  String get comune_marchio;

  /// No description provided for @comune_salta.
  ///
  /// In en, this message translates to:
  /// **'Skip to content'**
  String get comune_salta;

  /// No description provided for @comune_aria_home.
  ///
  /// In en, this message translates to:
  /// **'TAROTS chat home'**
  String get comune_aria_home;

  /// No description provided for @comune_aria_nav.
  ///
  /// In en, this message translates to:
  /// **'Main navigation'**
  String get comune_aria_nav;

  /// No description provided for @comune_aria_lingua.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get comune_aria_lingua;

  /// No description provided for @comune_nav_leggi.
  ///
  /// In en, this message translates to:
  /// **'Read'**
  String get comune_nav_leggi;

  /// No description provided for @comune_nav_diario.
  ///
  /// In en, this message translates to:
  /// **'The\nJournal'**
  String get comune_nav_diario;

  /// No description provided for @comune_nav_giorno.
  ///
  /// In en, this message translates to:
  /// **'Card of\nthe Day'**
  String get comune_nav_giorno;

  /// No description provided for @comune_nav_fisica.
  ///
  /// In en, this message translates to:
  /// **'Your own\ncards'**
  String get comune_nav_fisica;

  /// No description provided for @comune_nav_mazzi.
  ///
  /// In en, this message translates to:
  /// **'Decks'**
  String get comune_nav_mazzi;

  /// No description provided for @comune_nav_esplora.
  ///
  /// In en, this message translates to:
  /// **'Explore'**
  String get comune_nav_esplora;

  /// No description provided for @comune_nav_storia.
  ///
  /// In en, this message translates to:
  /// **'My story'**
  String get comune_nav_storia;

  /// No description provided for @comune_nav_negozio.
  ///
  /// In en, this message translates to:
  /// **'Shop'**
  String get comune_nav_negozio;

  /// No description provided for @comune_nav_breve_leggi.
  ///
  /// In en, this message translates to:
  /// **'Read'**
  String get comune_nav_breve_leggi;

  /// No description provided for @comune_nav_breve_fisica.
  ///
  /// In en, this message translates to:
  /// **'Your\ncards'**
  String get comune_nav_breve_fisica;

  /// No description provided for @comune_nav_breve_giorno.
  ///
  /// In en, this message translates to:
  /// **'Day\'s\ncard'**
  String get comune_nav_breve_giorno;

  /// No description provided for @comune_nav_breve_diario.
  ///
  /// In en, this message translates to:
  /// **'Journal'**
  String get comune_nav_breve_diario;

  /// No description provided for @comune_nav_breve_esplora.
  ///
  /// In en, this message translates to:
  /// **'Explore'**
  String get comune_nav_breve_esplora;

  /// No description provided for @comune_nav_breve_storia.
  ///
  /// In en, this message translates to:
  /// **'My\nstory'**
  String get comune_nav_breve_storia;

  /// No description provided for @comune_nav_breve_negozio.
  ///
  /// In en, this message translates to:
  /// **'Shop'**
  String get comune_nav_breve_negozio;

  /// No description provided for @comune_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get comune_entra;

  /// No description provided for @comune_esci.
  ///
  /// In en, this message translates to:
  /// **'Sign out'**
  String get comune_esci;

  /// No description provided for @comune_profilo.
  ///
  /// In en, this message translates to:
  /// **'Your account'**
  String get comune_profilo;

  /// No description provided for @comune_inizia_lettura.
  ///
  /// In en, this message translates to:
  /// **'Start reading'**
  String get comune_inizia_lettura;

  /// No description provided for @comune_admin.
  ///
  /// In en, this message translates to:
  /// **'Console'**
  String get comune_admin;

  /// No description provided for @comune_piede_motto.
  ///
  /// In en, this message translates to:
  /// **'A living Tarot experience: question, ritual, interpretation and the thread you choose to keep.'**
  String get comune_piede_motto;

  /// No description provided for @comune_piede_leggi.
  ///
  /// In en, this message translates to:
  /// **'Read'**
  String get comune_piede_leggi;

  /// No description provided for @comune_piede_leggi_gratis.
  ///
  /// In en, this message translates to:
  /// **'Start a free reading'**
  String get comune_piede_leggi_gratis;

  /// No description provided for @comune_piede_tue_carte.
  ///
  /// In en, this message translates to:
  /// **'Use your own cards'**
  String get comune_piede_tue_carte;

  /// No description provided for @comune_piede_giorno.
  ///
  /// In en, this message translates to:
  /// **'Card of the day'**
  String get comune_piede_giorno;

  /// No description provided for @comune_piede_storia.
  ///
  /// In en, this message translates to:
  /// **'My story'**
  String get comune_piede_storia;

  /// No description provided for @comune_piede_esplora.
  ///
  /// In en, this message translates to:
  /// **'Explore'**
  String get comune_piede_esplora;

  /// No description provided for @comune_piede_mazzi.
  ///
  /// In en, this message translates to:
  /// **'Decks'**
  String get comune_piede_mazzi;

  /// No description provided for @comune_piede_carte.
  ///
  /// In en, this message translates to:
  /// **'Card library'**
  String get comune_piede_carte;

  /// No description provided for @comune_piede_stese.
  ///
  /// In en, this message translates to:
  /// **'Spreads'**
  String get comune_piede_stese;

  /// No description provided for @comune_piede_diario.
  ///
  /// In en, this message translates to:
  /// **'Journal'**
  String get comune_piede_diario;

  /// No description provided for @comune_piede_voto.
  ///
  /// In en, this message translates to:
  /// **'Vote the next deck'**
  String get comune_piede_voto;

  /// No description provided for @comune_piede_info.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get comune_piede_info;

  /// No description provided for @comune_piede_prezzi.
  ///
  /// In en, this message translates to:
  /// **'Reading packages'**
  String get comune_piede_prezzi;

  /// No description provided for @comune_piede_negozio.
  ///
  /// In en, this message translates to:
  /// **'Deck & PDF'**
  String get comune_piede_negozio;

  /// No description provided for @comune_piede_privacy.
  ///
  /// In en, this message translates to:
  /// **'Method & privacy'**
  String get comune_piede_privacy;

  /// No description provided for @comune_piede_avvertenza.
  ///
  /// In en, this message translates to:
  /// **'Tarot is a language for reflection. No reading predicts the future or replaces professional advice.'**
  String get comune_piede_avvertenza;

  /// No description provided for @comune_chiudi.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get comune_chiudi;

  /// No description provided for @comune_annulla.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get comune_annulla;

  /// No description provided for @comune_salva.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get comune_salva;

  /// No description provided for @comune_salvato.
  ///
  /// In en, this message translates to:
  /// **'Saved'**
  String get comune_salvato;

  /// No description provided for @comune_indietro.
  ///
  /// In en, this message translates to:
  /// **'Back'**
  String get comune_indietro;

  /// No description provided for @comune_avanti.
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get comune_avanti;

  /// No description provided for @comune_carica.
  ///
  /// In en, this message translates to:
  /// **'Loading…'**
  String get comune_carica;

  /// No description provided for @comune_riprova.
  ///
  /// In en, this message translates to:
  /// **'Try again'**
  String get comune_riprova;

  /// No description provided for @comune_copia.
  ///
  /// In en, this message translates to:
  /// **'Copy'**
  String get comune_copia;

  /// No description provided for @comune_copiato.
  ///
  /// In en, this message translates to:
  /// **'Copied'**
  String get comune_copiato;

  /// No description provided for @comune_si.
  ///
  /// In en, this message translates to:
  /// **'Yes'**
  String get comune_si;

  /// No description provided for @comune_no.
  ///
  /// In en, this message translates to:
  /// **'No'**
  String get comune_no;

  /// No description provided for @comune_err_generico.
  ///
  /// In en, this message translates to:
  /// **'Something did not work. Try again in a moment.'**
  String get comune_err_generico;

  /// No description provided for @comune_err_operazione.
  ///
  /// In en, this message translates to:
  /// **'That did not go through. Nothing was changed.'**
  String get comune_err_operazione;

  /// No description provided for @comune_err_sessione.
  ///
  /// In en, this message translates to:
  /// **'Your session has ended. Sign in again to continue.'**
  String get comune_err_sessione;

  /// No description provided for @comune_err_richiesta.
  ///
  /// In en, this message translates to:
  /// **'The request did not go through.'**
  String get comune_err_richiesta;

  /// No description provided for @comune_dock_apri.
  ///
  /// In en, this message translates to:
  /// **'Talk to your reader'**
  String get comune_dock_apri;

  /// No description provided for @comune_dock_titolo_anonimo.
  ///
  /// In en, this message translates to:
  /// **'What is on your mind?'**
  String get comune_dock_titolo_anonimo;

  /// No description provided for @comune_dock_testo_anonimo.
  ///
  /// In en, this message translates to:
  /// **'Write your question. You can begin without an account: the ritual and a first response are free.'**
  String get comune_dock_testo_anonimo;

  /// No description provided for @comune_dock_segnaposto_anonimo.
  ///
  /// In en, this message translates to:
  /// **'Ask your own question…'**
  String get comune_dock_segnaposto_anonimo;

  /// No description provided for @comune_dock_invia_anonimo.
  ///
  /// In en, this message translates to:
  /// **'Begin'**
  String get comune_dock_invia_anonimo;

  /// No description provided for @comune_dock_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your reader'**
  String get comune_dock_titolo;

  /// No description provided for @comune_dock_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'Write to your reader…'**
  String get comune_dock_segnaposto;

  /// No description provided for @comune_dock_invia.
  ///
  /// In en, this message translates to:
  /// **'Send'**
  String get comune_dock_invia;

  /// No description provided for @comune_dock_proposta.
  ///
  /// In en, this message translates to:
  /// **'Read the cards about: {argomento}'**
  String comune_dock_proposta(Object argomento);

  /// No description provided for @comune_dock_muto.
  ///
  /// In en, this message translates to:
  /// **'Turn the sound on'**
  String get comune_dock_muto;

  /// No description provided for @comune_dock_suono.
  ///
  /// In en, this message translates to:
  /// **'Mute'**
  String get comune_dock_suono;

  /// No description provided for @comune_dock_vuoto.
  ///
  /// In en, this message translates to:
  /// **'Your reader remembers where you left off. Write when you are ready.'**
  String get comune_dock_vuoto;

  /// No description provided for @comune_dock_attesa.
  ///
  /// In en, this message translates to:
  /// **'Your reader is writing'**
  String get comune_dock_attesa;

  /// No description provided for @comune_oracolo_apri.
  ///
  /// In en, this message translates to:
  /// **'Open the oracle'**
  String get comune_oracolo_apri;

  /// No description provided for @comune_oracolo_leggi.
  ///
  /// In en, this message translates to:
  /// **'Read the cards on this'**
  String get comune_oracolo_leggi;

  /// No description provided for @comune_oracolo_temi_0_testo.
  ///
  /// In en, this message translates to:
  /// **'Something in love is opening. Shall we look at what?'**
  String get comune_oracolo_temi_0_testo;

  /// No description provided for @comune_oracolo_temi_0_domanda.
  ///
  /// In en, this message translates to:
  /// **'What is opening in my love life?'**
  String get comune_oracolo_temi_0_domanda;

  /// No description provided for @comune_oracolo_temi_1_testo.
  ///
  /// In en, this message translates to:
  /// **'Is there a decision you keep postponing?'**
  String get comune_oracolo_temi_1_testo;

  /// No description provided for @comune_oracolo_temi_1_domanda.
  ///
  /// In en, this message translates to:
  /// **'What does each path of my decision ask of me?'**
  String get comune_oracolo_temi_1_domanda;

  /// No description provided for @comune_oracolo_temi_2_testo.
  ///
  /// In en, this message translates to:
  /// **'Your work is asking for energy. Where should it go?'**
  String get comune_oracolo_temi_2_testo;

  /// No description provided for @comune_oracolo_temi_2_domanda.
  ///
  /// In en, this message translates to:
  /// **'Where should I place my energy at work?'**
  String get comune_oracolo_temi_2_domanda;

  /// No description provided for @comune_oracolo_temi_3_testo.
  ///
  /// In en, this message translates to:
  /// **'A relationship is changing. Shall we see how?'**
  String get comune_oracolo_temi_3_testo;

  /// No description provided for @comune_oracolo_temi_3_domanda.
  ///
  /// In en, this message translates to:
  /// **'What is changing in my relationship?'**
  String get comune_oracolo_temi_3_domanda;

  /// No description provided for @comune_oracolo_temi_4_testo.
  ///
  /// In en, this message translates to:
  /// **'Something without a name keeps returning. Let\'s give it one.'**
  String get comune_oracolo_temi_4_testo;

  /// No description provided for @comune_oracolo_temi_4_domanda.
  ///
  /// In en, this message translates to:
  /// **'What is this feeling that keeps returning?'**
  String get comune_oracolo_temi_4_domanda;

  /// No description provided for @comune_oracolo_temi_5_testo.
  ///
  /// In en, this message translates to:
  /// **'Which part of you wants to be seen right now?'**
  String get comune_oracolo_temi_5_testo;

  /// No description provided for @comune_oracolo_temi_5_domanda.
  ///
  /// In en, this message translates to:
  /// **'Which part of me wants to be seen now?'**
  String get comune_oracolo_temi_5_domanda;

  /// No description provided for @comune_oracolo_temi_6_testo.
  ///
  /// In en, this message translates to:
  /// **'An ending is close. What is it making room for?'**
  String get comune_oracolo_temi_6_testo;

  /// No description provided for @comune_oracolo_temi_6_domanda.
  ///
  /// In en, this message translates to:
  /// **'What is this ending making room for in my life?'**
  String get comune_oracolo_temi_6_domanda;

  /// No description provided for @comune_oracolo_temi_7_testo.
  ///
  /// In en, this message translates to:
  /// **'Someone keeps coming back to your thoughts. Shall we ask why?'**
  String get comune_oracolo_temi_7_testo;

  /// No description provided for @comune_oracolo_temi_7_domanda.
  ///
  /// In en, this message translates to:
  /// **'Why does this person keep coming back to my thoughts?'**
  String get comune_oracolo_temi_7_domanda;

  /// No description provided for @comune_oracolo_temi_8_testo.
  ///
  /// In en, this message translates to:
  /// **'A new beginning is near. What does it need from you?'**
  String get comune_oracolo_temi_8_testo;

  /// No description provided for @comune_oracolo_temi_8_domanda.
  ///
  /// In en, this message translates to:
  /// **'What does this new beginning need from me?'**
  String get comune_oracolo_temi_8_domanda;

  /// No description provided for @comune_oracolo_temi_9_testo.
  ///
  /// In en, this message translates to:
  /// **'Are you carrying something that is not yours to carry?'**
  String get comune_oracolo_temi_9_testo;

  /// No description provided for @comune_oracolo_temi_9_domanda.
  ///
  /// In en, this message translates to:
  /// **'What am I carrying that is not mine to carry?'**
  String get comune_oracolo_temi_9_domanda;

  /// No description provided for @comune_oracolo_temi_10_testo.
  ///
  /// In en, this message translates to:
  /// **'Money and security are on your mind. Shall we look at the pattern?'**
  String get comune_oracolo_temi_10_testo;

  /// No description provided for @comune_oracolo_temi_10_domanda.
  ///
  /// In en, this message translates to:
  /// **'What pattern is shaping my relationship with money?'**
  String get comune_oracolo_temi_10_domanda;

  /// No description provided for @comune_oracolo_temi_11_testo.
  ///
  /// In en, this message translates to:
  /// **'Your family is asking for attention. What is really at stake?'**
  String get comune_oracolo_temi_11_testo;

  /// No description provided for @comune_oracolo_temi_11_domanda.
  ///
  /// In en, this message translates to:
  /// **'What is really at stake in my family right now?'**
  String get comune_oracolo_temi_11_domanda;

  /// No description provided for @comune_cookie_titolo.
  ///
  /// In en, this message translates to:
  /// **'Cookies and privacy'**
  String get comune_cookie_titolo;

  /// No description provided for @comune_cookie_testo.
  ///
  /// In en, this message translates to:
  /// **'Technical cookies keep the site working. If you agree, a random identifier also recognises your browser when you return, and Google Analytics (with its own cookies) measures how the site is used.'**
  String get comune_cookie_testo;

  /// No description provided for @comune_cookie_leggi.
  ///
  /// In en, this message translates to:
  /// **'Read the privacy page'**
  String get comune_cookie_leggi;

  /// No description provided for @comune_cookie_si.
  ///
  /// In en, this message translates to:
  /// **'It\'s fine'**
  String get comune_cookie_si;

  /// No description provided for @comune_cookie_no.
  ///
  /// In en, this message translates to:
  /// **'Please no'**
  String get comune_cookie_no;

  /// No description provided for @comune_pubblicita_etichetta.
  ///
  /// In en, this message translates to:
  /// **'Advertisement'**
  String get comune_pubblicita_etichetta;

  /// No description provided for @comune_cookie_pubblicita.
  ///
  /// In en, this message translates to:
  /// **'If you agree, Google AdSense also shows ads in a few marked spaces and uses its own cookies to deliver and measure them.'**
  String get comune_cookie_pubblicita;

  /// No description provided for @comune_cookie_pubblicita_titolo.
  ///
  /// In en, this message translates to:
  /// **'Ads on the site'**
  String get comune_cookie_pubblicita_titolo;

  /// No description provided for @comune_cookie_solo_pubblicita.
  ///
  /// In en, this message translates to:
  /// **'Some pages now have a few spaces marked “Advertisement”. If you agree, Google AdSense fills them and uses its own cookies to deliver and measure the ads.'**
  String get comune_cookie_solo_pubblicita;

  /// No description provided for @comune_consenso_banner_testo.
  ///
  /// In en, this message translates to:
  /// **'Technical cookies keep the site working and need no consent. Everything else stays off until you turn it on: accept all, reject all, or choose one by one. You can change your mind at any time.'**
  String get comune_consenso_banner_testo;

  /// No description provided for @comune_consenso_accetta_tutto.
  ///
  /// In en, this message translates to:
  /// **'Accept all'**
  String get comune_consenso_accetta_tutto;

  /// No description provided for @comune_consenso_rifiuta_tutto.
  ///
  /// In en, this message translates to:
  /// **'Reject all'**
  String get comune_consenso_rifiuta_tutto;

  /// No description provided for @comune_consenso_scegli.
  ///
  /// In en, this message translates to:
  /// **'Choose'**
  String get comune_consenso_scegli;

  /// No description provided for @comune_consenso_salva.
  ///
  /// In en, this message translates to:
  /// **'Save my choices'**
  String get comune_consenso_salva;

  /// No description provided for @comune_consenso_statistiche.
  ///
  /// In en, this message translates to:
  /// **'Site statistics'**
  String get comune_consenso_statistiche;

  /// No description provided for @comune_consenso_statistiche_testo.
  ///
  /// In en, this message translates to:
  /// **'A random identifier recognises your browser when you come back. It stays with us, never with third parties.'**
  String get comune_consenso_statistiche_testo;

  /// No description provided for @comune_consenso_google.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics'**
  String get comune_consenso_google;

  /// No description provided for @comune_consenso_google_testo.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics 4 (Google Ireland) measures how the site is used, with its own cookies; data may go to the United States.'**
  String get comune_consenso_google_testo;

  /// No description provided for @comune_consenso_pubblicita.
  ///
  /// In en, this message translates to:
  /// **'Ads'**
  String get comune_consenso_pubblicita;

  /// No description provided for @comune_consenso_pubblicita_testo.
  ///
  /// In en, this message translates to:
  /// **'Google AdSense shows ads in a few marked spaces, with its own cookies.'**
  String get comune_consenso_pubblicita_testo;

  /// No description provided for @comune_consenso_tecnici.
  ///
  /// In en, this message translates to:
  /// **'Technical cookies (signing in, the free reading, these choices) are always on: without them the site does not work.'**
  String get comune_consenso_tecnici;

  /// No description provided for @comune_eta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Before you begin'**
  String get comune_eta_titolo;

  /// No description provided for @comune_eta_titolo_no.
  ///
  /// In en, this message translates to:
  /// **'TAROTS chat is not for you yet'**
  String get comune_eta_titolo_no;

  /// No description provided for @comune_eta_testo.
  ///
  /// In en, this message translates to:
  /// **'Where you are, TAROTS chat is for people aged {anni} or over. Please confirm your age before your first reading.'**
  String comune_eta_testo(Object anni);

  /// No description provided for @comune_eta_dichiaro.
  ///
  /// In en, this message translates to:
  /// **'I am at least {anni} years old'**
  String comune_eta_dichiaro(Object anni);

  /// No description provided for @comune_eta_perche.
  ///
  /// In en, this message translates to:
  /// **'The minimum age depends on the country: it is the age at which the law lets you use online services on your own.'**
  String get comune_eta_perche;

  /// No description provided for @comune_eta_conferma.
  ///
  /// In en, this message translates to:
  /// **'Confirm'**
  String get comune_eta_conferma;

  /// No description provided for @comune_eta_non_ora.
  ///
  /// In en, this message translates to:
  /// **'Not now'**
  String get comune_eta_non_ora;

  /// No description provided for @comune_eta_insufficiente.
  ///
  /// In en, this message translates to:
  /// **'The date of birth in your account says you are under {anni}, the minimum age where you are. If it is wrong, you can correct it in your account.'**
  String comune_eta_insufficiente(Object anni);

  /// No description provided for @comune_eta_correggi.
  ///
  /// In en, this message translates to:
  /// **'Correct my date of birth'**
  String get comune_eta_correggi;

  /// No description provided for @comune_cancellazione_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your account is being deleted'**
  String get comune_cancellazione_titolo;

  /// No description provided for @comune_cancellazione_testo.
  ///
  /// In en, this message translates to:
  /// **'You asked to delete this account. Until {data} you can still change your mind: cancel the request and everything is as it was. After that date your data is deleted for good.'**
  String comune_cancellazione_testo(Object data);

  /// No description provided for @comune_cancellazione_annulla.
  ///
  /// In en, this message translates to:
  /// **'Cancel the deletion'**
  String get comune_cancellazione_annulla;

  /// No description provided for @comune_cancellazione_esci.
  ///
  /// In en, this message translates to:
  /// **'Sign out'**
  String get comune_cancellazione_esci;

  /// No description provided for @comune_sic_titolo.
  ///
  /// In en, this message translates to:
  /// **'Protect your story'**
  String get comune_sic_titolo;

  /// No description provided for @comune_sic_testo.
  ///
  /// In en, this message translates to:
  /// **'Your readings and memory are private. Two-step verification adds a temporary code from an authenticator app, so a stolen password is not enough to get in. It is optional.'**
  String get comune_sic_testo;

  /// No description provided for @comune_sic_attiva.
  ///
  /// In en, this message translates to:
  /// **'Turn it on now'**
  String get comune_sic_attiva;

  /// No description provided for @comune_sic_piu_tardi.
  ///
  /// In en, this message translates to:
  /// **'Later'**
  String get comune_sic_piu_tardi;

  /// No description provided for @comune_sic_non_mostrare.
  ///
  /// In en, this message translates to:
  /// **'Do not remind me again'**
  String get comune_sic_non_mostrare;

  /// No description provided for @comune_e404_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Nothing here'**
  String get comune_e404_eyebrow;

  /// No description provided for @comune_e404_titolo.
  ///
  /// In en, this message translates to:
  /// **'This page has not been drawn.'**
  String get comune_e404_titolo;

  /// No description provided for @comune_e404_testo.
  ///
  /// In en, this message translates to:
  /// **'The address does not exist, or the page has moved. Here is where you can go instead.'**
  String get comune_e404_testo;

  /// No description provided for @comune_e500_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'An interruption'**
  String get comune_e500_eyebrow;

  /// No description provided for @comune_e500_titolo.
  ///
  /// In en, this message translates to:
  /// **'The ritual was interrupted.'**
  String get comune_e500_titolo;

  /// No description provided for @comune_e500_testo.
  ///
  /// In en, this message translates to:
  /// **'An unexpected error stopped the page. You can try again, or continue from one of these.'**
  String get comune_e500_testo;

  /// No description provided for @comune_e_home.
  ///
  /// In en, this message translates to:
  /// **'Back to the beginning'**
  String get comune_e_home;

  /// No description provided for @comune_testata_crediti.
  ///
  /// In en, this message translates to:
  /// **'Credits'**
  String get comune_testata_crediti;

  /// No description provided for @comune_testata_crediti_tip.
  ///
  /// In en, this message translates to:
  /// **'Credits: see the prices and buy'**
  String get comune_testata_crediti_tip;

  /// No description provided for @comune_testata_crediti_tip_n.
  ///
  /// In en, this message translates to:
  /// **'You have {n}: buy more'**
  String comune_testata_crediti_tip_n(Object n);

  /// No description provided for @comune_testata_crediti_n.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 credit} other{{n} credits}}'**
  String comune_testata_crediti_n(int n);

  /// No description provided for @comune_testata_carrello.
  ///
  /// In en, this message translates to:
  /// **'Cart'**
  String get comune_testata_carrello;

  /// No description provided for @comune_testata_carrello_tip.
  ///
  /// In en, this message translates to:
  /// **'Your cart'**
  String get comune_testata_carrello_tip;

  /// No description provided for @comune_testata_carrello_tip_n.
  ///
  /// In en, this message translates to:
  /// **'Your cart: {n} items'**
  String comune_testata_carrello_tip_n(Object n);

  /// No description provided for @comune_testata_profilo.
  ///
  /// In en, this message translates to:
  /// **'Account'**
  String get comune_testata_profilo;

  /// No description provided for @comune_testata_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign\nin'**
  String get comune_testata_entra;

  /// No description provided for @comune_traduzione_offerta.
  ///
  /// In en, this message translates to:
  /// **'Read this page in {lingua}? Your browser can translate it on your device.'**
  String comune_traduzione_offerta(Object lingua);

  /// No description provided for @comune_traduzione_traduci.
  ///
  /// In en, this message translates to:
  /// **'Translate'**
  String get comune_traduzione_traduci;

  /// No description provided for @comune_traduzione_scarico.
  ///
  /// In en, this message translates to:
  /// **'Downloading the translation model… {p}%'**
  String comune_traduzione_scarico(Object p);

  /// No description provided for @comune_traduzione_in_corso.
  ///
  /// In en, this message translates to:
  /// **'Translating…'**
  String get comune_traduzione_in_corso;

  /// No description provided for @comune_traduzione_tradotta.
  ///
  /// In en, this message translates to:
  /// **'Translated automatically on your device from {da}.'**
  String comune_traduzione_tradotta(Object da);

  /// No description provided for @comune_traduzione_originale.
  ///
  /// In en, this message translates to:
  /// **'Show the original ({da})'**
  String comune_traduzione_originale(Object da);

  /// No description provided for @comune_traduzione_e_originale.
  ///
  /// In en, this message translates to:
  /// **'You are reading the original in {da}.'**
  String comune_traduzione_e_originale(Object da);

  /// No description provided for @comune_traduzione_traduci_in_lingua.
  ///
  /// In en, this message translates to:
  /// **'Translate into {lingua}'**
  String comune_traduzione_traduci_in_lingua(Object lingua);

  /// No description provided for @comune_traduzione_errore.
  ///
  /// In en, this message translates to:
  /// **'The translation did not work: you are reading the original.'**
  String get comune_traduzione_errore;

  /// No description provided for @comune_traduzione_altra_lingua.
  ///
  /// In en, this message translates to:
  /// **'Another language:'**
  String get comune_traduzione_altra_lingua;

  /// No description provided for @comune_traduzione_mai.
  ///
  /// In en, this message translates to:
  /// **'Don\'t translate automatically'**
  String get comune_traduzione_mai;

  /// No description provided for @home_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'TAROTS chat — a living Tarot ritual'**
  String get home_meta_titolo;

  /// No description provided for @home_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'A living Tarot ritual with guided interpretation and a reader who remembers your story.'**
  String get home_meta_descrizione;

  /// No description provided for @home_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Thoth Tarot · guided ritual · contextual interpretation'**
  String get home_eyebrow;

  /// No description provided for @home_titolo_1.
  ///
  /// In en, this message translates to:
  /// **'A question can become a '**
  String get home_titolo_1;

  /// No description provided for @home_titolo_em.
  ///
  /// In en, this message translates to:
  /// **'way back'**
  String get home_titolo_em;

  /// No description provided for @home_titolo_2.
  ///
  /// In en, this message translates to:
  /// **' to yourself.'**
  String get home_titolo_2;

  /// No description provided for @home_lede.
  ///
  /// In en, this message translates to:
  /// **'Ask what is on your mind. Then shuffle, cut and choose the cards yourself. TAROTS chat connects the symbols, your question and the story you bring with you.'**
  String get home_lede;

  /// No description provided for @home_domanda_etichetta.
  ///
  /// In en, this message translates to:
  /// **'What is on your mind?'**
  String get home_domanda_etichetta;

  /// No description provided for @home_domanda_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'What is on your mind?'**
  String get home_domanda_segnaposto;

  /// No description provided for @home_domanda_invia.
  ///
  /// In en, this message translates to:
  /// **'Ask your question'**
  String get home_domanda_invia;

  /// No description provided for @home_domanda_breve.
  ///
  /// In en, this message translates to:
  /// **'A few more words help the cards: write at least three letters.'**
  String get home_domanda_breve;

  /// No description provided for @home_cta_gratis.
  ///
  /// In en, this message translates to:
  /// **'Start your free reading'**
  String get home_cta_gratis;

  /// No description provided for @home_cta_fisiche.
  ///
  /// In en, this message translates to:
  /// **'Already have cards in your hands?'**
  String get home_cta_fisiche;

  /// No description provided for @home_cta_giorno.
  ///
  /// In en, this message translates to:
  /// **'Or draw today\'s card, free'**
  String get home_cta_giorno;

  /// No description provided for @home_fiducia_1.
  ///
  /// In en, this message translates to:
  /// **'No prediction is guaranteed'**
  String get home_fiducia_1;

  /// No description provided for @home_fiducia_2.
  ///
  /// In en, this message translates to:
  /// **'You choose the cards'**
  String get home_fiducia_2;

  /// No description provided for @home_fiducia_3.
  ///
  /// In en, this message translates to:
  /// **'Memory stays yours to manage'**
  String get home_fiducia_3;

  /// No description provided for @home_oggetto_aria.
  ///
  /// In en, this message translates to:
  /// **'A Thoth Tarot card on a ritual table'**
  String get home_oggetto_aria;

  /// No description provided for @home_oggetto_carta.
  ///
  /// In en, this message translates to:
  /// **'The Lovers, a Thoth Tarot card'**
  String get home_oggetto_carta;

  /// No description provided for @home_nota_titolo.
  ///
  /// In en, this message translates to:
  /// **'A living ritual'**
  String get home_nota_titolo;

  /// No description provided for @home_nota_testo.
  ///
  /// In en, this message translates to:
  /// **'Not a random card. A moment you take part in.'**
  String get home_nota_testo;

  /// No description provided for @home_demo_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'See the experience'**
  String get home_demo_eyebrow;

  /// No description provided for @home_demo_titolo.
  ///
  /// In en, this message translates to:
  /// **'The conversation leads. The ritual makes it yours.'**
  String get home_demo_titolo;

  /// No description provided for @home_demo_intro.
  ///
  /// In en, this message translates to:
  /// **'You can begin without an account. Take part in the whole ritual, receive a first response, then decide whether the full reading deserves a place in your story.'**
  String get home_demo_intro;

  /// No description provided for @home_demo_contesto.
  ///
  /// In en, this message translates to:
  /// **'A question, in context'**
  String get home_demo_contesto;

  /// No description provided for @home_demo_1.
  ///
  /// In en, this message translates to:
  /// **'“I want to know whether I am avoiding a choice.”'**
  String get home_demo_1;

  /// No description provided for @home_demo_2.
  ///
  /// In en, this message translates to:
  /// **'We can look at the choice without forcing an answer. Is the tension about a relationship, work, or both?'**
  String get home_demo_2;

  /// No description provided for @home_demo_3.
  ///
  /// In en, this message translates to:
  /// **'“Both, but the relationship is what I feel first.”'**
  String get home_demo_3;

  /// No description provided for @home_demo_carte.
  ///
  /// In en, this message translates to:
  /// **'Then the cards'**
  String get home_demo_carte;

  /// No description provided for @home_demo_didascalia.
  ///
  /// In en, this message translates to:
  /// **'Shuffle · interrupt · cut · choose · reveal'**
  String get home_demo_didascalia;

  /// No description provided for @home_demo_esempio.
  ///
  /// In en, this message translates to:
  /// **'An example conversation'**
  String get home_demo_esempio;

  /// No description provided for @home_temi_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Begin where you are'**
  String get home_temi_eyebrow;

  /// No description provided for @home_temi_titolo.
  ///
  /// In en, this message translates to:
  /// **'What is asking for your attention?'**
  String get home_temi_titolo;

  /// No description provided for @home_temi_cta.
  ///
  /// In en, this message translates to:
  /// **'Ask your own question'**
  String get home_temi_cta;

  /// No description provided for @home_temi_0_chiave.
  ///
  /// In en, this message translates to:
  /// **'amore'**
  String get home_temi_0_chiave;

  /// No description provided for @home_temi_0_simbolo.
  ///
  /// In en, this message translates to:
  /// **'♁'**
  String get home_temi_0_simbolo;

  /// No description provided for @home_temi_0_nome.
  ///
  /// In en, this message translates to:
  /// **'Love'**
  String get home_temi_0_nome;

  /// No description provided for @home_temi_0_nota.
  ///
  /// In en, this message translates to:
  /// **'what is opening'**
  String get home_temi_0_nota;

  /// No description provided for @home_temi_1_chiave.
  ///
  /// In en, this message translates to:
  /// **'relazione'**
  String get home_temi_1_chiave;

  /// No description provided for @home_temi_1_simbolo.
  ///
  /// In en, this message translates to:
  /// **'☌'**
  String get home_temi_1_simbolo;

  /// No description provided for @home_temi_1_nome.
  ///
  /// In en, this message translates to:
  /// **'Relationship'**
  String get home_temi_1_nome;

  /// No description provided for @home_temi_1_nota.
  ///
  /// In en, this message translates to:
  /// **'what is changing'**
  String get home_temi_1_nota;

  /// No description provided for @home_temi_2_chiave.
  ///
  /// In en, this message translates to:
  /// **'lavoro'**
  String get home_temi_2_chiave;

  /// No description provided for @home_temi_2_simbolo.
  ///
  /// In en, this message translates to:
  /// **'♃'**
  String get home_temi_2_simbolo;

  /// No description provided for @home_temi_2_nome.
  ///
  /// In en, this message translates to:
  /// **'Career'**
  String get home_temi_2_nome;

  /// No description provided for @home_temi_2_nota.
  ///
  /// In en, this message translates to:
  /// **'where to place energy'**
  String get home_temi_2_nota;

  /// No description provided for @home_temi_3_chiave.
  ///
  /// In en, this message translates to:
  /// **'decisione'**
  String get home_temi_3_chiave;

  /// No description provided for @home_temi_3_simbolo.
  ///
  /// In en, this message translates to:
  /// **'↔'**
  String get home_temi_3_simbolo;

  /// No description provided for @home_temi_3_nome.
  ///
  /// In en, this message translates to:
  /// **'A difficult decision'**
  String get home_temi_3_nome;

  /// No description provided for @home_temi_3_nota.
  ///
  /// In en, this message translates to:
  /// **'what each path asks'**
  String get home_temi_3_nota;

  /// No description provided for @home_temi_4_chiave.
  ///
  /// In en, this message translates to:
  /// **'inspiegabile'**
  String get home_temi_4_chiave;

  /// No description provided for @home_temi_4_simbolo.
  ///
  /// In en, this message translates to:
  /// **'◌'**
  String get home_temi_4_simbolo;

  /// No description provided for @home_temi_4_nome.
  ///
  /// In en, this message translates to:
  /// **'Something unexplained'**
  String get home_temi_4_nome;

  /// No description provided for @home_temi_4_nota.
  ///
  /// In en, this message translates to:
  /// **'what wants a name'**
  String get home_temi_4_nota;

  /// No description provided for @home_temi_5_chiave.
  ///
  /// In en, this message translates to:
  /// **'se'**
  String get home_temi_5_chiave;

  /// No description provided for @home_temi_5_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✦'**
  String get home_temi_5_simbolo;

  /// No description provided for @home_temi_5_nome.
  ///
  /// In en, this message translates to:
  /// **'Self-discovery'**
  String get home_temi_5_nome;

  /// No description provided for @home_temi_5_nota.
  ///
  /// In en, this message translates to:
  /// **'what wants to be seen'**
  String get home_temi_5_nota;

  /// No description provided for @home_rito_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'The digital ritual'**
  String get home_rito_eyebrow;

  /// No description provided for @home_rito_titolo.
  ///
  /// In en, this message translates to:
  /// **'A reading has a tempo.'**
  String get home_rito_titolo;

  /// No description provided for @home_rito_passi_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'Ask'**
  String get home_rito_passi_0_titolo;

  /// No description provided for @home_rito_passi_0_testo.
  ///
  /// In en, this message translates to:
  /// **'Give the reading a real question.'**
  String get home_rito_passi_0_testo;

  /// No description provided for @home_rito_passi_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'Shuffle'**
  String get home_rito_passi_1_titolo;

  /// No description provided for @home_rito_passi_1_testo.
  ///
  /// In en, this message translates to:
  /// **'Begin the movement, then interrupt it.'**
  String get home_rito_passi_1_testo;

  /// No description provided for @home_rito_passi_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'Cut'**
  String get home_rito_passi_2_titolo;

  /// No description provided for @home_rito_passi_2_testo.
  ///
  /// In en, this message translates to:
  /// **'Choose where the deck divides.'**
  String get home_rito_passi_2_testo;

  /// No description provided for @home_rito_passi_3_titolo.
  ///
  /// In en, this message translates to:
  /// **'Draw'**
  String get home_rito_passi_3_titolo;

  /// No description provided for @home_rito_passi_3_testo.
  ///
  /// In en, this message translates to:
  /// **'Select cards from the opened fan.'**
  String get home_rito_passi_3_testo;

  /// No description provided for @home_rito_passi_4_titolo.
  ///
  /// In en, this message translates to:
  /// **'Reveal'**
  String get home_rito_passi_4_titolo;

  /// No description provided for @home_rito_passi_4_testo.
  ///
  /// In en, this message translates to:
  /// **'See each card in its place.'**
  String get home_rito_passi_4_testo;

  /// No description provided for @home_rito_passi_5_titolo.
  ///
  /// In en, this message translates to:
  /// **'Interpret'**
  String get home_rito_passi_5_titolo;

  /// No description provided for @home_rito_passi_5_testo.
  ///
  /// In en, this message translates to:
  /// **'Connect cards, question and context.'**
  String get home_rito_passi_5_testo;

  /// No description provided for @home_vero_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A real draw, not an animation'**
  String get home_vero_eyebrow;

  /// No description provided for @home_vero_titolo.
  ///
  /// In en, this message translates to:
  /// **'Every card you touch is a real card.'**
  String get home_vero_titolo;

  /// No description provided for @home_vero_testo.
  ///
  /// In en, this message translates to:
  /// **'When the deck moves, when you cut it, when you choose from the fan, you are not watching a graphic effect. On the table lies a real deck of virtual cards — the full 78, or the 22 Major Arcana — each with its own identity and its own orientation, like the cards in your hands.'**
  String get home_vero_testo;

  /// No description provided for @home_vero_fatti_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'Shuffled by chance'**
  String get home_vero_fatti_0_titolo;

  /// No description provided for @home_vero_fatti_0_testo.
  ///
  /// In en, this message translates to:
  /// **'The order comes from a cryptographic source of randomness, not from a script. No one decides it in advance — not even us. You decide when the shuffle ends.'**
  String get home_vero_fatti_0_testo;

  /// No description provided for @home_vero_fatti_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'Cut where you choose'**
  String get home_vero_fatti_1_titolo;

  /// No description provided for @home_vero_fatti_1_testo.
  ///
  /// In en, this message translates to:
  /// **'The point you touch is where the real deck divides: the cards after it move to the front, as they would between your hands.'**
  String get home_vero_fatti_1_testo;

  /// No description provided for @home_vero_fatti_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'Sealed before you draw'**
  String get home_vero_fatti_2_titolo;

  /// No description provided for @home_vero_fatti_2_testo.
  ///
  /// In en, this message translates to:
  /// **'Before the fan opens, every card already holds its place, sealed with a cryptographic fingerprint. The card you touch is the card you draw — and at the end you can verify that nothing changed.'**
  String get home_vero_fatti_2_testo;

  /// No description provided for @home_vero_chiusa.
  ///
  /// In en, this message translates to:
  /// **'A draw as honest as one made live, at a table. What the cards say remains a matter of reflection, never a guaranteed prediction.'**
  String get home_vero_chiusa;

  /// No description provided for @home_memoria_citazione.
  ///
  /// In en, this message translates to:
  /// **'“Last week you asked how your relationship might develop. How are things going now?”'**
  String get home_memoria_citazione;

  /// No description provided for @home_memoria_piede.
  ///
  /// In en, this message translates to:
  /// **'A follow-up begins with what matters, not a blank page.'**
  String get home_memoria_piede;

  /// No description provided for @home_memoria_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Your reader remembers your story'**
  String get home_memoria_eyebrow;

  /// No description provided for @home_memoria_titolo.
  ///
  /// In en, this message translates to:
  /// **'Continuity without pretending to know more than you share.'**
  String get home_memoria_titolo;

  /// No description provided for @home_memoria_voci_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'Questions and themes'**
  String get home_memoria_voci_0_titolo;

  /// No description provided for @home_memoria_voci_0_testo.
  ///
  /// In en, this message translates to:
  /// **'so you can return to the thread of a situation.'**
  String get home_memoria_voci_0_testo;

  /// No description provided for @home_memoria_voci_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'Readings and outcomes'**
  String get home_memoria_voci_1_titolo;

  /// No description provided for @home_memoria_voci_1_testo.
  ///
  /// In en, this message translates to:
  /// **'so reflection can include what happened next.'**
  String get home_memoria_voci_1_testo;

  /// No description provided for @home_memoria_voci_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your choices'**
  String get home_memoria_voci_2_titolo;

  /// No description provided for @home_memoria_voci_2_testo.
  ///
  /// In en, this message translates to:
  /// **'you can review, edit or delete what is remembered.'**
  String get home_memoria_voci_2_testo;

  /// No description provided for @home_memoria_cta.
  ///
  /// In en, this message translates to:
  /// **'See how memory works'**
  String get home_memoria_cta;

  /// No description provided for @home_memoria_etichetta.
  ///
  /// In en, this message translates to:
  /// **'your reader remembers'**
  String get home_memoria_etichetta;

  /// No description provided for @home_diff_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Why it feels different'**
  String get home_diff_eyebrow;

  /// No description provided for @home_diff_0_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✦'**
  String get home_diff_0_simbolo;

  /// No description provided for @home_diff_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'A ritual you participate in'**
  String get home_diff_0_titolo;

  /// No description provided for @home_diff_0_testo.
  ///
  /// In en, this message translates to:
  /// **'Real virtual cards: the interruption, the cut and the choice are yours, and they count.'**
  String get home_diff_0_testo;

  /// No description provided for @home_diff_1_simbolo.
  ///
  /// In en, this message translates to:
  /// **'◌'**
  String get home_diff_1_simbolo;

  /// No description provided for @home_diff_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'Contextual interpretation'**
  String get home_diff_1_titolo;

  /// No description provided for @home_diff_1_testo.
  ///
  /// In en, this message translates to:
  /// **'The reading holds the question, positions, combinations and conversation together.'**
  String get home_diff_1_testo;

  /// No description provided for @home_diff_2_simbolo.
  ///
  /// In en, this message translates to:
  /// **'↺'**
  String get home_diff_2_simbolo;

  /// No description provided for @home_diff_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'A story with memory'**
  String get home_diff_2_titolo;

  /// No description provided for @home_diff_2_testo.
  ///
  /// In en, this message translates to:
  /// **'Return to an earlier question and see it with what has changed.'**
  String get home_diff_2_testo;

  /// No description provided for @home_diff_3_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✋'**
  String get home_diff_3_simbolo;

  /// No description provided for @home_diff_3_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your physical deck is welcome'**
  String get home_diff_3_titolo;

  /// No description provided for @home_diff_3_testo.
  ///
  /// In en, this message translates to:
  /// **'Draw cards in the room, then bring their positions here for interpretation.'**
  String get home_diff_3_testo;

  /// No description provided for @home_mazzi_disponibile.
  ///
  /// In en, this message translates to:
  /// **'Available now'**
  String get home_mazzi_disponibile;

  /// No description provided for @home_mazzi_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Choose a visual language'**
  String get home_mazzi_eyebrow;

  /// No description provided for @home_mazzi_titolo.
  ///
  /// In en, this message translates to:
  /// **'Begin with the Thoth Tarot. Leave room for more worlds.'**
  String get home_mazzi_titolo;

  /// No description provided for @home_mazzi_intro.
  ///
  /// In en, this message translates to:
  /// **'The Thoth Tarot is available now. The reading experience is designed around a deck, so new decks can bring their own card library, ritual, stories and physical edition without replacing the path you are on.'**
  String get home_mazzi_intro;

  /// No description provided for @home_mazzi_futuri_aria.
  ///
  /// In en, this message translates to:
  /// **'Future decks, not yet available'**
  String get home_mazzi_futuri_aria;

  /// No description provided for @home_mazzi_futuri_0.
  ///
  /// In en, this message translates to:
  /// **'The Lovers · planned'**
  String get home_mazzi_futuri_0;

  /// No description provided for @home_mazzi_futuri_1.
  ///
  /// In en, this message translates to:
  /// **'Italian Celebration · planned'**
  String get home_mazzi_futuri_1;

  /// No description provided for @home_mazzi_futuri_2.
  ///
  /// In en, this message translates to:
  /// **'Halloween Tarots · planned'**
  String get home_mazzi_futuri_2;

  /// No description provided for @home_mazzi_cta.
  ///
  /// In en, this message translates to:
  /// **'Explore the Thoth deck'**
  String get home_mazzi_cta;

  /// No description provided for @home_mazzi_voto.
  ///
  /// In en, this message translates to:
  /// **'Help choose the next one'**
  String get home_mazzi_voto;

  /// No description provided for @home_fisico_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A bridge to the physical world'**
  String get home_fisico_eyebrow;

  /// No description provided for @home_fisico_titolo.
  ///
  /// In en, this message translates to:
  /// **'Already have a Tarot deck?'**
  String get home_fisico_titolo;

  /// No description provided for @home_fisico_intro.
  ///
  /// In en, this message translates to:
  /// **'Draw the cards yourself, put them in their positions, and let TAROTS chat help you read the pattern. The ritual stays in your hands.'**
  String get home_fisico_intro;

  /// No description provided for @home_fisico_cta.
  ///
  /// In en, this message translates to:
  /// **'Use your own cards'**
  String get home_fisico_cta;

  /// No description provided for @home_fisico_carta_alt.
  ///
  /// In en, this message translates to:
  /// **'The Hermit, Thoth Tarot card'**
  String get home_fisico_carta_alt;

  /// No description provided for @home_fisico_scheda_titolo.
  ///
  /// In en, this message translates to:
  /// **'Physical card reading'**
  String get home_fisico_scheda_titolo;

  /// No description provided for @home_fisico_scheda_testo.
  ///
  /// In en, this message translates to:
  /// **'Choose a spread, name the cards you drew, add your question and continue with a guided interpretation.'**
  String get home_fisico_scheda_testo;

  /// No description provided for @home_metodo_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Method, trust and privacy'**
  String get home_metodo_eyebrow;

  /// No description provided for @home_metodo_titolo.
  ///
  /// In en, this message translates to:
  /// **'What happens behind a reading.'**
  String get home_metodo_titolo;

  /// No description provided for @home_metodo_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'The Thoth tradition'**
  String get home_metodo_0_titolo;

  /// No description provided for @home_metodo_0_testo.
  ///
  /// In en, this message translates to:
  /// **'Every card carries its real attributions — Hebrew letter, path, decan, sephira — and neighbouring cards modulate each other through elemental dignities.'**
  String get home_metodo_0_testo;

  /// No description provided for @home_metodo_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'One card at a time'**
  String get home_metodo_1_titolo;

  /// No description provided for @home_metodo_1_testo.
  ///
  /// In en, this message translates to:
  /// **'Cards are revealed in order. Each interpretation holds the cards already seen, then the whole spread is read together with your question and your words.'**
  String get home_metodo_1_testo;

  /// No description provided for @home_metodo_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'The role of the AI'**
  String get home_metodo_2_titolo;

  /// No description provided for @home_metodo_2_testo.
  ///
  /// In en, this message translates to:
  /// **'An AI connects symbols, positions and your words. It interprets; it does not know the future, and it tells you so.'**
  String get home_metodo_2_testo;

  /// No description provided for @home_metodo_3_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your data'**
  String get home_metodo_3_titolo;

  /// No description provided for @home_metodo_3_testo.
  ///
  /// In en, this message translates to:
  /// **'Readings and memory stay in your account. The other person\'s surname never reaches the AI, and you can delete what is remembered at any time.'**
  String get home_metodo_3_testo;

  /// No description provided for @home_funnel_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Free first, deeper by choice'**
  String get home_funnel_eyebrow;

  /// No description provided for @home_funnel_titolo.
  ///
  /// In en, this message translates to:
  /// **'Value arrives before the invitation to register.'**
  String get home_funnel_titolo;

  /// No description provided for @home_funnel_intro.
  ///
  /// In en, this message translates to:
  /// **'Your first reading is free and needs no account: you take part in the whole ritual and see a first response. When you want the full interpretation, a free account keeps it and adds {n} more free readings.'**
  String home_funnel_intro(Object n);

  /// No description provided for @home_funnel_passi_0_etichetta.
  ///
  /// In en, this message translates to:
  /// **'01 · Start'**
  String get home_funnel_passi_0_etichetta;

  /// No description provided for @home_funnel_passi_0_testo.
  ///
  /// In en, this message translates to:
  /// **'Ask a question and take part in the ritual.'**
  String get home_funnel_passi_0_testo;

  /// No description provided for @home_funnel_passi_1_etichetta.
  ///
  /// In en, this message translates to:
  /// **'02 · Deepen'**
  String get home_funnel_passi_1_etichetta;

  /// No description provided for @home_funnel_passi_1_testo.
  ///
  /// In en, this message translates to:
  /// **'See a first response to the cards you chose.'**
  String get home_funnel_passi_1_testo;

  /// No description provided for @home_funnel_passi_2_etichetta.
  ///
  /// In en, this message translates to:
  /// **'03 · Keep it'**
  String get home_funnel_passi_2_etichetta;

  /// No description provided for @home_funnel_passi_2_testo.
  ///
  /// In en, this message translates to:
  /// **'Create a free account when the reading has earned its place.'**
  String get home_funnel_passi_2_testo;

  /// No description provided for @home_funnel_passi_3_etichetta.
  ///
  /// In en, this message translates to:
  /// **'04 · Return'**
  String get home_funnel_passi_3_etichetta;

  /// No description provided for @home_funnel_passi_3_testo.
  ///
  /// In en, this message translates to:
  /// **'Keep the thread, use your free readings, come back to the story.'**
  String get home_funnel_passi_3_testo;

  /// No description provided for @home_cond_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Share an opening'**
  String get home_cond_eyebrow;

  /// No description provided for @home_cond_titolo.
  ///
  /// In en, this message translates to:
  /// **'A reading can become someone else\'s way in.'**
  String get home_cond_titolo;

  /// No description provided for @home_cond_testo.
  ///
  /// In en, this message translates to:
  /// **'Share a reading or your invitation. Whoever signs up from your link receives free readings, and so do you: {n} for every person who joins.'**
  String home_cond_testo(Object n);

  /// No description provided for @home_cond_cta.
  ///
  /// In en, this message translates to:
  /// **'Find your invitation'**
  String get home_cond_cta;

  /// No description provided for @home_diario_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'The content graph'**
  String get home_diario_eyebrow;

  /// No description provided for @home_diario_titolo.
  ///
  /// In en, this message translates to:
  /// **'A journal that leads back to a question.'**
  String get home_diario_titolo;

  /// No description provided for @home_diario_cta.
  ///
  /// In en, this message translates to:
  /// **'Visit the journal'**
  String get home_diario_cta;

  /// No description provided for @home_diario_riserva_0_etichetta.
  ///
  /// In en, this message translates to:
  /// **'Card library'**
  String get home_diario_riserva_0_etichetta;

  /// No description provided for @home_diario_riserva_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'Read the images, correspondences and meanings'**
  String get home_diario_riserva_0_titolo;

  /// No description provided for @home_diario_riserva_1_etichetta.
  ///
  /// In en, this message translates to:
  /// **'Ritual guide'**
  String get home_diario_riserva_1_etichetta;

  /// No description provided for @home_diario_riserva_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'Which spread helps a difficult decision?'**
  String get home_diario_riserva_1_titolo;

  /// No description provided for @home_diario_riserva_2_etichetta.
  ///
  /// In en, this message translates to:
  /// **'Card of the day'**
  String get home_diario_riserva_2_etichetta;

  /// No description provided for @home_diario_riserva_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'A small encounter, free every day'**
  String get home_diario_riserva_2_titolo;

  /// No description provided for @home_faq_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A clear boundary'**
  String get home_faq_eyebrow;

  /// No description provided for @home_faq_titolo.
  ///
  /// In en, this message translates to:
  /// **'Mystical does not have to mean misleading.'**
  String get home_faq_titolo;

  /// No description provided for @home_faq_0_d.
  ///
  /// In en, this message translates to:
  /// **'Is this a prediction?'**
  String get home_faq_0_d;

  /// No description provided for @home_faq_0_r.
  ///
  /// In en, this message translates to:
  /// **'No. Tarot can be a reflective language for questions, patterns and choices. It does not guarantee future events or scientific certainty.'**
  String get home_faq_0_r;

  /// No description provided for @home_faq_1_d.
  ///
  /// In en, this message translates to:
  /// **'Is it free?'**
  String get home_faq_1_d;

  /// No description provided for @home_faq_1_r.
  ///
  /// In en, this message translates to:
  /// **'Your first reading is free, without an account: you take part in the whole ritual and see a first response. A free account unlocks the full interpretation and adds free readings. After that, readings use packages or a subscription. The card of the day is always free.'**
  String get home_faq_1_r;

  /// No description provided for @home_faq_2_d.
  ///
  /// In en, this message translates to:
  /// **'What does the reader remember?'**
  String get home_faq_2_d;

  /// No description provided for @home_faq_2_r.
  ///
  /// In en, this message translates to:
  /// **'When you choose to create an account, it can retain your questions, readings and selected context to support follow-ups. You can review, edit or delete it.'**
  String get home_faq_2_r;

  /// No description provided for @home_faq_3_d.
  ///
  /// In en, this message translates to:
  /// **'Do I need a TAROTS chat deck?'**
  String get home_faq_3_d;

  /// No description provided for @home_faq_3_r.
  ///
  /// In en, this message translates to:
  /// **'No. You can use the Thoth deck in the digital ritual or draw from your own physical Tarot deck and enter the cards you pulled.'**
  String get home_faq_3_r;

  /// No description provided for @home_faq_4_d.
  ///
  /// In en, this message translates to:
  /// **'Why create an account after the first experience?'**
  String get home_faq_4_d;

  /// No description provided for @home_faq_4_r.
  ///
  /// In en, this message translates to:
  /// **'Registration is where a reading becomes part of your story: it saves the full reading, unlocks the additional free readings and lets memory work for you.'**
  String get home_faq_4_r;

  /// No description provided for @home_finale_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'The first step is simple'**
  String get home_finale_eyebrow;

  /// No description provided for @home_finale_titolo.
  ///
  /// In en, this message translates to:
  /// **'Ask the question that has been waiting.'**
  String get home_finale_titolo;

  /// No description provided for @home_finale_testo.
  ///
  /// In en, this message translates to:
  /// **'Come into the ritual. Let the cards speak. Return when life gives the question a new shape.'**
  String get home_finale_testo;

  /// No description provided for @lettura_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Start a free reading'**
  String get lettura_meta_titolo;

  /// No description provided for @lettura_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Ask your question, take part in the ritual and receive a guided interpretation of the Thoth Tarot.'**
  String get lettura_meta_descrizione;

  /// No description provided for @lettura_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A free beginning'**
  String get lettura_eyebrow;

  /// No description provided for @lettura_titolo.
  ///
  /// In en, this message translates to:
  /// **'Start with the question, not the account.'**
  String get lettura_titolo;

  /// No description provided for @lettura_intro.
  ///
  /// In en, this message translates to:
  /// **'Write what is on your mind, choose the shape of the reading, then take part in the ritual: you shuffle, you cut, you choose. Your first reading needs no account.'**
  String get lettura_intro;

  /// No description provided for @lettura_intro_dentro.
  ///
  /// In en, this message translates to:
  /// **'Write what is on your mind, choose the shape of the reading, then take part in the ritual: you shuffle, you cut, you choose.'**
  String get lettura_intro_dentro;

  /// No description provided for @lettura_pannello_conversazione.
  ///
  /// In en, this message translates to:
  /// **'Conversation'**
  String get lettura_pannello_conversazione;

  /// No description provided for @lettura_domanda_titolo.
  ///
  /// In en, this message translates to:
  /// **'What is present for you?'**
  String get lettura_domanda_titolo;

  /// No description provided for @lettura_domanda_etichetta.
  ///
  /// In en, this message translates to:
  /// **'Your question'**
  String get lettura_domanda_etichetta;

  /// No description provided for @lettura_domanda_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'Write what you want to ask the cards: a question, a doubt, a situation…'**
  String get lettura_domanda_segnaposto;

  /// No description provided for @lettura_domanda_facoltativa.
  ///
  /// In en, this message translates to:
  /// **'The question is optional here: if you leave it empty, the reading begins from the bond you are exploring.'**
  String get lettura_domanda_facoltativa;

  /// No description provided for @lettura_domanda_corta.
  ///
  /// In en, this message translates to:
  /// **'Write at least a few words: the cards need a real question.'**
  String get lettura_domanda_corta;

  /// No description provided for @lettura_temi_amore.
  ///
  /// In en, this message translates to:
  /// **'In love, what is opening for me right now?'**
  String get lettura_temi_amore;

  /// No description provided for @lettura_temi_relazione.
  ///
  /// In en, this message translates to:
  /// **'What is changing in my relationship, and what does it ask of me?'**
  String get lettura_temi_relazione;

  /// No description provided for @lettura_temi_lavoro.
  ///
  /// In en, this message translates to:
  /// **'Where should I place my energy in my work?'**
  String get lettura_temi_lavoro;

  /// No description provided for @lettura_temi_decisione.
  ///
  /// In en, this message translates to:
  /// **'I am facing a difficult decision: what does each path ask of me?'**
  String get lettura_temi_decisione;

  /// No description provided for @lettura_temi_inspiegabile.
  ///
  /// In en, this message translates to:
  /// **'Something is happening that I cannot explain. What wants a name?'**
  String get lettura_temi_inspiegabile;

  /// No description provided for @lettura_temi_se.
  ///
  /// In en, this message translates to:
  /// **'What part of myself is asking to be seen?'**
  String get lettura_temi_se;

  /// No description provided for @lettura_domanda_carta.
  ///
  /// In en, this message translates to:
  /// **'What is {carta} asking me to look at?'**
  String lettura_domanda_carta(Object carta);

  /// No description provided for @lettura_tipo_titolo.
  ///
  /// In en, this message translates to:
  /// **'What kind of reading?'**
  String get lettura_tipo_titolo;

  /// No description provided for @lettura_tipi_standard_nome.
  ///
  /// In en, this message translates to:
  /// **'A question'**
  String get lettura_tipi_standard_nome;

  /// No description provided for @lettura_tipi_standard_testo.
  ///
  /// In en, this message translates to:
  /// **'One question, one traditional spread.'**
  String get lettura_tipi_standard_testo;

  /// No description provided for @lettura_tipi_compatibilita_nome.
  ///
  /// In en, this message translates to:
  /// **'Compatibility'**
  String get lettura_tipi_compatibilita_nome;

  /// No description provided for @lettura_tipi_compatibilita_testo.
  ///
  /// In en, this message translates to:
  /// **'What joins you and another person, and what sets you apart.'**
  String get lettura_tipi_compatibilita_testo;

  /// No description provided for @lettura_tipi_coppia_nome.
  ///
  /// In en, this message translates to:
  /// **'A couple'**
  String get lettura_tipi_coppia_nome;

  /// No description provided for @lettura_tipi_coppia_testo.
  ///
  /// In en, this message translates to:
  /// **'The state of the bond you are living: strengths, friction, direction.'**
  String get lettura_tipi_coppia_testo;

  /// No description provided for @lettura_tipi_amore_nome.
  ///
  /// In en, this message translates to:
  /// **'Love and compatibility'**
  String get lettura_tipi_amore_nome;

  /// No description provided for @lettura_tipi_amore_testo.
  ///
  /// In en, this message translates to:
  /// **'The bond with another person: what joins you, what sets you apart, where it is going.'**
  String get lettura_tipi_amore_testo;

  /// No description provided for @lettura_tipi_lavoro_nome.
  ///
  /// In en, this message translates to:
  /// **'Work and business'**
  String get lettura_tipi_lavoro_nome;

  /// No description provided for @lettura_tipi_lavoro_testo.
  ///
  /// In en, this message translates to:
  /// **'Career, projects, decisions at work, a business to start or to steer.'**
  String get lettura_tipi_lavoro_testo;

  /// No description provided for @lettura_tipo_serve_account.
  ///
  /// In en, this message translates to:
  /// **'Readings about two people need a free account: the other person\'s details stay private in your story.'**
  String get lettura_tipo_serve_account;

  /// No description provided for @lettura_tipo_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in to continue'**
  String get lettura_tipo_entra;

  /// No description provided for @lettura_stesa_titolo.
  ///
  /// In en, this message translates to:
  /// **'Reading schema'**
  String get lettura_stesa_titolo;

  /// No description provided for @lettura_stili_tradizionale_nome.
  ///
  /// In en, this message translates to:
  /// **'Traditional'**
  String get lettura_stili_tradizionale_nome;

  /// No description provided for @lettura_stili_tradizionale_testo.
  ///
  /// In en, this message translates to:
  /// **'The classic spreads of the manuals.'**
  String get lettura_stili_tradizionale_testo;

  /// No description provided for @lettura_stili_moderna_nome.
  ///
  /// In en, this message translates to:
  /// **'Modern'**
  String get lettura_stili_moderna_nome;

  /// No description provided for @lettura_stili_moderna_testo.
  ///
  /// In en, this message translates to:
  /// **'Spreads from contemporary practice.'**
  String get lettura_stili_moderna_testo;

  /// No description provided for @lettura_stili_tendenza_nome.
  ///
  /// In en, this message translates to:
  /// **'Trending'**
  String get lettura_stili_tendenza_nome;

  /// No description provided for @lettura_stili_tendenza_testo.
  ///
  /// In en, this message translates to:
  /// **'The spreads most used by readers right now.'**
  String get lettura_stili_tendenza_testo;

  /// No description provided for @lettura_n_carte.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 card} other{{n} cards}}'**
  String lettura_n_carte(int n);

  /// No description provided for @lettura_maggiori.
  ///
  /// In en, this message translates to:
  /// **'22 Major Arcana'**
  String get lettura_maggiori;

  /// No description provided for @lettura_completo.
  ///
  /// In en, this message translates to:
  /// **'Full deck of 78'**
  String get lettura_completo;

  /// No description provided for @lettura_posizioni.
  ///
  /// In en, this message translates to:
  /// **'The positions'**
  String get lettura_posizioni;

  /// No description provided for @lettura_persone_titolo.
  ///
  /// In en, this message translates to:
  /// **'The people'**
  String get lettura_persone_titolo;

  /// No description provided for @lettura_persone_di_te.
  ///
  /// In en, this message translates to:
  /// **'About you'**
  String get lettura_persone_di_te;

  /// No description provided for @lettura_persone_di_te_testo.
  ///
  /// In en, this message translates to:
  /// **'These readings also need a few details about you. They stay in your account, and we will not ask again.'**
  String get lettura_persone_di_te_testo;

  /// No description provided for @lettura_persone_altra.
  ///
  /// In en, this message translates to:
  /// **'The other person'**
  String get lettura_persone_altra;

  /// No description provided for @lettura_persone_nome.
  ///
  /// In en, this message translates to:
  /// **'First name'**
  String get lettura_persone_nome;

  /// No description provided for @lettura_persone_cognome.
  ///
  /// In en, this message translates to:
  /// **'Surname (optional)'**
  String get lettura_persone_cognome;

  /// No description provided for @lettura_persone_nascita.
  ///
  /// In en, this message translates to:
  /// **'Date of birth'**
  String get lettura_persone_nascita;

  /// No description provided for @lettura_persone_genere.
  ///
  /// In en, this message translates to:
  /// **'Gender'**
  String get lettura_persone_genere;

  /// No description provided for @lettura_persone_genere_scegli.
  ///
  /// In en, this message translates to:
  /// **'Choose…'**
  String get lettura_persone_genere_scegli;

  /// No description provided for @lettura_persone_genere_altro.
  ///
  /// In en, this message translates to:
  /// **'How they describe themselves'**
  String get lettura_persone_genere_altro;

  /// No description provided for @lettura_persone_trans.
  ///
  /// In en, this message translates to:
  /// **'Trans person (optional)'**
  String get lettura_persone_trans;

  /// No description provided for @lettura_art9_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your explicit consent'**
  String get lettura_art9_titolo;

  /// No description provided for @lettura_art9_testo.
  ///
  /// In en, this message translates to:
  /// **'Being trans is sensitive personal data. We use it in readings — only to speak about the person correctly — with your explicit consent. You can withdraw it at any time from your account, and the box is cleared.'**
  String get lettura_art9_testo;

  /// No description provided for @lettura_art9_si.
  ///
  /// In en, this message translates to:
  /// **'I consent'**
  String get lettura_art9_si;

  /// No description provided for @lettura_art9_no.
  ///
  /// In en, this message translates to:
  /// **'Not now'**
  String get lettura_art9_no;

  /// No description provided for @lettura_generi_donna.
  ///
  /// In en, this message translates to:
  /// **'Woman'**
  String get lettura_generi_donna;

  /// No description provided for @lettura_generi_uomo.
  ///
  /// In en, this message translates to:
  /// **'Man'**
  String get lettura_generi_uomo;

  /// No description provided for @lettura_generi_non_binario.
  ///
  /// In en, this message translates to:
  /// **'Non-binary'**
  String get lettura_generi_non_binario;

  /// No description provided for @lettura_generi_altro.
  ///
  /// In en, this message translates to:
  /// **'Other'**
  String get lettura_generi_altro;

  /// No description provided for @lettura_generi_non_dice.
  ///
  /// In en, this message translates to:
  /// **'Prefer not to say'**
  String get lettura_generi_non_dice;

  /// No description provided for @lettura_persone_ricorda.
  ///
  /// In en, this message translates to:
  /// **'Remember these details for next time'**
  String get lettura_persone_ricorda;

  /// No description provided for @lettura_persone_privacy.
  ///
  /// In en, this message translates to:
  /// **'The other person\'s details stay in your story. They are never shared, and the surname never reaches the AI. Enter them only if you are comfortable doing so; you can forget them from your account at any time.'**
  String get lettura_persone_privacy;

  /// No description provided for @lettura_persone_ripresi.
  ///
  /// In en, this message translates to:
  /// **'I have restored the details of {nome}.'**
  String lettura_persone_ripresi(Object nome);

  /// No description provided for @lettura_persone_dimentica.
  ///
  /// In en, this message translates to:
  /// **'Forget'**
  String get lettura_persone_dimentica;

  /// No description provided for @lettura_err_nome.
  ///
  /// In en, this message translates to:
  /// **'Write the first name.'**
  String get lettura_err_nome;

  /// No description provided for @lettura_err_genere.
  ///
  /// In en, this message translates to:
  /// **'Choose an option.'**
  String get lettura_err_genere;

  /// No description provided for @lettura_err_nascita.
  ///
  /// In en, this message translates to:
  /// **'Enter a valid date of birth.'**
  String get lettura_err_nascita;

  /// No description provided for @lettura_err_altro.
  ///
  /// In en, this message translates to:
  /// **'Write how they describe themselves.'**
  String get lettura_err_altro;

  /// No description provided for @lettura_err_incompleto.
  ///
  /// In en, this message translates to:
  /// **'Fill in the missing details to continue.'**
  String get lettura_err_incompleto;

  /// No description provided for @lettura_domanda_compat.
  ///
  /// In en, this message translates to:
  /// **'Compatibility with {nome}'**
  String lettura_domanda_compat(Object nome);

  /// No description provided for @lettura_domanda_coppia.
  ///
  /// In en, this message translates to:
  /// **'Our relationship, {nome} and me'**
  String lettura_domanda_coppia(Object nome);

  /// No description provided for @lettura_pannello_rito.
  ///
  /// In en, this message translates to:
  /// **'Your ritual'**
  String get lettura_pannello_rito;

  /// No description provided for @lettura_console_attesa.
  ///
  /// In en, this message translates to:
  /// **'The deck is waiting'**
  String get lettura_console_attesa;

  /// No description provided for @lettura_console_attesa_testo.
  ///
  /// In en, this message translates to:
  /// **'When your question is ready, begin. You will shuffle, interrupt, cut and choose the cards yourself.'**
  String get lettura_console_attesa_testo;

  /// No description provided for @lettura_vero_breve.
  ///
  /// In en, this message translates to:
  /// **'Not an animation: a real deck of virtual cards, shuffled by chance, cut where you touch and sealed before you draw. The card you choose is the card you receive.'**
  String get lettura_vero_breve;

  /// No description provided for @lettura_inizia.
  ///
  /// In en, this message translates to:
  /// **'Stop with the question and go to the ritual'**
  String get lettura_inizia;

  /// No description provided for @lettura_carte_svelate.
  ///
  /// In en, this message translates to:
  /// **'The cards, one by one'**
  String get lettura_carte_svelate;

  /// No description provided for @lettura_lettore_legge.
  ///
  /// In en, this message translates to:
  /// **'Your reader is reading the cards…'**
  String get lettura_lettore_legge;

  /// No description provided for @lettura_rito_riapri.
  ///
  /// In en, this message translates to:
  /// **'Open the ritual'**
  String get lettura_rito_riapri;

  /// No description provided for @lettura_rivela_tutto.
  ///
  /// In en, this message translates to:
  /// **'Reveal the cards and receive the interpretation'**
  String get lettura_rivela_tutto;

  /// No description provided for @lettura_cambia.
  ///
  /// In en, this message translates to:
  /// **'Change'**
  String get lettura_cambia;

  /// No description provided for @lettura_basta_dopo.
  ///
  /// In en, this message translates to:
  /// **'Available after the first answers'**
  String get lettura_basta_dopo;

  /// No description provided for @lettura_basta_domande.
  ///
  /// In en, this message translates to:
  /// **'Enough questions'**
  String get lettura_basta_domande;

  /// No description provided for @lettura_scelta_titolo.
  ///
  /// In en, this message translates to:
  /// **'What would you like to do?'**
  String get lettura_scelta_titolo;

  /// No description provided for @lettura_scelta_lettura.
  ///
  /// In en, this message translates to:
  /// **'Go to the reading'**
  String get lettura_scelta_lettura;

  /// No description provided for @lettura_scelta_libero.
  ///
  /// In en, this message translates to:
  /// **'I want to say something freely'**
  String get lettura_scelta_libero;

  /// No description provided for @lettura_scelta_altra.
  ///
  /// In en, this message translates to:
  /// **'I want to answer another question'**
  String get lettura_scelta_altra;

  /// No description provided for @lettura_libero_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'Write freely whatever comes to mind…'**
  String get lettura_libero_segnaposto;

  /// No description provided for @lettura_libero_invia.
  ///
  /// In en, this message translates to:
  /// **'Send'**
  String get lettura_libero_invia;

  /// No description provided for @lettura_invia_basta.
  ///
  /// In en, this message translates to:
  /// **'Send, no more questions'**
  String get lettura_invia_basta;

  /// No description provided for @lettura_invia_altra.
  ///
  /// In en, this message translates to:
  /// **'Send and ask me another question'**
  String get lettura_invia_altra;

  /// No description provided for @lettura_altra_domanda.
  ///
  /// In en, this message translates to:
  /// **'Ask me another question'**
  String get lettura_altra_domanda;

  /// No description provided for @lettura_invia_dire.
  ///
  /// In en, this message translates to:
  /// **'Send, I want to say something'**
  String get lettura_invia_dire;

  /// No description provided for @lettura_invia_dire_ancora.
  ///
  /// In en, this message translates to:
  /// **'Send, I want to say something else'**
  String get lettura_invia_dire_ancora;

  /// No description provided for @lettura_stampa_pdf.
  ///
  /// In en, this message translates to:
  /// **'Print to PDF'**
  String get lettura_stampa_pdf;

  /// No description provided for @lettura_vero_info.
  ///
  /// In en, this message translates to:
  /// **'Why these are real cards (optional)'**
  String get lettura_vero_info;

  /// No description provided for @lettura_stesa_info.
  ///
  /// In en, this message translates to:
  /// **'About this spread (optional)'**
  String get lettura_stesa_info;

  /// No description provided for @lettura_altro_no.
  ///
  /// In en, this message translates to:
  /// **'No, that\'s enough'**
  String get lettura_altro_no;

  /// No description provided for @lettura_altro_si.
  ///
  /// In en, this message translates to:
  /// **'Yeah, let\'s go'**
  String get lettura_altro_si;

  /// No description provided for @lettura_altro_titolo.
  ///
  /// In en, this message translates to:
  /// **'Would you like to tell me a little more?'**
  String get lettura_altro_titolo;

  /// No description provided for @lettura_inizia_breve.
  ///
  /// In en, this message translates to:
  /// **'Begin'**
  String get lettura_inizia_breve;

  /// No description provided for @lettura_cambia_tipo.
  ///
  /// In en, this message translates to:
  /// **'Change the kind of reading'**
  String get lettura_cambia_tipo;

  /// No description provided for @lettura_avviso_titolo.
  ///
  /// In en, this message translates to:
  /// **'Before we begin'**
  String get lettura_avviso_titolo;

  /// No description provided for @lettura_avviso_accetta.
  ///
  /// In en, this message translates to:
  /// **'I understand, let us begin'**
  String get lettura_avviso_accetta;

  /// No description provided for @lettura_tu.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get lettura_tu;

  /// No description provided for @lettura_lettore.
  ///
  /// In en, this message translates to:
  /// **'Your reader'**
  String get lettura_lettore;

  /// No description provided for @lettura_sistema.
  ///
  /// In en, this message translates to:
  /// **'✦'**
  String get lettura_sistema;

  /// No description provided for @lettura_pensa.
  ///
  /// In en, this message translates to:
  /// **'Your reader is thinking'**
  String get lettura_pensa;

  /// No description provided for @lettura_risposta_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'Write your answer…'**
  String get lettura_risposta_segnaposto;

  /// No description provided for @lettura_rispondi.
  ///
  /// In en, this message translates to:
  /// **'Answer'**
  String get lettura_rispondi;

  /// No description provided for @lettura_console_intervista.
  ///
  /// In en, this message translates to:
  /// **'A few questions first'**
  String get lettura_console_intervista;

  /// No description provided for @lettura_console_intervista_testo.
  ///
  /// In en, this message translates to:
  /// **'Your reader asks a few questions to understand the context. Answer in your own words, then the deck will be ready.'**
  String get lettura_console_intervista_testo;

  /// No description provided for @lettura_console_pronto.
  ///
  /// In en, this message translates to:
  /// **'The deck is ready'**
  String get lettura_console_pronto;

  /// No description provided for @lettura_console_pronto_testo.
  ///
  /// In en, this message translates to:
  /// **'When you are ready, begin the shuffle. The deck on the table is a real deck: you will decide when the shuffle ends.'**
  String get lettura_console_pronto_testo;

  /// No description provided for @lettura_mescola.
  ///
  /// In en, this message translates to:
  /// **'Begin the shuffle'**
  String get lettura_mescola;

  /// No description provided for @lettura_console_mescola.
  ///
  /// In en, this message translates to:
  /// **'The deck is moving'**
  String get lettura_console_mescola;

  /// No description provided for @lettura_console_mescola_testo.
  ///
  /// In en, this message translates to:
  /// **'Let it move for a moment. When it feels right, touch the deck: the shuffle ends when you say so.'**
  String get lettura_console_mescola_testo;

  /// No description provided for @lettura_ferma.
  ///
  /// In en, this message translates to:
  /// **'Interrupt the shuffle'**
  String get lettura_ferma;

  /// No description provided for @lettura_console_taglio.
  ///
  /// In en, this message translates to:
  /// **'Cut the deck'**
  String get lettura_console_taglio;

  /// No description provided for @lettura_console_taglio_testo.
  ///
  /// In en, this message translates to:
  /// **'Where you touch is where the real deck divides: the cards after it move to the front, as between your hands. Touch the point, or use the arrow keys and Enter.'**
  String get lettura_console_taglio_testo;

  /// No description provided for @lettura_taglio_aria.
  ///
  /// In en, this message translates to:
  /// **'Cut the deck at the chosen point'**
  String get lettura_taglio_aria;

  /// No description provided for @lettura_console_scelta.
  ///
  /// In en, this message translates to:
  /// **'Choose the cards'**
  String get lettura_console_scelta;

  /// No description provided for @lettura_console_scelta_sigillo.
  ///
  /// In en, this message translates to:
  /// **'The deck is sealed: every face-down card already holds its place. The one you touch is the one you draw.'**
  String get lettura_console_scelta_sigillo;

  /// No description provided for @lettura_scegli_uno.
  ///
  /// In en, this message translates to:
  /// **'Choose the last card'**
  String get lettura_scegli_uno;

  /// No description provided for @lettura_scegli_n.
  ///
  /// In en, this message translates to:
  /// **'Choose {n} more cards'**
  String lettura_scegli_n(Object n);

  /// No description provided for @lettura_ventaglio_aria.
  ///
  /// In en, this message translates to:
  /// **'The fan of face-down cards'**
  String get lettura_ventaglio_aria;

  /// No description provided for @lettura_carta_n.
  ///
  /// In en, this message translates to:
  /// **'Card {n}'**
  String lettura_carta_n(Object n);

  /// No description provided for @lettura_console_rivela.
  ///
  /// In en, this message translates to:
  /// **'Reveal the cards and receive the interpretation'**
  String get lettura_console_rivela;

  /// No description provided for @lettura_console_rivela_testo.
  ///
  /// In en, this message translates to:
  /// **'Your cards are on the table. Turn them over: each one is explained in its place, then the whole reading is interpreted.'**
  String get lettura_console_rivela_testo;

  /// No description provided for @lettura_rivela.
  ///
  /// In en, this message translates to:
  /// **'Reveal card {n}'**
  String lettura_rivela(Object n);

  /// No description provided for @lettura_console_sintesi.
  ///
  /// In en, this message translates to:
  /// **'Every card is in its place'**
  String get lettura_console_sintesi;

  /// No description provided for @lettura_console_sintesi_testo.
  ///
  /// In en, this message translates to:
  /// **'The cards can now speak to each other: your question, your words and the spread, held together.'**
  String get lettura_console_sintesi_testo;

  /// No description provided for @lettura_responso.
  ///
  /// In en, this message translates to:
  /// **'Receive the interpretation'**
  String get lettura_responso;

  /// No description provided for @lettura_carta_coperta.
  ///
  /// In en, this message translates to:
  /// **'Face-down card'**
  String get lettura_carta_coperta;

  /// No description provided for @lettura_dritta.
  ///
  /// In en, this message translates to:
  /// **'upright'**
  String get lettura_dritta;

  /// No description provided for @lettura_rovesciata.
  ///
  /// In en, this message translates to:
  /// **'reversed'**
  String get lettura_rovesciata;

  /// No description provided for @lettura_dignita.
  ///
  /// In en, this message translates to:
  /// **'Dignity'**
  String get lettura_dignita;

  /// No description provided for @lettura_doppia.
  ///
  /// In en, this message translates to:
  /// **'Double value'**
  String get lettura_doppia;

  /// No description provided for @lettura_legenda.
  ///
  /// In en, this message translates to:
  /// **'Who is who'**
  String get lettura_legenda;

  /// No description provided for @lettura_soggetti_tu.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get lettura_soggetti_tu;

  /// No description provided for @lettura_soggetti_partner.
  ///
  /// In en, this message translates to:
  /// **'The other person'**
  String get lettura_soggetti_partner;

  /// No description provided for @lettura_soggetti_coppia.
  ///
  /// In en, this message translates to:
  /// **'The relationship'**
  String get lettura_soggetti_coppia;

  /// No description provided for @lettura_soggetti_strada_a.
  ///
  /// In en, this message translates to:
  /// **'Path A'**
  String get lettura_soggetti_strada_a;

  /// No description provided for @lettura_soggetti_strada_b.
  ///
  /// In en, this message translates to:
  /// **'Path B'**
  String get lettura_soggetti_strada_b;

  /// No description provided for @lettura_tu_e.
  ///
  /// In en, this message translates to:
  /// **'You and {nome}'**
  String lettura_tu_e(Object nome);

  /// No description provided for @lettura_fasi_unione.
  ///
  /// In en, this message translates to:
  /// **'The cards speak to each other: question, conversation and spread are joined…'**
  String get lettura_fasi_unione;

  /// No description provided for @lettura_fasi_guardia.
  ///
  /// In en, this message translates to:
  /// **'The interpretation is being checked for care and clarity…'**
  String get lettura_fasi_guardia;

  /// No description provided for @lettura_fasi_revisione.
  ///
  /// In en, this message translates to:
  /// **'The interpretation is being revised with greater care…'**
  String get lettura_fasi_revisione;

  /// No description provided for @lettura_il_responso.
  ///
  /// In en, this message translates to:
  /// **'The interpretation'**
  String get lettura_il_responso;

  /// No description provided for @lettura_anteprima_titolo.
  ///
  /// In en, this message translates to:
  /// **'A first response'**
  String get lettura_anteprima_titolo;

  /// No description provided for @lettura_anteprima_testo.
  ///
  /// In en, this message translates to:
  /// **'This is the beginning of your reading. The full interpretation — every card in its place, their combinations and your context — is kept for you in a free account.'**
  String get lettura_anteprima_testo;

  /// No description provided for @lettura_anteprima_cta.
  ///
  /// In en, this message translates to:
  /// **'Get the full reading free'**
  String get lettura_anteprima_cta;

  /// No description provided for @lettura_anteprima_extra.
  ///
  /// In en, this message translates to:
  /// **'With a free account the full reading is yours, and you receive {n} more free readings.'**
  String lettura_anteprima_extra(Object n);

  /// No description provided for @lettura_verifica.
  ///
  /// In en, this message translates to:
  /// **'Verify the draw'**
  String get lettura_verifica;

  /// No description provided for @lettura_verifica_testo.
  ///
  /// In en, this message translates to:
  /// **'The deck was shuffled, cut where you touched and sealed before your choice. This is its fingerprint; with the salt revealed at the end, anyone can check that no card changed after you chose:'**
  String get lettura_verifica_testo;

  /// No description provided for @lettura_condividi.
  ///
  /// In en, this message translates to:
  /// **'Share this reading'**
  String get lettura_condividi;

  /// No description provided for @lettura_nuova.
  ///
  /// In en, this message translates to:
  /// **'Ask a new question'**
  String get lettura_nuova;

  /// No description provided for @lettura_vai_storia.
  ///
  /// In en, this message translates to:
  /// **'See it in your story'**
  String get lettura_vai_storia;

  /// No description provided for @lettura_crediti_finiti.
  ///
  /// In en, this message translates to:
  /// **'You have used your readings'**
  String get lettura_crediti_finiti;

  /// No description provided for @lettura_crediti_finiti_testo.
  ///
  /// In en, this message translates to:
  /// **'Each reading uses one credit, or one of your subscription\'s daily readings. Choose a package or a subscription to continue your practice.'**
  String get lettura_crediti_finiti_testo;

  /// No description provided for @lettura_vedi_prezzi.
  ///
  /// In en, this message translates to:
  /// **'See reading packages'**
  String get lettura_vedi_prezzi;

  /// No description provided for @lettura_gia_usata.
  ///
  /// In en, this message translates to:
  /// **'You have already used your free reading on this browser. Create a free account to continue: it adds free readings to your story.'**
  String get lettura_gia_usata;

  /// No description provided for @lettura_gia_usata_cta.
  ///
  /// In en, this message translates to:
  /// **'Create a free account'**
  String get lettura_gia_usata_cta;

  /// No description provided for @lettura_crisi_titolo.
  ///
  /// In en, this message translates to:
  /// **'Let us pause here'**
  String get lettura_crisi_titolo;

  /// No description provided for @lettura_pausa_titolo.
  ///
  /// In en, this message translates to:
  /// **'This reading is paused'**
  String get lettura_pausa_titolo;

  /// No description provided for @lettura_riprova.
  ///
  /// In en, this message translates to:
  /// **'Try again'**
  String get lettura_riprova;

  /// No description provided for @lettura_err_oracolo.
  ///
  /// In en, this message translates to:
  /// **'Your reader did not answer. Try again.'**
  String get lettura_err_oracolo;

  /// No description provided for @lettura_err_lettura.
  ///
  /// In en, this message translates to:
  /// **'The reading did not begin. Try again.'**
  String get lettura_err_lettura;

  /// No description provided for @lettura_err_mazzo.
  ///
  /// In en, this message translates to:
  /// **'The deck did not open. Try again.'**
  String get lettura_err_mazzo;

  /// No description provided for @lettura_err_posa.
  ///
  /// In en, this message translates to:
  /// **'The card was not placed. Try again.'**
  String get lettura_err_posa;

  /// No description provided for @lettura_err_giro.
  ///
  /// In en, this message translates to:
  /// **'The card did not turn over. Try again.'**
  String get lettura_err_giro;

  /// No description provided for @lettura_err_responso.
  ///
  /// In en, this message translates to:
  /// **'The interpretation did not arrive. Try again.'**
  String get lettura_err_responso;

  /// No description provided for @lettura_cond_titolo.
  ///
  /// In en, this message translates to:
  /// **'Share this reading'**
  String get lettura_cond_titolo;

  /// No description provided for @lettura_cond_anteprima.
  ///
  /// In en, this message translates to:
  /// **'Preview of what you share'**
  String get lettura_cond_anteprima;

  /// No description provided for @lettura_cond_testo.
  ///
  /// In en, this message translates to:
  /// **'Your words (optional)'**
  String get lettura_cond_testo;

  /// No description provided for @lettura_cond_testo_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'For example: this is what the cards showed me'**
  String get lettura_cond_testo_segnaposto;

  /// No description provided for @lettura_cond_testo_aiuto.
  ///
  /// In en, this message translates to:
  /// **'They appear on the image and in the post.'**
  String get lettura_cond_testo_aiuto;

  /// No description provided for @lettura_cond_preparo.
  ///
  /// In en, this message translates to:
  /// **'Preparing the image and the link…'**
  String get lettura_cond_preparo;

  /// No description provided for @lettura_cond_pronta.
  ///
  /// In en, this message translates to:
  /// **'Ready: choose where to share.'**
  String get lettura_cond_pronta;

  /// No description provided for @lettura_cond_errore.
  ///
  /// In en, this message translates to:
  /// **'The sharing could not be prepared.'**
  String get lettura_cond_errore;

  /// No description provided for @lettura_cond_su.
  ///
  /// In en, this message translates to:
  /// **'Share on'**
  String get lettura_cond_su;

  /// No description provided for @lettura_cond_con.
  ///
  /// In en, this message translates to:
  /// **'Share with {nome}'**
  String lettura_cond_con(Object nome);

  /// No description provided for @lettura_cond_email.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get lettura_cond_email;

  /// No description provided for @lettura_cond_link.
  ///
  /// In en, this message translates to:
  /// **'Link only'**
  String get lettura_cond_link;

  /// No description provided for @lettura_cond_copiato.
  ///
  /// In en, this message translates to:
  /// **'Link copied'**
  String get lettura_cond_copiato;

  /// No description provided for @lettura_cond_scaricata.
  ///
  /// In en, this message translates to:
  /// **'Image downloaded and text copied: upload it on {rete}.'**
  String lettura_cond_scaricata(Object rete);

  /// No description provided for @lettura_cond_apri.
  ///
  /// In en, this message translates to:
  /// **'Open {rete}'**
  String lettura_cond_apri(Object rete);

  /// No description provided for @lettura_cond_scarica.
  ///
  /// In en, this message translates to:
  /// **'Download the image'**
  String get lettura_cond_scarica;

  /// No description provided for @lettura_cond_premio_titolo.
  ///
  /// In en, this message translates to:
  /// **'Share and receive readings'**
  String get lettura_cond_premio_titolo;

  /// No description provided for @lettura_cond_premio_1.
  ///
  /// In en, this message translates to:
  /// **'Every {n} verified shares, one free reading'**
  String lettura_cond_premio_1(Object n);

  /// No description provided for @lettura_cond_premio_2.
  ///
  /// In en, this message translates to:
  /// **'Whoever signs up from your link gives you {n} free readings'**
  String lettura_cond_premio_2(Object n);

  /// No description provided for @lettura_cond_premio_3.
  ///
  /// In en, this message translates to:
  /// **'No limit: every opening you share can come back to you'**
  String get lettura_cond_premio_3;

  /// No description provided for @lettura_cond_contatore.
  ///
  /// In en, this message translates to:
  /// **'{v} verified shares · {m} to go until the next free reading'**
  String lettura_cond_contatore(Object v, Object m);

  /// No description provided for @lettura_cond_verificata.
  ///
  /// In en, this message translates to:
  /// **'A share is verified when someone else opens your link.'**
  String get lettura_cond_verificata;

  /// No description provided for @lettura_cond_speciale.
  ///
  /// In en, this message translates to:
  /// **'In readings about two people the other person\'s name never appears: a symbol and the words “someone special” take its place.'**
  String get lettura_cond_speciale;

  /// No description provided for @lettura_cond_attivo.
  ///
  /// In en, this message translates to:
  /// **'The link is active: whoever opens it sees the reading, never your name.'**
  String get lettura_cond_attivo;

  /// No description provided for @lettura_cond_disattiva.
  ///
  /// In en, this message translates to:
  /// **'Turn the link off'**
  String get lettura_cond_disattiva;

  /// No description provided for @lettura_mazzo_titolo.
  ///
  /// In en, this message translates to:
  /// **'Which deck'**
  String get lettura_mazzo_titolo;

  /// No description provided for @fisica_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Read your physical cards'**
  String get fisica_meta_titolo;

  /// No description provided for @fisica_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Draw the cards with your own Tarot deck, place them in a spread, and receive a guided interpretation.'**
  String get fisica_meta_descrizione;

  /// No description provided for @fisica_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Physical Tarot mode'**
  String get fisica_eyebrow;

  /// No description provided for @fisica_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your hands draw the cards. The reader helps you hear the pattern.'**
  String get fisica_titolo;

  /// No description provided for @fisica_intro.
  ///
  /// In en, this message translates to:
  /// **'Choose the spread you used, name the cards you actually drew, then add your question. Nothing is drawn again: the reading starts from your table.'**
  String get fisica_intro;

  /// No description provided for @fisica_passo_1.
  ///
  /// In en, this message translates to:
  /// **'1 · Place the cards'**
  String get fisica_passo_1;

  /// No description provided for @fisica_stesa_titolo.
  ///
  /// In en, this message translates to:
  /// **'Which spread did you lay out?'**
  String get fisica_stesa_titolo;

  /// No description provided for @fisica_cambia_stesa.
  ///
  /// In en, this message translates to:
  /// **'Choose another spread'**
  String get fisica_cambia_stesa;

  /// No description provided for @fisica_posiziona.
  ///
  /// In en, this message translates to:
  /// **'Touch each position and name the card you found there.'**
  String get fisica_posiziona;

  /// No description provided for @fisica_aggiungi.
  ///
  /// In en, this message translates to:
  /// **'Name'**
  String get fisica_aggiungi;

  /// No description provided for @fisica_modifica.
  ///
  /// In en, this message translates to:
  /// **'Change'**
  String get fisica_modifica;

  /// No description provided for @fisica_mancano.
  ///
  /// In en, this message translates to:
  /// **'{n} positions still to name'**
  String fisica_mancano(Object n);

  /// No description provided for @fisica_manca_una.
  ///
  /// In en, this message translates to:
  /// **'One position still to name'**
  String get fisica_manca_una;

  /// No description provided for @fisica_pronte.
  ///
  /// In en, this message translates to:
  /// **'Every card is in its place.'**
  String get fisica_pronte;

  /// No description provided for @fisica_passo_2.
  ///
  /// In en, this message translates to:
  /// **'2 · Give it a question'**
  String get fisica_passo_2;

  /// No description provided for @fisica_domanda_titolo.
  ///
  /// In en, this message translates to:
  /// **'What should the cards help you examine?'**
  String get fisica_domanda_titolo;

  /// No description provided for @fisica_domanda_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'Write your question in your own words…'**
  String get fisica_domanda_segnaposto;

  /// No description provided for @fisica_domanda_testo.
  ///
  /// In en, this message translates to:
  /// **'Your physical draw remains yours. The interpretation begins when you name what you want to understand.'**
  String get fisica_domanda_testo;

  /// No description provided for @fisica_interpreta.
  ///
  /// In en, this message translates to:
  /// **'Interpret my cards'**
  String get fisica_interpreta;

  /// No description provided for @fisica_serve_account.
  ///
  /// In en, this message translates to:
  /// **'Interpreting your own cards needs a free account: your table and question are kept while you sign in.'**
  String get fisica_serve_account;

  /// No description provided for @fisica_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in to continue'**
  String get fisica_entra;

  /// No description provided for @fisica_seme_titolo.
  ///
  /// In en, this message translates to:
  /// **'{posizione}: which suit?'**
  String fisica_seme_titolo(Object posizione);

  /// No description provided for @fisica_carta_titolo.
  ///
  /// In en, this message translates to:
  /// **'{posizione}: which card?'**
  String fisica_carta_titolo(Object posizione);

  /// No description provided for @fisica_semi_maggiori.
  ///
  /// In en, this message translates to:
  /// **'Major Arcana'**
  String get fisica_semi_maggiori;

  /// No description provided for @fisica_semi_bastoni.
  ///
  /// In en, this message translates to:
  /// **'Wands'**
  String get fisica_semi_bastoni;

  /// No description provided for @fisica_semi_coppe.
  ///
  /// In en, this message translates to:
  /// **'Cups'**
  String get fisica_semi_coppe;

  /// No description provided for @fisica_semi_spade.
  ///
  /// In en, this message translates to:
  /// **'Swords'**
  String get fisica_semi_spade;

  /// No description provided for @fisica_semi_dischi.
  ///
  /// In en, this message translates to:
  /// **'Disks'**
  String get fisica_semi_dischi;

  /// No description provided for @fisica_conferma.
  ///
  /// In en, this message translates to:
  /// **'Place this card'**
  String get fisica_conferma;

  /// No description provided for @fisica_gia_posata.
  ///
  /// In en, this message translates to:
  /// **'already on the table'**
  String get fisica_gia_posata;

  /// No description provided for @storia_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'My story'**
  String get storia_meta_titolo;

  /// No description provided for @storia_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Your readings, their outcomes and what your reader remembers — yours to review, edit or release.'**
  String get storia_meta_descrizione;

  /// No description provided for @storia_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Your reader remembers your story'**
  String get storia_eyebrow;

  /// No description provided for @storia_titolo.
  ///
  /// In en, this message translates to:
  /// **'A private thread you can return to, edit or release.'**
  String get storia_titolo;

  /// No description provided for @storia_intro.
  ///
  /// In en, this message translates to:
  /// **'Every reading you keep becomes part of a story. Your reader uses it to continue where you left off — and you decide what stays.'**
  String get storia_intro;

  /// No description provided for @storia_fuori_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your story begins with a reading'**
  String get storia_fuori_titolo;

  /// No description provided for @storia_fuori_testo.
  ///
  /// In en, this message translates to:
  /// **'With a free account, your readings are kept, you can note what happened next, and your reader can pick up the thread: “Last week you asked about your relationship. How are things going now?”'**
  String get storia_fuori_testo;

  /// No description provided for @storia_fuori_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get storia_fuori_entra;

  /// No description provided for @storia_fuori_inizia.
  ///
  /// In en, this message translates to:
  /// **'Start your free reading'**
  String get storia_fuori_inizia;

  /// No description provided for @storia_cosa_titolo.
  ///
  /// In en, this message translates to:
  /// **'What is remembered'**
  String get storia_cosa_titolo;

  /// No description provided for @storia_cosa_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'Questions and themes'**
  String get storia_cosa_0_titolo;

  /// No description provided for @storia_cosa_0_testo.
  ///
  /// In en, this message translates to:
  /// **'so you can return to the thread of a situation.'**
  String get storia_cosa_0_testo;

  /// No description provided for @storia_cosa_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'Readings and outcomes'**
  String get storia_cosa_1_titolo;

  /// No description provided for @storia_cosa_1_testo.
  ///
  /// In en, this message translates to:
  /// **'so reflection can include what happened next.'**
  String get storia_cosa_1_testo;

  /// No description provided for @storia_cosa_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'Context you choose to share'**
  String get storia_cosa_2_titolo;

  /// No description provided for @storia_cosa_2_testo.
  ///
  /// In en, this message translates to:
  /// **'so a follow-up does not start from a blank page.'**
  String get storia_cosa_2_testo;

  /// No description provided for @storia_perche_titolo.
  ///
  /// In en, this message translates to:
  /// **'Why, and who decides'**
  String get storia_perche_titolo;

  /// No description provided for @storia_perche_testo.
  ///
  /// In en, this message translates to:
  /// **'Memory exists only to make follow-ups meaningful. It is never shared, never used for advertising, and you can edit or delete any part of it — or all of it — at any time.'**
  String get storia_perche_testo;

  /// No description provided for @storia_letture_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your recent thread'**
  String get storia_letture_titolo;

  /// No description provided for @storia_letture_vuoto.
  ///
  /// In en, this message translates to:
  /// **'No readings yet. The cards are waiting for your first question.'**
  String get storia_letture_vuoto;

  /// No description provided for @storia_letture_inizia.
  ///
  /// In en, this message translates to:
  /// **'Ask your first question'**
  String get storia_letture_inizia;

  /// No description provided for @storia_continua.
  ///
  /// In en, this message translates to:
  /// **'Continue this reading'**
  String get storia_continua;

  /// No description provided for @storia_rileggi.
  ///
  /// In en, this message translates to:
  /// **'View the result again'**
  String get storia_rileggi;

  /// No description provided for @storia_riprendi_tema.
  ///
  /// In en, this message translates to:
  /// **'Ask this question again'**
  String get storia_riprendi_tema;

  /// No description provided for @storia_stampa_pdf.
  ///
  /// In en, this message translates to:
  /// **'Print to PDF'**
  String get storia_stampa_pdf;

  /// No description provided for @storia_stati_intervista.
  ///
  /// In en, this message translates to:
  /// **'in conversation'**
  String get storia_stati_intervista;

  /// No description provided for @storia_stati_ventaglio.
  ///
  /// In en, this message translates to:
  /// **'ready to shuffle'**
  String get storia_stati_ventaglio;

  /// No description provided for @storia_stati_scelta.
  ///
  /// In en, this message translates to:
  /// **'cards to choose'**
  String get storia_stati_scelta;

  /// No description provided for @storia_stati_rivelazione.
  ///
  /// In en, this message translates to:
  /// **'cards to reveal'**
  String get storia_stati_rivelazione;

  /// No description provided for @storia_stati_sintesi.
  ///
  /// In en, this message translates to:
  /// **'awaiting the interpretation'**
  String get storia_stati_sintesi;

  /// No description provided for @storia_stati_completata.
  ///
  /// In en, this message translates to:
  /// **'completed'**
  String get storia_stati_completata;

  /// No description provided for @storia_stati_annullata.
  ///
  /// In en, this message translates to:
  /// **'paused'**
  String get storia_stati_annullata;

  /// No description provided for @storia_badge_compatibilita.
  ///
  /// In en, this message translates to:
  /// **'Compatibility'**
  String get storia_badge_compatibilita;

  /// No description provided for @storia_badge_coppia.
  ///
  /// In en, this message translates to:
  /// **'Couple'**
  String get storia_badge_coppia;

  /// No description provided for @storia_esito.
  ///
  /// In en, this message translates to:
  /// **'Did it come true?'**
  String get storia_esito;

  /// No description provided for @storia_esiti_si.
  ///
  /// In en, this message translates to:
  /// **'Yes'**
  String get storia_esiti_si;

  /// No description provided for @storia_esiti_in_parte.
  ///
  /// In en, this message translates to:
  /// **'Partly'**
  String get storia_esiti_in_parte;

  /// No description provided for @storia_esiti_no.
  ///
  /// In en, this message translates to:
  /// **'No'**
  String get storia_esiti_no;

  /// No description provided for @storia_cancella.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get storia_cancella;

  /// No description provided for @storia_cancella_conferma_titolo.
  ///
  /// In en, this message translates to:
  /// **'Delete this reading?'**
  String get storia_cancella_conferma_titolo;

  /// No description provided for @storia_cancella_conferma_testo.
  ///
  /// In en, this message translates to:
  /// **'The reading, its interpretation and its link (if shared) are removed for good.'**
  String get storia_cancella_conferma_testo;

  /// No description provided for @storia_tutte.
  ///
  /// In en, this message translates to:
  /// **'All your readings'**
  String get storia_tutte;

  /// No description provided for @storia_dettaglio_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A reading in your story'**
  String get storia_dettaglio_eyebrow;

  /// No description provided for @storia_dettaglio_quando.
  ///
  /// In en, this message translates to:
  /// **'Asked on {data}'**
  String storia_dettaglio_quando(Object data);

  /// No description provided for @storia_il_quadro.
  ///
  /// In en, this message translates to:
  /// **'The picture'**
  String get storia_il_quadro;

  /// No description provided for @storia_l_interpretazione.
  ///
  /// In en, this message translates to:
  /// **'The interpretation'**
  String get storia_l_interpretazione;

  /// No description provided for @storia_esito_testo.
  ///
  /// In en, this message translates to:
  /// **'Coming back to a reading is part of the practice. Note how it went: your reader will take it into account.'**
  String get storia_esito_testo;

  /// No description provided for @storia_esito_salvato.
  ///
  /// In en, this message translates to:
  /// **'Noted.'**
  String get storia_esito_salvato;

  /// No description provided for @storia_condividi.
  ///
  /// In en, this message translates to:
  /// **'Share'**
  String get storia_condividi;

  /// No description provided for @storia_link_attivo.
  ///
  /// In en, this message translates to:
  /// **'Public link'**
  String get storia_link_attivo;

  /// No description provided for @storia_le_persone.
  ///
  /// In en, this message translates to:
  /// **'The people'**
  String get storia_le_persone;

  /// No description provided for @storia_tu.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get storia_tu;

  /// No description provided for @storia_persona_trans.
  ///
  /// In en, this message translates to:
  /// **'trans person'**
  String get storia_persona_trans;

  /// No description provided for @storia_compat_titolo.
  ///
  /// In en, this message translates to:
  /// **'Zodiac compatibility'**
  String get storia_compat_titolo;

  /// No description provided for @storia_aspetto.
  ///
  /// In en, this message translates to:
  /// **'Aspect'**
  String get storia_aspetto;

  /// No description provided for @storia_armonia.
  ///
  /// In en, this message translates to:
  /// **'Harmony'**
  String get storia_armonia;

  /// No description provided for @storia_elementi.
  ///
  /// In en, this message translates to:
  /// **'Elements'**
  String get storia_elementi;

  /// No description provided for @storia_carta_coppia.
  ///
  /// In en, this message translates to:
  /// **'The couple\'s card'**
  String get storia_carta_coppia;

  /// No description provided for @storia_cuspide.
  ///
  /// In en, this message translates to:
  /// **'on the cusp with {segno}'**
  String storia_cuspide(Object segno);

  /// No description provided for @storia_compat_avviso.
  ///
  /// In en, this message translates to:
  /// **'Sun signs only: without time and place of birth there is no ascendant or moon. A backdrop, not a verdict.'**
  String get storia_compat_avviso;

  /// No description provided for @storia_segni_ariete.
  ///
  /// In en, this message translates to:
  /// **'Aries'**
  String get storia_segni_ariete;

  /// No description provided for @storia_segni_toro.
  ///
  /// In en, this message translates to:
  /// **'Taurus'**
  String get storia_segni_toro;

  /// No description provided for @storia_segni_gemelli.
  ///
  /// In en, this message translates to:
  /// **'Gemini'**
  String get storia_segni_gemelli;

  /// No description provided for @storia_segni_cancro.
  ///
  /// In en, this message translates to:
  /// **'Cancer'**
  String get storia_segni_cancro;

  /// No description provided for @storia_segni_leone.
  ///
  /// In en, this message translates to:
  /// **'Leo'**
  String get storia_segni_leone;

  /// No description provided for @storia_segni_vergine.
  ///
  /// In en, this message translates to:
  /// **'Virgo'**
  String get storia_segni_vergine;

  /// No description provided for @storia_segni_bilancia.
  ///
  /// In en, this message translates to:
  /// **'Libra'**
  String get storia_segni_bilancia;

  /// No description provided for @storia_segni_scorpione.
  ///
  /// In en, this message translates to:
  /// **'Scorpio'**
  String get storia_segni_scorpione;

  /// No description provided for @storia_segni_sagittario.
  ///
  /// In en, this message translates to:
  /// **'Sagittarius'**
  String get storia_segni_sagittario;

  /// No description provided for @storia_segni_capricorno.
  ///
  /// In en, this message translates to:
  /// **'Capricorn'**
  String get storia_segni_capricorno;

  /// No description provided for @storia_segni_acquario.
  ///
  /// In en, this message translates to:
  /// **'Aquarius'**
  String get storia_segni_acquario;

  /// No description provided for @storia_segni_pesci.
  ///
  /// In en, this message translates to:
  /// **'Pisces'**
  String get storia_segni_pesci;

  /// No description provided for @storia_aspetti_congiunzione.
  ///
  /// In en, this message translates to:
  /// **'conjunction'**
  String get storia_aspetti_congiunzione;

  /// No description provided for @storia_aspetti_semisestile.
  ///
  /// In en, this message translates to:
  /// **'semi-sextile'**
  String get storia_aspetti_semisestile;

  /// No description provided for @storia_aspetti_sestile.
  ///
  /// In en, this message translates to:
  /// **'sextile'**
  String get storia_aspetti_sestile;

  /// No description provided for @storia_aspetti_quadrato.
  ///
  /// In en, this message translates to:
  /// **'square'**
  String get storia_aspetti_quadrato;

  /// No description provided for @storia_aspetti_trigono.
  ///
  /// In en, this message translates to:
  /// **'trine'**
  String get storia_aspetti_trigono;

  /// No description provided for @storia_aspetti_quinconce.
  ///
  /// In en, this message translates to:
  /// **'quincunx'**
  String get storia_aspetti_quinconce;

  /// No description provided for @storia_aspetti_opposizione.
  ///
  /// In en, this message translates to:
  /// **'opposition'**
  String get storia_aspetti_opposizione;

  /// No description provided for @storia_armonie_alta.
  ///
  /// In en, this message translates to:
  /// **'high'**
  String get storia_armonie_alta;

  /// No description provided for @storia_armonie_buona.
  ///
  /// In en, this message translates to:
  /// **'good'**
  String get storia_armonie_buona;

  /// No description provided for @storia_armonie_mista.
  ///
  /// In en, this message translates to:
  /// **'mixed'**
  String get storia_armonie_mista;

  /// No description provided for @storia_armonie_impegnativa.
  ///
  /// In en, this message translates to:
  /// **'demanding'**
  String get storia_armonie_impegnativa;

  /// No description provided for @storia_nomi_elementi_fuoco.
  ///
  /// In en, this message translates to:
  /// **'fire'**
  String get storia_nomi_elementi_fuoco;

  /// No description provided for @storia_nomi_elementi_terra.
  ///
  /// In en, this message translates to:
  /// **'earth'**
  String get storia_nomi_elementi_terra;

  /// No description provided for @storia_nomi_elementi_aria.
  ///
  /// In en, this message translates to:
  /// **'air'**
  String get storia_nomi_elementi_aria;

  /// No description provided for @storia_nomi_elementi_acqua.
  ///
  /// In en, this message translates to:
  /// **'water'**
  String get storia_nomi_elementi_acqua;

  /// No description provided for @storia_relazioni_elementi_rafforzata.
  ///
  /// In en, this message translates to:
  /// **'same element'**
  String get storia_relazioni_elementi_rafforzata;

  /// No description provided for @storia_relazioni_elementi_amica.
  ///
  /// In en, this message translates to:
  /// **'friendly elements'**
  String get storia_relazioni_elementi_amica;

  /// No description provided for @storia_relazioni_elementi_moderata.
  ///
  /// In en, this message translates to:
  /// **'moderate elements'**
  String get storia_relazioni_elementi_moderata;

  /// No description provided for @storia_relazioni_elementi_ostile.
  ///
  /// In en, this message translates to:
  /// **'opposing elements'**
  String get storia_relazioni_elementi_ostile;

  /// No description provided for @storia_relazioni_elementi_neutra.
  ///
  /// In en, this message translates to:
  /// **'neutral'**
  String get storia_relazioni_elementi_neutra;

  /// No description provided for @storia_generi_donna.
  ///
  /// In en, this message translates to:
  /// **'Woman'**
  String get storia_generi_donna;

  /// No description provided for @storia_generi_uomo.
  ///
  /// In en, this message translates to:
  /// **'Man'**
  String get storia_generi_uomo;

  /// No description provided for @storia_generi_non_binario.
  ///
  /// In en, this message translates to:
  /// **'Non-binary'**
  String get storia_generi_non_binario;

  /// No description provided for @storia_generi_altro.
  ///
  /// In en, this message translates to:
  /// **'Other'**
  String get storia_generi_altro;

  /// No description provided for @storia_generi_non_dice.
  ///
  /// In en, this message translates to:
  /// **'Prefer not to say'**
  String get storia_generi_non_dice;

  /// No description provided for @storia_indietro.
  ///
  /// In en, this message translates to:
  /// **'Back to your story'**
  String get storia_indietro;

  /// No description provided for @storia_memoria_titolo.
  ///
  /// In en, this message translates to:
  /// **'What your reader remembers'**
  String get storia_memoria_titolo;

  /// No description provided for @storia_memoria_testo.
  ///
  /// In en, this message translates to:
  /// **'Gathered from your readings and conversations. Edit what is no longer true; delete what you do not want kept.'**
  String get storia_memoria_testo;

  /// No description provided for @storia_memoria_vuoto.
  ///
  /// In en, this message translates to:
  /// **'Nothing remembered yet. After your first readings, what matters will appear here.'**
  String get storia_memoria_vuoto;

  /// No description provided for @storia_tipo_stabile.
  ///
  /// In en, this message translates to:
  /// **'Lasting'**
  String get storia_tipo_stabile;

  /// No description provided for @storia_tipo_variabile.
  ///
  /// In en, this message translates to:
  /// **'Changing'**
  String get storia_tipo_variabile;

  /// No description provided for @storia_fonte_lettura.
  ///
  /// In en, this message translates to:
  /// **'from a reading'**
  String get storia_fonte_lettura;

  /// No description provided for @storia_fonte_chat.
  ///
  /// In en, this message translates to:
  /// **'from a conversation'**
  String get storia_fonte_chat;

  /// No description provided for @storia_fonte_conversione.
  ///
  /// In en, this message translates to:
  /// **'from earlier memories'**
  String get storia_fonte_conversione;

  /// No description provided for @storia_categoria_stabile.
  ///
  /// In en, this message translates to:
  /// **'Lasting'**
  String get storia_categoria_stabile;

  /// No description provided for @storia_categoria_tema.
  ///
  /// In en, this message translates to:
  /// **'Question asked'**
  String get storia_categoria_tema;

  /// No description provided for @storia_categoria_volatile.
  ///
  /// In en, this message translates to:
  /// **'Current situation'**
  String get storia_categoria_volatile;

  /// No description provided for @storia_campi_amore.
  ///
  /// In en, this message translates to:
  /// **'Love'**
  String get storia_campi_amore;

  /// No description provided for @storia_campi_lavoro.
  ///
  /// In en, this message translates to:
  /// **'Work'**
  String get storia_campi_lavoro;

  /// No description provided for @storia_campi_salute.
  ///
  /// In en, this message translates to:
  /// **'Health'**
  String get storia_campi_salute;

  /// No description provided for @storia_campi_famiglia.
  ///
  /// In en, this message translates to:
  /// **'Family'**
  String get storia_campi_famiglia;

  /// No description provided for @storia_campi_denaro.
  ///
  /// In en, this message translates to:
  /// **'Money'**
  String get storia_campi_denaro;

  /// No description provided for @storia_campi_spirituale.
  ///
  /// In en, this message translates to:
  /// **'Spirituality'**
  String get storia_campi_spirituale;

  /// No description provided for @storia_campi_altro.
  ///
  /// In en, this message translates to:
  /// **'Other'**
  String get storia_campi_altro;

  /// No description provided for @storia_scade.
  ///
  /// In en, this message translates to:
  /// **'Fades on its own on {data}, unless a reading confirms it.'**
  String storia_scade(Object data);

  /// No description provided for @storia_memoria_oblio.
  ///
  /// In en, this message translates to:
  /// **'Questions you asked and current situations fade on their own after a few weeks unless they come back in a reading; what is lasting stays until you delete it.'**
  String get storia_memoria_oblio;

  /// No description provided for @storia_seleziona.
  ///
  /// In en, this message translates to:
  /// **'Select'**
  String get storia_seleziona;

  /// No description provided for @storia_modifica.
  ///
  /// In en, this message translates to:
  /// **'Edit'**
  String get storia_modifica;

  /// No description provided for @storia_elimina.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get storia_elimina;

  /// No description provided for @storia_campo.
  ///
  /// In en, this message translates to:
  /// **'Theme'**
  String get storia_campo;

  /// No description provided for @storia_salva.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get storia_salva;

  /// No description provided for @storia_annulla.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get storia_annulla;

  /// No description provided for @storia_elimina_selezionate.
  ///
  /// In en, this message translates to:
  /// **'Delete selected memories'**
  String get storia_elimina_selezionate;

  /// No description provided for @storia_elimina_tutte.
  ///
  /// In en, this message translates to:
  /// **'Delete all memories'**
  String get storia_elimina_tutte;

  /// No description provided for @storia_conferma_titolo.
  ///
  /// In en, this message translates to:
  /// **'Delete memories?'**
  String get storia_conferma_titolo;

  /// No description provided for @storia_conferma_una.
  ///
  /// In en, this message translates to:
  /// **'You are about to delete 1 selected memory.'**
  String get storia_conferma_una;

  /// No description provided for @storia_conferma_n.
  ///
  /// In en, this message translates to:
  /// **'You are about to delete {n} selected memories.'**
  String storia_conferma_n(Object n);

  /// No description provided for @storia_conferma_tutte.
  ///
  /// In en, this message translates to:
  /// **'You are about to delete everything your reader remembers.'**
  String get storia_conferma_tutte;

  /// No description provided for @storia_conferma_casella.
  ///
  /// In en, this message translates to:
  /// **'I understand this cannot be undone'**
  String get storia_conferma_casella;

  /// No description provided for @storia_conferma_continua.
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get storia_conferma_continua;

  /// No description provided for @storia_conferma_elimina.
  ///
  /// In en, this message translates to:
  /// **'Delete for good'**
  String get storia_conferma_elimina;

  /// No description provided for @condivisa_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A reading someone shared with you'**
  String get condivisa_eyebrow;

  /// No description provided for @condivisa_titolo_predefinito.
  ///
  /// In en, this message translates to:
  /// **'A question, the cards, and what they opened.'**
  String get condivisa_titolo_predefinito;

  /// No description provided for @condivisa_nota.
  ///
  /// In en, this message translates to:
  /// **'Shared from a personal Tarot reading. The name of whoever shared it is never shown.'**
  String get condivisa_nota;

  /// No description provided for @condivisa_domanda.
  ///
  /// In en, this message translates to:
  /// **'The question'**
  String get condivisa_domanda;

  /// No description provided for @condivisa_l_interpretazione.
  ///
  /// In en, this message translates to:
  /// **'The interpretation'**
  String get condivisa_l_interpretazione;

  /// No description provided for @condivisa_invito_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your own question is waiting.'**
  String get condivisa_invito_titolo;

  /// No description provided for @condivisa_invito_testo.
  ///
  /// In en, this message translates to:
  /// **'Take part in the ritual yourself: your first reading is free and needs no account. If you create one, whoever sent you this link receives {n} free readings.'**
  String condivisa_invito_testo(Object n);

  /// No description provided for @condivisa_inizia.
  ///
  /// In en, this message translates to:
  /// **'Start your free reading'**
  String get condivisa_inizia;

  /// No description provided for @condivisa_iscriviti.
  ///
  /// In en, this message translates to:
  /// **'Create a free account'**
  String get condivisa_iscriviti;

  /// No description provided for @condivisa_giorno.
  ///
  /// In en, this message translates to:
  /// **'Or draw today\'s card'**
  String get condivisa_giorno;

  /// No description provided for @condivisa_non_trovata_titolo.
  ///
  /// In en, this message translates to:
  /// **'This reading is no longer shared.'**
  String get condivisa_non_trovata_titolo;

  /// No description provided for @condivisa_non_trovata_testo.
  ///
  /// In en, this message translates to:
  /// **'Whoever shared it may have turned the link off. You can still begin your own reading.'**
  String get condivisa_non_trovata_testo;

  /// No description provided for @carte_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Thoth Tarot card library'**
  String get carte_meta_titolo;

  /// No description provided for @carte_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'The 78 cards of the Thoth Tarot: images, correspondences and meanings, each a way into a question.'**
  String get carte_meta_descrizione;

  /// No description provided for @carte_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Thoth Tarot card library'**
  String get carte_eyebrow;

  /// No description provided for @carte_titolo.
  ///
  /// In en, this message translates to:
  /// **'See the card before you ask it to speak.'**
  String get carte_titolo;

  /// No description provided for @carte_intro.
  ///
  /// In en, this message translates to:
  /// **'Each card joins an image, a set of correspondences and meanings on several levels. Its role in a reading still depends on the position, the cards around it and your question.'**
  String get carte_intro;

  /// No description provided for @carte_filtri_tutte.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get carte_filtri_tutte;

  /// No description provided for @carte_filtri_maggiori.
  ///
  /// In en, this message translates to:
  /// **'Major Arcana'**
  String get carte_filtri_maggiori;

  /// No description provided for @carte_filtri_bastoni.
  ///
  /// In en, this message translates to:
  /// **'Wands'**
  String get carte_filtri_bastoni;

  /// No description provided for @carte_filtri_coppe.
  ///
  /// In en, this message translates to:
  /// **'Cups'**
  String get carte_filtri_coppe;

  /// No description provided for @carte_filtri_spade.
  ///
  /// In en, this message translates to:
  /// **'Swords'**
  String get carte_filtri_spade;

  /// No description provided for @carte_filtri_dischi.
  ///
  /// In en, this message translates to:
  /// **'Disks'**
  String get carte_filtri_dischi;

  /// No description provided for @carte_filtri_aria.
  ///
  /// In en, this message translates to:
  /// **'Filter the cards'**
  String get carte_filtri_aria;

  /// No description provided for @carte_n_carte.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 card} other{{n} cards}}'**
  String carte_n_carte(int n);

  /// No description provided for @carte_carta_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Thoth Tarot · {arcano}'**
  String carte_carta_eyebrow(Object arcano);

  /// No description provided for @carte_carta_riflessione.
  ///
  /// In en, this message translates to:
  /// **'A reflective starting point'**
  String get carte_carta_riflessione;

  /// No description provided for @carte_carta_domanda.
  ///
  /// In en, this message translates to:
  /// **'What is {carta} asking you to look at?'**
  String carte_carta_domanda(Object carta);

  /// No description provided for @carte_carta_nota.
  ///
  /// In en, this message translates to:
  /// **'Meaning changes with the position, the surrounding cards and your question. Take what follows as a language, not a verdict.'**
  String get carte_carta_nota;

  /// No description provided for @carte_dritta.
  ///
  /// In en, this message translates to:
  /// **'Upright'**
  String get carte_dritta;

  /// No description provided for @carte_rovesciata.
  ///
  /// In en, this message translates to:
  /// **'Reversed'**
  String get carte_rovesciata;

  /// No description provided for @carte_rovesciata_nota.
  ///
  /// In en, this message translates to:
  /// **'In the Thoth tradition a reversed card is read through its dignity with the neighbouring cards; this is its shadow side.'**
  String get carte_rovesciata_nota;

  /// No description provided for @carte_livelli_essoterico.
  ///
  /// In en, this message translates to:
  /// **'At first sight'**
  String get carte_livelli_essoterico;

  /// No description provided for @carte_livelli_psicologico.
  ///
  /// In en, this message translates to:
  /// **'Within you'**
  String get carte_livelli_psicologico;

  /// No description provided for @carte_livelli_iniziatico.
  ///
  /// In en, this message translates to:
  /// **'On the path'**
  String get carte_livelli_iniziatico;

  /// No description provided for @carte_livelli_ombra.
  ///
  /// In en, this message translates to:
  /// **'The shadow'**
  String get carte_livelli_ombra;

  /// No description provided for @carte_ambiti_titolo.
  ///
  /// In en, this message translates to:
  /// **'In love, work and spirit'**
  String get carte_ambiti_titolo;

  /// No description provided for @carte_ambiti_amore.
  ///
  /// In en, this message translates to:
  /// **'Love'**
  String get carte_ambiti_amore;

  /// No description provided for @carte_ambiti_lavoro.
  ///
  /// In en, this message translates to:
  /// **'Work'**
  String get carte_ambiti_lavoro;

  /// No description provided for @carte_ambiti_spirito.
  ///
  /// In en, this message translates to:
  /// **'Spirit'**
  String get carte_ambiti_spirito;

  /// No description provided for @carte_corrispondenze.
  ///
  /// In en, this message translates to:
  /// **'Correspondences'**
  String get carte_corrispondenze;

  /// No description provided for @carte_sentiero.
  ///
  /// In en, this message translates to:
  /// **'path {n}'**
  String carte_sentiero(Object n);

  /// No description provided for @carte_crowley.
  ///
  /// In en, this message translates to:
  /// **'Crowley\'s note'**
  String get carte_crowley;

  /// No description provided for @carte_parole.
  ///
  /// In en, this message translates to:
  /// **'Key words'**
  String get carte_parole;

  /// No description provided for @carte_cta_leggi.
  ///
  /// In en, this message translates to:
  /// **'Read this card in a ritual'**
  String get carte_cta_leggi;

  /// No description provided for @carte_cta_fisica.
  ///
  /// In en, this message translates to:
  /// **'Draw it from your own deck'**
  String get carte_cta_fisica;

  /// No description provided for @carte_articoli_su.
  ///
  /// In en, this message translates to:
  /// **'From the journal'**
  String get carte_articoli_su;

  /// No description provided for @carte_precedente.
  ///
  /// In en, this message translates to:
  /// **'Previous card'**
  String get carte_precedente;

  /// No description provided for @carte_successiva.
  ///
  /// In en, this message translates to:
  /// **'Next card'**
  String get carte_successiva;

  /// No description provided for @carte_torna.
  ///
  /// In en, this message translates to:
  /// **'Back to the library'**
  String get carte_torna;

  /// No description provided for @carte_non_trovata.
  ///
  /// In en, this message translates to:
  /// **'This card is not in the library.'**
  String get carte_non_trovata;

  /// No description provided for @giorno_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Card of the day'**
  String get giorno_meta_titolo;

  /// No description provided for @giorno_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'A Thoth Tarot card for today, free and without an account: a small encounter and a prompt for reflection.'**
  String get giorno_meta_descrizione;

  /// No description provided for @giorno_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Card of the day'**
  String get giorno_eyebrow;

  /// No description provided for @giorno_titolo.
  ///
  /// In en, this message translates to:
  /// **'A small encounter, available without an account.'**
  String get giorno_titolo;

  /// No description provided for @giorno_intro.
  ///
  /// In en, this message translates to:
  /// **'One card for today, the same for everyone until midnight (UTC). Take the image as a reflective prompt, not a promise.'**
  String get giorno_intro;

  /// No description provided for @giorno_intro_dentro.
  ///
  /// In en, this message translates to:
  /// **'Your own card for today, free. Turn it when you are ready: it counts your days in a row.'**
  String get giorno_intro_dentro;

  /// No description provided for @giorno_di_tutti.
  ///
  /// In en, this message translates to:
  /// **'Today\'s card'**
  String get giorno_di_tutti;

  /// No description provided for @giorno_tua.
  ///
  /// In en, this message translates to:
  /// **'Your card for today'**
  String get giorno_tua;

  /// No description provided for @giorno_gira.
  ///
  /// In en, this message translates to:
  /// **'Turn the card'**
  String get giorno_gira;

  /// No description provided for @giorno_serie.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 day in a row} other{{n} days in a row}}'**
  String giorno_serie(int n);

  /// No description provided for @giorno_domanda.
  ///
  /// In en, this message translates to:
  /// **'If something specific is asking for attention, bring it into a reading.'**
  String get giorno_domanda;

  /// No description provided for @giorno_cta.
  ///
  /// In en, this message translates to:
  /// **'Ask a fuller question'**
  String get giorno_cta;

  /// No description provided for @giorno_significato.
  ///
  /// In en, this message translates to:
  /// **'The full meaning of {carta}'**
  String giorno_significato(Object carta);

  /// No description provided for @giorno_personale.
  ///
  /// In en, this message translates to:
  /// **'With a free account, the card is drawn for you each day, and your streak keeps the practice alive.'**
  String get giorno_personale;

  /// No description provided for @giorno_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get giorno_entra;

  /// No description provided for @stese_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Tarot spreads'**
  String get stese_meta_titolo;

  /// No description provided for @stese_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'The layouts a reading can take: the position gives each card its meaning.'**
  String get stese_meta_descrizione;

  /// No description provided for @stese_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Spreads'**
  String get stese_eyebrow;

  /// No description provided for @stese_titolo.
  ///
  /// In en, this message translates to:
  /// **'Choose a shape that helps the question unfold.'**
  String get stese_titolo;

  /// No description provided for @stese_intro.
  ///
  /// In en, this message translates to:
  /// **'The position gives each card its meaning. Here are the classic layouts and those made to read a bond between two people.'**
  String get stese_intro;

  /// No description provided for @stese_standard.
  ///
  /// In en, this message translates to:
  /// **'Classic spreads'**
  String get stese_standard;

  /// No description provided for @stese_standard_testo.
  ///
  /// In en, this message translates to:
  /// **'From the simplest to the Celtic Cross and the Astrological Wheel.'**
  String get stese_standard_testo;

  /// No description provided for @stese_compat.
  ///
  /// In en, this message translates to:
  /// **'Compatibility'**
  String get stese_compat;

  /// No description provided for @stese_compat_testo.
  ///
  /// In en, this message translates to:
  /// **'What joins you and another person, and what sets you apart.'**
  String get stese_compat_testo;

  /// No description provided for @stese_coppia.
  ///
  /// In en, this message translates to:
  /// **'A couple'**
  String get stese_coppia;

  /// No description provided for @stese_coppia_testo.
  ///
  /// In en, this message translates to:
  /// **'The state of the bond you are living: strengths, friction, direction.'**
  String get stese_coppia_testo;

  /// No description provided for @stese_fisica.
  ///
  /// In en, this message translates to:
  /// **'Physical draw'**
  String get stese_fisica;

  /// No description provided for @stese_fisica_testo.
  ///
  /// In en, this message translates to:
  /// **'Place the cards you already pulled from your own deck.'**
  String get stese_fisica_testo;

  /// No description provided for @stese_maggiori.
  ///
  /// In en, this message translates to:
  /// **'22 Major Arcana'**
  String get stese_maggiori;

  /// No description provided for @stese_completo.
  ///
  /// In en, this message translates to:
  /// **'Full deck'**
  String get stese_completo;

  /// No description provided for @stese_stesa_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A spread'**
  String get stese_stesa_eyebrow;

  /// No description provided for @stese_stesa_posizioni.
  ///
  /// In en, this message translates to:
  /// **'The positions'**
  String get stese_stesa_posizioni;

  /// No description provided for @stese_stesa_posizione.
  ///
  /// In en, this message translates to:
  /// **'Position {n}'**
  String stese_stesa_posizione(Object n);

  /// No description provided for @stese_stesa_come.
  ///
  /// In en, this message translates to:
  /// **'How to read it'**
  String get stese_stesa_come;

  /// No description provided for @stese_stesa_coppie.
  ///
  /// In en, this message translates to:
  /// **'Positions to read together'**
  String get stese_stesa_coppie;

  /// No description provided for @stese_stesa_origine.
  ///
  /// In en, this message translates to:
  /// **'Origin'**
  String get stese_stesa_origine;

  /// No description provided for @stese_stesa_cta.
  ///
  /// In en, this message translates to:
  /// **'Begin a reading with this spread'**
  String get stese_stesa_cta;

  /// No description provided for @stese_stesa_tutte.
  ///
  /// In en, this message translates to:
  /// **'All spreads'**
  String get stese_stesa_tutte;

  /// No description provided for @stese_stesa_altre.
  ///
  /// In en, this message translates to:
  /// **'More spreads of the same kind'**
  String get stese_stesa_altre;

  /// No description provided for @stese_stesa_diagramma.
  ///
  /// In en, this message translates to:
  /// **'The layout of the spread: numbered positions on the table.'**
  String get stese_stesa_diagramma;

  /// No description provided for @stese_non_trovata_stesa.
  ///
  /// In en, this message translates to:
  /// **'This spread does not exist.'**
  String get stese_non_trovata_stesa;

  /// No description provided for @mazzi_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Tarot decks'**
  String get mazzi_meta_titolo;

  /// No description provided for @mazzi_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Each deck is a visual language with its own atmosphere. The Thoth Tarot is available now; more worlds are in development.'**
  String get mazzi_meta_descrizione;

  /// No description provided for @mazzi_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'A multi-deck home'**
  String get mazzi_eyebrow;

  /// No description provided for @mazzi_titolo.
  ///
  /// In en, this message translates to:
  /// **'Each deck is a language with its own atmosphere.'**
  String get mazzi_titolo;

  /// No description provided for @mazzi_intro.
  ///
  /// In en, this message translates to:
  /// **'Deck pages are not shop shelves. They are entrances into an image system, a card library, readings and a physical ritual.'**
  String get mazzi_intro;

  /// No description provided for @mazzi_disponibile.
  ///
  /// In en, this message translates to:
  /// **'Available now'**
  String get mazzi_disponibile;

  /// No description provided for @mazzi_pianificato.
  ///
  /// In en, this message translates to:
  /// **'Planned'**
  String get mazzi_pianificato;

  /// No description provided for @mazzi_incluso.
  ///
  /// In en, this message translates to:
  /// **'Included with every reading'**
  String get mazzi_incluso;

  /// No description provided for @mazzi_entra.
  ///
  /// In en, this message translates to:
  /// **'Enter the {mazzo} deck'**
  String mazzi_entra(Object mazzo);

  /// No description provided for @mazzi_in_sviluppo.
  ///
  /// In en, this message translates to:
  /// **'In development'**
  String get mazzi_in_sviluppo;

  /// No description provided for @mazzi_futuri_0_simbolo.
  ///
  /// In en, this message translates to:
  /// **'♡'**
  String get mazzi_futuri_0_simbolo;

  /// No description provided for @mazzi_futuri_0_nome.
  ///
  /// In en, this message translates to:
  /// **'The Lovers'**
  String get mazzi_futuri_0_nome;

  /// No description provided for @mazzi_futuri_1_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✺'**
  String get mazzi_futuri_1_simbolo;

  /// No description provided for @mazzi_futuri_1_nome.
  ///
  /// In en, this message translates to:
  /// **'Italian Celebration'**
  String get mazzi_futuri_1_nome;

  /// No description provided for @mazzi_futuri_2_simbolo.
  ///
  /// In en, this message translates to:
  /// **'☾'**
  String get mazzi_futuri_2_simbolo;

  /// No description provided for @mazzi_futuri_2_nome.
  ///
  /// In en, this message translates to:
  /// **'Halloween Tarots'**
  String get mazzi_futuri_2_nome;

  /// No description provided for @mazzi_futuri_3_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✡'**
  String get mazzi_futuri_3_simbolo;

  /// No description provided for @mazzi_futuri_3_nome.
  ///
  /// In en, this message translates to:
  /// **'Jewish Secrets'**
  String get mazzi_futuri_3_nome;

  /// No description provided for @mazzi_futuro_testo.
  ///
  /// In en, this message translates to:
  /// **'A future deck, not yet selectable for readings.'**
  String get mazzi_futuro_testo;

  /// No description provided for @mazzi_voto_titolo.
  ///
  /// In en, this message translates to:
  /// **'Help choose the next deck'**
  String get mazzi_voto_titolo;

  /// No description provided for @mazzi_voto_testo.
  ///
  /// In en, this message translates to:
  /// **'Look at the candidates and vote for the world you would like to read with. Your vote counts.'**
  String get mazzi_voto_testo;

  /// No description provided for @mazzi_voto_cta.
  ///
  /// In en, this message translates to:
  /// **'Vote the next deck'**
  String get mazzi_voto_cta;

  /// No description provided for @mazzi_mazzo_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'The {mazzo}'**
  String mazzi_mazzo_eyebrow(Object mazzo);

  /// No description provided for @mazzi_thoth_titolo.
  ///
  /// In en, this message translates to:
  /// **'A deck of vivid symbols, held inside a personal question.'**
  String get mazzi_thoth_titolo;

  /// No description provided for @mazzi_thoth_intro.
  ///
  /// In en, this message translates to:
  /// **'Explore the image language, draw in the guided ritual, or bring a physical draw to the reader.'**
  String get mazzi_thoth_intro;

  /// No description provided for @mazzi_altro_titolo.
  ///
  /// In en, this message translates to:
  /// **'A visual world for your readings.'**
  String get mazzi_altro_titolo;

  /// No description provided for @mazzi_slogan.
  ///
  /// In en, this message translates to:
  /// **'Your deck. Your ritual. Your reader.'**
  String get mazzi_slogan;

  /// No description provided for @mazzi_slogan_testo.
  ///
  /// In en, this message translates to:
  /// **'The card library, the readings, the journal and the physical edition of a deck lead into one shared personal story.'**
  String get mazzi_slogan_testo;

  /// No description provided for @mazzi_cta_leggi.
  ///
  /// In en, this message translates to:
  /// **'Start a reading with this deck'**
  String get mazzi_cta_leggi;

  /// No description provided for @mazzi_cta_carte.
  ///
  /// In en, this message translates to:
  /// **'Open the card library'**
  String get mazzi_cta_carte;

  /// No description provided for @mazzi_cta_fisica.
  ///
  /// In en, this message translates to:
  /// **'Read physical cards'**
  String get mazzi_cta_fisica;

  /// No description provided for @mazzi_cta_negozio.
  ///
  /// In en, this message translates to:
  /// **'Physical deck & PDF'**
  String get mazzi_cta_negozio;

  /// No description provided for @mazzi_campione.
  ///
  /// In en, this message translates to:
  /// **'Some cards of the deck'**
  String get mazzi_campione;

  /// No description provided for @mazzi_non_trovato.
  ///
  /// In en, this message translates to:
  /// **'This deck does not exist.'**
  String get mazzi_non_trovato;

  /// No description provided for @mazzi_voto_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Vote the next deck'**
  String get mazzi_voto_meta_titolo;

  /// No description provided for @mazzi_voto_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Choose which Tarot deck we create next.'**
  String get mazzi_voto_meta_descrizione;

  /// No description provided for @mazzi_voto_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Multi-deck, by choice'**
  String get mazzi_voto_eyebrow;

  /// No description provided for @mazzi_voto_titolo_pagina.
  ///
  /// In en, this message translates to:
  /// **'Which world should we open next?'**
  String get mazzi_voto_titolo_pagina;

  /// No description provided for @mazzi_voto_intro.
  ///
  /// In en, this message translates to:
  /// **'Each round proposes a few candidate decks. You have one vote per round; you can change it while the round is open. Percentages appear after you vote, so they never steer your choice.'**
  String get mazzi_voto_intro;

  /// No description provided for @mazzi_voto_fuori.
  ///
  /// In en, this message translates to:
  /// **'Voting needs a free account: one person, one vote.'**
  String get mazzi_voto_fuori;

  /// No description provided for @mazzi_voto_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in to vote'**
  String get mazzi_voto_entra;

  /// No description provided for @mazzi_voto_bottone.
  ///
  /// In en, this message translates to:
  /// **'Vote for this deck'**
  String get mazzi_voto_bottone;

  /// No description provided for @mazzi_voto_votato.
  ///
  /// In en, this message translates to:
  /// **'Your vote'**
  String get mazzi_voto_votato;

  /// No description provided for @mazzi_voto_cambia.
  ///
  /// In en, this message translates to:
  /// **'You can change your vote while the round stays open.'**
  String get mazzi_voto_cambia;

  /// No description provided for @mazzi_voto_grazie.
  ///
  /// In en, this message translates to:
  /// **'Thank you. Here is how the round is going:'**
  String get mazzi_voto_grazie;

  /// No description provided for @mazzi_voto_nessuna.
  ///
  /// In en, this message translates to:
  /// **'There is no open round right now. Come back soon.'**
  String get mazzi_voto_nessuna;

  /// No description provided for @mazzi_voto_vincitori.
  ///
  /// In en, this message translates to:
  /// **'The previous round'**
  String get mazzi_voto_vincitori;

  /// No description provided for @mazzi_voto_ultimo.
  ///
  /// In en, this message translates to:
  /// **'The result of the last round'**
  String get mazzi_voto_ultimo;

  /// No description provided for @mazzi_voto_percentuale.
  ///
  /// In en, this message translates to:
  /// **'{n}%'**
  String mazzi_voto_percentuale(Object n);

  /// No description provided for @mazzi_suggerisci_titolo.
  ///
  /// In en, this message translates to:
  /// **'Suggest a theme'**
  String get mazzi_suggerisci_titolo;

  /// No description provided for @mazzi_suggerisci_testo.
  ///
  /// In en, this message translates to:
  /// **'An idea for the next deck? Tell us: the most inspiring suggestions become candidates in a future round.'**
  String get mazzi_suggerisci_testo;

  /// No description provided for @mazzi_suggerisci_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'For example: a deck inspired by the Japanese seasons…'**
  String get mazzi_suggerisci_segnaposto;

  /// No description provided for @mazzi_suggerisci_invia.
  ///
  /// In en, this message translates to:
  /// **'Send the suggestion'**
  String get mazzi_suggerisci_invia;

  /// No description provided for @mazzi_suggerisci_grazie.
  ///
  /// In en, this message translates to:
  /// **'Thank you: your suggestion has been received.'**
  String get mazzi_suggerisci_grazie;

  /// No description provided for @mazzi_stampa_cta.
  ///
  /// In en, this message translates to:
  /// **'Print your own Tarot'**
  String get mazzi_stampa_cta;

  /// No description provided for @mazzi_campioni_titolo.
  ///
  /// In en, this message translates to:
  /// **'Example cards of {mazzo}'**
  String mazzi_campioni_titolo(Object mazzo);

  /// No description provided for @mazzi_campione_ingrandisci.
  ///
  /// In en, this message translates to:
  /// **'Enlarge example card {n} of {mazzo}'**
  String mazzi_campione_ingrandisci(Object n, Object mazzo);

  /// No description provided for @mazzi_campione_zoom.
  ///
  /// In en, this message translates to:
  /// **'{mazzo} · card {n} of {tot}'**
  String mazzi_campione_zoom(Object mazzo, Object n, Object tot);

  /// No description provided for @mazzi_campione_chiudi.
  ///
  /// In en, this message translates to:
  /// **'Close the enlarged card'**
  String get mazzi_campione_chiudi;

  /// No description provided for @negozio_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Deck and printable ritual'**
  String get negozio_meta_titolo;

  /// No description provided for @negozio_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Decks, printable PDF and the physical box set: a way to bring the ritual into your hands.'**
  String get negozio_meta_descrizione;

  /// No description provided for @negozio_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Deck and printable ritual'**
  String get negozio_eyebrow;

  /// No description provided for @negozio_titolo.
  ///
  /// In en, this message translates to:
  /// **'A physical extension, not the reason you came.'**
  String get negozio_titolo;

  /// No description provided for @negozio_intro.
  ///
  /// In en, this message translates to:
  /// **'A deck or a PDF makes the ritual tangible and brings you back to a reading — with the cards in your hands, then here for the interpretation. Readings stay at the centre.'**
  String get negozio_intro;

  /// No description provided for @negozio_ponte_titolo.
  ///
  /// In en, this message translates to:
  /// **'From the table to the reader'**
  String get negozio_ponte_titolo;

  /// No description provided for @negozio_ponte_testo.
  ///
  /// In en, this message translates to:
  /// **'Draw from a physical deck, then continue online: place the cards you pulled and let the reader interpret them.'**
  String get negozio_ponte_testo;

  /// No description provided for @negozio_ponte_cta.
  ///
  /// In en, this message translates to:
  /// **'Continue with your cards'**
  String get negozio_ponte_cta;

  /// No description provided for @negozio_vuoto.
  ///
  /// In en, this message translates to:
  /// **'The decks will appear here soon.'**
  String get negozio_vuoto;

  /// No description provided for @negozio_incluso.
  ///
  /// In en, this message translates to:
  /// **'Included with every account'**
  String get negozio_incluso;

  /// No description provided for @negozio_posseduto.
  ///
  /// In en, this message translates to:
  /// **'Already yours'**
  String get negozio_posseduto;

  /// No description provided for @negozio_offerta_fino.
  ///
  /// In en, this message translates to:
  /// **'Offer valid until {data}'**
  String negozio_offerta_fino(Object data);

  /// No description provided for @negozio_digitale.
  ///
  /// In en, this message translates to:
  /// **'Digital deck'**
  String get negozio_digitale;

  /// No description provided for @negozio_pdf.
  ///
  /// In en, this message translates to:
  /// **'Printable PDF'**
  String get negozio_pdf;

  /// No description provided for @negozio_fisico.
  ///
  /// In en, this message translates to:
  /// **'Physical box set'**
  String get negozio_fisico;

  /// No description provided for @negozio_pdf_gratis.
  ///
  /// In en, this message translates to:
  /// **'Download the free PDF'**
  String get negozio_pdf_gratis;

  /// No description provided for @negozio_aggiungi.
  ///
  /// In en, this message translates to:
  /// **'Add to cart'**
  String get negozio_aggiungi;

  /// No description provided for @negozio_nel_carrello.
  ///
  /// In en, this message translates to:
  /// **'In your cart: {n}'**
  String negozio_nel_carrello(Object n);

  /// No description provided for @negozio_carrello.
  ///
  /// In en, this message translates to:
  /// **'Your cart'**
  String get negozio_carrello;

  /// No description provided for @negozio_carrello_vuoto.
  ///
  /// In en, this message translates to:
  /// **'Your cart is empty.'**
  String get negozio_carrello_vuoto;

  /// No description provided for @negozio_rimuovi.
  ///
  /// In en, this message translates to:
  /// **'Remove'**
  String get negozio_rimuovi;

  /// No description provided for @negozio_totale.
  ///
  /// In en, this message translates to:
  /// **'Total'**
  String get negozio_totale;

  /// No description provided for @negozio_nota_sconto.
  ///
  /// In en, this message translates to:
  /// **'Different decks in the same order receive a larger discount: you will see it at checkout.'**
  String get negozio_nota_sconto;

  /// No description provided for @negozio_indirizzo.
  ///
  /// In en, this message translates to:
  /// **'Shipping address'**
  String get negozio_indirizzo;

  /// No description provided for @negozio_indirizzo_manca.
  ///
  /// In en, this message translates to:
  /// **'The physical box set needs a shipping address.'**
  String get negozio_indirizzo_manca;

  /// No description provided for @negozio_indirizzo_profilo.
  ///
  /// In en, this message translates to:
  /// **'Add one in your account'**
  String get negozio_indirizzo_profilo;

  /// No description provided for @negozio_completa.
  ///
  /// In en, this message translates to:
  /// **'Complete the order'**
  String get negozio_completa;

  /// No description provided for @negozio_entra_per.
  ///
  /// In en, this message translates to:
  /// **'Sign in to complete the order'**
  String get negozio_entra_per;

  /// No description provided for @negozio_in_corso.
  ///
  /// In en, this message translates to:
  /// **'One moment…'**
  String get negozio_in_corso;

  /// No description provided for @negozio_pagato.
  ///
  /// In en, this message translates to:
  /// **'Order paid: the decks you bought are now available in your readings.'**
  String get negozio_pagato;

  /// No description provided for @negozio_annullato.
  ///
  /// In en, this message translates to:
  /// **'Order cancelled: nothing was charged.'**
  String get negozio_annullato;

  /// No description provided for @negozio_non_verificato.
  ///
  /// In en, this message translates to:
  /// **'The payment could not be verified. Check your orders in your account.'**
  String get negozio_non_verificato;

  /// No description provided for @negozio_scarica_pdf.
  ///
  /// In en, this message translates to:
  /// **'Download your PDF'**
  String get negozio_scarica_pdf;

  /// No description provided for @negozio_pdf_in_corso.
  ///
  /// In en, this message translates to:
  /// **'Preparing the PDF…'**
  String get negozio_pdf_in_corso;

  /// No description provided for @negozio_pdf_errore.
  ///
  /// In en, this message translates to:
  /// **'The PDF could not be downloaded. Try again.'**
  String get negozio_pdf_errore;

  /// No description provided for @negozio_aggiungi_fisico.
  ///
  /// In en, this message translates to:
  /// **'Add physical deck'**
  String get negozio_aggiungi_fisico;

  /// No description provided for @negozio_aggiungi_pdf.
  ///
  /// In en, this message translates to:
  /// **'Add printable deck (PDF)'**
  String get negozio_aggiungi_pdf;

  /// No description provided for @negozio_aggiungi_digitale.
  ///
  /// In en, this message translates to:
  /// **'Add digital deck'**
  String get negozio_aggiungi_digitale;

  /// No description provided for @negozio_aggiunto.
  ///
  /// In en, this message translates to:
  /// **'Added to your cart: {cosa}'**
  String negozio_aggiunto(Object cosa);

  /// No description provided for @negozio_prezzo_in_arrivo.
  ///
  /// In en, this message translates to:
  /// **'Price coming soon'**
  String get negozio_prezzo_in_arrivo;

  /// No description provided for @negozio_vedi_carte.
  ///
  /// In en, this message translates to:
  /// **'See the cards'**
  String get negozio_vedi_carte;

  /// No description provided for @negozio_vedi_carte_di.
  ///
  /// In en, this message translates to:
  /// **'See the cards of {mazzo}'**
  String negozio_vedi_carte_di(Object mazzo);

  /// No description provided for @negozio_vai_carrello.
  ///
  /// In en, this message translates to:
  /// **'Go to cart'**
  String get negozio_vai_carrello;

  /// No description provided for @negozio_vai_negozio.
  ///
  /// In en, this message translates to:
  /// **'Browse the decks'**
  String get negozio_vai_negozio;

  /// No description provided for @negozio_continua.
  ///
  /// In en, this message translates to:
  /// **'Continue shopping'**
  String get negozio_continua;

  /// No description provided for @negozio_offerta.
  ///
  /// In en, this message translates to:
  /// **'Offer'**
  String get negozio_offerta;

  /// No description provided for @negozio_pezzi.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 item in your cart} other{{n} items in your cart}}'**
  String negozio_pezzi(int n);

  /// No description provided for @negozio_nota_account.
  ///
  /// In en, this message translates to:
  /// **'You can fill your cart without an account: you will sign in only to complete the order.'**
  String get negozio_nota_account;

  /// No description provided for @negozio_galleria_titolo.
  ///
  /// In en, this message translates to:
  /// **'The cards of {mazzo}'**
  String negozio_galleria_titolo(Object mazzo);

  /// No description provided for @negozio_galleria_prec.
  ///
  /// In en, this message translates to:
  /// **'Previous'**
  String get negozio_galleria_prec;

  /// No description provided for @negozio_galleria_succ.
  ///
  /// In en, this message translates to:
  /// **'Next'**
  String get negozio_galleria_succ;

  /// No description provided for @negozio_galleria_torna.
  ///
  /// In en, this message translates to:
  /// **'All the cards'**
  String get negozio_galleria_torna;

  /// No description provided for @negozio_galleria_nota.
  ///
  /// In en, this message translates to:
  /// **'tap a card to enlarge it'**
  String get negozio_galleria_nota;

  /// No description provided for @negozio_galleria_gruppi.
  ///
  /// In en, this message translates to:
  /// **'Jump to a group of cards'**
  String get negozio_galleria_gruppi;

  /// No description provided for @negozio_galleria_ingrandisci.
  ///
  /// In en, this message translates to:
  /// **'Enlarge {carta}'**
  String negozio_galleria_ingrandisci(Object carta);

  /// No description provided for @negozio_carrello_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your cart'**
  String get negozio_carrello_meta_titolo;

  /// No description provided for @negozio_carrello_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'The decks in your cart, with prices, discounts and the total before you order.'**
  String get negozio_carrello_meta_descrizione;

  /// No description provided for @negozio_non_disponibile.
  ///
  /// In en, this message translates to:
  /// **'Something in your cart is no longer available: remove it to continue.'**
  String get negozio_non_disponibile;

  /// No description provided for @negozio_quantita_di.
  ///
  /// In en, this message translates to:
  /// **'Quantity of {cosa}'**
  String negozio_quantita_di(Object cosa);

  /// No description provided for @negozio_meno.
  ///
  /// In en, this message translates to:
  /// **'One less'**
  String get negozio_meno;

  /// No description provided for @negozio_piu.
  ///
  /// In en, this message translates to:
  /// **'One more'**
  String get negozio_piu;

  /// No description provided for @negozio_subtotale.
  ///
  /// In en, this message translates to:
  /// **'Subtotal'**
  String get negozio_subtotale;

  /// No description provided for @negozio_sconto_scaglioni.
  ///
  /// In en, this message translates to:
  /// **'Discount for different decks ({p}%)'**
  String negozio_sconto_scaglioni(Object p);

  /// No description provided for @negozio_pagamento_non_attivo.
  ///
  /// In en, this message translates to:
  /// **'Payments are not active yet: completing the order registers it without charging you. We will write to you when you can pay for it.'**
  String get negozio_pagamento_non_attivo;

  /// No description provided for @negozio_ordine_registrato.
  ///
  /// In en, this message translates to:
  /// **'Order {numero} registered ({totale}). Payments are not active yet: nothing has been charged, and we will write to you when you can complete it.'**
  String negozio_ordine_registrato(Object numero, Object totale);

  /// No description provided for @negozio_vedi_ordini.
  ///
  /// In en, this message translates to:
  /// **'See your orders'**
  String get negozio_vedi_ordini;

  /// No description provided for @prezzi_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Reading packages and subscriptions'**
  String get prezzi_meta_titolo;

  /// No description provided for @prezzi_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Your first reading is free. Then packages or a subscription, when continuity has become useful.'**
  String get prezzi_meta_descrizione;

  /// No description provided for @prezzi_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Readings, packages and subscriptions'**
  String get prezzi_eyebrow;

  /// No description provided for @prezzi_titolo.
  ///
  /// In en, this message translates to:
  /// **'Choose continuity when it has become useful.'**
  String get prezzi_titolo;

  /// No description provided for @prezzi_intro.
  ///
  /// In en, this message translates to:
  /// **'The first reading is free and needs no account. A free account adds more readings. Packages and subscriptions are for a practice you want to keep returning to.'**
  String get prezzi_intro;

  /// No description provided for @prezzi_gratis_titolo.
  ///
  /// In en, this message translates to:
  /// **'Free beginning'**
  String get prezzi_gratis_titolo;

  /// No description provided for @prezzi_gratis_prezzo.
  ///
  /// In en, this message translates to:
  /// **'Free'**
  String get prezzi_gratis_prezzo;

  /// No description provided for @prezzi_gratis_testo.
  ///
  /// In en, this message translates to:
  /// **'Try the ritual and a first response. Create an account after the value has been shown.'**
  String get prezzi_gratis_testo;

  /// No description provided for @prezzi_gratis_voci_0.
  ///
  /// In en, this message translates to:
  /// **'A free first reading, no account'**
  String get prezzi_gratis_voci_0;

  /// No description provided for @prezzi_gratis_voci_1.
  ///
  /// In en, this message translates to:
  /// **'{n} more free readings with a free account'**
  String prezzi_gratis_voci_1(Object n);

  /// No description provided for @prezzi_gratis_voci_2.
  ///
  /// In en, this message translates to:
  /// **'The card of the day, always free'**
  String get prezzi_gratis_voci_2;

  /// No description provided for @prezzi_gratis_cta.
  ///
  /// In en, this message translates to:
  /// **'Start your free reading'**
  String get prezzi_gratis_cta;

  /// No description provided for @prezzi_pacchetti.
  ///
  /// In en, this message translates to:
  /// **'Reading packages'**
  String get prezzi_pacchetti;

  /// No description provided for @prezzi_pacchetti_testo.
  ///
  /// In en, this message translates to:
  /// **'For the moments you want to return to a question, at your own pace.'**
  String get prezzi_pacchetti_testo;

  /// No description provided for @prezzi_abbonamenti.
  ///
  /// In en, this message translates to:
  /// **'Subscriptions'**
  String get prezzi_abbonamenti;

  /// No description provided for @prezzi_abbonamenti_testo.
  ///
  /// In en, this message translates to:
  /// **'For a continuing practice, with memory and follow-up at the centre.'**
  String get prezzi_abbonamenti_testo;

  /// No description provided for @prezzi_per_lettura.
  ///
  /// In en, this message translates to:
  /// **'{n} readings · {prezzo} per reading'**
  String prezzi_per_lettura(Object n, Object prezzo);

  /// No description provided for @prezzi_al_giorno.
  ///
  /// In en, this message translates to:
  /// **'{n} readings a day'**
  String prezzi_al_giorno(Object n);

  /// No description provided for @prezzi_giorno_gratis.
  ///
  /// In en, this message translates to:
  /// **'Free card of the day'**
  String get prezzi_giorno_gratis;

  /// No description provided for @prezzi_al_mese.
  ///
  /// In en, this message translates to:
  /// **'/ month'**
  String get prezzi_al_mese;

  /// No description provided for @prezzi_gratuito.
  ///
  /// In en, this message translates to:
  /// **'Free'**
  String get prezzi_gratuito;

  /// No description provided for @prezzi_acquista.
  ///
  /// In en, this message translates to:
  /// **'Choose this package'**
  String get prezzi_acquista;

  /// No description provided for @prezzi_abbonati.
  ///
  /// In en, this message translates to:
  /// **'Subscribe'**
  String get prezzi_abbonati;

  /// No description provided for @prezzi_scegli.
  ///
  /// In en, this message translates to:
  /// **'Choose'**
  String get prezzi_scegli;

  /// No description provided for @prezzi_il_tuo.
  ///
  /// In en, this message translates to:
  /// **'Your plan'**
  String get prezzi_il_tuo;

  /// No description provided for @prezzi_scontato.
  ///
  /// In en, this message translates to:
  /// **'discounted'**
  String get prezzi_scontato;

  /// No description provided for @prezzi_gratis_codice.
  ///
  /// In en, this message translates to:
  /// **'Free with this code'**
  String get prezzi_gratis_codice;

  /// No description provided for @prezzi_non_vale.
  ///
  /// In en, this message translates to:
  /// **'The code does not apply to this offer.'**
  String get prezzi_non_vale;

  /// No description provided for @prezzi_saldo.
  ///
  /// In en, this message translates to:
  /// **'Your balance'**
  String get prezzi_saldo;

  /// No description provided for @prezzi_crediti.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 reading credit} other{{n} reading credits}}'**
  String prezzi_crediti(int n);

  /// No description provided for @prezzi_piano.
  ///
  /// In en, this message translates to:
  /// **'Subscription'**
  String get prezzi_piano;

  /// No description provided for @prezzi_disdetto.
  ///
  /// In en, this message translates to:
  /// **'Cancelled: stays active until {data}.'**
  String prezzi_disdetto(Object data);

  /// No description provided for @prezzi_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'Renews on {data}.'**
  String prezzi_rinnovo(Object data);

  /// No description provided for @prezzi_oggi.
  ///
  /// In en, this message translates to:
  /// **'Today\'s readings'**
  String get prezzi_oggi;

  /// No description provided for @prezzi_disdici.
  ///
  /// In en, this message translates to:
  /// **'Cancel the subscription'**
  String get prezzi_disdici;

  /// No description provided for @prezzi_codici.
  ///
  /// In en, this message translates to:
  /// **'Have a code?'**
  String get prezzi_codici;

  /// No description provided for @prezzi_codice_sconto.
  ///
  /// In en, this message translates to:
  /// **'Discount code'**
  String get prezzi_codice_sconto;

  /// No description provided for @prezzi_codice_sconto_aiuto.
  ///
  /// In en, this message translates to:
  /// **'Each code says how long it lasts: the first payment, a few months, or every renewal.'**
  String get prezzi_codice_sconto_aiuto;

  /// No description provided for @prezzi_codice_regalo.
  ///
  /// In en, this message translates to:
  /// **'Gift code'**
  String get prezzi_codice_regalo;

  /// No description provided for @prezzi_codice_regalo_aiuto.
  ///
  /// In en, this message translates to:
  /// **'A gift code adds readings right away, no payment.'**
  String get prezzi_codice_regalo_aiuto;

  /// No description provided for @prezzi_applica.
  ///
  /// In en, this message translates to:
  /// **'Apply'**
  String get prezzi_applica;

  /// No description provided for @prezzi_riscatta.
  ///
  /// In en, this message translates to:
  /// **'Redeem'**
  String get prezzi_riscatta;

  /// No description provided for @prezzi_togli.
  ///
  /// In en, this message translates to:
  /// **'Remove the code'**
  String get prezzi_togli;

  /// No description provided for @prezzi_applicato.
  ///
  /// In en, this message translates to:
  /// **'Code {codice} applied: the prices below are already discounted.'**
  String prezzi_applicato(Object codice);

  /// No description provided for @prezzi_riscattato.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{You received 1 reading.} other{You received {n} readings.}}'**
  String prezzi_riscattato(int n);

  /// No description provided for @prezzi_errori_codice_coupon_sconosciuto.
  ///
  /// In en, this message translates to:
  /// **'This code does not exist.'**
  String get prezzi_errori_codice_coupon_sconosciuto;

  /// No description provided for @prezzi_errori_codice_coupon_non_attivo.
  ///
  /// In en, this message translates to:
  /// **'This code is no longer active.'**
  String get prezzi_errori_codice_coupon_non_attivo;

  /// No description provided for @prezzi_errori_codice_coupon_non_ancora_valido.
  ///
  /// In en, this message translates to:
  /// **'This code is not valid yet.'**
  String get prezzi_errori_codice_coupon_non_ancora_valido;

  /// No description provided for @prezzi_errori_codice_coupon_scaduto.
  ///
  /// In en, this message translates to:
  /// **'This code has expired.'**
  String get prezzi_errori_codice_coupon_scaduto;

  /// No description provided for @prezzi_errori_codice_coupon_esaurito.
  ///
  /// In en, this message translates to:
  /// **'This code has been used up.'**
  String get prezzi_errori_codice_coupon_esaurito;

  /// No description provided for @prezzi_errori_codice_coupon_gia_usato.
  ///
  /// In en, this message translates to:
  /// **'You have already used this code.'**
  String get prezzi_errori_codice_coupon_gia_usato;

  /// No description provided for @prezzi_errori_codice_coupon_non_per_questo_piano.
  ///
  /// In en, this message translates to:
  /// **'This code does not apply to this offer.'**
  String get prezzi_errori_codice_coupon_non_per_questo_piano;

  /// No description provided for @prezzi_errori_codice_coupon_solo_primo_acquisto.
  ///
  /// In en, this message translates to:
  /// **'This code only works on a first purchase.'**
  String get prezzi_errori_codice_coupon_solo_primo_acquisto;

  /// No description provided for @prezzi_errori_codice_coupon_azzera_abbonamento.
  ///
  /// In en, this message translates to:
  /// **'This code cannot be applied to this subscription.'**
  String get prezzi_errori_codice_coupon_azzera_abbonamento;

  /// No description provided for @prezzi_errori_codice_coupon_sconto.
  ///
  /// In en, this message translates to:
  /// **'This is a discount code: use it with an offer above.'**
  String get prezzi_errori_codice_coupon_sconto;

  /// No description provided for @prezzi_errori_codice_coupon_regalo.
  ///
  /// In en, this message translates to:
  /// **'This is a gift code: redeem it below.'**
  String get prezzi_errori_codice_coupon_regalo;

  /// No description provided for @prezzi_errori_codice_coupon_non_cumulabile.
  ///
  /// In en, this message translates to:
  /// **'This code doesn\'t add to your other discounts, and the one you already have is higher.'**
  String get prezzi_errori_codice_coupon_non_cumulabile;

  /// No description provided for @prezzi_errori_codice_troppi_tentativi.
  ///
  /// In en, this message translates to:
  /// **'Too many wrong codes: try again in an hour.'**
  String get prezzi_errori_codice_troppi_tentativi;

  /// No description provided for @prezzi_coupon_applicato.
  ///
  /// In en, this message translates to:
  /// **'Code {codice} applied'**
  String prezzi_coupon_applicato(Object codice);

  /// No description provided for @prezzi_coupon_sconto_pacchetto.
  ///
  /// In en, this message translates to:
  /// **'{sconto} on packages'**
  String prezzi_coupon_sconto_pacchetto(Object sconto);

  /// No description provided for @prezzi_coupon_durata_una_volta.
  ///
  /// In en, this message translates to:
  /// **'{sconto} on the first payment'**
  String prezzi_coupon_durata_una_volta(Object sconto);

  /// No description provided for @prezzi_coupon_durata_periodi.
  ///
  /// In en, this message translates to:
  /// **'{sconto} on your first {n} payments'**
  String prezzi_coupon_durata_periodi(Object sconto, Object n);

  /// No description provided for @prezzi_coupon_durata_sempre.
  ///
  /// In en, this message translates to:
  /// **'{sconto} on every payment, renewals included'**
  String prezzi_coupon_durata_sempre(Object sconto);

  /// No description provided for @prezzi_coupon_cumulabile.
  ///
  /// In en, this message translates to:
  /// **'It adds to the automatic-renewal and trial discounts.'**
  String get prezzi_coupon_cumulabile;

  /// No description provided for @prezzi_coupon_non_cumulabile.
  ///
  /// In en, this message translates to:
  /// **'It doesn\'t add to other discounts: you always get the higher one.'**
  String get prezzi_coupon_non_cumulabile;

  /// No description provided for @prezzi_coupon_scade_oggi.
  ///
  /// In en, this message translates to:
  /// **'Expires today'**
  String get prezzi_coupon_scade_oggi;

  /// No description provided for @prezzi_coupon_scade_tra.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{Expires tomorrow} other{Expires in {n} days}}'**
  String prezzi_coupon_scade_tra(int n);

  /// No description provided for @prezzi_coupon_risparmi.
  ///
  /// In en, this message translates to:
  /// **'You save {importo}'**
  String prezzi_coupon_risparmi(Object importo);

  /// No description provided for @prezzi_coupon_badge.
  ///
  /// In en, this message translates to:
  /// **'{sconto} with your code'**
  String prezzi_coupon_badge(Object sconto);

  /// No description provided for @prezzi_coupon_vince_entrambi.
  ///
  /// In en, this message translates to:
  /// **'Code and automatic-renewal discount, combined.'**
  String get prezzi_coupon_vince_entrambi;

  /// No description provided for @prezzi_coupon_vince_coupon.
  ///
  /// In en, this message translates to:
  /// **'The code\'s discount is higher than the automatic-renewal one ({base}): it applies instead.'**
  String prezzi_coupon_vince_coupon(Object base);

  /// No description provided for @prezzi_coupon_vince_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'Your automatic-renewal discount ({base}) is higher and the code doesn\'t add to it: you already pay the lower price.'**
  String prezzi_coupon_vince_rinnovo(Object base);

  /// No description provided for @prezzi_coupon_vince_prova.
  ///
  /// In en, this message translates to:
  /// **'The trial discount ({base}) is higher and the code doesn\'t add to it.'**
  String prezzi_coupon_vince_prova(Object base);

  /// No description provided for @prezzi_coupon_poi.
  ///
  /// In en, this message translates to:
  /// **'Then {prezzo}.'**
  String prezzi_coupon_poi(Object prezzo);

  /// No description provided for @prezzi_coupon_togli.
  ///
  /// In en, this message translates to:
  /// **'Remove the code'**
  String get prezzi_coupon_togli;

  /// No description provided for @prezzi_coupon_nella_prova.
  ///
  /// In en, this message translates to:
  /// **'Code {codice}: the first payment after the trial is {prezzo} instead of {listino}.'**
  String prezzi_coupon_nella_prova(Object codice, Object prezzo, Object listino);

  /// No description provided for @prezzi_coupon_nella_prova_no.
  ///
  /// In en, this message translates to:
  /// **'Code {codice}: the trial discount is higher, so it stays.'**
  String prezzi_coupon_nella_prova_no(Object codice);

  /// No description provided for @prezzi_coupon_solo_stripe.
  ///
  /// In en, this message translates to:
  /// **'Codes work on card payments on the website; in the app, use the card (Stripe) button.'**
  String get prezzi_coupon_solo_stripe;

  /// No description provided for @prezzi_movimenti.
  ///
  /// In en, this message translates to:
  /// **'Recent activity'**
  String get prezzi_movimenti;

  /// No description provided for @prezzi_nessun_movimento.
  ///
  /// In en, this message translates to:
  /// **'No activity yet.'**
  String get prezzi_nessun_movimento;

  /// No description provided for @prezzi_motivi_accredito_piano.
  ///
  /// In en, this message translates to:
  /// **'Plan readings'**
  String get prezzi_motivi_accredito_piano;

  /// No description provided for @prezzi_motivi_acquisto.
  ///
  /// In en, this message translates to:
  /// **'Package purchased'**
  String get prezzi_motivi_acquisto;

  /// No description provided for @prezzi_motivi_consumo.
  ///
  /// In en, this message translates to:
  /// **'Reading'**
  String get prezzi_motivi_consumo;

  /// No description provided for @prezzi_motivi_rimborso.
  ///
  /// In en, this message translates to:
  /// **'Refund'**
  String get prezzi_motivi_rimborso;

  /// No description provided for @prezzi_motivi_rettifica.
  ///
  /// In en, this message translates to:
  /// **'Adjustment'**
  String get prezzi_motivi_rettifica;

  /// No description provided for @prezzi_motivi_scadenza.
  ///
  /// In en, this message translates to:
  /// **'Expiry'**
  String get prezzi_motivi_scadenza;

  /// No description provided for @prezzi_motivi_omaggio.
  ///
  /// In en, this message translates to:
  /// **'Gift'**
  String get prezzi_motivi_omaggio;

  /// No description provided for @prezzi_motivi_storno.
  ///
  /// In en, this message translates to:
  /// **'Payment reversed'**
  String get prezzi_motivi_storno;

  /// No description provided for @prezzi_motivi_storno_annullato.
  ///
  /// In en, this message translates to:
  /// **'Reversal cancelled'**
  String get prezzi_motivi_storno_annullato;

  /// No description provided for @prezzi_pagato_pacchetto.
  ///
  /// In en, this message translates to:
  /// **'Payment complete: the readings of «{nome}» are in your balance.'**
  String prezzi_pagato_pacchetto(Object nome);

  /// No description provided for @prezzi_pagato_piano.
  ///
  /// In en, this message translates to:
  /// **'Payment complete: the plan «{nome}» is active.'**
  String prezzi_pagato_piano(Object nome);

  /// No description provided for @prezzi_non_completato.
  ///
  /// In en, this message translates to:
  /// **'The payment was not completed.'**
  String get prezzi_non_completato;

  /// No description provided for @prezzi_non_verificato.
  ///
  /// In en, this message translates to:
  /// **'The payment could not be verified.'**
  String get prezzi_non_verificato;

  /// No description provided for @prezzi_torno.
  ///
  /// In en, this message translates to:
  /// **'Returning to your reading…'**
  String get prezzi_torno;

  /// No description provided for @prezzi_fiducia.
  ///
  /// In en, this message translates to:
  /// **'No prediction is guaranteed by any plan: every reading is an interpretation for reflection.'**
  String get prezzi_fiducia;

  /// No description provided for @blog_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'The journal'**
  String get blog_meta_titolo;

  /// No description provided for @blog_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Ideas to sit with, not answers to consume: cards, spreads and the themes that run through them.'**
  String get blog_meta_descrizione;

  /// No description provided for @blog_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'The journal'**
  String get blog_eyebrow;

  /// No description provided for @blog_titolo.
  ///
  /// In en, this message translates to:
  /// **'Ideas to sit with, not answers to consume.'**
  String get blog_titolo;

  /// No description provided for @blog_intro.
  ///
  /// In en, this message translates to:
  /// **'Articles connect to cards, deck imagery, questions and readings. Follow an image to a meaning, then back to your own question.'**
  String get blog_intro;

  /// No description provided for @blog_cerca.
  ///
  /// In en, this message translates to:
  /// **'Search the journal'**
  String get blog_cerca;

  /// No description provided for @blog_cerca_segnaposto.
  ///
  /// In en, this message translates to:
  /// **'Search for an article…'**
  String get blog_cerca_segnaposto;

  /// No description provided for @blog_cerca_vai.
  ///
  /// In en, this message translates to:
  /// **'Search'**
  String get blog_cerca_vai;

  /// No description provided for @blog_risultati.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 result for “{q}”} other{{n} results for “{q}”}}'**
  String blog_risultati(int n, Object q);

  /// No description provided for @blog_in_evidenza.
  ///
  /// In en, this message translates to:
  /// **'Featured'**
  String get blog_in_evidenza;

  /// No description provided for @blog_ultimi.
  ///
  /// In en, this message translates to:
  /// **'Latest articles'**
  String get blog_ultimi;

  /// No description provided for @blog_sezioni.
  ///
  /// In en, this message translates to:
  /// **'Sections'**
  String get blog_sezioni;

  /// No description provided for @blog_etichette.
  ///
  /// In en, this message translates to:
  /// **'Topics'**
  String get blog_etichette;

  /// No description provided for @blog_sottosezioni.
  ///
  /// In en, this message translates to:
  /// **'In this section'**
  String get blog_sottosezioni;

  /// No description provided for @blog_articoli.
  ///
  /// In en, this message translates to:
  /// **'Articles'**
  String get blog_articoli;

  /// No description provided for @blog_carte_sezione.
  ///
  /// In en, this message translates to:
  /// **'The cards in this section'**
  String get blog_carte_sezione;

  /// No description provided for @blog_stese_sezione.
  ///
  /// In en, this message translates to:
  /// **'The spreads in this section'**
  String get blog_stese_sezione;

  /// No description provided for @blog_conta_carte.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 card} other{{n} cards}}'**
  String blog_conta_carte(int n);

  /// No description provided for @blog_conta_stese.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 spread} other{{n} spreads}}'**
  String blog_conta_stese(int n);

  /// No description provided for @blog_conta_articoli.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 article} other{{n} articles}}'**
  String blog_conta_articoli(int n);

  /// No description provided for @blog_vuoto.
  ///
  /// In en, this message translates to:
  /// **'There are no articles here yet.'**
  String get blog_vuoto;

  /// No description provided for @blog_nessun_risultato.
  ///
  /// In en, this message translates to:
  /// **'No article matches your search.'**
  String get blog_nessun_risultato;

  /// No description provided for @blog_min.
  ///
  /// In en, this message translates to:
  /// **'{n} min read'**
  String blog_min(Object n);

  /// No description provided for @blog_di.
  ///
  /// In en, this message translates to:
  /// **'by {nome}'**
  String blog_di(Object nome);

  /// No description provided for @blog_aggiornato.
  ///
  /// In en, this message translates to:
  /// **'Updated {data}'**
  String blog_aggiornato(Object data);

  /// No description provided for @blog_percorso.
  ///
  /// In en, this message translates to:
  /// **'Path'**
  String get blog_percorso;

  /// No description provided for @blog_pagina.
  ///
  /// In en, this message translates to:
  /// **'Page {p} of {n}'**
  String blog_pagina(Object p, Object n);

  /// No description provided for @blog_piu_recenti.
  ///
  /// In en, this message translates to:
  /// **'← Newer'**
  String get blog_piu_recenti;

  /// No description provided for @blog_meno_recenti.
  ///
  /// In en, this message translates to:
  /// **'Older →'**
  String get blog_meno_recenti;

  /// No description provided for @blog_rss.
  ///
  /// In en, this message translates to:
  /// **'RSS feed'**
  String get blog_rss;

  /// No description provided for @blog_tipo_carta.
  ///
  /// In en, this message translates to:
  /// **'Card'**
  String get blog_tipo_carta;

  /// No description provided for @blog_tipo_stesa.
  ///
  /// In en, this message translates to:
  /// **'Spread'**
  String get blog_tipo_stesa;

  /// No description provided for @blog_tipo_articolo.
  ///
  /// In en, this message translates to:
  /// **'Article'**
  String get blog_tipo_articolo;

  /// No description provided for @blog_si_parla_di.
  ///
  /// In en, this message translates to:
  /// **'This article talks about'**
  String get blog_si_parla_di;

  /// No description provided for @blog_domande.
  ///
  /// In en, this message translates to:
  /// **'Questions'**
  String get blog_domande;

  /// No description provided for @blog_correlati.
  ///
  /// In en, this message translates to:
  /// **'You might also like'**
  String get blog_correlati;

  /// No description provided for @blog_precedente.
  ///
  /// In en, this message translates to:
  /// **'Previous article'**
  String get blog_precedente;

  /// No description provided for @blog_successivo.
  ///
  /// In en, this message translates to:
  /// **'Next article'**
  String get blog_successivo;

  /// No description provided for @blog_condividi.
  ///
  /// In en, this message translates to:
  /// **'Share this article'**
  String get blog_condividi;

  /// No description provided for @blog_copia_link.
  ///
  /// In en, this message translates to:
  /// **'Copy the link'**
  String get blog_copia_link;

  /// No description provided for @blog_copiato.
  ///
  /// In en, this message translates to:
  /// **'Link copied'**
  String get blog_copiato;

  /// No description provided for @blog_ponte_titolo.
  ///
  /// In en, this message translates to:
  /// **'Bring it into a question'**
  String get blog_ponte_titolo;

  /// No description provided for @blog_ponte_testo.
  ///
  /// In en, this message translates to:
  /// **'An article opens a door; a reading walks through it. Ask what this means for you, in your situation.'**
  String get blog_ponte_testo;

  /// No description provided for @blog_ponte_cta.
  ///
  /// In en, this message translates to:
  /// **'Ask your own question'**
  String get blog_ponte_cta;

  /// No description provided for @blog_non_trovato.
  ///
  /// In en, this message translates to:
  /// **'This article does not exist, or it is no longer published.'**
  String get blog_non_trovato;

  /// No description provided for @blog_pagina_prima.
  ///
  /// In en, this message translates to:
  /// **'First page'**
  String get blog_pagina_prima;

  /// No description provided for @blog_pagina_ultima.
  ///
  /// In en, this message translates to:
  /// **'Last page'**
  String get blog_pagina_ultima;

  /// No description provided for @blog_pagina_precedente.
  ///
  /// In en, this message translates to:
  /// **'Previous page'**
  String get blog_pagina_precedente;

  /// No description provided for @blog_pagina_successiva.
  ///
  /// In en, this message translates to:
  /// **'Next page'**
  String get blog_pagina_successiva;

  /// No description provided for @blog_pagina_n.
  ///
  /// In en, this message translates to:
  /// **'Page {p}'**
  String blog_pagina_n(Object p);

  /// No description provided for @blog_per_pagina.
  ///
  /// In en, this message translates to:
  /// **'Per page'**
  String get blog_per_pagina;

  /// No description provided for @blog_stesa_inizia.
  ///
  /// In en, this message translates to:
  /// **'Begin a reading with this spread'**
  String get blog_stesa_inizia;

  /// No description provided for @blog_stesa_posizioni.
  ///
  /// In en, this message translates to:
  /// **'See the positions'**
  String get blog_stesa_posizioni;

  /// No description provided for @blog_articoli_su.
  ///
  /// In en, this message translates to:
  /// **'Every article about {nome}'**
  String blog_articoli_su(Object nome);

  /// No description provided for @blog_esplora_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Explore the Tarot'**
  String get blog_esplora_meta_titolo;

  /// No description provided for @blog_esplora_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'The journal, the cards, the spreads and the decks as one connected graph that leads back to your own question.'**
  String get blog_esplora_meta_descrizione;

  /// No description provided for @blog_esplora_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Explore the Tarot'**
  String get blog_esplora_eyebrow;

  /// No description provided for @blog_esplora_titolo.
  ///
  /// In en, this message translates to:
  /// **'Follow an image to a meaning, then back to your own question.'**
  String get blog_esplora_titolo;

  /// No description provided for @blog_esplora_intro.
  ///
  /// In en, this message translates to:
  /// **'The journal, the cards, the spreads and the decks are one connected graph — not disconnected pages.'**
  String get blog_esplora_intro;

  /// No description provided for @blog_esplora_voci_0_chiave.
  ///
  /// In en, this message translates to:
  /// **'diario'**
  String get blog_esplora_voci_0_chiave;

  /// No description provided for @blog_esplora_voci_0_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✎'**
  String get blog_esplora_voci_0_simbolo;

  /// No description provided for @blog_esplora_voci_0_titolo.
  ///
  /// In en, this message translates to:
  /// **'The journal'**
  String get blog_esplora_voci_0_titolo;

  /// No description provided for @blog_esplora_voci_0_testo.
  ///
  /// In en, this message translates to:
  /// **'Guides, reflections and the themes running through the cards.'**
  String get blog_esplora_voci_0_testo;

  /// No description provided for @blog_esplora_voci_1_chiave.
  ///
  /// In en, this message translates to:
  /// **'carte'**
  String get blog_esplora_voci_1_chiave;

  /// No description provided for @blog_esplora_voci_1_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✦'**
  String get blog_esplora_voci_1_simbolo;

  /// No description provided for @blog_esplora_voci_1_titolo.
  ///
  /// In en, this message translates to:
  /// **'Card library'**
  String get blog_esplora_voci_1_titolo;

  /// No description provided for @blog_esplora_voci_1_testo.
  ///
  /// In en, this message translates to:
  /// **'The 78 Thoth cards: images, correspondences, meanings.'**
  String get blog_esplora_voci_1_testo;

  /// No description provided for @blog_esplora_voci_2_chiave.
  ///
  /// In en, this message translates to:
  /// **'stese'**
  String get blog_esplora_voci_2_chiave;

  /// No description provided for @blog_esplora_voci_2_simbolo.
  ///
  /// In en, this message translates to:
  /// **'▦'**
  String get blog_esplora_voci_2_simbolo;

  /// No description provided for @blog_esplora_voci_2_titolo.
  ///
  /// In en, this message translates to:
  /// **'Spreads'**
  String get blog_esplora_voci_2_titolo;

  /// No description provided for @blog_esplora_voci_2_testo.
  ///
  /// In en, this message translates to:
  /// **'The shapes a reading can take, position by position.'**
  String get blog_esplora_voci_2_testo;

  /// No description provided for @blog_esplora_voci_3_chiave.
  ///
  /// In en, this message translates to:
  /// **'mazzi'**
  String get blog_esplora_voci_3_chiave;

  /// No description provided for @blog_esplora_voci_3_simbolo.
  ///
  /// In en, this message translates to:
  /// **'❖'**
  String get blog_esplora_voci_3_simbolo;

  /// No description provided for @blog_esplora_voci_3_titolo.
  ///
  /// In en, this message translates to:
  /// **'Decks'**
  String get blog_esplora_voci_3_titolo;

  /// No description provided for @blog_esplora_voci_3_testo.
  ///
  /// In en, this message translates to:
  /// **'The visual worlds you can read with, now and next.'**
  String get blog_esplora_voci_3_testo;

  /// No description provided for @blog_esplora_voci_4_chiave.
  ///
  /// In en, this message translates to:
  /// **'giorno'**
  String get blog_esplora_voci_4_chiave;

  /// No description provided for @blog_esplora_voci_4_simbolo.
  ///
  /// In en, this message translates to:
  /// **'☉'**
  String get blog_esplora_voci_4_simbolo;

  /// No description provided for @blog_esplora_voci_4_titolo.
  ///
  /// In en, this message translates to:
  /// **'Card of the day'**
  String get blog_esplora_voci_4_titolo;

  /// No description provided for @blog_esplora_voci_4_testo.
  ///
  /// In en, this message translates to:
  /// **'A small encounter, free, every day.'**
  String get blog_esplora_voci_4_testo;

  /// No description provided for @blog_esplora_voci_5_chiave.
  ///
  /// In en, this message translates to:
  /// **'fisica'**
  String get blog_esplora_voci_5_chiave;

  /// No description provided for @blog_esplora_voci_5_simbolo.
  ///
  /// In en, this message translates to:
  /// **'✋'**
  String get blog_esplora_voci_5_simbolo;

  /// No description provided for @blog_esplora_voci_5_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your own cards'**
  String get blog_esplora_voci_5_titolo;

  /// No description provided for @blog_esplora_voci_5_testo.
  ///
  /// In en, this message translates to:
  /// **'Draw with your deck, read the pattern here.'**
  String get blog_esplora_voci_5_testo;

  /// No description provided for @blog_esplora_ultimi.
  ///
  /// In en, this message translates to:
  /// **'From the journal'**
  String get blog_esplora_ultimi;

  /// No description provided for @blog_nove_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'The Journal'**
  String get blog_nove_eyebrow;

  /// No description provided for @blog_nove_titolo.
  ///
  /// In en, this message translates to:
  /// **'From the Journal'**
  String get blog_nove_titolo;

  /// No description provided for @blog_nove_ultimi.
  ///
  /// In en, this message translates to:
  /// **'Read the latest posts'**
  String get blog_nove_ultimi;

  /// No description provided for @blog_nove_attinenti.
  ///
  /// In en, this message translates to:
  /// **'Chosen for this page'**
  String get blog_nove_attinenti;

  /// No description provided for @blog_a_caso.
  ///
  /// In en, this message translates to:
  /// **'More to read, picked for you today'**
  String get blog_a_caso;

  /// No description provided for @blog_nove_sezione.
  ///
  /// In en, this message translates to:
  /// **'More in {sezione}'**
  String blog_nove_sezione(Object sezione);

  /// No description provided for @blog_copyright.
  ///
  /// In en, this message translates to:
  /// **'© {anno} TAROTS chat (tarots.chat). All rights reserved. No part of this article may be reproduced, distributed or adapted without the owner\'s written permission.'**
  String blog_copyright(Object anno);

  /// No description provided for @profilo_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your account'**
  String get profilo_meta_titolo;

  /// No description provided for @profilo_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Your story is yours to manage.'**
  String get profilo_meta_descrizione;

  /// No description provided for @profilo_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Your account'**
  String get profilo_eyebrow;

  /// No description provided for @profilo_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your story is yours to manage.'**
  String get profilo_titolo;

  /// No description provided for @profilo_intro.
  ///
  /// In en, this message translates to:
  /// **'Readings, memory, invitations and the details of your physical decks, arranged as parts of one personal story.'**
  String get profilo_intro;

  /// No description provided for @profilo_fuori.
  ///
  /// In en, this message translates to:
  /// **'Sign in to manage your account.'**
  String get profilo_fuori;

  /// No description provided for @profilo_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get profilo_entra;

  /// No description provided for @profilo_esci.
  ///
  /// In en, this message translates to:
  /// **'Sign out'**
  String get profilo_esci;

  /// No description provided for @profilo_storia_link.
  ///
  /// In en, this message translates to:
  /// **'Readings and memory live in My story'**
  String get profilo_storia_link;

  /// No description provided for @profilo_storia_cta.
  ///
  /// In en, this message translates to:
  /// **'Open My story'**
  String get profilo_storia_cta;

  /// No description provided for @profilo_carte_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your personal cards'**
  String get profilo_carte_titolo;

  /// No description provided for @profilo_carte_testo.
  ///
  /// In en, this message translates to:
  /// **'From your date of birth, by theosophical reduction, come the soul card — the lesson of a lifetime — and the card of your personal year. If you give it, your reader takes it into account.'**
  String get profilo_carte_testo;

  /// No description provided for @profilo_nascita.
  ///
  /// In en, this message translates to:
  /// **'Date of birth'**
  String get profilo_nascita;

  /// No description provided for @profilo_carta_anima.
  ///
  /// In en, this message translates to:
  /// **'Soul card'**
  String get profilo_carta_anima;

  /// No description provided for @profilo_carta_anno.
  ///
  /// In en, this message translates to:
  /// **'Year card'**
  String get profilo_carta_anno;

  /// No description provided for @profilo_genere_titolo.
  ///
  /// In en, this message translates to:
  /// **'Gender'**
  String get profilo_genere_titolo;

  /// No description provided for @profilo_genere_testo.
  ///
  /// In en, this message translates to:
  /// **'Only used by readings about two people, for pronouns and agreement. «Prefer not to say» is a valid answer.'**
  String get profilo_genere_testo;

  /// No description provided for @profilo_partner_titolo.
  ///
  /// In en, this message translates to:
  /// **'Remembered person'**
  String get profilo_partner_titolo;

  /// No description provided for @profilo_partner_vuoto.
  ///
  /// In en, this message translates to:
  /// **'No one is remembered. You can choose to remember someone in a compatibility or couple reading.'**
  String get profilo_partner_vuoto;

  /// No description provided for @profilo_partner_dimentica.
  ///
  /// In en, this message translates to:
  /// **'Forget this person'**
  String get profilo_partner_dimentica;

  /// No description provided for @profilo_partner_conferma.
  ///
  /// In en, this message translates to:
  /// **'Forget the remembered person?'**
  String get profilo_partner_conferma;

  /// No description provided for @profilo_registro_titolo.
  ///
  /// In en, this message translates to:
  /// **'How your reader speaks to you'**
  String get profilo_registro_titolo;

  /// No description provided for @profilo_registro_testo.
  ///
  /// In en, this message translates to:
  /// **'The esoteric register is the traditional Tarot language; the everyday register avoids unexplained technical terms.'**
  String get profilo_registro_testo;

  /// No description provided for @profilo_registro_esoterico.
  ///
  /// In en, this message translates to:
  /// **'Esoteric language (traditional)'**
  String get profilo_registro_esoterico;

  /// No description provided for @profilo_registro_quotidiano.
  ///
  /// In en, this message translates to:
  /// **'Everyday language'**
  String get profilo_registro_quotidiano;

  /// No description provided for @profilo_mazzo_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your deck'**
  String get profilo_mazzo_titolo;

  /// No description provided for @profilo_mazzo_testo.
  ///
  /// In en, this message translates to:
  /// **'The deck you see by default in new readings.'**
  String get profilo_mazzo_testo;

  /// No description provided for @profilo_mazzo_predefinito.
  ///
  /// In en, this message translates to:
  /// **'(default)'**
  String get profilo_mazzo_predefinito;

  /// No description provided for @profilo_avatar_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your picture and public name'**
  String get profilo_avatar_titolo;

  /// No description provided for @profilo_avatar_testo.
  ///
  /// In en, this message translates to:
  /// **'They appear next to your comments in the journal. A photo or a logo, cropped to a square.'**
  String get profilo_avatar_testo;

  /// No description provided for @profilo_avatar_carica.
  ///
  /// In en, this message translates to:
  /// **'Choose a picture'**
  String get profilo_avatar_carica;

  /// No description provided for @profilo_avatar_togli.
  ///
  /// In en, this message translates to:
  /// **'Remove the picture'**
  String get profilo_avatar_togli;

  /// No description provided for @profilo_avatar_errore.
  ///
  /// In en, this message translates to:
  /// **'The image is not valid (PNG, JPEG or WebP, at least 64 px per side, at most 8 MB).'**
  String get profilo_avatar_errore;

  /// No description provided for @profilo_nome_pubblico.
  ///
  /// In en, this message translates to:
  /// **'Public name'**
  String get profilo_nome_pubblico;

  /// No description provided for @profilo_nome_pubblico_testo.
  ///
  /// In en, this message translates to:
  /// **'If you leave it empty your first name is used; never your email.'**
  String get profilo_nome_pubblico_testo;

  /// No description provided for @profilo_nome_salvato.
  ///
  /// In en, this message translates to:
  /// **'Name saved'**
  String get profilo_nome_salvato;

  /// No description provided for @profilo_invito_titolo.
  ///
  /// In en, this message translates to:
  /// **'Invite those you love'**
  String get profilo_invito_titolo;

  /// No description provided for @profilo_invito_testo.
  ///
  /// In en, this message translates to:
  /// **'Every new account receives {iscrizione} free readings. With your code, whoever signs up receives {invito} instead — and you receive the same {invito}.'**
  String profilo_invito_testo(Object iscrizione, Object invito);

  /// No description provided for @profilo_invito_commissione.
  ///
  /// In en, this message translates to:
  /// **'And beyond the first time: for every future purchase of the people you invite, {percentuale}% comes back to you in readings.'**
  String profilo_invito_commissione(Object percentuale);

  /// No description provided for @profilo_invito_condividi.
  ///
  /// In en, this message translates to:
  /// **'Share your invitation'**
  String get profilo_invito_condividi;

  /// No description provided for @profilo_invito_copiato.
  ///
  /// In en, this message translates to:
  /// **'Copied'**
  String get profilo_invito_copiato;

  /// No description provided for @profilo_invito_testo_condivisione.
  ///
  /// In en, this message translates to:
  /// **'My TAROTS chat invitation code: {codice}'**
  String profilo_invito_testo_condivisione(Object codice);

  /// No description provided for @profilo_bigliettino.
  ///
  /// In en, this message translates to:
  /// **'Download the invitation card'**
  String get profilo_bigliettino;

  /// No description provided for @profilo_bigliettino_claim.
  ///
  /// In en, this message translates to:
  /// **'A living Tarot ritual, with a reader who remembers your story'**
  String get profilo_bigliettino_claim;

  /// No description provided for @profilo_bigliettino_omaggio.
  ///
  /// In en, this message translates to:
  /// **'{n} free readings'**
  String profilo_bigliettino_omaggio(Object n);

  /// No description provided for @profilo_hai_codice.
  ///
  /// In en, this message translates to:
  /// **'Do you have an invitation code?'**
  String get profilo_hai_codice;

  /// No description provided for @profilo_riscatta.
  ///
  /// In en, this message translates to:
  /// **'Redeem'**
  String get profilo_riscatta;

  /// No description provided for @profilo_regalo.
  ///
  /// In en, this message translates to:
  /// **'You received {n} free readings.'**
  String profilo_regalo(Object n);

  /// No description provided for @profilo_cond_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your shares'**
  String get profilo_cond_titolo;

  /// No description provided for @profilo_cond_testo.
  ///
  /// In en, this message translates to:
  /// **'Every {soglia} verified shares you receive a free reading, and whoever signs up from your link gives you {crediti}. A share is verified when someone else opens your link.'**
  String profilo_cond_testo(Object soglia, Object crediti);

  /// No description provided for @profilo_cond_prossimo.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{1 more until the next free reading} other{{n} more until the next free reading}}'**
  String profilo_cond_prossimo(int n);

  /// No description provided for @profilo_cond_verificate.
  ///
  /// In en, this message translates to:
  /// **'Verified shares'**
  String get profilo_cond_verificate;

  /// No description provided for @profilo_cond_premi.
  ///
  /// In en, this message translates to:
  /// **'Free readings received'**
  String get profilo_cond_premi;

  /// No description provided for @profilo_cond_iscritti.
  ///
  /// In en, this message translates to:
  /// **'Sign-ups from your link'**
  String get profilo_cond_iscritti;

  /// No description provided for @profilo_ordini_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your orders'**
  String get profilo_ordini_titolo;

  /// No description provided for @profilo_ordini_vuoto.
  ///
  /// In en, this message translates to:
  /// **'No orders yet.'**
  String get profilo_ordini_vuoto;

  /// No description provided for @profilo_ordini_stato_aperto.
  ///
  /// In en, this message translates to:
  /// **'awaiting payment'**
  String get profilo_ordini_stato_aperto;

  /// No description provided for @profilo_ordini_stato_pagato.
  ///
  /// In en, this message translates to:
  /// **'paid'**
  String get profilo_ordini_stato_pagato;

  /// No description provided for @profilo_ordini_stato_annullato.
  ///
  /// In en, this message translates to:
  /// **'cancelled'**
  String get profilo_ordini_stato_annullato;

  /// No description provided for @profilo_ordini_stato_scaduto.
  ///
  /// In en, this message translates to:
  /// **'expired'**
  String get profilo_ordini_stato_scaduto;

  /// No description provided for @profilo_ordini_evasione_in_attesa.
  ///
  /// In en, this message translates to:
  /// **'awaiting shipment'**
  String get profilo_ordini_evasione_in_attesa;

  /// No description provided for @profilo_ordini_evasione_spedito.
  ///
  /// In en, this message translates to:
  /// **'shipped'**
  String get profilo_ordini_evasione_spedito;

  /// No description provided for @profilo_ordini_evasione_consegnato.
  ///
  /// In en, this message translates to:
  /// **'delivered'**
  String get profilo_ordini_evasione_consegnato;

  /// No description provided for @profilo_ordini_sconto.
  ///
  /// In en, this message translates to:
  /// **'discount for multiple decks'**
  String get profilo_ordini_sconto;

  /// No description provided for @profilo_ordini_tipo_digitale.
  ///
  /// In en, this message translates to:
  /// **'digital deck'**
  String get profilo_ordini_tipo_digitale;

  /// No description provided for @profilo_ordini_tipo_pdf.
  ///
  /// In en, this message translates to:
  /// **'printable PDF'**
  String get profilo_ordini_tipo_pdf;

  /// No description provided for @profilo_ordini_tipo_fisico.
  ///
  /// In en, this message translates to:
  /// **'physical box set'**
  String get profilo_ordini_tipo_fisico;

  /// No description provided for @profilo_indirizzi_titolo.
  ///
  /// In en, this message translates to:
  /// **'Shipping addresses'**
  String get profilo_indirizzi_titolo;

  /// No description provided for @profilo_indirizzi_testo.
  ///
  /// In en, this message translates to:
  /// **'For receiving a physical deck. The default one is proposed at checkout.'**
  String get profilo_indirizzi_testo;

  /// No description provided for @profilo_indirizzi_vuoto.
  ///
  /// In en, this message translates to:
  /// **'No address saved yet.'**
  String get profilo_indirizzi_vuoto;

  /// No description provided for @profilo_indirizzi_nome.
  ///
  /// In en, this message translates to:
  /// **'Full name'**
  String get profilo_indirizzi_nome;

  /// No description provided for @profilo_indirizzi_via.
  ///
  /// In en, this message translates to:
  /// **'Street and number'**
  String get profilo_indirizzi_via;

  /// No description provided for @profilo_indirizzi_citta.
  ///
  /// In en, this message translates to:
  /// **'City'**
  String get profilo_indirizzi_citta;

  /// No description provided for @profilo_indirizzi_cap.
  ///
  /// In en, this message translates to:
  /// **'Postal code'**
  String get profilo_indirizzi_cap;

  /// No description provided for @profilo_indirizzi_provincia.
  ///
  /// In en, this message translates to:
  /// **'State or province (optional)'**
  String get profilo_indirizzi_provincia;

  /// No description provided for @profilo_indirizzi_paese.
  ///
  /// In en, this message translates to:
  /// **'Country (code, e.g. IT)'**
  String get profilo_indirizzi_paese;

  /// No description provided for @profilo_indirizzi_telefono.
  ///
  /// In en, this message translates to:
  /// **'Phone (optional)'**
  String get profilo_indirizzi_telefono;

  /// No description provided for @profilo_indirizzi_predefinito.
  ///
  /// In en, this message translates to:
  /// **'Default'**
  String get profilo_indirizzi_predefinito;

  /// No description provided for @profilo_indirizzi_imposta.
  ///
  /// In en, this message translates to:
  /// **'Make default'**
  String get profilo_indirizzi_imposta;

  /// No description provided for @profilo_indirizzi_aggiungi.
  ///
  /// In en, this message translates to:
  /// **'Add an address'**
  String get profilo_indirizzi_aggiungi;

  /// No description provided for @profilo_indirizzi_salva.
  ///
  /// In en, this message translates to:
  /// **'Save the address'**
  String get profilo_indirizzi_salva;

  /// No description provided for @profilo_indirizzi_elimina.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get profilo_indirizzi_elimina;

  /// No description provided for @profilo_sic_titolo.
  ///
  /// In en, this message translates to:
  /// **'Account security'**
  String get profilo_sic_titolo;

  /// No description provided for @profilo_sic_testo.
  ///
  /// In en, this message translates to:
  /// **'Two-step verification adds a temporary code from an authenticator app (Google Authenticator, Microsoft Authenticator, FreeOTP): a stolen password is not enough to get in. It is optional.'**
  String get profilo_sic_testo;

  /// No description provided for @profilo_sic_stato.
  ///
  /// In en, this message translates to:
  /// **'Two-step verification'**
  String get profilo_sic_stato;

  /// No description provided for @profilo_sic_attiva.
  ///
  /// In en, this message translates to:
  /// **'On'**
  String get profilo_sic_attiva;

  /// No description provided for @profilo_sic_spenta.
  ///
  /// In en, this message translates to:
  /// **'Off'**
  String get profilo_sic_spenta;

  /// No description provided for @profilo_sic_ignota.
  ///
  /// In en, this message translates to:
  /// **'Status not available: check it in your account'**
  String get profilo_sic_ignota;

  /// No description provided for @profilo_sic_attiva_ora.
  ///
  /// In en, this message translates to:
  /// **'Turn on two-step verification'**
  String get profilo_sic_attiva_ora;

  /// No description provided for @profilo_sic_gestisci.
  ///
  /// In en, this message translates to:
  /// **'Manage in your account'**
  String get profilo_sic_gestisci;

  /// No description provided for @profilo_sic_promemoria.
  ///
  /// In en, this message translates to:
  /// **'Remind me to turn it on every time I sign in'**
  String get profilo_sic_promemoria;

  /// No description provided for @profilo_acc_titolo.
  ///
  /// In en, this message translates to:
  /// **'Sign-in methods'**
  String get profilo_acc_titolo;

  /// No description provided for @profilo_acc_testo.
  ///
  /// In en, this message translates to:
  /// **'One account, several ways in. Link Apple and Google here: in the app (Apple on iPhone, Google on Android) you will find your story right away, even if you hide your email from Apple.'**
  String get profilo_acc_testo;

  /// No description provided for @profilo_acc_collegati.
  ///
  /// In en, this message translates to:
  /// **'Linked:'**
  String get profilo_acc_collegati;

  /// No description provided for @profilo_acc_nessuno.
  ///
  /// In en, this message translates to:
  /// **'no social account yet'**
  String get profilo_acc_nessuno;

  /// No description provided for @profilo_acc_non_raggiungibile.
  ///
  /// In en, this message translates to:
  /// **'We can\'t show your sign-in methods right now. Try again in a little while.'**
  String get profilo_acc_non_raggiungibile;

  /// No description provided for @profilo_acc_collega_apple.
  ///
  /// In en, this message translates to:
  /// **'Link your Apple ID'**
  String get profilo_acc_collega_apple;

  /// No description provided for @profilo_acc_collega_google.
  ///
  /// In en, this message translates to:
  /// **'Link Google'**
  String get profilo_acc_collega_google;

  /// No description provided for @profilo_acc_fatto.
  ///
  /// In en, this message translates to:
  /// **'Done: {provider} is now linked to this account.'**
  String profilo_acc_fatto(Object provider);

  /// No description provided for @profilo_acc_errore_sessione.
  ///
  /// In en, this message translates to:
  /// **'Your session had expired, so nothing was linked. Try again: we\'ll ask you to sign in first.'**
  String get profilo_acc_errore_sessione;

  /// No description provided for @profilo_acc_errore.
  ///
  /// In en, this message translates to:
  /// **'The link didn\'t work. Try again in a little while.'**
  String get profilo_acc_errore;

  /// No description provided for @profilo_acc_codice_titolo.
  ///
  /// In en, this message translates to:
  /// **'Do you have a code from the app?'**
  String get profilo_acc_codice_titolo;

  /// No description provided for @profilo_acc_codice_testo.
  ///
  /// In en, this message translates to:
  /// **'If the app created a new account (for example with Apple\'s «Hide My Email»), it shows you an 8-character code. Enter it here within 10 minutes: that sign-in moves to this account, together with anything you did in the app.'**
  String get profilo_acc_codice_testo;

  /// No description provided for @profilo_acc_codice_campo.
  ///
  /// In en, this message translates to:
  /// **'Code from the app'**
  String get profilo_acc_codice_campo;

  /// No description provided for @profilo_acc_codice_usa.
  ///
  /// In en, this message translates to:
  /// **'Link'**
  String get profilo_acc_codice_usa;

  /// No description provided for @profilo_acc_codice_fatto.
  ///
  /// In en, this message translates to:
  /// **'Done: {provider} now brings you to this account. In the app, sign out and sign in again.'**
  String profilo_acc_codice_fatto(Object provider);

  /// No description provided for @profilo_acc_codice_errori_codice_non_valido.
  ///
  /// In en, this message translates to:
  /// **'This code isn\'t valid or has expired. Ask the app for a new one (it lasts 10 minutes).'**
  String get profilo_acc_codice_errori_codice_non_valido;

  /// No description provided for @profilo_acc_codice_errori_stesso_account.
  ///
  /// In en, this message translates to:
  /// **'This code belongs to this same account: enter it in your other account, the one on the site.'**
  String get profilo_acc_codice_errori_stesso_account;

  /// No description provided for @profilo_acc_codice_errori_gia_collegato.
  ///
  /// In en, this message translates to:
  /// **'This account already has a {provider} sign-in: an account can have only one.'**
  String profilo_acc_codice_errori_gia_collegato(Object provider);

  /// No description provided for @profilo_acc_codice_errori_abbonamento_attivo.
  ///
  /// In en, this message translates to:
  /// **'The app account has an active subscription: write to us and we\'ll move it for you, without losing any days.'**
  String get profilo_acc_codice_errori_abbonamento_attivo;

  /// No description provided for @profilo_acc_codice_errori_troppi_tentativi.
  ///
  /// In en, this message translates to:
  /// **'Too many attempts. Try again in an hour.'**
  String get profilo_acc_codice_errori_troppi_tentativi;

  /// No description provided for @profilo_acc_codice_errori_nessuna_identita.
  ///
  /// In en, this message translates to:
  /// **'The app account has no sign-in to move.'**
  String get profilo_acc_codice_errori_nessuna_identita;

  /// No description provided for @profilo_acc_codice_errori_keycloak.
  ///
  /// In en, this message translates to:
  /// **'The sign-in service isn\'t answering. Try again in a little while.'**
  String get profilo_acc_codice_errori_keycloak;

  /// No description provided for @profilo_acc_codice_errori_generico.
  ///
  /// In en, this message translates to:
  /// **'Something went wrong. Try again in a little while.'**
  String get profilo_acc_codice_errori_generico;

  /// No description provided for @profilo_nome_manca.
  ///
  /// In en, this message translates to:
  /// **'What\'s your name? If you signed in with Apple, your name didn\'t reach us. Write it here so your reader can call you by name — only if you like.'**
  String get profilo_nome_manca;

  /// No description provided for @profilo_stat_titolo.
  ///
  /// In en, this message translates to:
  /// **'Usage statistics'**
  String get profilo_stat_titolo;

  /// No description provided for @profilo_stat_testo.
  ///
  /// In en, this message translates to:
  /// **'Your visits are linked to your account so we can understand how to improve the service. If you object, we stop linking them and immediately delete the link with past ones.'**
  String get profilo_stat_testo;

  /// No description provided for @profilo_stat_opponi.
  ///
  /// In en, this message translates to:
  /// **'Do not link my visits to my account'**
  String get profilo_stat_opponi;

  /// No description provided for @profilo_stat_privacy.
  ///
  /// In en, this message translates to:
  /// **'Read the privacy page'**
  String get profilo_stat_privacy;

  /// No description provided for @profilo_dati_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your details'**
  String get profilo_dati_titolo;

  /// No description provided for @profilo_dati_testo.
  ///
  /// In en, this message translates to:
  /// **'Your name and where you are now. When you sign in with Google, Facebook or another social, we fill in only the fields that are still empty with what that account shares — never over what you wrote. Date of birth and gender serve your readings (personal cards, pronouns).'**
  String get profilo_dati_testo;

  /// No description provided for @profilo_nome.
  ///
  /// In en, this message translates to:
  /// **'First name'**
  String get profilo_nome;

  /// No description provided for @profilo_cognome.
  ///
  /// In en, this message translates to:
  /// **'Last name'**
  String get profilo_cognome;

  /// No description provided for @profilo_da_social.
  ///
  /// In en, this message translates to:
  /// **'from {provider}, {data}'**
  String profilo_da_social(Object provider, Object data);

  /// No description provided for @profilo_da_account.
  ///
  /// In en, this message translates to:
  /// **'from your sign-up'**
  String get profilo_da_account;

  /// No description provided for @profilo_posizione_titolo.
  ///
  /// In en, this message translates to:
  /// **'Where you are now'**
  String get profilo_posizione_titolo;

  /// No description provided for @profilo_posizione_testo.
  ///
  /// In en, this message translates to:
  /// **'Country and city, updated at each sign-in from the social (if it shares it) or estimated from your connection (approximate; the IP address is not stored). If it is wrong, correct it: from then on it stays as you wrote it.'**
  String get profilo_posizione_testo;

  /// No description provided for @profilo_posizione_nessuna.
  ///
  /// In en, this message translates to:
  /// **'Not detected yet.'**
  String get profilo_posizione_nessuna;

  /// No description provided for @profilo_posizione_ip.
  ///
  /// In en, this message translates to:
  /// **'estimated from your connection, {data}'**
  String profilo_posizione_ip(Object data);

  /// No description provided for @profilo_posizione_utente.
  ///
  /// In en, this message translates to:
  /// **'set by you'**
  String get profilo_posizione_utente;

  /// No description provided for @profilo_posizione_paese.
  ///
  /// In en, this message translates to:
  /// **'Country (code, e.g. IT)'**
  String get profilo_posizione_paese;

  /// No description provided for @profilo_posizione_citta.
  ///
  /// In en, this message translates to:
  /// **'City'**
  String get profilo_posizione_citta;

  /// No description provided for @profilo_posizione_correggi.
  ///
  /// In en, this message translates to:
  /// **'Save the location'**
  String get profilo_posizione_correggi;

  /// No description provided for @profilo_posizione_automatica.
  ///
  /// In en, this message translates to:
  /// **'Detect it automatically again'**
  String get profilo_posizione_automatica;

  /// No description provided for @profilo_importa_social.
  ///
  /// In en, this message translates to:
  /// **'When I sign in with a social, fill in my empty details from it'**
  String get profilo_importa_social;

  /// No description provided for @profilo_rileva_posizione.
  ///
  /// In en, this message translates to:
  /// **'Detect where I am at each sign-in'**
  String get profilo_rileva_posizione;

  /// No description provided for @profilo_dimentica_social.
  ///
  /// In en, this message translates to:
  /// **'Delete what came from socials'**
  String get profilo_dimentica_social;

  /// No description provided for @profilo_dimentica_conferma.
  ///
  /// In en, this message translates to:
  /// **'Delete the details taken from your socials (those you corrected stay) and your current location, and stop taking them?'**
  String get profilo_dimentica_conferma;

  /// No description provided for @profilo_dimentica_fatto.
  ///
  /// In en, this message translates to:
  /// **'Deleted. Nothing more will be taken from your socials.'**
  String get profilo_dimentica_fatto;

  /// No description provided for @profilo_salvato.
  ///
  /// In en, this message translates to:
  /// **'Saved'**
  String get profilo_salvato;

  /// No description provided for @profilo_unione_titolo.
  ///
  /// In en, this message translates to:
  /// **'You already had an account with this email'**
  String get profilo_unione_titolo;

  /// No description provided for @profilo_unione_esisteva.
  ///
  /// In en, this message translates to:
  /// **'An account with your email already existed, but its email had never been confirmed: anyone could have created it.'**
  String get profilo_unione_esisteva;

  /// No description provided for @profilo_unione_creato.
  ///
  /// In en, this message translates to:
  /// **'It was created on {data}.'**
  String profilo_unione_creato(Object data);

  /// No description provided for @profilo_unione_tolti.
  ///
  /// In en, this message translates to:
  /// **'To be safe, we removed its old ways to sign in ({tolti}). From now on you sign in with the social you just used.'**
  String profilo_unione_tolti(Object tolti);

  /// No description provided for @profilo_unione_contiene.
  ///
  /// In en, this message translates to:
  /// **'It contains —'**
  String get profilo_unione_contiene;

  /// No description provided for @profilo_unione_letture.
  ///
  /// In en, this message translates to:
  /// **'readings:'**
  String get profilo_unione_letture;

  /// No description provided for @profilo_unione_memorie.
  ///
  /// In en, this message translates to:
  /// **'memories:'**
  String get profilo_unione_memorie;

  /// No description provided for @profilo_unione_crediti.
  ///
  /// In en, this message translates to:
  /// **'credits:'**
  String get profilo_unione_crediti;

  /// No description provided for @profilo_unione_acquisti.
  ///
  /// In en, this message translates to:
  /// **'purchases:'**
  String get profilo_unione_acquisti;

  /// No description provided for @profilo_unione_vuoto.
  ///
  /// In en, this message translates to:
  /// **'It is empty: no readings, no memories, no purchases.'**
  String get profilo_unione_vuoto;

  /// No description provided for @profilo_unione_domanda.
  ///
  /// In en, this message translates to:
  /// **'Was it yours?'**
  String get profilo_unione_domanda;

  /// No description provided for @profilo_unione_mia.
  ///
  /// In en, this message translates to:
  /// **'Yes, it\'s mine: keep it'**
  String get profilo_unione_mia;

  /// No description provided for @profilo_unione_non_mia.
  ///
  /// In en, this message translates to:
  /// **'No, I didn\'t create it'**
  String get profilo_unione_non_mia;

  /// No description provided for @profilo_unione_non_mia_vuoto.
  ///
  /// In en, this message translates to:
  /// **'We delete it, and you start with a new account.'**
  String get profilo_unione_non_mia_vuoto;

  /// No description provided for @profilo_unione_non_mia_pieno.
  ///
  /// In en, this message translates to:
  /// **'We separate it from you: its readings, memories and credits won\'t be yours. You start with a new account.'**
  String get profilo_unione_non_mia_pieno;

  /// No description provided for @profilo_unione_password_titolo.
  ///
  /// In en, this message translates to:
  /// **'Also sign in with email and password (optional)'**
  String get profilo_unione_password_titolo;

  /// No description provided for @profilo_unione_password_aiuto.
  ///
  /// In en, this message translates to:
  /// **'It can be the one you used before, if you remember it. At least 6 characters, different from your email.'**
  String get profilo_unione_password_aiuto;

  /// No description provided for @profilo_unione_mostra.
  ///
  /// In en, this message translates to:
  /// **'Show'**
  String get profilo_unione_mostra;

  /// No description provided for @profilo_unione_nascondi.
  ///
  /// In en, this message translates to:
  /// **'Hide'**
  String get profilo_unione_nascondi;

  /// No description provided for @profilo_unione_conferma.
  ///
  /// In en, this message translates to:
  /// **'Confirm'**
  String get profilo_unione_conferma;

  /// No description provided for @profilo_unione_dopo.
  ///
  /// In en, this message translates to:
  /// **'Later'**
  String get profilo_unione_dopo;

  /// No description provided for @profilo_unione_cred_password.
  ///
  /// In en, this message translates to:
  /// **'password'**
  String get profilo_unione_cred_password;

  /// No description provided for @profilo_unione_cred_otp.
  ///
  /// In en, this message translates to:
  /// **'authenticator app code'**
  String get profilo_unione_cred_otp;

  /// No description provided for @profilo_unione_cred_chiave.
  ///
  /// In en, this message translates to:
  /// **'security key'**
  String get profilo_unione_cred_chiave;

  /// No description provided for @profilo_unione_pw_corta.
  ///
  /// In en, this message translates to:
  /// **'The password is too short: at least 6 characters.'**
  String get profilo_unione_pw_corta;

  /// No description provided for @profilo_unione_pw_nome.
  ///
  /// In en, this message translates to:
  /// **'The password can\'t be your username.'**
  String get profilo_unione_pw_nome;

  /// No description provided for @profilo_unione_pw_email.
  ///
  /// In en, this message translates to:
  /// **'The password can\'t be your email.'**
  String get profilo_unione_pw_email;

  /// No description provided for @profilo_unione_pw_storia.
  ///
  /// In en, this message translates to:
  /// **'You used this password recently: choose another one.'**
  String get profilo_unione_pw_storia;

  /// No description provided for @profilo_unione_pw_altro.
  ///
  /// In en, this message translates to:
  /// **'This password isn\'t accepted: try another one.'**
  String get profilo_unione_pw_altro;

  /// No description provided for @profilo_unione_errore.
  ///
  /// In en, this message translates to:
  /// **'Your answer wasn\'t saved. Try again.'**
  String get profilo_unione_errore;

  /// No description provided for @profilo_privacy_titolo.
  ///
  /// In en, this message translates to:
  /// **'Privacy and consents'**
  String get profilo_privacy_titolo;

  /// No description provided for @profilo_privacy_testo.
  ///
  /// In en, this message translates to:
  /// **'Every choice is yours, and you can change it here at any time, as easily as you made it.'**
  String get profilo_privacy_testo;

  /// No description provided for @profilo_cons_statistiche.
  ///
  /// In en, this message translates to:
  /// **'Site statistics'**
  String get profilo_cons_statistiche;

  /// No description provided for @profilo_cons_statistiche_testo.
  ///
  /// In en, this message translates to:
  /// **'A random identifier recognises this browser when you come back. Turning it off makes our servers forget it.'**
  String get profilo_cons_statistiche_testo;

  /// No description provided for @profilo_cons_google.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics'**
  String get profilo_cons_google;

  /// No description provided for @profilo_cons_google_testo.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics 4 measures how the site is used, with its own cookies. Turning it off stops it and deletes its cookies.'**
  String get profilo_cons_google_testo;

  /// No description provided for @profilo_cons_pubblicita.
  ///
  /// In en, this message translates to:
  /// **'Ads'**
  String get profilo_cons_pubblicita;

  /// No description provided for @profilo_cons_pubblicita_testo.
  ///
  /// In en, this message translates to:
  /// **'Google AdSense ads in the marked spaces of some pages.'**
  String get profilo_cons_pubblicita_testo;

  /// No description provided for @profilo_cons_testi.
  ///
  /// In en, this message translates to:
  /// **'Your words for statistics and blog ideas'**
  String get profilo_cons_testi;

  /// No description provided for @profilo_cons_testi_testo.
  ///
  /// In en, this message translates to:
  /// **'Your questions and conversations may be used anonymously and in aggregate — at least five people, never quoted — to understand which topics matter and to choose blog articles. Nothing is extracted yet.'**
  String get profilo_cons_testi_testo;

  /// No description provided for @profilo_cons_art9.
  ///
  /// In en, this message translates to:
  /// **'Sensitive data'**
  String get profilo_cons_art9;

  /// No description provided for @profilo_cons_art9_testo.
  ///
  /// In en, this message translates to:
  /// **'The “trans person” box and what you tell about your health, used in readings and remembered by your reader. Turning it off clears the box and deletes the memories about health.'**
  String get profilo_cons_art9_testo;

  /// No description provided for @profilo_cons_marketing.
  ///
  /// In en, this message translates to:
  /// **'Promotions'**
  String get profilo_cons_marketing;

  /// No description provided for @profilo_cons_marketing_testo.
  ///
  /// In en, this message translates to:
  /// **'Offers and news through notifications (app and browser), when they arrive. Daily card reminders are not promotions.'**
  String get profilo_cons_marketing_testo;

  /// No description provided for @profilo_cons_attivo.
  ///
  /// In en, this message translates to:
  /// **'On'**
  String get profilo_cons_attivo;

  /// No description provided for @profilo_cons_spento.
  ///
  /// In en, this message translates to:
  /// **'Off'**
  String get profilo_cons_spento;

  /// No description provided for @profilo_cons_mai.
  ///
  /// In en, this message translates to:
  /// **'Never chosen: off'**
  String get profilo_cons_mai;

  /// No description provided for @profilo_esporta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your data'**
  String get profilo_esporta_titolo;

  /// No description provided for @profilo_esporta_testo.
  ///
  /// In en, this message translates to:
  /// **'Download everything your account holds in one ZIP file: profile, readings with the interview, memory, chat, choices, credits, orders. Once a day.'**
  String get profilo_esporta_testo;

  /// No description provided for @profilo_esporta_cta.
  ///
  /// In en, this message translates to:
  /// **'Download my data'**
  String get profilo_esporta_cta;

  /// No description provided for @profilo_esporta_fatto.
  ///
  /// In en, this message translates to:
  /// **'The download has started.'**
  String get profilo_esporta_fatto;

  /// No description provided for @profilo_esporta_attendi.
  ///
  /// In en, this message translates to:
  /// **'You already downloaded your data in the last 24 hours: you can do it again from {data}.'**
  String profilo_esporta_attendi(Object data);

  /// No description provided for @profilo_esporta_ultima.
  ///
  /// In en, this message translates to:
  /// **'Last download: {data}.'**
  String profilo_esporta_ultima(Object data);

  /// No description provided for @profilo_chat_titolo.
  ///
  /// In en, this message translates to:
  /// **'Chat with the oracle'**
  String get profilo_chat_titolo;

  /// No description provided for @profilo_chat_testo.
  ///
  /// In en, this message translates to:
  /// **'The conversation with the oracle stays in your account until you delete it.'**
  String get profilo_chat_testo;

  /// No description provided for @profilo_chat_cancella.
  ///
  /// In en, this message translates to:
  /// **'Delete the whole chat'**
  String get profilo_chat_cancella;

  /// No description provided for @profilo_chat_conferma.
  ///
  /// In en, this message translates to:
  /// **'All the messages of the chat will be deleted for good. The memories it created stay: you manage them from My story.'**
  String get profilo_chat_conferma;

  /// No description provided for @profilo_chat_cancellata.
  ///
  /// In en, this message translates to:
  /// **'The chat has been deleted.'**
  String get profilo_chat_cancellata;

  /// No description provided for @profilo_elimina_titolo.
  ///
  /// In en, this message translates to:
  /// **'Delete my account'**
  String get profilo_elimina_titolo;

  /// No description provided for @profilo_elimina_breve.
  ///
  /// In en, this message translates to:
  /// **'The account is closed at once; for {giorni} days you can change your mind by signing in again, then your data is deleted.'**
  String profilo_elimina_breve(Object giorni);

  /// No description provided for @profilo_elimina_cta.
  ///
  /// In en, this message translates to:
  /// **'Delete my account'**
  String get profilo_elimina_cta;

  /// No description provided for @profilo_elimina_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Delete your account'**
  String get profilo_elimina_meta_titolo;

  /// No description provided for @profilo_elimina_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'How to delete your TAROTS chat account and what happens to your data.'**
  String get profilo_elimina_meta_descrizione;

  /// No description provided for @profilo_elimina_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Your account'**
  String get profilo_elimina_eyebrow;

  /// No description provided for @profilo_elimina_h1.
  ///
  /// In en, this message translates to:
  /// **'Delete your account'**
  String get profilo_elimina_h1;

  /// No description provided for @profilo_elimina_intro.
  ///
  /// In en, this message translates to:
  /// **'You can delete your TAROTS chat account and your data at any time, from the website or the app. Here is what happens.'**
  String get profilo_elimina_intro;

  /// No description provided for @profilo_elimina_cosa_titolo.
  ///
  /// In en, this message translates to:
  /// **'What happens'**
  String get profilo_elimina_cosa_titolo;

  /// No description provided for @profilo_elimina_passo1.
  ///
  /// In en, this message translates to:
  /// **'Your account is closed at once and you are signed out everywhere. For {giorni} days you can change your mind: sign in again and cancel the request.'**
  String profilo_elimina_passo1(Object giorni);

  /// No description provided for @profilo_elimina_passo2.
  ///
  /// In en, this message translates to:
  /// **'After that your account and your personal data are deleted for good: readings, memory, chat, choices, addresses, picture.'**
  String get profilo_elimina_passo2;

  /// No description provided for @profilo_elimina_passo3.
  ///
  /// In en, this message translates to:
  /// **'If you want to keep your data, download it first.'**
  String get profilo_elimina_passo3;

  /// No description provided for @profilo_elimina_resta_titolo.
  ///
  /// In en, this message translates to:
  /// **'What we must keep'**
  String get profilo_elimina_resta_titolo;

  /// No description provided for @profilo_elimina_resta.
  ///
  /// In en, this message translates to:
  /// **'Only the accounting records the law requires (credits, payments, orders), detached from your identity: no name, email or address stays with them.'**
  String get profilo_elimina_resta;

  /// No description provided for @profilo_elimina_app.
  ///
  /// In en, this message translates to:
  /// **'The same applies to the app. Everything else about your data:'**
  String get profilo_elimina_app;

  /// No description provided for @profilo_elimina_entra_titolo.
  ///
  /// In en, this message translates to:
  /// **'Sign in to continue'**
  String get profilo_elimina_entra_titolo;

  /// No description provided for @profilo_elimina_entra_testo.
  ///
  /// In en, this message translates to:
  /// **'To delete your account, sign in with the account you want to delete.'**
  String get profilo_elimina_entra_testo;

  /// No description provided for @profilo_elimina_prima.
  ///
  /// In en, this message translates to:
  /// **'Before you go, you can download your data.'**
  String get profilo_elimina_prima;

  /// No description provided for @profilo_elimina_capito.
  ///
  /// In en, this message translates to:
  /// **'I understand: the account is closed now and deleted for good after {giorni} days.'**
  String profilo_elimina_capito(Object giorni);

  /// No description provided for @profilo_elimina_scrivi.
  ///
  /// In en, this message translates to:
  /// **'To confirm, type {parola}'**
  String profilo_elimina_scrivi(Object parola);

  /// No description provided for @profilo_elimina_parola.
  ///
  /// In en, this message translates to:
  /// **'DELETE'**
  String get profilo_elimina_parola;

  /// No description provided for @profilo_elimina_fatto_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your account is closed'**
  String get profilo_elimina_fatto_titolo;

  /// No description provided for @profilo_elimina_fatto.
  ///
  /// In en, this message translates to:
  /// **'Your data will be deleted on {data}. Until then you can change your mind by signing in again.'**
  String profilo_elimina_fatto(Object data);

  /// No description provided for @privacy_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Method & privacy'**
  String get privacy_meta_titolo;

  /// No description provided for @privacy_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'What is kept, why, and how you decide: readings, memory, statistics and cookies.'**
  String get privacy_meta_descrizione;

  /// No description provided for @privacy_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Method & privacy'**
  String get privacy_eyebrow;

  /// No description provided for @privacy_titolo.
  ///
  /// In en, this message translates to:
  /// **'Mystical does not have to mean opaque.'**
  String get privacy_titolo;

  /// No description provided for @privacy_intro.
  ///
  /// In en, this message translates to:
  /// **'What is kept, why, and how you decide. The same rules apply to every page of TAROTS chat.'**
  String get privacy_intro;

  /// No description provided for @privacy_letture_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your readings and your memory'**
  String get privacy_letture_titolo;

  /// No description provided for @privacy_letture_testo.
  ///
  /// In en, this message translates to:
  /// **'Readings are kept in your account so you can return to them. What your reader remembers comes from your readings and conversations, and you can review, edit or delete it at any time from My story. Deleting a reading removes it for good.'**
  String get privacy_letture_testo;

  /// No description provided for @privacy_letture_cta.
  ///
  /// In en, this message translates to:
  /// **'Manage what is remembered'**
  String get privacy_letture_cta;

  /// No description provided for @privacy_letture_accesso.
  ///
  /// In en, this message translates to:
  /// **'For security reasons only (for example to handle a report of abuse or a request for help), the administrators of TAROTS chat can read your readings, conversations, what the reader remembers and your profile data. Each access requires a stated reason and is recorded in a log.'**
  String get privacy_letture_accesso;

  /// No description provided for @privacy_ai_titolo.
  ///
  /// In en, this message translates to:
  /// **'How the AI is used'**
  String get privacy_ai_titolo;

  /// No description provided for @privacy_ai_testo.
  ///
  /// In en, this message translates to:
  /// **'An AI interprets the cards in the context of your question and your words. Names never reach the AI provider: it receives a placeholder (“Persona_1”) and you read the real name; the other person\'s surname is never sent. The AI does not know the future, and no reading is a prediction. With every request we ask the provider not to store the answers: your texts are not kept by it to train its models.'**
  String get privacy_ai_testo;

  /// No description provided for @privacy_custode_titolo.
  ///
  /// In en, this message translates to:
  /// **'Who is responsible for your data'**
  String get privacy_custode_titolo;

  /// No description provided for @privacy_custode_testo.
  ///
  /// In en, this message translates to:
  /// **'The data controller for the personal data collected by TAROTS chat (https://tarots.chat) is {titolare}.'**
  String privacy_custode_testo(Object titolare);

  /// No description provided for @privacy_custode_testo_senza_nome.
  ///
  /// In en, this message translates to:
  /// **'The data controller for the personal data collected by TAROTS chat (https://tarots.chat) can be reached at the privacy contact below.'**
  String get privacy_custode_testo_senza_nome;

  /// No description provided for @privacy_custode_indirizzo.
  ///
  /// In en, this message translates to:
  /// **'Postal address: {indirizzo}.'**
  String privacy_custode_indirizzo(Object indirizzo);

  /// No description provided for @privacy_custode_indirizzo_vuoto.
  ///
  /// In en, this message translates to:
  /// **'Postal address: available on request from the privacy contact.'**
  String get privacy_custode_indirizzo_vuoto;

  /// No description provided for @privacy_custode_codice.
  ///
  /// In en, this message translates to:
  /// **'Tax code or VAT number: {codice}.'**
  String privacy_custode_codice(Object codice);

  /// No description provided for @privacy_custode_email.
  ///
  /// In en, this message translates to:
  /// **'Privacy contact: {email}'**
  String privacy_custode_email(Object email);

  /// No description provided for @privacy_custode_email_vuoto.
  ///
  /// In en, this message translates to:
  /// **'Privacy contact: being updated; meanwhile you can exercise your rights from your account.'**
  String get privacy_custode_email_vuoto;

  /// No description provided for @privacy_custode_dpo.
  ///
  /// In en, this message translates to:
  /// **'Data protection officer (DPO): {dpo}.'**
  String privacy_custode_dpo(Object dpo);

  /// No description provided for @privacy_custode_dpo_no.
  ///
  /// In en, this message translates to:
  /// **'No data protection officer (DPO) has been appointed.'**
  String get privacy_custode_dpo_no;

  /// No description provided for @privacy_scelte_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your choices on this browser'**
  String get privacy_scelte_titolo;

  /// No description provided for @privacy_scelte_testo.
  ///
  /// In en, this message translates to:
  /// **'Everything below is off until you turn it on, and you can change it here at any time. Technical cookies (signing in, the anonymous free reading, remembering these choices) need no consent: without them the site does not work.'**
  String get privacy_scelte_testo;

  /// No description provided for @privacy_scelte_account.
  ///
  /// In en, this message translates to:
  /// **'The choices that concern your account — your words for statistics, sensitive data, promotions — are in your account.'**
  String get privacy_scelte_account;

  /// No description provided for @privacy_scelte_account_cta.
  ///
  /// In en, this message translates to:
  /// **'Privacy and consents'**
  String get privacy_scelte_account_cta;

  /// No description provided for @privacy_finalita_titolo.
  ///
  /// In en, this message translates to:
  /// **'What we use, why, and on what legal basis'**
  String get privacy_finalita_titolo;

  /// No description provided for @privacy_finalita_intro.
  ///
  /// In en, this message translates to:
  /// **'Each use of your data has its own purpose and its own legal basis under the GDPR:'**
  String get privacy_finalita_intro;

  /// No description provided for @privacy_finalita_0_cosa.
  ///
  /// In en, this message translates to:
  /// **'Account and profile'**
  String get privacy_finalita_0_cosa;

  /// No description provided for @privacy_finalita_0_perche.
  ///
  /// In en, this message translates to:
  /// **'To give you an account, keep your readings and personal cards, and sign you in (also with a social account).'**
  String get privacy_finalita_0_perche;

  /// No description provided for @privacy_finalita_0_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: the contract you ask for (art. 6.1.b GDPR).'**
  String get privacy_finalita_0_base;

  /// No description provided for @privacy_finalita_1_cosa.
  ///
  /// In en, this message translates to:
  /// **'Readings, interview, memory and chat'**
  String get privacy_finalita_1_cosa;

  /// No description provided for @privacy_finalita_1_perche.
  ///
  /// In en, this message translates to:
  /// **'To read the cards for you with an AI and remember what helps in the next readings.'**
  String get privacy_finalita_1_perche;

  /// No description provided for @privacy_finalita_1_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: contract; for sensitive data, your explicit consent (art. 9.2.a).'**
  String get privacy_finalita_1_base;

  /// No description provided for @privacy_finalita_2_cosa.
  ///
  /// In en, this message translates to:
  /// **'The free reading without an account'**
  String get privacy_finalita_2_cosa;

  /// No description provided for @privacy_finalita_2_perche.
  ///
  /// In en, this message translates to:
  /// **'To let you try one reading before signing up.'**
  String get privacy_finalita_2_perche;

  /// No description provided for @privacy_finalita_2_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: steps you ask for before a contract (art. 6.1.b).'**
  String get privacy_finalita_2_base;

  /// No description provided for @privacy_finalita_3_cosa.
  ///
  /// In en, this message translates to:
  /// **'Payments, credits, orders and shipping'**
  String get privacy_finalita_3_cosa;

  /// No description provided for @privacy_finalita_3_perche.
  ///
  /// In en, this message translates to:
  /// **'To sell credits, plans and decks, and to keep the accounts the law requires.'**
  String get privacy_finalita_3_perche;

  /// No description provided for @privacy_finalita_3_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: contract and legal obligations (art. 6.1.b and 6.1.c).'**
  String get privacy_finalita_3_base;

  /// No description provided for @privacy_finalita_4_cosa.
  ///
  /// In en, this message translates to:
  /// **'Security and records'**
  String get privacy_finalita_4_cosa;

  /// No description provided for @privacy_finalita_4_perche.
  ///
  /// In en, this message translates to:
  /// **'To protect accounts and the service, and to know who did what. IP addresses are stored only shortened, with a keyed fingerprint.'**
  String get privacy_finalita_4_perche;

  /// No description provided for @privacy_finalita_4_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: legitimate interest (art. 6.1.f).'**
  String get privacy_finalita_4_base;

  /// No description provided for @privacy_finalita_5_cosa.
  ///
  /// In en, this message translates to:
  /// **'Anonymous statistics'**
  String get privacy_finalita_5_cosa;

  /// No description provided for @privacy_finalita_5_perche.
  ///
  /// In en, this message translates to:
  /// **'To count visits without cookies and without storing anything in your browser.'**
  String get privacy_finalita_5_perche;

  /// No description provided for @privacy_finalita_5_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: legitimate interest.'**
  String get privacy_finalita_5_base;

  /// No description provided for @privacy_finalita_6_cosa.
  ///
  /// In en, this message translates to:
  /// **'Statistics linked to your account'**
  String get privacy_finalita_6_cosa;

  /// No description provided for @privacy_finalita_6_perche.
  ///
  /// In en, this message translates to:
  /// **'To understand which channels bring members and what leads to a purchase.'**
  String get privacy_finalita_6_perche;

  /// No description provided for @privacy_finalita_6_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: legitimate interest; you can object from your account (art. 21).'**
  String get privacy_finalita_6_base;

  /// No description provided for @privacy_finalita_7_cosa.
  ///
  /// In en, this message translates to:
  /// **'Site statistics with a browser identifier'**
  String get privacy_finalita_7_cosa;

  /// No description provided for @privacy_finalita_7_perche.
  ///
  /// In en, this message translates to:
  /// **'To recognise your browser when you come back.'**
  String get privacy_finalita_7_perche;

  /// No description provided for @privacy_finalita_7_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: your consent (art. 6.1.a).'**
  String get privacy_finalita_7_base;

  /// No description provided for @privacy_finalita_8_cosa.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics'**
  String get privacy_finalita_8_cosa;

  /// No description provided for @privacy_finalita_8_perche.
  ///
  /// In en, this message translates to:
  /// **'To measure how the site is used.'**
  String get privacy_finalita_8_perche;

  /// No description provided for @privacy_finalita_8_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: your consent.'**
  String get privacy_finalita_8_base;

  /// No description provided for @privacy_finalita_9_cosa.
  ///
  /// In en, this message translates to:
  /// **'Ads'**
  String get privacy_finalita_9_cosa;

  /// No description provided for @privacy_finalita_9_perche.
  ///
  /// In en, this message translates to:
  /// **'To show Google AdSense ads in a few marked spaces, only if they are switched on.'**
  String get privacy_finalita_9_perche;

  /// No description provided for @privacy_finalita_9_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: your consent.'**
  String get privacy_finalita_9_base;

  /// No description provided for @privacy_finalita_10_cosa.
  ///
  /// In en, this message translates to:
  /// **'Your words for statistics and blog ideas'**
  String get privacy_finalita_10_cosa;

  /// No description provided for @privacy_finalita_10_perche.
  ///
  /// In en, this message translates to:
  /// **'To understand, anonymously and in aggregate, which topics matter to people (never quoting anyone). Not active yet.'**
  String get privacy_finalita_10_perche;

  /// No description provided for @privacy_finalita_10_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: your separate, optional consent.'**
  String get privacy_finalita_10_base;

  /// No description provided for @privacy_finalita_11_cosa.
  ///
  /// In en, this message translates to:
  /// **'Promotions'**
  String get privacy_finalita_11_cosa;

  /// No description provided for @privacy_finalita_11_perche.
  ///
  /// In en, this message translates to:
  /// **'Offers and news through notifications, when they arrive.'**
  String get privacy_finalita_11_perche;

  /// No description provided for @privacy_finalita_11_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: your consent.'**
  String get privacy_finalita_11_base;

  /// No description provided for @privacy_finalita_12_cosa.
  ///
  /// In en, this message translates to:
  /// **'Minimum age'**
  String get privacy_finalita_12_cosa;

  /// No description provided for @privacy_finalita_12_perche.
  ///
  /// In en, this message translates to:
  /// **'To check you are old enough to use the service on your own.'**
  String get privacy_finalita_12_perche;

  /// No description provided for @privacy_finalita_12_base.
  ///
  /// In en, this message translates to:
  /// **'Basis: legal obligation (art. 8 GDPR) and contract.'**
  String get privacy_finalita_12_base;

  /// No description provided for @privacy_art9_titolo.
  ///
  /// In en, this message translates to:
  /// **'Sensitive data'**
  String get privacy_art9_titolo;

  /// No description provided for @privacy_art9_testo.
  ///
  /// In en, this message translates to:
  /// **'Some things you may tell us are special categories of data: being trans, your health. The “trans person” box and memories about your health are used only with your explicit consent, which you give where you tick the box and can withdraw at any time from your account: the box is then cleared and those memories deleted. Without it, they never reach the AI.'**
  String get privacy_art9_testo;

  /// No description provided for @privacy_art9_crisi.
  ///
  /// In en, this message translates to:
  /// **'If you write that you want to harm yourself, the reading stops and we show where to find help straight away. We only count that it happened, without linking it to you.'**
  String get privacy_art9_crisi;

  /// No description provided for @privacy_stat_titolo.
  ///
  /// In en, this message translates to:
  /// **'Usage statistics'**
  String get privacy_stat_titolo;

  /// No description provided for @privacy_stat_anonime.
  ///
  /// In en, this message translates to:
  /// **'We measure anonymously how the site is used: pages visited, where the visit comes from (search engine, social network, campaign), device and browser type, approximate country and city. No cookies, and nothing is stored in your browser. Your IP address is only used at the moment of the visit, to estimate country and city and to compute a fingerprint that changes every day: it is never stored.'**
  String get privacy_stat_anonime;

  /// No description provided for @privacy_stat_account.
  ///
  /// In en, this message translates to:
  /// **'If you have an account and are signed in, your visits are linked to your account, based on our legitimate interest in understanding how to improve the service (for example which channel new members come from and what leads to a purchase). You can object at any time from your account: from then on visits are no longer linked, and the link with past ones is deleted.'**
  String get privacy_stat_account;

  /// No description provided for @privacy_stat_esteso.
  ///
  /// In en, this message translates to:
  /// **'If you turn on “Site statistics”, we also recognise your browser when you come back on later days, with a random identifier kept in your browser. If you decline or change your mind, the identifier is forgotten by our servers too.'**
  String get privacy_stat_esteso;

  /// No description provided for @privacy_stat_google.
  ///
  /// In en, this message translates to:
  /// **'If you turn on “Google Analytics”, we also use Google Analytics 4, a service of Google Ireland Ltd., which sets its own cookies (_ga) to count visits and understand how the site is used. It is loaded only after your consent (Google Consent Mode), with Google signals and ad personalisation turned off; Google Analytics 4 does not store IP addresses. Google may process the data in the United States under the EU-US Data Privacy Framework. If you decline or withdraw your consent, Google Analytics stops and its cookies are deleted.'**
  String get privacy_stat_google;

  /// No description provided for @privacy_stat_conservazione.
  ///
  /// In en, this message translates to:
  /// **'Detailed visits and events are kept for 25 months; after that only anonymous daily totals remain. Automated analyses and exports only use aggregated data.'**
  String get privacy_stat_conservazione;

  /// No description provided for @privacy_stat_geo.
  ///
  /// In en, this message translates to:
  /// **'IP geolocation:'**
  String get privacy_stat_geo;

  /// No description provided for @privacy_pubblicita_titolo.
  ///
  /// In en, this message translates to:
  /// **'Advertising'**
  String get privacy_pubblicita_titolo;

  /// No description provided for @privacy_pubblicita_testo.
  ///
  /// In en, this message translates to:
  /// **'Some pages can show up to three spaces marked “Advertisement”, filled by Google AdSense, a service of Google Ireland Ltd. Ads load only if you accept here or in the banner: Google then sets its own cookies (such as __gads and __gpi) to deliver ads, limit how often you see them and measure them, and may process data in the United States under the EU-US Data Privacy Framework. Ads are not personalised unless this page says otherwise. If you decline, the spaces are not shown and nothing is loaded from Google AdSense.'**
  String get privacy_pubblicita_testo;

  /// No description provided for @privacy_social_titolo.
  ///
  /// In en, this message translates to:
  /// **'Signing in with a social'**
  String get privacy_social_titolo;

  /// No description provided for @privacy_social_account.
  ///
  /// In en, this message translates to:
  /// **'One account per person: if you sign in with Google, Facebook, Apple, GitHub or LinkedIn using the same email as an existing account, it is the same account, with the same readings and credits.'**
  String get privacy_social_account;

  /// No description provided for @privacy_social_cosa.
  ///
  /// In en, this message translates to:
  /// **'From that account we receive what it shares with us: first and last name, email, profile picture, language and — only if you allow it on the provider\'s screen — date of birth, gender and city. We use them only to fill in the fields of your account that are still empty, never over what you wrote.'**
  String get privacy_social_cosa;

  /// No description provided for @privacy_social_perche.
  ///
  /// In en, this message translates to:
  /// **'Why: the date of birth gives your personal cards (soul card and year card) and gender is used for pronouns and agreement in readings about two people; name, language and picture save you retyping them. Legal basis: the service you ask for, and your choice on the provider\'s screen.'**
  String get privacy_social_perche;

  /// No description provided for @privacy_social_posizione.
  ///
  /// In en, this message translates to:
  /// **'Current location: country and city, from the social if it shares them, otherwise estimated at each sign-in from your IP address with a database kept on our server (the address is not stored and nothing is sent to third parties). It helps us adapt the service.'**
  String get privacy_social_posizione;

  /// No description provided for @privacy_social_controllo.
  ///
  /// In en, this message translates to:
  /// **'From your account you see where each detail comes from, correct or delete it, stop the import or the location, or delete in one go everything that came from socials. Linked socials are managed from your account settings (“Linked accounts”).'**
  String get privacy_social_controllo;

  /// No description provided for @privacy_social_cta.
  ///
  /// In en, this message translates to:
  /// **'Manage your details'**
  String get privacy_social_cta;

  /// No description provided for @privacy_responsabili_titolo.
  ///
  /// In en, this message translates to:
  /// **'Who else handles your data, and where'**
  String get privacy_responsabili_titolo;

  /// No description provided for @privacy_responsabili_intro.
  ///
  /// In en, this message translates to:
  /// **'We do not sell your data and do not share it with partners. These providers process it on our behalf, or as independent controllers when you choose to use them:'**
  String get privacy_responsabili_intro;

  /// No description provided for @privacy_responsabili_0_chi.
  ///
  /// In en, this message translates to:
  /// **'Hosting'**
  String get privacy_responsabili_0_chi;

  /// No description provided for @privacy_responsabili_0_cosa.
  ///
  /// In en, this message translates to:
  /// **'our server and database. Provider and location: {hosting}.'**
  String privacy_responsabili_0_cosa(Object hosting);

  /// No description provided for @privacy_responsabili_1_chi.
  ///
  /// In en, this message translates to:
  /// **'AI providers'**
  String get privacy_responsabili_1_chi;

  /// No description provided for @privacy_responsabili_1_cosa.
  ///
  /// In en, this message translates to:
  /// **'the language-model providers we configure receive the text of your question, interview and chat — with names replaced by a placeholder and never the surname — only to write the reading. Current providers and countries: {fornitori_ai}.'**
  String privacy_responsabili_1_cosa(Object fornitori_ai);

  /// No description provided for @privacy_responsabili_2_chi.
  ///
  /// In en, this message translates to:
  /// **'Google'**
  String get privacy_responsabili_2_chi;

  /// No description provided for @privacy_responsabili_2_cosa.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics and AdSense (only with your consent) and sign-in with Google (Google Ireland Ltd., data may go to the United States).'**
  String get privacy_responsabili_2_cosa;

  /// No description provided for @privacy_responsabili_3_chi.
  ///
  /// In en, this message translates to:
  /// **'Sign-in providers'**
  String get privacy_responsabili_3_chi;

  /// No description provided for @privacy_responsabili_3_cosa.
  ///
  /// In en, this message translates to:
  /// **'Apple, Facebook (Meta), GitHub and LinkedIn, only if you choose to sign in with them: they are independent controllers of your account with them.'**
  String get privacy_responsabili_3_cosa;

  /// No description provided for @privacy_responsabili_4_chi.
  ///
  /// In en, this message translates to:
  /// **'Payments'**
  String get privacy_responsabili_4_chi;

  /// No description provided for @privacy_responsabili_4_cosa.
  ///
  /// In en, this message translates to:
  /// **'Stripe, for card payments (Stripe Payments Europe, data may go to the United States). We never see your card number.'**
  String get privacy_responsabili_4_cosa;

  /// No description provided for @privacy_responsabili_5_chi.
  ///
  /// In en, this message translates to:
  /// **'App notifications'**
  String get privacy_responsabili_5_chi;

  /// No description provided for @privacy_responsabili_5_cosa.
  ///
  /// In en, this message translates to:
  /// **'Firebase Cloud Messaging (Google), for the app notifications, when they arrive.'**
  String get privacy_responsabili_5_cosa;

  /// No description provided for @privacy_responsabili_6_chi.
  ///
  /// In en, this message translates to:
  /// **'Email and backups'**
  String get privacy_responsabili_6_chi;

  /// No description provided for @privacy_responsabili_6_cosa.
  ///
  /// In en, this message translates to:
  /// **'mail you write to an @tarots.chat address goes through Namecheap\'s forwarding service (United States) and lands in a Gmail mailbox of the data controller (Google); the emails we send you leave from our own server, hosted by Hivelocity in London; backups are kept in our own storage in Italy, with no third parties.'**
  String get privacy_responsabili_6_cosa;

  /// No description provided for @privacy_hosting_vuoto.
  ///
  /// In en, this message translates to:
  /// **'a provider bound by a data processing agreement'**
  String get privacy_hosting_vuoto;

  /// No description provided for @privacy_fornitori_ai_vuoto.
  ///
  /// In en, this message translates to:
  /// **'none active at the moment'**
  String get privacy_fornitori_ai_vuoto;

  /// No description provided for @privacy_fornitori_ai_proprio.
  ///
  /// In en, this message translates to:
  /// **'on our own server, no third party'**
  String get privacy_fornitori_ai_proprio;

  /// No description provided for @privacy_trasferimenti.
  ///
  /// In en, this message translates to:
  /// **'When data leaves the European Economic Area we rely on an adequacy decision of the European Commission (the United Kingdom; the United States for companies certified under the EU-US Data Privacy Framework) or on the Commission\'s standard contractual clauses.'**
  String get privacy_trasferimenti;

  /// No description provided for @privacy_conservazione_titolo.
  ///
  /// In en, this message translates to:
  /// **'How long we keep it'**
  String get privacy_conservazione_titolo;

  /// No description provided for @privacy_conservazione_0.
  ///
  /// In en, this message translates to:
  /// **'Account, readings, memory and chat: until you delete them or your account. There is no automatic expiry: we may also delete old data ourselves, for example free readings without an account and old chats.'**
  String get privacy_conservazione_0;

  /// No description provided for @privacy_conservazione_1.
  ///
  /// In en, this message translates to:
  /// **'The free reading without an account: until we delete it; if you sign up, it becomes part of your account.'**
  String get privacy_conservazione_1;

  /// No description provided for @privacy_conservazione_2.
  ///
  /// In en, this message translates to:
  /// **'Detailed visit statistics: 25 months, then only anonymous daily totals.'**
  String get privacy_conservazione_2;

  /// No description provided for @privacy_conservazione_3.
  ///
  /// In en, this message translates to:
  /// **'Your consent choices: as long as we need to prove them.'**
  String get privacy_conservazione_3;

  /// No description provided for @privacy_conservazione_4.
  ///
  /// In en, this message translates to:
  /// **'Accounting records (payments, credits, orders): as long as the law requires (in Italy, ten years). If you delete your account, they stay detached from your identity.'**
  String get privacy_conservazione_4;

  /// No description provided for @privacy_conservazione_5.
  ///
  /// In en, this message translates to:
  /// **'Backups: deleted data disappears from the backups as they rotate, within about a week.'**
  String get privacy_conservazione_5;

  /// No description provided for @privacy_diritti_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your rights'**
  String get privacy_diritti_titolo;

  /// No description provided for @privacy_diritti_testo.
  ///
  /// In en, this message translates to:
  /// **'You can ask to access your data, correct it, delete it, receive it in a portable format, restrict its use or object to it, and withdraw any consent at any time — without affecting what was done before.'**
  String get privacy_diritti_testo;

  /// No description provided for @privacy_diritti_come.
  ///
  /// In en, this message translates to:
  /// **'Most of it you can do yourself: download your data and delete your account from your account page, and change every consent there or on this page. For anything else, write to the privacy contact above: we answer within one month.'**
  String get privacy_diritti_come;

  /// No description provided for @privacy_diritti_cta_dati.
  ///
  /// In en, this message translates to:
  /// **'Your data and consents'**
  String get privacy_diritti_cta_dati;

  /// No description provided for @privacy_diritti_cta_elimina.
  ///
  /// In en, this message translates to:
  /// **'Delete your account'**
  String get privacy_diritti_cta_elimina;

  /// No description provided for @privacy_garante_titolo.
  ///
  /// In en, this message translates to:
  /// **'Complaints'**
  String get privacy_garante_titolo;

  /// No description provided for @privacy_garante_testo.
  ///
  /// In en, this message translates to:
  /// **'If you think your data is processed unlawfully, you can complain to the Italian data protection authority (Garante per la protezione dei dati personali, www.garanteprivacy.it) or to the authority of the country where you live or work.'**
  String get privacy_garante_testo;

  /// No description provided for @privacy_eta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Minimum age'**
  String get privacy_eta_titolo;

  /// No description provided for @privacy_eta_testo.
  ///
  /// In en, this message translates to:
  /// **'TAROTS chat is for people aged 16 or over; 14 in Italy and Spain, 15 in France — the age at which the law lets you use online services on your own. We ask you to confirm it before the first reading. If the date of birth in your account is below the minimum, readings and chat stop.'**
  String get privacy_eta_testo;

  /// No description provided for @privacy_versione.
  ///
  /// In en, this message translates to:
  /// **'Version 3 — 3 October 2026.'**
  String get privacy_versione;

  /// No description provided for @abbonamento_banner_etichetta.
  ///
  /// In en, this message translates to:
  /// **'Free trial'**
  String get abbonamento_banner_etichetta;

  /// No description provided for @abbonamento_banner_titolo.
  ///
  /// In en, this message translates to:
  /// **'{giorni} days of included readings, free. Then −{sconto}% for life.'**
  String abbonamento_banner_titolo(Object giorni, Object sconto);

  /// No description provided for @abbonamento_banner_testo.
  ///
  /// In en, this message translates to:
  /// **'When the trial ends it becomes a yearly plan at {sconto}% off, for as long as you stay. Cancel from your profile before then and you pay nothing.'**
  String abbonamento_banner_testo(Object sconto);

  /// No description provided for @abbonamento_banner_cta.
  ///
  /// In en, this message translates to:
  /// **'Try it free for {giorni} days'**
  String abbonamento_banner_cta(Object giorni);

  /// No description provided for @abbonamento_banner_chiudi.
  ///
  /// In en, this message translates to:
  /// **'Hide the trial offer'**
  String get abbonamento_banner_chiudi;

  /// No description provided for @abbonamento_prova_meta_titolo.
  ///
  /// In en, this message translates to:
  /// **'Free trial: {giorni} days, then −{sconto}% for life'**
  String abbonamento_prova_meta_titolo(Object giorni, Object sconto);

  /// No description provided for @abbonamento_prova_meta_descrizione.
  ///
  /// In en, this message translates to:
  /// **'Try a TAROTS chat subscription free for {giorni} days. Then a yearly plan at {sconto}% off, for as long as you stay. Cancel anytime before it ends and pay nothing.'**
  String abbonamento_prova_meta_descrizione(Object giorni, Object sconto);

  /// No description provided for @abbonamento_prova_eyebrow.
  ///
  /// In en, this message translates to:
  /// **'Free trial'**
  String get abbonamento_prova_eyebrow;

  /// No description provided for @abbonamento_prova_titolo.
  ///
  /// In en, this message translates to:
  /// **'{giorni} days to read with us. Free.'**
  String abbonamento_prova_titolo(Object giorni);

  /// No description provided for @abbonamento_prova_intro.
  ///
  /// In en, this message translates to:
  /// **'Every included reading of the plan you choose, with memory and follow-up, for {giorni} days. If you stay, you keep a price no one else gets: −{sconto}% on the yearly plan, for life.'**
  String abbonamento_prova_intro(Object giorni, Object sconto);

  /// No description provided for @abbonamento_prova_vantaggio_titolo.
  ///
  /// In en, this message translates to:
  /// **'−{sconto}% for life'**
  String abbonamento_prova_vantaggio_titolo(Object sconto);

  /// No description provided for @abbonamento_prova_vantaggio_testo.
  ///
  /// In en, this message translates to:
  /// **'Not a first-year discount: the yearly price after your trial stays {sconto}% lower at every renewal, for as long as your subscription stays active.'**
  String abbonamento_prova_vantaggio_testo(Object sconto);

  /// No description provided for @abbonamento_prova_come_titolo.
  ///
  /// In en, this message translates to:
  /// **'How it works, step by step'**
  String get abbonamento_prova_come_titolo;

  /// No description provided for @abbonamento_prova_passo_oggi.
  ///
  /// In en, this message translates to:
  /// **'Today: {zero}. You register a payment method with Stripe; nothing is charged.'**
  String abbonamento_prova_passo_oggi(Object zero);

  /// No description provided for @abbonamento_prova_passo_promemoria.
  ///
  /// In en, this message translates to:
  /// **'{giorni_promemoria} days before the end we email you a reminder with the date and the amount.'**
  String abbonamento_prova_passo_promemoria(Object giorni_promemoria);

  /// No description provided for @abbonamento_prova_passo_fine.
  ///
  /// In en, this message translates to:
  /// **'On day {giorni}: the trial becomes a yearly plan at {sconto}% off, and the card is charged then — not before.'**
  String abbonamento_prova_passo_fine(Object giorni, Object sconto);

  /// No description provided for @abbonamento_prova_passo_disdici.
  ///
  /// In en, this message translates to:
  /// **'To cancel: Profile → Subscription → Automatic renewal. Cancel during the trial and you pay nothing; the trial still runs to the end.'**
  String get abbonamento_prova_passo_disdici;

  /// No description provided for @abbonamento_prova_scegli.
  ///
  /// In en, this message translates to:
  /// **'Choose your level'**
  String get abbonamento_prova_scegli;

  /// No description provided for @abbonamento_prova_listino.
  ///
  /// In en, this message translates to:
  /// **'Yearly list price'**
  String get abbonamento_prova_listino;

  /// No description provided for @abbonamento_prova_dopo.
  ///
  /// In en, this message translates to:
  /// **'After the trial, every year'**
  String get abbonamento_prova_dopo;

  /// No description provided for @abbonamento_prova_cta.
  ///
  /// In en, this message translates to:
  /// **'Start the trial with {piano}'**
  String abbonamento_prova_cta(Object piano);

  /// No description provided for @abbonamento_prova_entra.
  ///
  /// In en, this message translates to:
  /// **'Create a free account to start'**
  String get abbonamento_prova_entra;

  /// No description provided for @abbonamento_prova_entra_testo.
  ///
  /// In en, this message translates to:
  /// **'The trial needs an account: it takes a moment, and you come right back here.'**
  String get abbonamento_prova_entra_testo;

  /// No description provided for @abbonamento_prova_non_idonea.
  ///
  /// In en, this message translates to:
  /// **'The free trial is one per person, and your account has already used it (or already has a subscription). The subscriptions are on the pricing page.'**
  String get abbonamento_prova_non_idonea;

  /// No description provided for @abbonamento_prova_non_disponibile.
  ///
  /// In en, this message translates to:
  /// **'The free trial is not available right now.'**
  String get abbonamento_prova_non_disponibile;

  /// No description provided for @abbonamento_prova_vai_prezzi.
  ///
  /// In en, this message translates to:
  /// **'See the subscriptions'**
  String get abbonamento_prova_vai_prezzi;

  /// No description provided for @abbonamento_prova_attivata.
  ///
  /// In en, this message translates to:
  /// **'Your trial has started: enjoy your readings. You\'ll find the date and the renewal in your profile.'**
  String get abbonamento_prova_attivata;

  /// No description provided for @abbonamento_prova_rifiutata.
  ///
  /// In en, this message translates to:
  /// **'This card has already had a free trial, so we closed the new one without charging anything. You can subscribe normally from the pricing page.'**
  String get abbonamento_prova_rifiutata;

  /// No description provided for @abbonamento_prova_onesta.
  ///
  /// In en, this message translates to:
  /// **'One trial per person and per card. The price is shown before you confirm, and the reminder arrives before any charge.'**
  String get abbonamento_prova_onesta;

  /// No description provided for @abbonamento_limite_titolo_letture_al_giorno.
  ///
  /// In en, this message translates to:
  /// **'You\'ve used today\'s readings'**
  String get abbonamento_limite_titolo_letture_al_giorno;

  /// No description provided for @abbonamento_limite_titolo_letture_alla_settimana.
  ///
  /// In en, this message translates to:
  /// **'You\'ve used this week\'s readings'**
  String get abbonamento_limite_titolo_letture_alla_settimana;

  /// No description provided for @abbonamento_limite_titolo_letture_al_mese.
  ///
  /// In en, this message translates to:
  /// **'You\'ve used this month\'s readings'**
  String get abbonamento_limite_titolo_letture_al_mese;

  /// No description provided for @abbonamento_limite_titolo_letture_totali.
  ///
  /// In en, this message translates to:
  /// **'You\'ve used the readings of this period'**
  String get abbonamento_limite_titolo_letture_totali;

  /// No description provided for @abbonamento_limite_periodo_letture_al_giorno.
  ///
  /// In en, this message translates to:
  /// **'in the last 24 hours'**
  String get abbonamento_limite_periodo_letture_al_giorno;

  /// No description provided for @abbonamento_limite_periodo_letture_alla_settimana.
  ///
  /// In en, this message translates to:
  /// **'in the last 7 days'**
  String get abbonamento_limite_periodo_letture_alla_settimana;

  /// No description provided for @abbonamento_limite_periodo_letture_al_mese.
  ///
  /// In en, this message translates to:
  /// **'in the last 30 days'**
  String get abbonamento_limite_periodo_letture_al_mese;

  /// No description provided for @abbonamento_limite_periodo_letture_totali.
  ///
  /// In en, this message translates to:
  /// **'in this paid period'**
  String get abbonamento_limite_periodo_letture_totali;

  /// No description provided for @abbonamento_limite_testo.
  ///
  /// In en, this message translates to:
  /// **'Your subscription includes {valore} readings {periodo}. Readings done {periodo}: {fatte}.'**
  String abbonamento_limite_testo(Object valore, Object periodo, Object fatte);

  /// No description provided for @abbonamento_limite_si_libera.
  ///
  /// In en, this message translates to:
  /// **'The next included reading frees up on {data}.'**
  String abbonamento_limite_si_libera(Object data);

  /// No description provided for @abbonamento_condono_titolo.
  ///
  /// In en, this message translates to:
  /// **'This one is on us'**
  String get abbonamento_condono_titolo;

  /// No description provided for @abbonamento_condono_testo.
  ///
  /// In en, this message translates to:
  /// **'For the people we care about, the first readings beyond the limit are a permission agreed in advance: this reading is a gift and uses no credits. Gifts left in this period after this one: {rimasti}.'**
  String abbonamento_condono_testo(Object rimasti);

  /// No description provided for @abbonamento_condono_cta.
  ///
  /// In en, this message translates to:
  /// **'Continue with the gift reading'**
  String get abbonamento_condono_cta;

  /// No description provided for @abbonamento_credito_domanda.
  ///
  /// In en, this message translates to:
  /// **'Would you like to use 1 credit for this reading? Your balance: {saldo}. Credits never expire.'**
  String abbonamento_credito_domanda(Object saldo);

  /// No description provided for @abbonamento_credito_cta.
  ///
  /// In en, this message translates to:
  /// **'Use 1 credit'**
  String get abbonamento_credito_cta;

  /// No description provided for @abbonamento_acquisto_testo.
  ///
  /// In en, this message translates to:
  /// **'You have no credits left. You can buy a package — credits never expire — or wait for the next included reading.'**
  String get abbonamento_acquisto_testo;

  /// No description provided for @abbonamento_acquisto_cta.
  ///
  /// In en, this message translates to:
  /// **'See the packages'**
  String get abbonamento_acquisto_cta;

  /// No description provided for @abbonamento_non_ora.
  ///
  /// In en, this message translates to:
  /// **'Not now'**
  String get abbonamento_non_ora;

  /// No description provided for @abbonamento_sezione_titolo.
  ///
  /// In en, this message translates to:
  /// **'Subscription'**
  String get abbonamento_sezione_titolo;

  /// No description provided for @abbonamento_nessuno.
  ///
  /// In en, this message translates to:
  /// **'You don\'t have a subscription. Single readings are paid with credits, which never expire.'**
  String get abbonamento_nessuno;

  /// No description provided for @abbonamento_vedi_piani.
  ///
  /// In en, this message translates to:
  /// **'See the plans'**
  String get abbonamento_vedi_piani;

  /// No description provided for @abbonamento_prova_cta_profilo.
  ///
  /// In en, this message translates to:
  /// **'Try a subscription free for {giorni} days'**
  String abbonamento_prova_cta_profilo(Object giorni);

  /// No description provided for @abbonamento_stato_attivo.
  ///
  /// In en, this message translates to:
  /// **'Active'**
  String get abbonamento_stato_attivo;

  /// No description provided for @abbonamento_stato_in_prova.
  ///
  /// In en, this message translates to:
  /// **'Free trial'**
  String get abbonamento_stato_in_prova;

  /// No description provided for @abbonamento_stato_in_sospeso.
  ///
  /// In en, this message translates to:
  /// **'Payment pending'**
  String get abbonamento_stato_in_sospeso;

  /// No description provided for @abbonamento_stato_sospeso.
  ///
  /// In en, this message translates to:
  /// **'Paused'**
  String get abbonamento_stato_sospeso;

  /// No description provided for @abbonamento_stato_disdetto.
  ///
  /// In en, this message translates to:
  /// **'Ended'**
  String get abbonamento_stato_disdetto;

  /// No description provided for @abbonamento_stato_scaduto.
  ///
  /// In en, this message translates to:
  /// **'Expired'**
  String get abbonamento_stato_scaduto;

  /// No description provided for @abbonamento_mensile.
  ///
  /// In en, this message translates to:
  /// **'monthly'**
  String get abbonamento_mensile;

  /// No description provided for @abbonamento_annuale.
  ///
  /// In en, this message translates to:
  /// **'yearly'**
  String get abbonamento_annuale;

  /// No description provided for @abbonamento_periodo_fino.
  ///
  /// In en, this message translates to:
  /// **'Paid period until {data}'**
  String abbonamento_periodo_fino(Object data);

  /// No description provided for @abbonamento_prova_fino.
  ///
  /// In en, this message translates to:
  /// **'Free trial until {data}. Then {importo} a year (−{sconto}% for life).'**
  String abbonamento_prova_fino(Object data, Object importo, Object sconto);

  /// No description provided for @abbonamento_rinnovo_titolo.
  ///
  /// In en, this message translates to:
  /// **'Automatic renewal'**
  String get abbonamento_rinnovo_titolo;

  /// No description provided for @abbonamento_rinnovo_acceso.
  ///
  /// In en, this message translates to:
  /// **'On: it renews on {data} for {importo}.'**
  String abbonamento_rinnovo_acceso(Object data, Object importo);

  /// No description provided for @abbonamento_rinnovo_acceso_sconto.
  ///
  /// In en, this message translates to:
  /// **'Includes the automatic-renewal discount.'**
  String get abbonamento_rinnovo_acceso_sconto;

  /// No description provided for @abbonamento_coupon_rinnovi.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{Code {codice} discount: 1 more renewal.} other{Code {codice} discount: {n} more renewals.}}'**
  String abbonamento_coupon_rinnovi(int n, Object codice);

  /// No description provided for @abbonamento_coupon_sempre.
  ///
  /// In en, this message translates to:
  /// **'Code {codice} discount: on every renewal.'**
  String abbonamento_coupon_sempre(Object codice);

  /// No description provided for @abbonamento_rinnovo_spento.
  ///
  /// In en, this message translates to:
  /// **'Off: your subscription stays active until {data}, then it ends. You can turn renewal back on until that day.'**
  String abbonamento_rinnovo_spento(Object data);

  /// No description provided for @abbonamento_rinnovo_interruttore.
  ///
  /// In en, this message translates to:
  /// **'Renew automatically'**
  String get abbonamento_rinnovo_interruttore;

  /// No description provided for @abbonamento_conferma_titolo.
  ///
  /// In en, this message translates to:
  /// **'Turn off automatic renewal?'**
  String get abbonamento_conferma_titolo;

  /// No description provided for @abbonamento_conferma_testo.
  ///
  /// In en, this message translates to:
  /// **'Please confirm that you want to turn off the automatic renewal of your {piano} subscription. It stays active until {data}, with all its included readings. After that date nothing will be charged, and the automatic-renewal discount will no longer apply to a new purchase. We will send you a confirmation email.'**
  String abbonamento_conferma_testo(Object piano, Object data);

  /// No description provided for @abbonamento_conferma_si.
  ///
  /// In en, this message translates to:
  /// **'Yes, turn off renewal'**
  String get abbonamento_conferma_si;

  /// No description provided for @abbonamento_conferma_no.
  ///
  /// In en, this message translates to:
  /// **'Keep renewal on'**
  String get abbonamento_conferma_no;

  /// No description provided for @abbonamento_spento_ok.
  ///
  /// In en, this message translates to:
  /// **'Automatic renewal is off. We\'ve sent you a confirmation email.'**
  String get abbonamento_spento_ok;

  /// No description provided for @abbonamento_acceso_ok.
  ///
  /// In en, this message translates to:
  /// **'Automatic renewal is on again.'**
  String get abbonamento_acceso_ok;

  /// No description provided for @abbonamento_cambia_piano.
  ///
  /// In en, this message translates to:
  /// **'Change plan'**
  String get abbonamento_cambia_piano;

  /// No description provided for @abbonamento_successivo.
  ///
  /// In en, this message translates to:
  /// **'From {data} you\'ll switch to {piano} ({periodo}).'**
  String abbonamento_successivo(Object data, Object piano, Object periodo);

  /// No description provided for @abbonamento_annulla_successivo.
  ///
  /// In en, this message translates to:
  /// **'Cancel the change'**
  String get abbonamento_annulla_successivo;

  /// No description provided for @abbonamento_tolleranza.
  ///
  /// In en, this message translates to:
  /// **'The renewal payment didn\'t go through. Your included readings stay active until {data}: settle the open invoice to keep them.'**
  String abbonamento_tolleranza(Object data);

  /// No description provided for @abbonamento_sospeso_testo.
  ///
  /// In en, this message translates to:
  /// **'Your subscription is paused because the payment didn\'t arrive. Pay the open invoice and everything starts again at once.'**
  String get abbonamento_sospeso_testo;

  /// No description provided for @abbonamento_sistema.
  ///
  /// In en, this message translates to:
  /// **'Fix the payment'**
  String get abbonamento_sistema;

  /// No description provided for @abbonamento_sistema_nota.
  ///
  /// In en, this message translates to:
  /// **'You\'ll pay the same invoice that is already open: paying it stops the automatic retries, so you\'re never charged twice.'**
  String get abbonamento_sistema_nota;

  /// No description provided for @abbonamento_sistema_pagata.
  ///
  /// In en, this message translates to:
  /// **'That invoice is no longer open: the payment has arrived or is on its way. Reload in a minute.'**
  String get abbonamento_sistema_pagata;

  /// No description provided for @abbonamento_store_testo.
  ///
  /// In en, this message translates to:
  /// **'This subscription was bought on {store}: renewal, plan changes and payments are managed there, and {store} calculates any balance.'**
  String abbonamento_store_testo(Object store);

  /// No description provided for @abbonamento_store_apri.
  ///
  /// In en, this message translates to:
  /// **'Open {store}'**
  String abbonamento_store_apri(Object store);

  /// No description provided for @abbonamento_store_google_play.
  ///
  /// In en, this message translates to:
  /// **'Google Play'**
  String get abbonamento_store_google_play;

  /// No description provided for @abbonamento_store_app_store.
  ///
  /// In en, this message translates to:
  /// **'the App Store'**
  String get abbonamento_store_app_store;

  /// No description provided for @abbonamento_store_gestisci.
  ///
  /// In en, this message translates to:
  /// **'Manage in {store}'**
  String abbonamento_store_gestisci(Object store);

  /// No description provided for @abbonamento_store_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'Automatic renewal is on: {store} takes the next payment, at the store\'s price.'**
  String abbonamento_store_rinnovo(Object store);

  /// No description provided for @abbonamento_store_disdetto.
  ///
  /// In en, this message translates to:
  /// **'Automatic renewal is off: your subscription stays active until {data}, then it ends. You can turn it back on in {store}.'**
  String abbonamento_store_disdetto(Object data, Object store);

  /// No description provided for @abbonamento_store_tolleranza.
  ///
  /// In en, this message translates to:
  /// **'The renewal payment didn\'t go through: {store} is trying again by itself, and meanwhile your included readings stay active. Update your payment method in {store}.'**
  String abbonamento_store_tolleranza(Object store);

  /// No description provided for @abbonamento_store_sospeso.
  ///
  /// In en, this message translates to:
  /// **'Your subscription is paused because {store} couldn\'t collect the renewal. Update your payment method in {store}: as soon as the payment goes through, everything starts again by itself.'**
  String abbonamento_store_sospeso(Object store);

  /// No description provided for @abbonamento_store_nota.
  ///
  /// In en, this message translates to:
  /// **'Cancelling, changing plan and the payment method are handled there: there are no buttons for them here, because {store} collects the payment.'**
  String abbonamento_store_nota(Object store);

  /// No description provided for @abbonamento_cambio_titolo.
  ///
  /// In en, this message translates to:
  /// **'Switch to {piano}'**
  String abbonamento_cambio_titolo(Object piano);

  /// No description provided for @abbonamento_cambio_residuo.
  ///
  /// In en, this message translates to:
  /// **'Remaining value of your subscription'**
  String get abbonamento_cambio_residuo;

  /// No description provided for @abbonamento_cambio_residuo_nota.
  ///
  /// In en, this message translates to:
  /// **'{rimasti} days left out of {totale}, on {pagato} paid'**
  String abbonamento_cambio_residuo_nota(Object rimasti, Object totale, Object pagato);

  /// No description provided for @abbonamento_cambio_nuovo_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'New subscription with renewal discount'**
  String get abbonamento_cambio_nuovo_rinnovo;

  /// No description provided for @abbonamento_cambio_nuovo.
  ///
  /// In en, this message translates to:
  /// **'New subscription'**
  String get abbonamento_cambio_nuovo;

  /// No description provided for @abbonamento_cambio_nuovo_nota.
  ///
  /// In en, this message translates to:
  /// **'list price {listino} − {sconto}% for automatic renewal'**
  String abbonamento_cambio_nuovo_nota(Object listino, Object sconto);

  /// No description provided for @abbonamento_cambio_totale.
  ///
  /// In en, this message translates to:
  /// **'Total to pay'**
  String get abbonamento_cambio_totale;

  /// No description provided for @abbonamento_cambio_subito.
  ///
  /// In en, this message translates to:
  /// **'The new period starts today. Your current subscription closes with no further charges.'**
  String get abbonamento_cambio_subito;

  /// No description provided for @abbonamento_cambio_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'Automatic renewal (−{sconto}%)'**
  String abbonamento_cambio_rinnovo(Object sconto);

  /// No description provided for @abbonamento_cambio_paga.
  ///
  /// In en, this message translates to:
  /// **'Pay {importo}'**
  String abbonamento_cambio_paga(Object importo);

  /// No description provided for @abbonamento_cambio_downgrade.
  ///
  /// In en, this message translates to:
  /// **'The change starts on {data}, at the end of the period you\'ve already paid. From that day you\'ll pay {importo}.'**
  String abbonamento_cambio_downgrade(Object data, Object importo);

  /// No description provided for @abbonamento_cambio_programma.
  ///
  /// In en, this message translates to:
  /// **'Schedule the change'**
  String get abbonamento_cambio_programma;

  /// No description provided for @abbonamento_cambio_programmato.
  ///
  /// In en, this message translates to:
  /// **'Done: the change is scheduled for {data}.'**
  String abbonamento_cambio_programmato(Object data);

  /// No description provided for @abbonamento_cambio_zero.
  ///
  /// In en, this message translates to:
  /// **'Nothing to pay: the remaining value covers the new subscription.'**
  String get abbonamento_cambio_zero;

  /// No description provided for @abbonamento_periodo_mensile.
  ///
  /// In en, this message translates to:
  /// **'Monthly'**
  String get abbonamento_periodo_mensile;

  /// No description provided for @abbonamento_periodo_annuale.
  ///
  /// In en, this message translates to:
  /// **'Yearly'**
  String get abbonamento_periodo_annuale;

  /// No description provided for @abbonamento_scegli_periodo.
  ///
  /// In en, this message translates to:
  /// **'Billing period'**
  String get abbonamento_scegli_periodo;

  /// No description provided for @abbonamento_rinnovo_prezzi.
  ///
  /// In en, this message translates to:
  /// **'Automatic renewal'**
  String get abbonamento_rinnovo_prezzi;

  /// No description provided for @abbonamento_rinnovo_prezzi_testo.
  ///
  /// In en, this message translates to:
  /// **'On: −{sconto}% on every renewal, and you can turn it off whenever you like. Off: list price, one period only.'**
  String abbonamento_rinnovo_prezzi_testo(Object sconto);

  /// No description provided for @abbonamento_con_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'with automatic renewal'**
  String get abbonamento_con_rinnovo;

  /// No description provided for @abbonamento_senza_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'without renewal: {prezzo}'**
  String abbonamento_senza_rinnovo(Object prezzo);

  /// No description provided for @abbonamento_badge_rinnovo.
  ///
  /// In en, this message translates to:
  /// **'−{sconto}% with renewal'**
  String abbonamento_badge_rinnovo(Object sconto);

  /// No description provided for @abbonamento_al_anno.
  ///
  /// In en, this message translates to:
  /// **'/ year'**
  String get abbonamento_al_anno;

  /// No description provided for @abbonamento_passa.
  ///
  /// In en, this message translates to:
  /// **'Switch to this plan'**
  String get abbonamento_passa;

  /// No description provided for @abbonamento_prova_banda_titolo.
  ///
  /// In en, this message translates to:
  /// **'Not sure yet? Try it free for {giorni} days.'**
  String abbonamento_prova_banda_titolo(Object giorni);

  /// No description provided for @abbonamento_prova_banda_testo.
  ///
  /// In en, this message translates to:
  /// **'Then the yearly plan at −{sconto}% for life. Cancel before the end and pay nothing.'**
  String abbonamento_prova_banda_testo(Object sconto);

  /// No description provided for @abbonamento_prova_banda_cta.
  ///
  /// In en, this message translates to:
  /// **'Discover the free trial'**
  String get abbonamento_prova_banda_cta;

  /// No description provided for @app_consensi_titolo.
  ///
  /// In en, this message translates to:
  /// **'Privacy and your data'**
  String get app_consensi_titolo;

  /// No description provided for @app_consensi_testo.
  ///
  /// In en, this message translates to:
  /// **'Technical data on this device keeps the app working and needs no consent. Everything else stays off until you turn it on: accept all, reject all, or choose one by one. You can change your mind at any time in your profile.'**
  String get app_consensi_testo;

  /// No description provided for @app_consenso_statistiche.
  ///
  /// In en, this message translates to:
  /// **'App statistics'**
  String get app_consenso_statistiche;

  /// No description provided for @app_consenso_statistiche_testo.
  ///
  /// In en, this message translates to:
  /// **'A random identifier recognises this device when you come back. It stays with us, never with third parties.'**
  String get app_consenso_statistiche_testo;

  /// No description provided for @app_consenso_google.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics'**
  String get app_consenso_google;

  /// No description provided for @app_consenso_google_testo.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics for Firebase (Google Ireland) measures how the app is used, with an identifier stored on the device; data may go to the United States.'**
  String get app_consenso_google_testo;

  /// No description provided for @app_consenso_tecnici.
  ///
  /// In en, this message translates to:
  /// **'Technical data on the device (signing in, the free reading, these choices) is always kept: without it the app does not work.'**
  String get app_consenso_tecnici;

  /// No description provided for @app_cons_statistiche_testo.
  ///
  /// In en, this message translates to:
  /// **'A random identifier recognises this device when you come back. Turning it off makes our servers forget it.'**
  String get app_cons_statistiche_testo;

  /// No description provided for @app_cons_google_testo.
  ///
  /// In en, this message translates to:
  /// **'Google Analytics for Firebase measures how the app is used. Turning it off stops it at once.'**
  String get app_cons_google_testo;

  /// No description provided for @app_scelte_titolo.
  ///
  /// In en, this message translates to:
  /// **'Your choices on this device'**
  String get app_scelte_titolo;

  /// No description provided for @app_scelte_testo.
  ///
  /// In en, this message translates to:
  /// **'Everything below is off until you turn it on, and you can change it here at any time. Technical data on the device (signing in, the anonymous free reading, remembering these choices) needs no consent: without it the app does not work.'**
  String get app_scelte_testo;

  /// No description provided for @app_gia_usata.
  ///
  /// In en, this message translates to:
  /// **'You have already used your free reading on this device. Create a free account to continue: it adds free readings to your story.'**
  String get app_gia_usata;

  /// No description provided for @app_pagamento_browser.
  ///
  /// In en, this message translates to:
  /// **'The payment page opens in your browser. When you have finished, you come back here.'**
  String get app_pagamento_browser;

  /// No description provided for @app_pagamento_attesa.
  ///
  /// In en, this message translates to:
  /// **'Checking your payment…'**
  String get app_pagamento_attesa;

  /// No description provided for @app_pagamento_non_concluso.
  ///
  /// In en, this message translates to:
  /// **'The payment has not been completed. Nothing has been charged.'**
  String get app_pagamento_non_concluso;

  /// No description provided for @app_video_apri.
  ///
  /// In en, this message translates to:
  /// **'Watch the video on {fonte}'**
  String app_video_apri(Object fonte);

  /// No description provided for @app_file_pronto.
  ///
  /// In en, this message translates to:
  /// **'Your file is ready: choose where to save or send it.'**
  String get app_file_pronto;

  /// No description provided for @app_codice_titolo.
  ///
  /// In en, this message translates to:
  /// **'Already have an account on the website?'**
  String get app_codice_titolo;

  /// No description provided for @app_codice_testo.
  ///
  /// In en, this message translates to:
  /// **'If you already used TAROTS chat on the website with a different sign-in, the app may have created a new account. Create a code here and enter it in your profile on the website («Do you have a code from the app?») within 10 minutes: this sign-in moves to your account there, together with what you did in the app.'**
  String get app_codice_testo;

  /// No description provided for @app_codice_crea.
  ///
  /// In en, this message translates to:
  /// **'Create the code'**
  String get app_codice_crea;

  /// No description provided for @app_codice_valido.
  ///
  /// In en, this message translates to:
  /// **'Valid until {ora}. On the website: Profile → Sign-in methods → «Do you have a code from the app?».'**
  String app_codice_valido(Object ora);

  /// No description provided for @app_codice_nuovo.
  ///
  /// In en, this message translates to:
  /// **'Create a new code'**
  String get app_codice_nuovo;

  /// No description provided for @app_codice_relay.
  ///
  /// In en, this message translates to:
  /// **'You signed in with Apple and hid your email, so this is a new account. If you already have one on the website, move this sign-in there now.'**
  String get app_codice_relay;

  /// No description provided for @app_sessione_spostata_titolo.
  ///
  /// In en, this message translates to:
  /// **'Sign in again'**
  String get app_sessione_spostata_titolo;

  /// No description provided for @app_sessione_spostata.
  ///
  /// In en, this message translates to:
  /// **'Your session in the app has ended. If you entered the app\'s code on the website, your sign-in now leads to your account there: sign in again and you will find your story.'**
  String get app_sessione_spostata;

  /// No description provided for @app_sessione_entra.
  ///
  /// In en, this message translates to:
  /// **'Sign in again'**
  String get app_sessione_entra;

  /// No description provided for @app_store_nota.
  ///
  /// In en, this message translates to:
  /// **'You pay with {store}. Subscriptions renew on their own until you cancel them in {store}.'**
  String app_store_nota(Object store);

  /// No description provided for @app_store_non_disponibile.
  ///
  /// In en, this message translates to:
  /// **'Purchases with {store} aren\'t available on this device right now. Check that you\'re signed in to {store} and try again.'**
  String app_store_non_disponibile(Object store);

  /// No description provided for @app_store_ripristina.
  ///
  /// In en, this message translates to:
  /// **'Restore purchases'**
  String get app_store_ripristina;

  /// No description provided for @app_store_ripristinati.
  ///
  /// In en, this message translates to:
  /// **'Purchases restored.'**
  String get app_store_ripristinati;

  /// No description provided for @app_store_niente_da_ripristinare.
  ///
  /// In en, this message translates to:
  /// **'There was nothing to restore.'**
  String get app_store_niente_da_ripristinare;

  /// No description provided for @app_store_in_corso.
  ///
  /// In en, this message translates to:
  /// **'Checking your purchase…'**
  String get app_store_in_corso;

  /// No description provided for @app_store_in_attesa.
  ///
  /// In en, this message translates to:
  /// **'Your payment is pending: the credits arrive as soon as {store} confirms it. You can close the app in the meantime.'**
  String app_store_in_attesa(Object store);

  /// No description provided for @app_store_annullato.
  ///
  /// In en, this message translates to:
  /// **'Purchase cancelled: nothing was charged.'**
  String get app_store_annullato;

  /// No description provided for @app_store_err_account.
  ///
  /// In en, this message translates to:
  /// **'This purchase was made with another TAROTS chat account: sign in with the account you bought it with.'**
  String get app_store_err_account;

  /// No description provided for @app_store_err_registrazione.
  ///
  /// In en, this message translates to:
  /// **'We couldn\'t register this purchase yet. It\'s kept safe and we\'ll try again: if it doesn\'t show up within a day, write to us.'**
  String get app_store_err_registrazione;

  /// No description provided for @app_store_err_rete.
  ///
  /// In en, this message translates to:
  /// **'We can\'t reach our server to confirm the purchase. It\'s kept safe: we\'ll try again as soon as you\'re back online.'**
  String get app_store_err_rete;

  /// No description provided for @app_store_err_non_valido.
  ///
  /// In en, this message translates to:
  /// **'{store} didn\'t confirm this purchase. Nothing was added to your account.'**
  String app_store_err_non_valido(Object store);

  /// No description provided for @app_store_err_posseduto.
  ///
  /// In en, this message translates to:
  /// **'You already own this. Tap «Restore purchases».'**
  String get app_store_err_posseduto;

  /// No description provided for @app_store_err_generico.
  ///
  /// In en, this message translates to:
  /// **'The purchase didn\'t go through. Please try again.'**
  String get app_store_err_generico;

  /// No description provided for @app_store_carta.
  ///
  /// In en, this message translates to:
  /// **'Pay by card'**
  String get app_store_carta;

  /// No description provided for @app_store_carta_testo.
  ///
  /// In en, this message translates to:
  /// **'Card payments go through Stripe on our website, and you come back here when you\'re done.'**
  String get app_store_carta_testo;

  /// No description provided for @app_store_metodo.
  ///
  /// In en, this message translates to:
  /// **'How to pay'**
  String get app_store_metodo;

  /// No description provided for @app_store_codici.
  ///
  /// In en, this message translates to:
  /// **'Discount codes only apply to card payments; gift codes always work.'**
  String get app_store_codici;

  /// No description provided for @app_store_abbonamento_web.
  ///
  /// In en, this message translates to:
  /// **'Your current subscription wasn\'t bought with {store}. To switch to {store}, turn off its automatic renewal in your profile: you can subscribe here when it ends.'**
  String app_store_abbonamento_web(Object store);

  /// No description provided for @app_store_altro_store.
  ///
  /// In en, this message translates to:
  /// **'Your subscription is managed by {store}: change or cancel it there.'**
  String app_store_altro_store(Object store);

  /// No description provided for @app_push_stato_attive.
  ///
  /// In en, this message translates to:
  /// **'Notifications are on on this device.'**
  String get app_push_stato_attive;

  /// No description provided for @app_push_stato_spente.
  ///
  /// In en, this message translates to:
  /// **'Notifications are off on this device.'**
  String get app_push_stato_spente;

  /// No description provided for @app_push_attiva.
  ///
  /// In en, this message translates to:
  /// **'Turn on notifications here'**
  String get app_push_attiva;

  /// No description provided for @app_push_disattiva.
  ///
  /// In en, this message translates to:
  /// **'Turn off on this device'**
  String get app_push_disattiva;

  /// No description provided for @app_push_negato.
  ///
  /// In en, this message translates to:
  /// **'Notifications for TAROTS chat are turned off in your phone\'s settings. Turn them on there, then come back.'**
  String get app_push_negato;

  /// No description provided for @app_push_impostazioni.
  ///
  /// In en, this message translates to:
  /// **'Open settings'**
  String get app_push_impostazioni;

  /// No description provided for @app_push_non_disponibile.
  ///
  /// In en, this message translates to:
  /// **'Notifications aren\'t available in this version of the app yet.'**
  String get app_push_non_disponibile;

  /// No description provided for @app_canale_servizio.
  ///
  /// In en, this message translates to:
  /// **'Card of the day and reminders'**
  String get app_canale_servizio;

  /// No description provided for @app_canale_servizio_testo.
  ///
  /// In en, this message translates to:
  /// **'Your card of the day, your streak, the end of a trial, a payment to fix.'**
  String get app_canale_servizio_testo;

  /// No description provided for @app_canale_promozioni.
  ///
  /// In en, this message translates to:
  /// **'Offers and news'**
  String get app_canale_promozioni;

  /// No description provided for @app_canale_promozioni_testo.
  ///
  /// In en, this message translates to:
  /// **'Only if you turned on promotions in your privacy choices.'**
  String get app_canale_promozioni_testo;

  /// No description provided for @app_elimina_store.
  ///
  /// In en, this message translates to:
  /// **'A subscription bought with {store} doesn\'t stop on its own: cancel it in {store} so it isn\'t renewed.'**
  String app_elimina_store(Object store);

  /// No description provided for @app_lingua_titolo.
  ///
  /// In en, this message translates to:
  /// **'Reading language'**
  String get app_lingua_titolo;

  /// No description provided for @app_lingua_testo.
  ///
  /// In en, this message translates to:
  /// **'Articles, cards and spreads are written in English. Choose the language you want to read them in: your phone translates them by itself, without sending them anywhere. Every language except English needs a download of about 30 MB, only once.'**
  String get app_lingua_testo;

  /// No description provided for @app_lingua_cerca.
  ///
  /// In en, this message translates to:
  /// **'Search for a language'**
  String get app_lingua_cerca;

  /// No description provided for @app_lingua_continua.
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get app_lingua_continua;

  /// No description provided for @app_lingua_scarico.
  ///
  /// In en, this message translates to:
  /// **'Downloading {lingua}… it can take a minute.'**
  String app_lingua_scarico(Object lingua);

  /// No description provided for @app_lingua_errore.
  ///
  /// In en, this message translates to:
  /// **'The download didn\'t work (are you online?). The contents stay in English for now: we\'ll try again when you open them.'**
  String get app_lingua_errore;

  /// No description provided for @app_lingua_voce.
  ///
  /// In en, this message translates to:
  /// **'Reading language: {lingua}'**
  String app_lingua_voce(Object lingua);

  /// No description provided for @app_lingua_cambia.
  ///
  /// In en, this message translates to:
  /// **'Change'**
  String get app_lingua_cambia;

  /// No description provided for @notifiche_titolo.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notifiche_titolo;

  /// No description provided for @notifiche_intro.
  ///
  /// In en, this message translates to:
  /// **'A gentle reminder for your card of the day and, if you want them, a few other messages. You choose what and when.'**
  String get notifiche_intro;

  /// No description provided for @notifiche_stato_attive.
  ///
  /// In en, this message translates to:
  /// **'Notifications are on in this browser.'**
  String get notifiche_stato_attive;

  /// No description provided for @notifiche_stato_spente.
  ///
  /// In en, this message translates to:
  /// **'Notifications are off in this browser.'**
  String get notifiche_stato_spente;

  /// No description provided for @notifiche_attiva.
  ///
  /// In en, this message translates to:
  /// **'Turn on notifications here'**
  String get notifiche_attiva;

  /// No description provided for @notifiche_disattiva.
  ///
  /// In en, this message translates to:
  /// **'Turn off in this browser'**
  String get notifiche_disattiva;

  /// No description provided for @notifiche_attivazione.
  ///
  /// In en, this message translates to:
  /// **'Turning on…'**
  String get notifiche_attivazione;

  /// No description provided for @notifiche_negato.
  ///
  /// In en, this message translates to:
  /// **'Your browser is blocking notifications from this site. Allow them in the site settings (the padlock next to the address), then try again.'**
  String get notifiche_negato;

  /// No description provided for @notifiche_errore.
  ///
  /// In en, this message translates to:
  /// **'That didn\'t work. Please try again in a moment.'**
  String get notifiche_errore;

  /// No description provided for @notifiche_non_supportato.
  ///
  /// In en, this message translates to:
  /// **'This browser can\'t receive notifications from the site.'**
  String get notifiche_non_supportato;

  /// No description provided for @notifiche_ios_titolo.
  ///
  /// In en, this message translates to:
  /// **'On iPhone and iPad'**
  String get notifiche_ios_titolo;

  /// No description provided for @notifiche_ios_testo.
  ///
  /// In en, this message translates to:
  /// **'Safari shows notifications only from the site added to your Home Screen: tap Share, then “Add to Home Screen”, open TAROTS chat from the new icon and turn notifications on from your profile.'**
  String get notifiche_ios_testo;

  /// No description provided for @notifiche_altri.
  ///
  /// In en, this message translates to:
  /// **'{n, plural, =1{Notifications are also on for 1 other device.} other{Notifications are also on for {n} other devices.}}'**
  String notifiche_altri(int n);

  /// No description provided for @notifiche_carta.
  ///
  /// In en, this message translates to:
  /// **'Card of the day'**
  String get notifiche_carta;

  /// No description provided for @notifiche_carta_testo.
  ///
  /// In en, this message translates to:
  /// **'A reminder in the morning, if you haven\'t turned your card yet.'**
  String get notifiche_carta_testo;

  /// No description provided for @notifiche_ora.
  ///
  /// In en, this message translates to:
  /// **'Time'**
  String get notifiche_ora;

  /// No description provided for @notifiche_promemoria.
  ///
  /// In en, this message translates to:
  /// **'Reminders'**
  String get notifiche_promemoria;

  /// No description provided for @notifiche_promemoria_testo.
  ///
  /// In en, this message translates to:
  /// **'Your streak of days, the end of a trial, a payment to fix.'**
  String get notifiche_promemoria_testo;

  /// No description provided for @notifiche_promozioni.
  ///
  /// In en, this message translates to:
  /// **'Offers and news'**
  String get notifiche_promozioni;

  /// No description provided for @notifiche_promozioni_testo.
  ///
  /// In en, this message translates to:
  /// **'At most {n} a week. It\'s the same choice as “Promotions” in Privacy and consents.'**
  String notifiche_promozioni_testo(Object n);

  /// No description provided for @notifiche_silenzio.
  ///
  /// In en, this message translates to:
  /// **'Quiet hours'**
  String get notifiche_silenzio;

  /// No description provided for @notifiche_silenzio_testo.
  ///
  /// In en, this message translates to:
  /// **'No notifications between these times, at your local time.'**
  String get notifiche_silenzio_testo;

  /// No description provided for @notifiche_dalle.
  ///
  /// In en, this message translates to:
  /// **'From'**
  String get notifiche_dalle;

  /// No description provided for @notifiche_alle.
  ///
  /// In en, this message translates to:
  /// **'To'**
  String get notifiche_alle;

  /// No description provided for @notifiche_fuso.
  ///
  /// In en, this message translates to:
  /// **'Your time zone: {fuso}. It\'s updated automatically.'**
  String notifiche_fuso(Object fuso);

  /// No description provided for @notifiche_salvato.
  ///
  /// In en, this message translates to:
  /// **'Saved.'**
  String get notifiche_salvato;

  /// No description provided for @notifiche_invito_titolo.
  ///
  /// In en, this message translates to:
  /// **'Shall we remind you every morning?'**
  String get notifiche_invito_titolo;

  /// No description provided for @notifiche_invito_testo.
  ///
  /// In en, this message translates to:
  /// **'A quiet notification when your card of the day is ready. Only that, and you can turn it off whenever you like.'**
  String get notifiche_invito_testo;

  /// No description provided for @notifiche_invito_si.
  ///
  /// In en, this message translates to:
  /// **'Yes, remind me'**
  String get notifiche_invito_si;

  /// No description provided for @notifiche_invito_no.
  ///
  /// In en, this message translates to:
  /// **'Not now'**
  String get notifiche_invito_no;

  /// No description provided for @notifiche_invito_fatto.
  ///
  /// In en, this message translates to:
  /// **'Done: see you tomorrow morning.'**
  String get notifiche_invito_fatto;
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>[
    'ar',
    'de',
    'en',
    'es',
    'fr',
    'hi',
    'hu',
    'it',
    'ko',
    'pl',
    'pt',
    'ro',
    'ru',
    'uk',
    'zh',
  ].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return AppLocalizationsAr();
    case 'de':
      return AppLocalizationsDe();
    case 'en':
      return AppLocalizationsEn();
    case 'es':
      return AppLocalizationsEs();
    case 'fr':
      return AppLocalizationsFr();
    case 'hi':
      return AppLocalizationsHi();
    case 'hu':
      return AppLocalizationsHu();
    case 'it':
      return AppLocalizationsIt();
    case 'ko':
      return AppLocalizationsKo();
    case 'pl':
      return AppLocalizationsPl();
    case 'pt':
      return AppLocalizationsPt();
    case 'ro':
      return AppLocalizationsRo();
    case 'ru':
      return AppLocalizationsRu();
    case 'uk':
      return AppLocalizationsUk();
    case 'zh':
      return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
