# TAROTS chat — l'app (Android, iPhone, iPad)

L'app Flutter, identica alla versione mobile del sito (la v2: `frontend/v2`, `frontend/app/(v2)`). Fatte le **Fasi 7 e
8** del piano v9: le fondamenta e tutte le schermate del sito (struttura con barra dell'oracolo, banner della prova e
carrello; home, carta del giorno, carte, stese, mazzi, voto, negozio e carrello, rito di lettura, lettura delle proprie
carte, lettura condivisa, la mia storia e il dettaglio con condivisione e PDF, profilo con privacy, consensi,
abbonamento, esportazione ed eliminazione, prezzi coi codici sconto, prova gratuita, diario, privacy, pagine d'errore).
**Fase 9** (fatta): gli acquisti negli store (Google Play, App Store) con la verifica sul server, le notifiche push, il
collegamento fra sito e app (App Links e Universal Links, con la parte web della Fase 10). Niente pubblicità nell'app.

Strumenti su questo PC: Flutter in `E:\Dev\flutter\bin\flutter.bat`, JDK 17 in `E:\Dev\jdk-17`, Android SDK in
`E:\Dev\android-sdk`, emulatore `tarots_pixel`. Nei terminali aperti prima dell'installazione Flutter non è nel PATH:
si usa il percorso completo (qui sotto `flutter` per brevità).

## Comandi

Tutti da `mobile/`, salvo dove detto.

| Cosa | Comando |
|---|---|
| Dipendenze (rigenera anche le classi dei testi) | `flutter pub get` |
| Analisi (deve restare pulita) | `flutter analyze` |
| Test (unitari, contratto, golden) | `flutter test` |
| Test senza i golden (su un sistema che non è Windows) | `flutter test --exclude-tags golden` |
| Rigenerare i golden dopo una modifica voluta | `flutter test --update-goldens --tags golden` |
| Modelli (freezed, json) dopo aver cambiato `lib/modelli/` | `dart run build_runner build` |
| Testi dell'app dai dizionari della v2 | da `frontend/`: `node scripts/genera-arb.mjs`, poi `flutter gen-l10n` |
| Stile dell'app da `v2.css` | da `frontend/`: `node scripts/genera-token.mjs` |
| Controllo: testi e stile sono aggiornati? | da `frontend/`: `node scripts/controlla-mobile.mjs` (esce con 1 se no) |
| Schema OpenAPI per il test di contratto | `..\backend\.venv\Scripts\python.exe tool\genera_openapi.py` |
| Risultati attesi degli indirizzi (dal TypeScript del sito) | `node tool\indirizzi_attesi.mjs` |
| APK di prova | `flutter build apk --debug` (→ `build\app\outputs\flutter-apk\app-debug.apk`) |
| Le risposte dell'API di ogni golden, per il confronto | `flutter test tool/registra_rete_test.dart` |
| Il confronto col sito (catture + `confronto/rapporto.html`) | `python confronto\cattura_sito.py [--senza-testata]` |

Per la build Android servono `JAVA_HOME=E:\Dev\jdk-17` e `ANDROID_HOME=E:\Dev\android-sdk`.
`android/gradle.properties` spegne la compilazione incrementale di Kotlin: con la cache di pub su `C:` e il progetto
su `E:` si rompe («Could not close incremental caches»).

### L'app sull'emulatore con l'API locale

```
E:\Dev\android-sdk\emulator\emulator.exe -avd tarots_pixel
flutter run -d emulator-5554 --dart-define=API_URL=http://10.0.2.2:8100 --dart-define=SITO_URL=http://10.0.2.2:3000 --dart-define=AUTH_DISATTIVATA=true
```

`10.0.2.2` è il PC visto dall'emulatore. Da un telefono vero nella stessa rete: `http://192.168.1.91:8100` e `:3000`.
`AUTH_DISATTIVATA=true` è come `NEXT_PUBLIC_AUTH_DISABLED` del sito: l'app è «dentro» senza token e il backend locale
(con `TAROT_AUTH_DISABLED`) usa il suo utente di sviluppo. Un collegamento del sito apre la pagina nell'app:
`adb shell am start -a android.intent.action.VIEW -d https://tarots.chat/card-of-the-day chat.tarots.app`.

### Configurazione (`--dart-define`)

| Nome | Predefinito | Cosa |
|---|---|---|
| `API_URL` | `http://10.0.2.2:8100` | L'API FastAPI |
| `SITO_URL` | `http://10.0.2.2:3000` | Il sito (immagini delle carte `/cards/<id>.webp`) |
| `AUTH_DISATTIVATA` | `false` | La sessione di sviluppo |
| `KEYCLOAK_URL` | vuoto | Keycloak (`https://auth.tarots.chat`); vuoto = accesso non configurato |
| `KEYCLOAK_REALM` | `tarots` | Il realm |
| `KEYCLOAK_CLIENT_ID` | `tarot-mobile` | Il client pubblico dell'app (lo crea la Fase 6) |
| `KEYCLOAK_INSICURO` | `false` | Keycloak in http, solo in locale |
| `VERSIONE_APP` | `1.0.0` | Nell'agente delle statistiche e nella registrazione delle notifiche |
| `ACQUISTI_STORE` | `true` | Fase 9: si compra nello store; `false` torna al pagamento web della Fase 8 (comodo su un emulatore senza Play Store) |

## Struttura

```
mobile/
  lib/
    main.dart, app.dart        avvio (orientamento, cookie su disco, Firebase), MaterialApp col router
    config.dart                le --dart-define
    archivio.dart              preferenze locali (lingua, consensi, età, id delle statistiche, carrello, invito)
    tema/                      token.g.dart (GENERATO da v2.css) e gli stili di testo del sito
    l10n/                      app_<lingua>.arb e liste.g.dart (GENERATI dai dizionari), generato/ (gen-l10n)
    lingua/                    le 15 lingue, la scelta salvata, il verso del testo, la lingua del profilo
    rotte/                     percorsi (R), indirizzi (porting di indirizzi.ts), router, navigazione (vai, ancore)
    api/                       client dio (lingua, Bearer, rinnovo, cookie), errori, parser SSE, tutte le chiamate
    modelli/                   carte, stese, letture, profilo, cassa e abbonamenti, blog, voto, privacy (freezed + json)
    auth/                      Keycloak con flutter_appauth (Google su Android, Apple su iOS), cassaforte, sessione
    analytics/                 lanterna (statistiche interne), Tracciato (data-an), Firebase, identità del visitatore
    consensi/                  consensi del primo avvio e età minima
    dati/                      i provider dei dati, il carrello, gli inviti e la lettura condivisa d'origine
    cassa/                     pagamento con carta nel browser col ritorno all'app, codici sconto, cambio di piano
    acquisti/                  Fase 9: lo store (negozio.dart: Google Play e App Store), gli acquisti con la verifica
                               sul server (acquisti.dart), l'esito e «Ripristina gli acquisti» (vista.dart)
    notifiche/                 Fase 9: FCM e notifiche locali (push.dart), permesso, token, tocchi (notifiche.dart),
                               l'invito dopo la carta del giorno (invito.dart), il fuso del telefono (fuso.dart)
    componenti/                testata, piede, oracolo, banner della prova, dialogo, campi, bottoni, carte, diario…
    lettura/                   il rito (tavolo, ventaglio, preparazione, persone, dialogo, responso), condivisione, PDF
    catalogo/, profilo/, blog/ i pezzi comuni di quelle pagine (il markdown degli articoli è in blog/)
    pagine/                    una per rotta
  test/                        unitari e di widget per ogni area, contratto, golden/ (tutte le schermate, 3 misure)
  tool/                        genera_openapi.py, indirizzi_attesi.mjs, registra_rete_test.dart (rete per il confronto)
  confronto/                   cattura_sito.py (Playwright, Edge), schermate.json e rete/ (generati), rapporto.html,
                               catture/ (non nel repo), emulatore/
```

### Scelte

- **Una sola fonte per testi e stile**: gli ARB si generano dai dizionari TypeScript della v2 (letti col compilatore
  TypeScript del sito, quindi esattamente ciò che legge il sito), con `{segnaposto}` → argomenti ICU, `{uno, molti}` →
  plurali ICU (`=1`/`other`, come `plurale()`), gli a capo conservati (`nav_breve_*`, `testata_*`). Elenchi e mappe dei
  dizionari diventano voci appiattite (`home_temi_0_nome`) e tornano elenchi in Dart con `liste.g.dart`
  (`t.homeTemi`). Una voce nuova dell'inglese non ancora copiata nelle altre lingue usa l'inglese, con un avviso.
- **Gli stessi percorsi del sito**: le rotte sono le cartelle del sito (`/daily-card`, `/cards/:id`…); un indirizzo
  pubblico (`/card-of-the-day`, `/it/carta-del-giorno`, i vecchi `/carte/x`) passa da `indirizzi.dart`, lo stesso codice
  del proxy del sito, verificato indirizzo per indirizzo contro il TypeScript.
- **Orientamento**: telefono in verticale, iPad (e tablet) in tutte le orientazioni (motivi in `lib/main.dart`).
- **Fedeltà al CSS**: misure in px logici come i px CSS, `clamp()` e `vw` calcolati sulla larghezza, interlinea
  distribuita come nel browser, `text-wrap: balance` (titoli) e `pretty` (paragrafi) riprodotti, `ch` misurato sul
  carattere, la testata del telefono con l'algoritmo flex del sito (basi, spazio che avanza, `min-content`).
- **Statistiche come il sito** (Fase 8): lanterna manda sempre il livello base (visite, tempo attivo, tocchi, eventi,
  senza identificativo: il server conta con un'impronta che cambia ogni giorno), come `osservatore.tsx` e
  `lib/analytics.ts` del sito; l'identificativo dell'installazione (livello esteso) solo col consenso `statistiche`, e
  la revoca lo fa dimenticare anche al server. Firebase solo col consenso `google_analytics`. Il percorso mandato è
  quello che il sito manderebbe per la stessa pagina.

## Attivare Firebase (statistiche Google e notifiche)

Oggi Firebase non è configurato: all'avvio il log dice «Firebase inattivo…» e «Notifiche spente…», le statistiche
Google e le notifiche restano spente (nel profilo, sezione «Notifiche»: «Le notifiche non sono ancora disponibili in
questa versione dell'app»); tutto il resto funziona, anche le preferenze delle notifiche (valgono per il sito). Per
attivarlo, una volta:

1. Su https://console.firebase.google.com/ (account Google dell'attività) un progetto, con un'app **Android**
   `chat.tarots.app` e un'app **Apple** `chat.tarots.app` (Google Analytics collegato al GA4 del sito, se si vogliono i
   dati insieme). È lo stesso progetto del service account caricato in console → Notifications → Impostazioni.
2. Scaricare `google-services.json` in `android/app/` e `GoogleService-Info.plist` in `ios/Runner/` (aggiunto al
   target Runner in Xcode o da Codemagic). I due file non vanno nel repo (`.gitignore`): Codemagic li mette alla build.
3. Android: aggiungere il plugin Gradle `com.google.gms.google-services` (in `android/settings.gradle.kts` e
   `android/app/build.gradle.kts`), oppure lanciare `flutterfire configure` che lo fa da sé.
4. Per iPhone e iPad: la chiave APNs `.p8` in Firebase (Impostazioni progetto → Cloud Messaging → app Apple), vedi
   `deploy/k8s/LEGGIMI.md`, «Notifiche».
5. Niente da cambiare nel codice: `avviaFirebase()` (`lib/analytics/firebase.dart`) trova la configurazione.
   - Statistiche: la raccolta resta spenta (`firebase_analytics_collection_enabled=false`,
     `FIREBASE_ANALYTICS_COLLECTION_ENABLED=false`) e si accende solo col consenso `google_analytics`. Niente AD_ID
     (rimosso dal manifesto), niente IDFA (AdSupport non collegato), schermate mandate a mano col percorso del sito.
   - Notifiche: nessun token FCM finché la persona non le accende (`firebase_messaging_auto_init_enabled=false`,
     `FirebaseMessagingAutoInitEnabled=false`); il permesso si chiede solo dopo un sì (vedi sotto).
6. Prova: console → Notifications → Campagne → «invia a me», con l'app accesa su un telefono vero (sull'emulatore
   serve un'immagine «Google Play»).

## Fase 9: gli acquisti negli store

Su Android si compra con **Google Play**, su iPhone e iPad con l'**App Store** (`in_app_purchase`, StoreKit 2). La
pagina dei prezzi mostra i prodotti dello store coi **prezzi dello store** (nella valuta del telefono); il **pagamento
con carta** (Stripe, nel browser) compare solo dove la console lo ammette per il paese dello store (App mobili →
Politica Stripe): è lì, e solo lì, che valgono i **codici sconto** (negli store no). Il codice regalo vale sempre.

Come funziona un acquisto (`lib/acquisti/acquisti.dart`):

1. il catalogo viene dal server (`GET /billing/store/catalogo?piattaforma=&paese_store=`) col token dell'account,
   che va allo store (`obfuscatedAccountId` su Google, `appAccountToken` su Apple): un acquisto non può finire su un
   altro account;
2. lo store fa pagare; l'acquisto arriva all'app e va **subito al server** (`POST /billing/store/google/verifica` o
   `apple/verifica`), che lo rilegge dallo store e accredita una volta sola;
3. **solo dopo** l'app lo chiude presso lo store (Apple `finish`; su Google il server consuma il pacchetto o conferma
   l'abbonamento da sé, l'app lo fa solo se il server non c'è riuscito). Un acquisto che il server non ha registrato
   non si chiude: si riprova all'accesso e al ritorno in primo piano (Google lo rimborsa da solo dopo 3 giorni se
   nessuno lo conferma, Apple lo ridà all'avvio);
4. **in attesa** (un pagamento in contanti su Google, «Chiedi di acquistare» su Apple): niente crediti, un avviso;
   arrivano quando lo store incassa;
5. «**Ripristina gli acquisti**» (Apple lo chiede) rimanda allo store e poi al server ciò che lo store ha;
6. un abbonamento si **cambia** nello stesso store (Google col conguaglio, Apple nello stesso gruppo); se è stato
   pagato con carta o nell'altro store, la pagina lo dice. Nel profilo, «Gestisci in Google Play / App Store» apre la
   pagina dello store sull'abbonamento (Google `…/subscriptions?sku=…&package=chat.tarots.app`, Apple
   `showManageSubscriptions`).

Gli errori sono detti in chiaro (altro account, rete, store che non risponde, già posseduto, annullato…); un telefono
senza Play Store (l'emulatore `tarots_pixel`) mostra «Gli acquisti con Google Play non sono disponibili su questo
dispositivo». Per provare il pagamento web su un emulatore così: `--dart-define=ACQUISTI_STORE=false`.

### Cosa fare in Play Console (Android)

1. **Prodotti**: Monetizza → Prodotti in-app (i pacchetti: `crediti_5`, `crediti_15`, `crediti_50`) e Abbonamenti
   (per esempio `abbonamento_base` e `abbonamento_oro`, ognuno coi base plan `mensile`, `annuale` e, per la prova,
   `prova`: l'annuale a metà prezzo con un'offerta «prova gratuita 14 giorni» per i nuovi clienti). Poi in console del
   sito → App mobili → Prodotti si collega ogni prodotto al suo piano (`abbonamento_oro:prova` come «annuale prova»).
   Dettagli: `deploy/k8s/LEGGIMI.md`, «Acquisti negli store».
2. **Test delle licenze**: Impostazioni → Test delle licenze, gli account Gmail dei tester (comprano senza addebito).
3. L'app deve essere **caricata almeno in un canale di test** (test interno) perché i prodotti si vedano: un APK
   installato a mano con la stessa firma va bene per provare, ma il package deve esistere in Play Console.
4. Le **impronte SHA-256** dei certificati (Test e rilascio → Configurazione → Integrità dell'app → Firma dell'app:
   chiave di firma e chiave di caricamento) vanno copiate in console del sito → App mobili → Android → «Collegamenti
   del sito nell'app»: servono agli App Links (sotto). Quella della chiave di debug di questo PC (per provare un APK di
   debug) è `0C:BA:84:BC:B8:3D:15:90:AB:4B:ED:EA:C4:14:3E:E9:55:FB:8B:CB:7E:1D:01:2A:43:10:3F:73:76:48:36:3E`.

## Fase 9: le notifiche

- **Permesso in due tempi**, come sul sito: mai all'avvio. Dopo aver girato la carta del giorno l'app chiede «Vuoi
  che te la ricordiamo ogni mattina?» (un «non ora» la fa tacere un mese); oppure profilo → «Notifiche» → «Attiva le
  notifiche qui». Solo allora il telefono chiede il permesso (Android 13+ e iOS).
- Dato il permesso, il token FCM va a `POST /me/dispositivi` con piattaforma, lingua, fuso (`flutter_timezone`) e
  versione dell'app; di nuovo a ogni avvio, a ogni token nuovo e a ogni cambio di lingua. All'**uscita** (e prima di
  chiudere l'account) `DELETE /me/dispositivi` con la sessione ancora valida, e il token si cancella.
- Il **tocco** apre la pagina del `link` della notifica (un percorso del sito: `/daily-card` → la stessa rotta
  dell'app) e la segna come aperta (`POST /notifiche/aperta`).
- **Due canali Android** coi nomi nella lingua dell'app: «Carta del giorno e promemoria» (`servizio`) e «Offerte e
  novità» (`promozioni`): la persona può spegnere le promozioni dalle impostazioni del telefono. Con l'app aperta le
  notifiche le mostra l'app, con l'**immagine grande** se c'è; con l'app chiusa le mostra Firebase (anche l'immagine).
- La sezione «Notifiche» del profilo è quella del sito (carta del giorno e ora, promemoria, offerte — lo stesso
  consenso «Promozioni», che il link «niente più promozioni» spegne —, ore di silenzio, fuso).
- Il fuso del telefono va sul profilo a ogni avvio (decide il giorno della carta del giorno, che l'app chiede con
  `?fuso=` come il sito).

## Fase 9: l'account

Eliminazione ed esportazione funzionano dall'app (profilo → Privacy e consensi; pagina `/account/elimina`): prima di
chiedere la cancellazione il telefono esce dalle notifiche dell'account, poi l'app esce da sola (revoca del token
offline, token locali cancellati: il server ha già chiuso le sessioni) e mostra la data della cancellazione. Chi ha un
abbonamento di uno store legge, prima e dopo, che va disdetto nello store (col bottone per farlo). Resta aperto,
lato backend, la revoca del token presso Apple (`tarot/cancellazione.py`, TODO della Fase 6).

## Collegamenti fra sito e app (Fase 10, parte web)

- **Android App Links**: nel manifesto un filtro `autoVerify` per `https://tarots.chat` **solo sulle pagine
  dell'app** (le stesse di `PERCORSI_APP` nel backend; mai `/auth` — il ritorno del login di Google passa di lì —,
  `/api`, `/admin`, `/old`); `www.tarots.chat` (che reindirizza) sta in un filtro senza verifica. Android verifica con
  `https://tarots.chat/.well-known/assetlinks.json`, che il sito scrive coi valori della console (package e impronte).
  Il ritorno da un pagamento con carta su Android è `https://tarots.chat/pricing?checkout=…`, che così si apre
  nell'app. Controllo sul telefono: `adb shell pm get-app-links chat.tarots.app` («verified» accanto a tarots.chat;
  per riprovare la verifica `adb shell pm verify-app-links --re-verify chat.tarots.app`).
- **iOS Universal Links** (scritti, non compilati): `ios/Runner/Runner.entitlements` con `applinks:tarots.chat`; il
  sito pubblica `/.well-known/apple-app-site-association` con Team ID, bundle ID e percorsi dalla console → App mobili
  → iOS. Il ritorno da un pagamento resta il deep link `chat.tarots.app://ritorno/…`.

### iOS: cosa resta quando si deciderà di compilare

1. Apple Developer → Identifiers → `chat.tarots.app`: accendere **Push Notifications**, **Associated Domains**, **In-App
   Purchase** e «Sign in with Apple»; rigenerare i profili (Codemagic lo fa con la chiave di App Store Connect).
2. `GoogleService-Info.plist` in `ios/Runner/` e la chiave APNs in Firebase (sopra).
3. In console → App mobili → iOS il **Team ID** (senza, `apple-app-site-association` è vuoto).
4. La **Notification Service Extension** per l'immagine grande: il codice è in `ios/ImmagineNotifica/`
   (`NotificationService.swift`, `Info.plist`), senza dipendenze. Va aggiunta al progetto: Xcode → File → New → Target
   → Notification Service Extension, nome `ImmagineNotifica`, bundle id `chat.tarots.app.ImmagineNotifica`,
   deployment target 15.0; sostituire i file creati da Xcode con quelli della cartella; «Embed» nel target Runner.
   L'estensione ha bisogno del suo App ID e profilo (Codemagic li crea se ha la chiave API).
5. `aps-environment` in `Runner.entitlements` è `development`: il profilo di distribuzione lo porta a `production`.
6. Prova: sandbox di Apple (account di prova in App Store Connect → Utenti e accesso → Sandbox), TestFlight.
   `AppDelegate.swift` ha il canale `chat.tarots.app/store` per `showManageSubscriptions` e il delegato delle
   notifiche: è codice scritto ma mai compilato, da controllare alla prima build.

## Fase 8: scelte e differenze dal sito

- **Pagamenti con carta** (dalla Fase 9 solo per il carrello del negozio fisico e dove la console ammette la carta):
  il checkout web (Stripe, o il simulatore del backend) si apre nel browser di sistema. Su iPhone il
  ritorno è il deep link `chat.tarots.app://ritorno/<percorso>?checkout=<id>` (schema ammesso da
  `ritorno_schemi_app` del backend). Su Android no: lo schema `chat.tarots.app` è già del ritorno dell'accesso
  (flutter_appauth) e un secondo filtro faceva scegliere fra due «TAROTS chat»; il ritorno è la pagina del sito
  (`https://tarots.chat/pricing?checkout=<id>`), che con `assetlinks.json` (Fase 10, qui sotto) si apre
  direttamente nell'app. In ogni caso, tornata in primo piano, l'app va da sé alla pagina di ritorno
  (`lib/cassa/ritorno.dart`) e chiede l'esito al server.
- **Collegamento col sito** (Fase 6): nel profilo «Hai già un account sul sito?» crea un codice
  (`POST /me/collega/codice`) da inserire nel profilo del sito entro 10 minuti; l'app lo propone da sé al primo
  accesso con un'email nascosta di Apple (`@privaterelay.appleid.com`). Usato il codice, il token dell'app non vale
  più: la sessione si chiude con un avviso chiaro e il pulsante per rientrare (`lib/profilo/codice_app.dart`). Se il
  nome manca, il profilo lo chiede come il sito.
- **Prova del rito anonimo in locale**: con `TAROT_AUTH_DISABLED` l'API tratta ogni richiesta come l'utente di
  sviluppo; per il rito senza account serve una seconda API sullo stesso database senza quella variabile.
- **Barra dell'oracolo**: per chi non ha un account i temi dei dizionari; per chi è dentro la chat proattiva, con il
  tetto per visita di `/impostazioni-chat` (una visita: l'app aperta, ricomincia dopo mezz'ora in secondo piano).
- **Statistiche come il sito** (vedi sopra) e testi dei consensi dell'app nella sezione `app` dei dizionari
  (`frontend/v2/i18n/<lingua>/app.ts`, sei lingue tradotte).
- **Markdown degli articoli**: il parser ufficiale `markdown` (dart-lang), disegnato con le regole del CSS e con le
  direttive di `direttive-blog.ts`. I video si aprono fuori dall'app.
- **File**: l'archivio dei propri dati, i PDF degli ordini e l'immagine di una lettura passano dal foglio di
  condivisione del telefono; «Stampa in PDF» compone il PDF nell'app (`printing`).
- Differenze rimaste e motivi: nel rapporto della Fase 8 e in `confronto/rapporto.html`.

## Cosa manca (Fase 10)

- **Fase 6** (backend, fatta): il client Keycloak `tarot-mobile` (PKCE, redirect `chat.tarots.app:/oauth2redirect`,
  `offline_access`) e l'estensione Apple. L'accesso vero non è ancora provato dall'app (i test usano un Keycloak finto).
- **iOS**: il codice è scritto ma, per decisione dell'operatore, non si compila (niente build iOS né Codemagic) fino
  alla versione definitiva (sopra, «iOS: cosa resta»).
- **Fase 9, da provare con gli store veri**: un acquisto con un tester di Play (license testing) e con la sandbox di
  Apple, un rimborso di prova → storno, le notifiche su un telefono vero con Firebase configurato.
- **Fase 10**: `codemagic.yaml`, firma di rilascio (keystore fuori dal repo), icone e schermata d'avvio con il marchio
  (anche l'icona piccola delle notifiche, oggi una stella provvisoria in `res/drawable/ic_notifica.xml`), schede degli
  store, Data Safety e privacy label.
